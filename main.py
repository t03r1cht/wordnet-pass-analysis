from nltk.corpus import wordnet as wn
import nltk
import hashlib
import timeit
import subprocess
from subprocess import CalledProcessError
import time
import sys
import random
import shutil
import signal
from colorama import init, Fore, Back, Style
import platform
import os
import datetime
import sys
import argparse
from translators import translator_registrar, translator


# pip installation über py binary: py -m pip install nltk

parser = argparse.ArgumentParser(
    description="Password hash anaylsis using WordNet and the HaveIBeenPwned database.")
parser.add_argument("-p", "--pass-database", type=str,
                    help="Path to the HIBP password database.", dest="pass_db_path")
parser.add_argument("-d", "--depth", type=int,
                    help="Depth in the DAG", dest="dag_depth")
parser.add_argument("-t", "--total", type=int,
                    help="Set the maximum number of lemmas that should be processed.", dest="max_lemmas_processed")
parser.add_argument("-g", "--graph", action="store_true",
                    help="Display a directed graph for WordNet.", dest="draw_dag")
parser.add_argument("-s", "--root-syn-name", type=str,
                    help="Name of the word specified to be the root synset.", dest="root_syn_name")
parser.add_argument("-c", "--classification", action="store_true",
                    help="Subsume the hits for each class of the search hierarchy.", dest="subsume_for_classes")
parser.add_argument("-r", "--result-file", type=str,
                    help="Name of the result file.", dest="result_file_name")
parser.add_argument("-z", "--is-debug", action="store_true",
                    help="Debug mode.", dest="is_debug")
args = parser.parse_args()

total_processed = 0
started = ""
translation_handler = None
hits_for_lemmas = {}
total_found = 0


def sigint_handler(sig, frame):
    """
    Register the handler for the SIGINT signal.

    This is absolutely necessary to exit the program with Ctrl+C because a user easily misconfigure the
    programe (i.e. -d > 4) for it to result in a combinatorial explosion because of its recursion.
    """
    print()
    print("Caught Ctrl+C, shutting down...")
    cleanup()
    sys.exit(0)


def cleanup():
    """
    Some cleanup work like closing the file handler.
    """
    outfile_f.close()


def get_shell_width():
    """
    Return the number of colums in the current shell view.
    """
    cols, _ = shutil.get_terminal_size((80, 20))
    return cols


def get_curr_time():
    """
    Return the current time as a string.
    """
    return datetime.datetime.now().strftime("%Y%m%d_%H.%M.%S")


def clear_terminal():
    """
    Clear the terminal. This is required to properly display the stats while running.
    """
    os.system("clear") if platform.system(
    ) == "Linux" or platform.system() == "Darwin" else os.system("cls")


def update_stats(current, finished):
    """
    Print out the stats while the program is running.
    """
    if not args.is_debug:
        clear_terminal()
        print()
        print()
        c_t = get_curr_time()
        print("  WordNet Password Analysis // Time: %s" % c_t)
        print()
        global started
        print("  Started: \t%s" % started)
        print("  Processing: \t%s" % current)
        print("  Done: \t%d" % finished)
        print()


def lookup_pass(hash):
    """
    Wrapper for _lookup_in_hash_file. Returns the occurrences of the
    searched hash/password in the HIBP password file.
    """
    occurrences = _lookup_in_hash_file(hash)
    if occurrences is None:
        return 0
    else:
        return int(occurrences.split(":")[1])


def _lookup_in_hash_file(hash):
    """
    Implements actual file access.
    """
    try:
        result = subprocess.check_output(
            ["look", "-f", hash, args.pass_db_path])
    except CalledProcessError as e:
        return None
    return result.decode("utf-8").strip("\n").strip("\r")


def hash_sha1(s):
    """
    Hash the password.
    """
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


