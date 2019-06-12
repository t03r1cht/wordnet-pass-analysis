import argparse
import collections
import datetime
import hashlib
import os
import platform
import random
import shutil
import signal
import subprocess
import sys
import time
import timeit
from collections import OrderedDict
from subprocess import CalledProcessError

import nltk
from colorama import Back, Fore, Style, init
from yaspin import yaspin

from combinators import combinator, combinator_registrar
from permutators import permutator, permutator_registrar

# pip installation über py binary: py -m pip install nltk

parser = argparse.ArgumentParser(
    description="Password hash anaylsis using WordNet and the HaveIBeenPwned database.")
parser.add_argument("-p", "--pass-database", type=str,
                    help="Path to the HIBP password database.", dest="pass_db_path")
parser.add_argument("-d", "--depth", type=int,
                    help="Depth in the DAG", dest="dag_depth")
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
# parser.add_argument("-t", "--hyperbolic-tree", action="store_true",
#                     help="Draw a hyperbolic tree from WordNet.", dest="draw_hypertree")
parser.add_argument("-l", "--from-lists", type=str,
                    help="Path to the folder containing self-created password lists.", dest="from_lists")
parser.add_argument("-z", "--download-wordnet", action="store_true",
                    help="Download WordNet.", dest="dl_wordnet")
parser.add_argument("-t", "--lookup-utility", action="store_true",
                    help="If set, use sgrep instead of the look utility.", dest="lookup_utility")
# parser.add_argument("-z", "--is-debug", action="store_true",
#                     help="Debug mode.", dest="is_debug")
args = parser.parse_args()

started = ""
permutation_handler = None
hits_for_lemmas = OrderedDict()
hits_for_list_lemmas = OrderedDict()

# For tracking progress
total_processed = 0
total_hits_sum = 0
total_found = 0
total_not_found = 0
pwned_pw_amount = 551509767
counter = 0
total_base_lemmas = 0  # track the total number of base lemmas
lemmas_to_process = 0
glob_started_time = None


def log_ok(s):
    print("[  {0}][+] {1}".format(get_curr_time_str(), s))


def log_err(s):
    print("[  {0}][-] {1}".format(get_curr_time_str(), s))


def log_status(s):
    print("[  {0}][*] {1}".format(get_curr_time_str(), s))


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


def _init_file_handles(started_time):
    # Open the file handler for a file with the starting time
    if args.summary_file_name is not None:
        outfile_summary_name = args.summary_file_name
    elif args.root_syn_name:
        outfile_summary_name = "{0}_{1}_summary.txt".format(
            started_time, args.root_syn_name)
    else:
        outfile_summary_name = "{0}_summary.txt".format(
            started_time)

    if args.result_file_name is not None:
        outfile_passwords_name = args.result_file_name
    elif args.root_syn_name:
        outfile_passwords_name = "{0}_{1}_passwords.txt".format(
            started_time, args.root_syn_name)
    else:
        outfile_passwords_name = "{0}_passwords.txt".format(
            started_time)

    global outfile_summary
    outfile_summary = open(outfile_summary_name, "w+")

    global outfile_passwords
    outfile_passwords = open(outfile_passwords_name, "w+")


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
    # return datetime.datetime.now().strftime("%Y%m%d_%H.%M.%S")
    return datetime.datetime.now()


def get_curr_time_str():
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


def inc_total_processed():
    """
    Increment the global variable to track the overall progress of processed lemmas.
    """
    global total_processed
    total_processed += 1


def inc_total_found():
    """
    Increment the global variable to track the passwords which could be found.
    """
    global total_found
    total_found += 1


def inc_total_not_found():
    """
    Increment the global variable to track the the passwords which could not be found.
    """
    global total_not_found
    total_not_found += 1


