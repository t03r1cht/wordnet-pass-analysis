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
    description="Password hash anaylsis using WordNet and the HaveIBeenPwned database")
parser.add_argument("-p", "--pass-database", type=str,
                    help="Path to the HIBP password database", dest="pass_db_path")
parser.add_argument("-d", "--depth", type=int,
                    help="Depth in the DAG", dest="dag_depth")
parser.add_argument("-t", "--total", type=int,
                    help="Set the maximum number of lemmas that should be processed.", dest="max_lemmas_processed")
parser.add_argument("-g", "--graph", type=int,
                    help="Display a directed graph for WordNet.", dest="draw_dag")
parser.add_argument("-s", "--root-syn-name", type=str,
                    help="Name of the word specified to be the root synset.", dest="root_syn_name")
args = parser.parse_args()

total_processed = 0
started = ""
outfile_name = "results.txt"
outfile_f = open(outfile_name, "w+")
translation_handler = None


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
    Return the current time, nicely formatted as a string.
    """
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


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
        for lemma in hypo.lemma_names():
            # Apply a set of translators to each lemma
            translations_for_lemma(lemma, hypo.min_depth())
        # Execute the function again with the new root synset being each hyponym we just found.
        recurse_nouns_from_root(
            root_syn=hypo, start_depth=start_depth, rel_depth=rel_depth)


def translations_for_lemma(lemma, depth):
    """
    Compute all translations by using the registered translator.
    """
    for translation_handler in translator.all:
        # The translator returns the translated lemma.
        trans = translation_handler(lemma)
        # In some cases, translator may return a variable list of translations.
        if type(trans) == list:
            for p in trans:
                lookup(p, depth)
        else:
            lookup(trans, depth)


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
    _write_to_results_file("%s%s %d" % (
        lemma_depth * "  ", lemma_name, occurrences))


def _write_summary_to_result_file():
    """
    Writes the bottom lines containing the summary to the result file.
    """
    _write_to_results_file("")
    _write_to_results_file(40 * "=")
    _write_to_results_file("Starting Time: %s" % started_time)
    _write_to_results_file("Total lemmas processed: %d" % total_processed)
    finished_time = get_curr_time()
    print("  Finished: %s" % finished_time)
    _write_to_results_file("Finishing Time: %s" % finished_time)


def _write_to_results_file(s):
    """
    Writes generic data to the result file.
    """
    outfile_f.write("%s\n" % s)


def _proper_shutdown():
    _write_summary_to_result_file()
    print()
    print("  Results written to %s" % outfile_name)
    cleanup()


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


if __name__ == "__main__":
    if args.draw_dag == 1:
        from wn_graph import draw_graph
        draw_graph(args.root_syn_name, args.dag_depth)
    else:
        init()
        signal.signal(signal.SIGINT, sigint_handler)
        clear_terminal()
        nltk.download("wordnet")
        print()
        root_synsets = wn.synsets(args.root_syn_name)
        if len(root_synsets) == 0:
            print("  No synset found for: %s" % root_syn_name)
            sys.exit(0)
        # If multiple synsets were found, prompt the user to choose which one to use.
        if len(root_synsets) > 1:
            choice_root_syn = prompt_synset_choice(root_synsets)
        else:
            choice_root_syn = root_synsets[0]

        started_time = get_curr_time()

        print(choice_root_syn.lemma_names())
        for root_lemma in choice_root_syn.lemma_names():
            translations_for_lemma(root_lemma, choice_root_syn.min_depth())
            inc_total_processed()
        recurse_nouns_from_root(
            root_syn=choice_root_syn, start_depth=choice_root_syn.min_depth(), rel_depth=args.dag_depth)

        _proper_shutdown()
        print()
        cleanup()