def recurse_nouns_from_root(root_syn, start_depth, rel_depth=1):
    """
    Iterates over each hyponym synset until the desired depth in the DAG is reached.

    For each level of hyponyms in the DAG, this function will unpack each lemma of each
    synset of said depth level, which can be confusing when looking at results.txt.

    Each indented set of lemmas is the sum of all unpacked lemmas of each synset of the current graph level.
    """

    # If the current depth in the DAG is reached, do not continue to iterate this path.
    if (root_syn.min_depth() - start_depth) >= rel_depth:
        return
    curr_root_syn = root_syn
    for hypo in curr_root_syn.hyponyms():
        total_hits = 0
        for lemma in hypo.lemma_names():
            # Apply a set of translators to each lemma
            lemma_hits = translations_for_lemma(lemma, hypo.min_depth())
            total_hits += lemma_hits
            #print("finished %s with %d hits" % (lemma, lemma_hits))
            print()
        print(hypo.min_depth())
        print("%s%s: %d" % (hypo.min_depth() * "  ", hypo.name(), total_hits))
        append_with_hits(hypo.name(), total_hits)
        # Execute the function again with the new root synset being each hyponym we just found.
        recurse_nouns_from_root(
            root_syn=hypo, start_depth=start_depth, rel_depth=rel_depth)


def translations_for_lemma(lemma, depth):
    """
    Create all translations by using the registered translator using the lemma as base.
    """
    total_hits = 0
    for translation_handler in translator.all:
        # The translator returns the translated lemma.
        trans = translation_handler(lemma)
        # In some cases, translator may return a variable list of translations.

        if type(trans) == list:
            for p in trans:
                trans_hits = lookup(p, depth)
                total_hits += trans_hits
        else:
            total_hits += lookup(trans, depth)
    return total_hits


def lookup(translation, depth):
    """
    Hashes the (translated) lemma and looks it up in  the HIBP password file.
    """
    # Hash and lookup translated lemma
    hashed_lemma = hash_sha1(translation)
    occurrences = lookup_pass(hashed_lemma)
    # Handle the -t parameter
    if args.max_lemmas_processed is not None:
        if total_processed >= args.max_lemmas_processed:
            _proper_shutdown()
            sys.exit(0)
    # Increment "total" counter
    inc_total_processed()
    update_stats(current="%s / %d" %
                 (translation, occurrences), finished=total_processed)

    # Print the translations to the result file.
    _write_result_to_results_file(translation, depth, occurrences)

    # Return occurrences in order to be able to subsume them for each class.
    global total_found
    total_found += occurrences
    return occurrences


def append_with_hits(lemma, total_hits):
    global hits_for_lemmas
    if lemma in hits_for_lemmas:
        hits_for_lemmas[lemma] += total_hits
    else:
        hits_for_lemmas[lemma] = total_hits


def inc_total_processed():
    """
    Increment the global variable to track the overall progress of processed lemmas.
    """
    global total_processed
    total_processed += 1


def _write_result_to_results_file(lemma_name, lemma_depth, occurrences):
    """
    Writes a properly indented result to the result file.
    """
    if not args.subsume_for_classes:
        _write_to_results_file("%s%s %d" % (
            lemma_depth * "  ", lemma_name, occurrences))


def _write_summary_to_result_file(started_time, root_syn):
    """
    Writes the bottom lines containing the summary to the result file.
    """
    if args.subsume_for_classes:
        global hits_for_lemmas
        for k, v in hits_for_lemmas.items():
            _write_to_results_file("%s: %d" % (k, v))

    _write_to_results_file("")
    _write_to_results_file(40 * "=")
    _write_to_results_file("")
    _write_to_results_file("Search Lemma: %s" % root_syn.name())
    _write_to_results_file("Search Lemma Synonyms: %s" %
                           root_syn.lemma_names())
    _write_to_results_file("Search Lemma Definition: %s" %
                           root_syn.definition())
    _write_to_results_file("Search Lemma Examples: %s" % root_syn.examples())
    _write_to_results_file("Total Lemmas Processed: %d" % total_processed)
    global total_found
    _write_to_results_file(
        "Total hits for password searches: %d" % total_found)
    finished_time = get_curr_time()
    _write_to_results_file("Starting Time: %s" % started_time)
    print("  Finished: %s" % finished_time)
    _write_to_results_file("Finishing Time: %s" % finished_time)