def cleanup():
    """
    Some cleanup work like closing the file handler.
    """
    outfile_summary.close()
    outfile_passwords.close()


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
        if args.lookup_utility:
            result = subprocess.check_output(
                ["sgrep", "-i", "-b", hash, args.pass_db_path])
        else:
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
        return 0, 0, 0
    global glob_started_time
    curr_time = get_curr_time()
    time_diff = curr_time - glob_started_time

    clear_terminal()
    log_status("Processed Lemmas: {0}\nTested Passwords: {1}\nCurrent Lemma: {2}\nElapsed Time: {3:2f}/{4:2f} (s/m)".format(
        total_base_lemmas,
        total_processed,
        hypo,
        time_diff.seconds,
        time_diff.seconds / 60,
    ))
    curr_root_syn = root_syn
    hits_below = 0
    total_hits_for_current_synset = 0
    not_found_for_current_synset = 0
    found_for_current_synset = 0
    global total_base_lemmas
    for hypo in curr_root_syn.hyponyms():
        total_hits = 0
        not_found = 0
        found = 0
        for lemma in hypo.lemma_names():
            total_base_lemmas += 1
            # Apply a set of permutations to each lemma
            lemma_hits, not_found_cnt, found_cnt = permutations_for_lemma_experimental(
                lemma, hypo.min_depth())
            total_hits += lemma_hits
            total_hits_for_current_synset += lemma_hits
            not_found += not_found_cnt
            found += found_cnt
            not_found_for_current_synset += not_found_cnt
            found_for_current_synset += found_cnt
        # Execute the function again with the new root synset being each hyponym we just found.
        hits_below, not_found_below, found_below = recurse_nouns_from_root(
            root_syn=hypo, start_depth=start_depth, rel_depth=rel_depth)
        # Add the sum of all hits below the current synset to the hits list of the current synset so
        # below hits are automatically included (not included in the terminal output, we separate both these
        # numbers into total_hits and hits_below so we can distinguis how many hits we found below and how
        # many were produced by the current synset).
        # Works because of... recursion
        total_hits_for_current_synset += hits_below
        not_found_for_current_synset += not_found_below
        found_for_current_synset += found_below
        if args.subsume_for_classes:
            append_with_hits(hypo, total_hits, hits_below,
                             not_found, not_found_below, found, found_below)
        total_base_lemmas += 1

    return total_hits_for_current_synset, not_found_for_current_synset, found_for_current_synset


def permutations_for_lemma(lemma, depth):
    """
    Create all permutatuons by using the registered permutator using the lemma as base.
    """
    total_hits = 0
    not_found_cnt = 0
    found_cnt = 0
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
                    found_cnt += 1
        else:
            trans_hits = lookup(trans, depth)
            if trans_hits == 0:
                not_found_cnt += 1
            else:
                found_cnt += 1
            total_hits += trans_hits

    return total_hits, not_found_cnt, found_cnt


def permutations_for_lemma_experimental(lemma, depth):
    total_hits = 0
    not_found_cnt = 0
    found_cnt = 0
    for combination_handler in combinator.all:
        # Generate all permutations
        permutations = combination_handler(lemma, permutator.all)
        if permutations == None:
            continue
        # Combinators always return a list of permutations
        if type(permutations) == list:
            for p in permutations:
                trans_hits = lookup(p, depth)
                total_hits += trans_hits
                if trans_hits == 0:
                    not_found_cnt += 1
                else:
                    found_cnt += 1
        else:
            trans_hits = lookup(permutations, depth)
            if trans_hits == 0:
                not_found_cnt += 1
            else:
                found_cnt += 1
            total_hits += trans_hits

    return total_hits, not_found_cnt, found_cnt


def lookup(permutation, depth):
    """
    Hashes the (translated) lemma and looks it up in  the HIBP password file.
    """
    # Hash and lookup translated lemma
    hashed_lemma = hash_sha1(permutation)
    occurrences = lookup_pass(hashed_lemma)
    # Increment "total" counter
    inc_total_processed()
    # Track found/not found
    if occurrences == 0:
        inc_total_not_found()
    else:
        inc_total_found()

    # Print the permutations to the result file.
    _write_result_to_passwords_file(permutation, depth, occurrences)
    # Return occurrences in order to be able to subsume them for each class.
    global total_hits_sum
    total_hits_sum += occurrences
    return occurrences


