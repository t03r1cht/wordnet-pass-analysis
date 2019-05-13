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
from permutators import permutator_registrar, permutator
from collections import OrderedDict
import collections
from yaspin import yaspin


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
parser.add_argument("--result-file", type=str,
                    help="Name of the result file.", dest="result_file_name")
parser.add_argument("--summary-file", type=str,
                    help="Name of the summary file.", dest="summary_file_name")
# parser.add_argument("-z", "--is-debug", action="store_true",
#                     help="Debug mode.", dest="is_debug")
args = parser.parse_args()

total_processed = 0
started = ""
permutation_handler = None
hits_for_lemmas = OrderedDict()
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
    outfile_summary.close()
    outfile_passwords.close()


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
    if not args.subsume_for_classes:
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
    # Example:  rel_depth = 3, curr = 9, start = 7
    #           9 - 5 = 4,
    if (root_syn.min_depth() - start_depth) >= rel_depth:
        return 0, 0
    curr_root_syn = root_syn
    hits_below = 0
    total_hits_for_current_synset = 0
    not_found_for_current_synset = 0
    for hypo in curr_root_syn.hyponyms():
        total_hits = 0
        not_found = 0
        for lemma in hypo.lemma_names():
            # Apply a set of permutations to each lemma
            lemma_hits, not_found_cnt = permutations_for_lemma(
                lemma, hypo.min_depth())
            total_hits += lemma_hits
            total_hits_for_current_synset += lemma_hits
            not_found += not_found_cnt
            not_found_for_current_synset += not_found_cnt
        # Execute the function again with the new root synset being each hyponym we just found.
        hits_below, not_found_below = recurse_nouns_from_root(
            root_syn=hypo, start_depth=start_depth, rel_depth=rel_depth)
        # Add the sum of all hits below the current synset to the hits list of the current synset so
        # below hits are automatically included (not included in the terminal output, we separate both these
        # numbers into total_hits and hits_below so we can distinguis how many hits we found below and how
        # many were produced by the current synset).
        # Works because of... recursion
        total_hits_for_current_synset += hits_below
        not_found_for_current_synset += not_found_below
        if args.subsume_for_classes:
            append_with_hits(hypo, total_hits, hits_below,
                             not_found, not_found_below)
    return total_hits_for_current_synset, not_found_for_current_synset


def permutations_for_lemma(lemma, depth):
    """
    Create all permutatuons by using the registered permutator using the lemma as base.
    """
    total_hits = 0
    not_found_cnt = 0
    for permutation_handler in permutator.all:
        # The permutator returns the permutated lemma.
        trans = permutation_handler(lemma)
        # In case some permutators could not be applied to the lemma
        # For example when a lemma solely consists of vowels and one permutator strips vowels.
        # That would leave us with a NoneType password.
        if trans == None:
            continue
        # In some cases, permutator may return a variable list of permutations.
        if type(trans) == list:
            for p in trans:
                trans_hits = lookup(p, depth)
                total_hits += trans_hits
                if trans_hits == 0:
                    not_found_cnt += 1
        else:
            total_hits += lookup(trans, depth)
            not_found_cnt += 1
    return total_hits, not_found_cnt


def lookup(permutation, depth):
    """
    Hashes the (translated) lemma and looks it up in  the HIBP password file.
    """
    # Hash and lookup translated lemma
    hashed_lemma = hash_sha1(permutation)
    occurrences = lookup_pass(hashed_lemma)
    # Handle the -t parameter
    if args.max_lemmas_processed is not None:
        if total_processed >= args.max_lemmas_processed:
            sys.exit(0)
    # Increment "total" counter
    inc_total_processed()
    # Print the permutations to the result file.
    _write_result_to_passwords_file(permutation, depth, occurrences)

    # Return occurrences in order to be able to subsume them for each class.
    global total_found
    total_found += occurrences
    return occurrences


def append_with_hits(lemma, total_hits, below_hits, not_found, not_found_below):
    global hits_for_lemmas
    res_set = [lemma, total_hits, below_hits, not_found, not_found_below]
    if lemma.name() in hits_for_lemmas:
        hits_for_lemmas[lemma.name()][1] += total_hits
    else:
        hits_for_lemmas[lemma.name()] = res_set


def inc_total_processed():
    """
    Increment the global variable to track the overall progress of processed lemmas.
    """
    global total_processed
    total_processed += 1


def _write_result_to_passwords_file(lemma_name, lemma_depth, occurrences):
    """
    Writes a properly indented result to the result file.
    """
    _write_to_passwords_file("%s%s %d" % (
        lemma_depth * "  ", lemma_name, occurrences))