def _write_to_results_file(s):
    """
    Writes generic data to the result file.
    """
    outfile_f.write("%s\n" % s)


def prompt_synset_choice(root_synsets):
    print("  Multiple synset were found. Please choose: ")
    for elem in range(len(root_synsets)):
        print("    [%d] %s" % (elem, root_synsets[elem]))
    print()
    choice = input("Your choice [0-%d]: " % ((len(root_synsets)-1)))
    try:
        int_choice = int(choice)
    except ValueError:
        print("Invalid choice: %s" % choice)
        return
    if int_choice < 0 or int_choice > len(root_synsets) - 1:
        print("Invalid choice: %s" % choice)
        return
    # Make the choice the new root synset from we will start our recursion.
    return root_synsets[int_choice]


def _download_wordnet():
    """
    """
    nltk.download("wordnet")


def option_draw_graph():
    """
    Draw the graph.
    """
    from wn_graph import draw_graph
    draw_graph(args.root_syn_name, args.dag_depth)


"""
alle begriffe aus abs lvl x
suche nach allen lemmas in lvl
1 lvl verknüpfung --> stark verbunden
"""


def option_lookup_passwords():
    """
    Lookup the passwords in the pwned passwords list.
    """
    init()
    signal.signal(signal.SIGINT, sigint_handler)
    clear_terminal()
    print()
    started_time = get_curr_time()
    # Open the file handler for a file with the starting time
    if args.result_file_name is not None:
        outfile_name = args.result_file_name
    else:
        outfile_name = "{0}_{1}.txt".format(started_time, args.root_syn_name)
    global outfile_f
    outfile_f = open(outfile_name, "w+")

    root_synsets = wn.synsets(args.root_syn_name)
    if len(root_synsets) == 0:
        print("  No synset found for: %s" % root_syn_name)
        sys.exit(0)

    # If multiple synsets were found, prompt the user to choose which one to use.
    if len(root_synsets) > 1:
        choice_root_syn = prompt_synset_choice(root_synsets)
    else:
        choice_root_syn = root_synsets[0]
    first_level_hits = 0
    print(choice_root_syn.min_depth())
    print(choice_root_syn.name())
    for root_lemma in choice_root_syn.lemma_names():
        hits = translations_for_lemma(
            root_lemma, choice_root_syn.min_depth())
        first_level_hits += hits
        inc_total_processed()
    print("%s%s: %d" % (choice_root_syn.min_depth() *
                        "  ", choice_root_syn.name(), first_level_hits))

    append_with_hits(choice_root_syn.name(), first_level_hits)

    global total_found
    total_found += first_level_hits
    hits_below = recurse_nouns_from_root(
        root_syn=choice_root_syn, start_depth=choice_root_syn.min_depth(), rel_depth=args.dag_depth)
    # Shutdown the script
    _write_summary_to_result_file(started_time, choice_root_syn)
    print()
    print("  Results written to %s" % outfile_name)
    print()
    cleanup()


if __name__ == "__main__":
    try:
        from nltk.corpus import wordnet as wn
    except ImportError:
        _download_wordnet()
    if args.draw_dag:
        # Evaluate command line parameters
        if args.dag_depth is None or args.root_syn_name is None:
            print("Error: Missing parameters.")
            parser.print_usage()
            sys.exit(0)
        print("Running platform pre-check...")
        if "Linux" in platform.platform():
            print(
                "You are running this script on Linux (%s). Due to currently unresolved bugs, the graph feature can only be used on Windows and MacOS." % platform.platform())
            sys.exit(0)
        option_draw_graph()
    else:
        # Evaluate command line parameters
        if args.pass_db_path is None or args.dag_depth is None or args.root_syn_name is None:
            print("Error: Missing parameters.")
            parser.print_usage()
            sys.exit(0)
        option_lookup_passwords()