def append_with_hits(lemma, total_hits, below_hits, not_found, not_found_below, found, found_below):
    global hits_for_lemmas
    res_set = [lemma, total_hits, below_hits,
               not_found, not_found_below, found, found_below]
    if lemma.name() in hits_for_lemmas:
        hits_for_lemmas[lemma.name()][1] += total_hits
    else:
        hits_for_lemmas[lemma.name()] = res_set


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
    log_ok("Writing summary to result file...")
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
            total_not_found_loc = v[3] + v[4]
            this_found = v[5]
            below_found = v[6]
            total_found_loc = v[5] + v[6]
            pct_total_of_total = (total_found_loc / total_found) * 100
            pct_this_of_total = (this_found / total_found) * 100
            _write_to_summary_file("{0}{1}  pct_total={2:.2f}|pct_this={12:.2f}|total_hits={3}|this_hits={4}|below_hits={5}|total_found={6}|this_found={7}|below_found={8}|total_not_found={9}|this_not_found={10}|below_not_found={11}".format(
                (v[0].min_depth() - opts["start_depth"]) *
                "  ",  # indendation
                synset_id,  # synset id
                pct_total_of_total,
                total_hits,  # hits of each synset
                this_hits,
                below_hits,
                total_found_loc,
                this_found,
                below_found,
                total_not_found_loc,
                this_not_found,
                below_not_found,
                pct_this_of_total))

        _write_to_summary_file("")
        _write_to_summary_file(40 * "=")
        _write_to_summary_file("")
        _write_to_summary_file("    *** Searched Lemma ***")
        _write_to_summary_file("")
        _write_to_summary_file("Identifier: %s" % opts["root_syn"].name())
        _write_to_summary_file("Synonyms: %s" %
                               opts["root_syn"].lemma_names())
        _write_to_summary_file("Definition: %s" %
                               opts["root_syn"].definition())
        _write_to_summary_file("Examples: %s" %
                               opts["root_syn"].examples())
        _write_to_summary_file("")
        _write_to_summary_file("    *** Stats ***")
        _write_to_summary_file("")
        _write_to_summary_file(
            "Total Passwords Searched: {0} ({1:.2f}%)".format(total_processed,
                                                              (total_processed / total_processed * 100)))
        _write_to_summary_file(
            "Total Passwords (Success): {0} ({1:.2f}%)".format(total_found,
                                                               (total_found / total_processed * 100)))
        _write_to_summary_file(
            "Total Passwords (Failure): {0} ({1:.2f}%)".format(total_not_found,
                                                               (total_not_found / total_processed * 100)))
        _write_to_summary_file(
            "Total hits for password searches: {0} ({1:.2f} hits per password)".format(
                total_hits_sum, total_hits_sum / total_processed))
        _write_to_summary_file("")
        _write_to_summary_file("Pct Found Passwords (Total): {0:.5f}%".format(
                               (total_hits_sum / pwned_pw_amount * 100)))
        _write_to_summary_file("Pct Not Found Passwords (Total): {0:.5f}%".format(
                               ((1 - (total_hits_sum / pwned_pw_amount)) * 100)))
        _write_to_summary_file("")
        _write_to_summary_file("Base Lemmas (Total): {0} ({1:.2f} permutations per base lemma)".format(
            total_base_lemmas, total_processed / total_base_lemmas))
        _write_to_summary_file("")
        _write_to_summary_file("")
        started_time = opts["started_time"]
        finished_time = get_curr_time()
        time_delta = finished_time - started_time
        _write_to_summary_file(
            "Average Time per Base Lemma: {0:.3f} s".format(time_delta.seconds / total_base_lemmas))
        _write_to_summary_file("Starting Time: %s" % started_time)
        _write_to_summary_file("Finishing Time: %s" % finished_time)
        log_ok("Writing summary to %s" % outfile_summary.name)
        log_ok("Writing tested passwords to %s" % outfile_passwords.name)