def _write_summary_to_result_file(opts):
    """
    Writes the bottom lines containing the summary to the result file.
    """

    with yaspin(text="Writing summary to result file...", color="cyan") as sp:

        # If we set the -c flag, instead of logging the single passwords that were searched,
        # we print only their respective classes to the result file
        if args.subsume_for_classes:
            _write_to_summary_file("")
            _write_to_summary_file(40 * "=")
            _write_to_summary_file("")
            _write_to_summary_file("    *** Synset Distribution ***")
            _write_to_summary_file("")

            global hits_for_lemmas
            reversed_dict = collections.OrderedDict(
                reversed(list(hits_for_lemmas.items())))

            # The hits_for_lemmas dictionary contains all synset names (name.pos.nn) and their sum of hits
            for k, v in reversed_dict.items():
                synset_id = v[0].name()
                this_hits = v[1]
                below_hits = v[2]
                total_hits = v[1] + v[2]
                this_not_found = v[3]
                below_not_found = v[4]
                total_not_found = v[3] + v[4]
                _write_to_summary_file("%s%s,total_found=%d,this_found=%d,below_found=%d,total_not_found=%d,this_not_found=%d,below_not_found=%d," % (
                    (v[0].min_depth() - opts["start_depth"]) *
                    "  ",  # indendation
                    synset_id,  # synset id
                    total_hits,  # hits of each synset
                    this_hits,
                    below_hits,
                    total_not_found,
                    this_not_found,
                    below_not_found))

        _write_to_summary_file("")
        _write_to_summary_file(40 * "=")
        _write_to_summary_file("")
        _write_to_summary_file("    *** Summary ***")
        _write_to_summary_file("")
        _write_to_summary_file("Search Lemma: %s" % opts["root_syn"].name())
        _write_to_summary_file("Search Lemma Synonyms: %s" %
                               opts["root_syn"].lemma_names())
        _write_to_summary_file("Search Lemma Definition: %s" %
                               opts["root_syn"].definition())
        _write_to_summary_file("Search Lemma Examples: %s" %
                               opts["root_syn"].examples())
        _write_to_summary_file("Total Passwords Searched : %d" % total_processed)
        global total_found
        _write_to_summary_file(
            "Total hits for password searches: %d" % total_found)
        finished_time = get_curr_time()
        _write_to_summary_file("Starting Time: %s" % opts["started_time"])
        _write_to_summary_file("Finishing Time: %s" % finished_time)
        sp.write("Writing summary to %s" % outfile_summary.name)
        sp.write("Writing tested passwords to %s" % outfile_passwords.name)
        sp.ok("✔")


def _write_to_summary_file(s):
    """
    Writes generic data to the result file.
    """
    outfile_summary.write("%s\n" % s)


def _write_to_passwords_file(s):
    """
    Writes generic data to the result file.
    """
    outfile_passwords.write("%s\n" % s)


def prompt_synset_choice(root_synsets):
    print("  Multiple synset were found. Please choose: ")
    for elem in range(len(root_synsets)):
        print("    [%d] %s" % (elem, root_synsets[elem]))
    print()
    choice = input("Your choice [0-%d]: " % ((len(root_synsets)-1)))
    print()
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
    Download the NLTK wordnet corpus.
    """
    nltk.download("wordnet")


def option_draw_graph():
    """
    Draw the graph.
    """
    from wn_graph import draw_graph
    draw_graph(args.root_syn_name, args.dag_depth)


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
    if args.summary_file_name is not None:
        outfile_summary_name = args.summary_file_name
    else:
        outfile_summary_name = "{0}_{1}_summary.txt".format(
            started_time, args.root_syn_name)

    if args.result_file_name is not None:
        outfile_passwords_name = args.result_file_name
    else:
        outfile_passwords_name = "{0}_{1}_passwords.txt".format(
            started_time, args.root_syn_name)

    global outfile_summary
    outfile_summary = open(outfile_summary_name, "w+")

    global outfile_passwords
    outfile_passwords = open(outfile_passwords_name, "w+")

    root_synsets = wn.synsets(args.root_syn_name)
    if len(root_synsets) == 0:
        print("  No synset found for: %s" % root_syn_name)
        sys.exit(0)

    # If multiple synsets were found, prompt the user to choose which one to use.
    if len(root_synsets) > 1:
        choice_root_syn = prompt_synset_choice(root_synsets)
    else:
        choice_root_syn = root_synsets[0]

    with yaspin(text="Processing user-specified WordNet root level...", color="cyan") as sp:
        first_level_hits = 0
        first_level_not_found = 0
        for root_lemma in choice_root_syn.lemma_names():
            hits, not_found = permutations_for_lemma(
                root_lemma, choice_root_syn.min_depth())
            first_level_hits += hits
            first_level_not_found += not_found
            inc_total_processed()
        sp.ok("✔")

    with yaspin(text="Processing WordNet subtrees...", color="cyan") as sp:
        hits_below, not_found_below = recurse_nouns_from_root(
            root_syn=choice_root_syn, start_depth=choice_root_syn.min_depth(), rel_depth=args.dag_depth)
        sp.ok("✔")

    # Append the dict with the root synset after we processed the subtrees, since we are going to reverse
    # the entire OrderedDict. Because of the recursion, the synsets are going to be added from hierarchical
    # bottom to top to the OrderedDict. If we just reverse it, we have the top to bottom order back.
    if args.subsume_for_classes:
        append_with_hits(choice_root_syn, first_level_hits,
                         hits_below, first_level_not_found, not_found_below)

    # Writing results to result file
    # Using a options dictionary to pass option information to the function
    opts = {}
    opts["root_syn"] = choice_root_syn
    opts["started_time"] = started_time
    opts["hits_below_root"] = hits_below
    opts["start_depth"] = choice_root_syn.min_depth()
    _write_summary_to_result_file(opts)
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