def _write_lists_summary_to_result_file(opts):
    """
    Writes the bottom lines containing the summary to the result file.
    """
    log_ok("Writing summary to result file...")
    _write_to_summary_file("    *** Search Summary ***")
    _write_to_summary_file("")
    _write_to_summary_file("")
    for word_list in hits_for_list_lemmas:
        # items() returns a tuple key-value pair with index 0 being the key and index 1 being the value
        # Write stats for file
        list_total_hits = hits_for_list_lemmas[word_list]["_total_hits"]
        list_found_count = hits_for_list_lemmas[word_list]["_found_count"]
        list_not_found_count = hits_for_list_lemmas[word_list]["_not_found_count"]
        pct_found = list_found_count / total_found * 100

        _write_to_summary_file(
            "{0} [pct_found={1:.2f}%|total_hits={2}|found={3}|not_found={4}]".format(
                word_list,
                pct_found,
                list_total_hits,
                list_found_count,
                list_not_found_count))

        # Write stats for each word of the file

        # create list without the fields that start with "_" containing values used for the file stats entry (see above)
        lemma_only_list = []

        for item in hits_for_list_lemmas[word_list].items():
            if not item[0].startswith("_"):
                lemma_only_list.append(item)

        for dict_item in lemma_only_list:
            lemma_name = dict_item[0]
            value_array = dict_item[1]
            total_hits_loc = value_array[0]
            found_count_loc = value_array[1]
            not_found_count_loc = value_array[2]
            pct_found_lemma = found_count_loc / total_found * 100
            _write_to_summary_file("  {0} [pct_found={4:.2f}%|total_hits={1}|searched={5}|found={2}|not_found={3}]".format(
                lemma_name,
                total_hits_loc,
                found_count_loc,
                not_found_count_loc,
                pct_found_lemma,
                found_count_loc + not_found_count_loc))

    _write_to_summary_file("")
    _write_to_summary_file("")
    _write_to_summary_file("    *** Stats ***")
    _write_to_summary_file("")
    _write_to_summary_file("")
    _write_to_summary_file(
        "Total Passwords Searched: {0} ({1:.2f}%)".format(total_processed,
                                                          (total_processed / total_processed * 100)))
    _write_to_summary_file(
        "Total Passwords (Success): {0} ({1:.2f}%)".format(total_found,
                                                           (total_found / total_processed * 100)))
    _write_to_summary_file(
        "Total Passwords (Failure): {0} ({1:.2f}%)".format(total_not_found,
                                                           (total_not_found / total_processed * 100)))
    _write_to_summary_file(
        "Total hits for password searches: {0} ({1:.2f} hits per password)".format(
            total_hits_sum, total_hits_sum / total_processed))
    _write_to_summary_file("")
    _write_to_summary_file("Pct Found Passwords (Total): {0:.5f}%".format(
        (total_hits_sum / pwned_pw_amount * 100)))
    _write_to_summary_file("Pct Not Found Passwords (Total): {0:.5f}%".format(
        ((1 - (total_hits_sum / pwned_pw_amount)) * 100)))
    _write_to_summary_file("")
    _write_to_summary_file("Base Lemmas (Total): {0} ({1:.2f} permutations per base lemma)".format(
        total_base_lemmas, total_processed / total_base_lemmas))
    _write_to_summary_file("")
    _write_to_summary_file("")
    started_time = opts["started_time"]
    finished_time = get_curr_time()
    time_delta = finished_time - started_time
    _write_to_summary_file(
        "Average Time per Base Lemma: {0:.3f} s".format(time_delta.seconds / total_base_lemmas))
    _write_to_summary_file("Starting Time: %s" % started_time)
    _write_to_summary_file("Finishing Time: %s" % finished_time)
    log_ok("Writing summary to %s" % outfile_summary.name)
    log_ok("Writing tested passwords to %s" % outfile_passwords.name)


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
        print("    [{0}] Name: {1}, Synonyms: {2}".format(
            elem,
            root_synsets[elem].name(),
            root_synsets[elem].lemma_names()))
    print()
    choice = input("Your choice [0-%d]: " % ((len(root_synsets)-1)))
    print()
    try:
        int_choice = int(choice)
    except ValueError:
        print("Invalid choice: %s" % choice)
        sys.exit(0)
    if int_choice < 0 or int_choice > len(root_synsets) - 1:
        print("Invalid choice: %s" % choice)
        sys.exit(0)
    # Make the choice the new root synset from we will start our recursion.
    return root_synsets[int_choice]


def _download_wordnet():
    """
    Download the NLTK wordnet corpus.
    """
    try:
        from nltk.corpus import wordnet as wn
    except:
        log_err("Error importing nltk.corpus.wordnet")
        log_ok("Downloading WordNet...")
        nltk.download("wordnet")
        log_status("OK")
        sys.exit(0)


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
    global glob_started_time
    glob_started_time = started_time

    root_synsets = wn.synsets(args.root_syn_name, "n")
    if len(root_synsets) == 0:
        print("  No synset found for: %s" % args.root_syn_name)
        sys.exit(0)

    # If multiple synsets were found, prompt the user to choose which one to use.
    if len(root_synsets) > 1:
        choice_root_syn = prompt_synset_choice(root_synsets)
    else:
        choice_root_syn = root_synsets[0]

    # Initiate the file handles for the result and summary file
    _init_file_handles(get_curr_time_str())
    global total_base_lemmas
    log_ok("Processing user-specified WordNet root level...")
    first_level_hits = 0
    first_level_not_found = 0
    first_level_found = 0
    for root_lemma in choice_root_syn.lemma_names():
        total_base_lemmas += 1
        hits, not_found, found = permutations_for_lemma_experimental(
            root_lemma, choice_root_syn.min_depth())
        first_level_hits += hits
        first_level_not_found += not_found
        first_level_found += found

    log_ok("Processing WordNet subtrees...")
    hits_below, not_found_below, found_below = recurse_nouns_from_root(
        root_syn=choice_root_syn, start_depth=choice_root_syn.min_depth(), rel_depth=args.dag_depth)

    # Append the dict with the root synset after we processed the subtrees, since we are going to reverse
    # the entire OrderedDict. Because of the recursion, the synsets are going to be added from hierarchical
    # bottom to top to the OrderedDict. If we just reverse it, we have the top to bottom order back.
    if args.subsume_for_classes:
        append_with_hits(choice_root_syn, first_level_hits,
                         hits_below, first_level_not_found, not_found_below, first_level_found, found_below)

    # Writing results to result file
    # Using a options dictionary to pass option information to the function
    opts = {}
    opts["root_syn"] = choice_root_syn
    opts["started_time"] = started_time

    opts["hits_below_root"] = hits_below
    opts["start_depth"] = choice_root_syn.min_depth()
    _write_summary_to_result_file(opts)
    cleanup()


def option_hypertree():
    # import igraph instead of jgraph
    import jgraph
    from h3.tree import Tree
    edges = jgraph.Graph.Barabasi(
        n=500, m=3, directed=True).spanning_tree(None, True).get_edgelist()
    tree = Tree(edges)
    tree.scatter_plot(equators=False, tagging=False)


def option_permutate_from_lists():
    signal.signal(signal.SIGINT, sigint_handler)
    clear_terminal()
    # Initialize the file handles to write to
    _init_file_handles(get_curr_time_str())
    # Check if the specified directory is valid
    log_ok("Checking prerequisites...")
    if not args.from_lists:
        log_err("Please enter a path to a directory containing password base lists.")
        return
    # Check if directory exists and is a directory
    if not os.path.isdir(args.from_lists):
        log_err("Not a directory")
        return

    # Check if directory contains at least 1 file
    if len(os.listdir(args.from_lists)) == 0:
        log_err("Directory is empty.")
        return

    # Gather filenames from dir
    dir_content = os.listdir(args.from_lists)
    dir_txt_content = []
    for f in dir_content:
        if f.endswith(".txt"):
            dir_txt_content.append(f)

    if len(dir_txt_content) > 0:
        log_status("Found %d text files in %s" %
                   (len(dir_txt_content), args.from_lists))
    else:
        log_err("Could not find any textfiles")

    started_time = get_curr_time()

    # Create options dict
    opts = {}
    opts["started_time"] = started_time
    opts["list_dir"] = args.from_lists
    # Iterate over each list
    global total_base_lemmas
    # for progress tracking
    global lemmas_to_process
    for txt_file in dir_txt_content:
        try:
            result = subprocess.check_output(
                ["wc", "-l", "{0}/{1}".format(args.from_lists, txt_file)])
        except CalledProcessError as e:
            log_err(
                "Could not count lines for destination directory! % s" % e)
            return None
        result = result.decode(
            "utf-8").strip("\n").strip("\r").lstrip().split(" ")[0]
        lemmas_to_process += int(result)
    log_status("Total lemmas to process: %d" % lemmas_to_process)
    log_status("Starting: %s" % started_time)
    # Track finished lists
    finished_lists = 0
    # Iterate over each list in the specified directory
    for pass_list in dir_txt_content:
        try:
            pass_file = open("%s/%s" % (args.from_lists, pass_list))
            curr_pass_list = pass_file.readlines()
            pass_file.close()
        except Exception as e:
            log_err("Failed to open file '%s'" % pass_list)
            # Continue with next file instead of terminating the script
            continue
        for password_base in curr_pass_list:
            if password_base.startswith("#") or password_base == "" or password_base == " " or password_base == "\n":
                continue
            else:
                total_base_lemmas += 1
                password_base = password_base.strip("\n").strip("\r")
                total_hits, not_found_cnt, found_cnt = permutations_for_lemma_experimental(
                    password_base, 0)
                append_list_lemma_to_list(
                    pass_list, password_base, total_hits, found_cnt, not_found_cnt)
            curr_time = get_curr_time()
            time_diff = curr_time - started_time
            curr_lemma_time = time_diff.seconds / total_base_lemmas
            remaining_lemmas = lemmas_to_process - total_base_lemmas
            remaining_time_est = remaining_lemmas * curr_lemma_time

            clear_terminal()
            log_status("Current list: {0}\nProcessed Lemmas: {1}/{2}\nTested Passwords: {7}\nFinished Lists: {8}/{9}\nCurrent Lemma: {10}\nElapsed Time (seconds): {3:.2f}\nEstimated Remaining Time (m/h): {4:.2f}/{5:.2f}\nCurrent Average Time per Lemma (s): {6:.2f}\n".format(
                pass_list,
                total_base_lemmas,
                lemmas_to_process,
                time_diff.seconds,
                remaining_time_est / 60,
                remaining_time_est / 60 / 60,
                curr_lemma_time,
                total_processed,
                finished_lists,
                len(dir_txt_content),
                password_base))

    finished_lists += 1
    _write_lists_summary_to_result_file(opts)
    print()
    cleanup()


def append_list_lemma_to_list(list_name, lemma, total_hits, found_count, not_found_count):
    global hits_for_list_lemmas
    content = [total_hits, found_count, not_found_count]
    if not list_name in hits_for_list_lemmas:
        hits_for_list_lemmas[list_name] = {}

    hits_for_list_lemmas[list_name][lemma] = content
    # Update the total stats for the file
    # Add the total hits to the file total hits
    if not "_total_hits" in hits_for_list_lemmas[list_name]:
        hits_for_list_lemmas[list_name]["_total_hits"] = total_hits
    else:
        hits_for_list_lemmas[list_name]["_total_hits"] += total_hits

    if not "_found_count" in hits_for_list_lemmas[list_name]:
        hits_for_list_lemmas[list_name]["_found_count"] = found_count
    else:
        hits_for_list_lemmas[list_name]["_found_count"] += found_count

    if not "_not_found_count" in hits_for_list_lemmas[list_name]:
        hits_for_list_lemmas[list_name]["_not_found_count"] = not_found_count
    else:
        hits_for_list_lemmas[list_name]["_not_found_count"] += not_found_count


if __name__ == "__main__":
    # try:
    #     from nltk.corpus import wordnet as wn
    #     print("import ok")
    # except ImportError:
    #     print("ERROR IMPORT")
    #     _download_wordnet()

    if args.dl_wordnet:
        _download_wordnet()

    if args.lookup_utility:
        print("NOTE: Make sure you have sgrep installed and added to PATH.")
        print()
        print()

    from nltk.corpus import wordnet as wn

    # WordNet graph
    if args.draw_dag:
        # Evaluate command line parameters
        if args.dag_depth is None or args.root_syn_name is None:
            print("Error: Missing parameters.")
            parser.print_usage()
            sys.exit(0)
        # print("Running platform pre-check...")
        # if "Linux" in platform.platform():
        #     print(
        #         "You are running this script on Linux (%s). Due to currently unresolved bugs, the graph feature can only be used on Windows and MacOS." % platform.platform())
        #     sys.exit(0)
        option_draw_graph()
    # Draw the hyperbolic tree
    # elif args.draw_hypertree:
    #     option_hypertree()
    # Lookup words from self-created lists
    elif args.from_lists:
        option_permutate_from_lists()
    else:
        # Evaluate command line parameters
        if args.pass_db_path is None or args.dag_depth is None or args.root_syn_name is None:
            print("Error: Missing parameters.")
            parser.print_usage()
            sys.exit(0)

        # print("Running platform pre-check...")
        # if "Darwin" not in platform.platform():
        #     print(
        #         "You are running this script on %s. Looking up passwords is currently only working on MacOS (Darwin) (and probably BSD-based systems). This is due to the fact that any OS other than the aforementioned are shipped with the 32-bit 'look' utility, whereas the BSD-based 'look' utility (e.g. MacOS) is 64-bit. This allows using the look utility on very large files." % platform.platform())
        #     sys.exit(0)
        option_lookup_passwords()
