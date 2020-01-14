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
import unicodedata
from collections import OrderedDict
from subprocess import CalledProcessError
from pymongo import MongoClient
import pymongo
import operator
import stats

import nltk

from combinators import combinator, combinator_registrar
from permutators import permutator, permutator_registrar

import mongo
from helper import log_ok, log_err, log_status, remove_control_characters, get_curr_time, get_curr_time_str, get_shell_width, clear_terminal, get_txt_files_from_dir, format_number

# ADJ, ADJ_SAT, ADV, NOUN, VERB = 'a', 's', 'r', 'n', 'v'
"""
Find duplicates: db.getCollection('passwords_wn_noun').aggregate([{"$group": {_id: "$name", sum: {"$sum": 1}}}, {"$sort": {"sum": -1}}])
"""

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
parser.add_argument("-l", "--from-lists", type=str,
                    help="Path to the folder containing self-created password lists.", dest="from_lists")
parser.add_argument(
    "--wn", type=str, help="Use the WordNet as default dictionary.", dest="wn")
parser.add_argument("-z", "--download-wordnet", action="store_true",
                    help="Download WordNet.", dest="dl_wordnet")
parser.add_argument("-t", "--lookup-utility", action="store_true",
                    help="If set, use sgrep instead of the look utility.", dest="lookup_utility")
parser.add_argument("-v", "--verbose", action="store_true",
                    help="Verbose output.", dest="verbose")
parser.add_argument("-e", "--extensive", action="store_true",
                    help="Print all tested password to a separate result file. Use --result-file option to set custom file name..", dest="extensive")
parser.add_argument("--skip-warning", action="store_true",
                    help="Skip the warning when using the -e (--extensive) flag.", dest="skip_warning")
parser.add_argument("--test", action="store_true",
                    help="Test", dest="test")
parser.add_argument("--purge-db", action="store_true",
                    help="Purge Database before writing", dest="purge_db")
parser.add_argument("--classify-lists", type=str,
                    help="Classify lists. -l param is required!", dest="classify_lists")
parser.add_argument("--classify-wn", type=str,
                    help="Classify wordnet synsets.", dest="classify_wn")
parser.add_argument("--top", type=int,
                    help="Limit output for --classify-x queries.", dest="top")
parser.add_argument("--plot", type=str, help="Plot graph.", dest="plot")
parser.add_argument("--misc_list", type=str,
                    help="Lookup miscellaneous list. Lookup will only use words in lists, not generate any permutations.", dest="misc_list")
parser.add_argument("--start_level", type=int,
                    help="Start level to draw the WordNet hierarchy in a pie chart.", dest="start_level")
parser.add_argument("--stats", type=str,
                    help="Print stats depending on the parameter.", dest="stats")
parser.add_argument("--mongo-addr", type=str,
                    help="Specify mongo address.", dest="mongo")
parser.add_argument("--dict", type=str,
                    help="Specify dict path.", dest="dict_source")
parser.add_argument("--dict-id", type=str,
                    help="Specify dict ID for the database. Please use only characters.", dest="dict_id")
parser.add_argument("--wn-type", type=str,
                    help="Specify the part of speech of the WordNet you want to recurse.", dest="wn_pos")
parser.add_argument("--pw-type", type=str,
                    help="Password class. WN Noun, List, Dict etc.", dest="pw_type")
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
synset_cnt = 0
# We need this dictionary to track which verb synsets were iterated over by the recursion.
# We will then lookup those still unprocessed manually by getting the diff
wn_verbs_check_map = {}

ILL_TAG = get_curr_time_str()


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
    # disabled
    return
    outfile_summary.close()
    outfile_passwords.close()


def _init_file_handles(started_time, of_summary=None):
    """
    Deprecated. Open log file handlers.
    """
    # disabled
    return
    # Open the file handler for a file with the starting time
    global outfile_summary, outfile_passwords

    if of_summary:
        # of_summary option is used by the --classify-only handler so we can create only the summary file
        if args.summary_file_name is not None:
            outfile_summary_name = args.summary_file_name
        else:
            outfile_summary_name = "{0}_summary.txt".format(started_time)

        outfile_summary = open(outfile_summary_name, "w+")
    else:
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

        outfile_summary = open(outfile_summary_name, "w+")
        outfile_passwords = open(outfile_passwords_name, "w+")


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
            # Use sgrep with -i and -b parameter to look for the searched hash.
            # The raw output of this method is something like A283BCD8899:18287 where the first part in front of the colon is the produced hash and the last part
            # is the number of occurrences of the hash in the HaveIBeenPwned hash file.
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
    Iterates over each noun hyponym synset until the desired depth in the DAG is reached.

    For each level of hyponyms in the DAG, this function will unpack each lemma of each
    synset of said depth level, which can be confusing when looking at results.txt.

    Each indented set of lemmas is the sum of all unpacked lemmas of each synset of the current graph level.
    """

    # Depth = level in the WordNet "tree"
    # If the current depth in the DAG (directed acyclic graph) is reached, do not continue to iterate this path.
    # Example:  rel_depth = 3, curr = 9, start = 7
    #           9 - 5 = 4,
    if (root_syn.min_depth() - start_depth) >= rel_depth:
        return 0, 0, 0
    global glob_started_time
    global total_base_lemmas
    curr_time = get_curr_time()
    time_diff = curr_time - glob_started_time

    clear_terminal()
    global synset_cnt
    synset_cnt += 1
    log_status("Processed Lemmas: {0}\nProcessed Synsets: {5} \nTested Passwords: {1}\nCurrent Lemma: {2}\nElapsed Time: {3}/{4:.2f} (s/m)".format(
        total_base_lemmas,
        total_processed,
        root_syn,
        time_diff.seconds,
        time_diff.seconds / 60,
        synset_cnt
    ))
    curr_root_syn = root_syn
    hits_below = 0
    total_hits_for_current_synset = 0
    not_found_for_current_synset = 0
    found_for_current_synset = 0
    # Get the children for the current synset and iterate over them
    for hypo in curr_root_syn.hyponyms():
        total_hits = 0
        not_found = 0
        found = 0
        # For each children of the current synset, determine all of its lemmas (lemmas = synset synonyms)
        for lemma in hypo.lemma_names():
            total_base_lemmas += 1
            # For each synset lemma, apply a set of permutations to them to generate possible passwords, e.g.
            # with the lemma "cat" possible permutations may be "Cat", "CAT", "c4t", "cat123" and so on.
            # This is what permutations_for_lemma() does
            lemma_hits, not_found_cnt, found_cnt = permutations_for_lemma(
                lemma, hypo.min_depth(), hypo.name())
            # 1. Total hits for the current synset (not all synsets have more than 1 synonym, but in case they do, add all hits together)
            total_hits += lemma_hits
            # 2. Total hits for the current synset including the hits of all of THIS synsets children (the children recursion only goes as far as the desired end-level)
            total_hits_for_current_synset += lemma_hits
            # 3. The total count of password variations that were not found in the HIBP password file
            not_found += not_found_cnt
            # 4. The total count of password variations that were found in the HIBP password file
            found += found_cnt
            # 5. The count of password variations for THIS synset that were not found in the HIBP password file
            not_found_for_current_synset += not_found_cnt
            # 6. The count of password variations for THIS synset that were found in the HIBP password file
            found_for_current_synset += found_cnt
        # Create this synset in the database and save its relatives (hypernym and hyponyms)
        mongo.store_synset_with_relatives(hypo, curr_root_syn.name())
        # Recursive execution of this function with the new parent synset (of which we will in turn determine its children) set to be this child.
        hits_below, not_found_below, found_below = recurse_nouns_from_root(
            root_syn=hypo, start_depth=start_depth, rel_depth=rel_depth)

        # Add the sum of all hits below the current synset to the hits list of the current synset so
        # below hits are automatically included (not included in the terminal output, we separate both these
        # numbers into total_hits and hits_below so we can distinguish how many hits we found below and how
        # many were produced by the current synset).
        # Works because of... recursion
        total_hits_for_current_synset += hits_below
        not_found_for_current_synset += not_found_below
        found_for_current_synset += found_below
        # Update the synset with these stats
        mongo.update_synset_with_stats(
            hypo, hits_below, not_found_below, found_below, total_hits, found_cnt, not_found_cnt)
        if args.subsume_for_classes:
            append_with_hits(hypo, total_hits, hits_below,
                             not_found, not_found_below, found, found_below)
        total_base_lemmas += 1

    return total_hits_for_current_synset, not_found_for_current_synset, found_for_current_synset


def recurse_verbs_from_root(root_syn):
    """
    Iterates over each verb hyponym synset until the desired depth in the DAG is reached.

    For each level of hyponyms in the DAG, this function will unpack each lemma of each
    synset of said depth level, which can be confusing when looking at results.txt.

    Each indented set of lemmas is the sum of all unpacked lemmas of each synset of the current graph level.
    """

    global glob_started_time
    global total_base_lemmas
    curr_time = get_curr_time()
    time_diff = curr_time - glob_started_time

    clear_terminal()
    global synset_cnt
    synset_cnt += 1
    log_status("Processed Lemmas: {0}\nProcessed Synsets: {5} \nTested Passwords: {1}\nCurrent Lemma: {2}\nElapsed Time: {3}/{4:.2f} (s/m)".format(
        total_base_lemmas,
        total_processed,
        root_syn,
        time_diff.seconds,
        time_diff.seconds / 60,
        synset_cnt
    ))
    curr_root_syn = root_syn
    hits_below = 0
    total_hits_for_current_synset = 0
    not_found_for_current_synset = 0
    found_for_current_synset = 0

    # Set the dict entry to 1 to signify that we have "touched" this synset via the recursion
    global wn_verbs_check_map
    wn_verbs_check_map[curr_root_syn.name()] = 1

    # Get the children for the current synset and iterate over them
    for hypo in curr_root_syn.hyponyms():
        total_hits = 0
        not_found = 0
        found = 0
        # For each children of the current synset, determine all of its lemmas (lemmas = synset synonyms)
        for lemma in hypo.lemma_names():
            total_base_lemmas += 1
            # For each synset lemma, apply a set of permutations to them to generate possible passwords, e.g.
            # with the lemma "cat" possible permutations may be "Cat", "CAT", "c4t", "cat123" and so on.
            # This is what permutations_for_lemma() does
            lemma_hits, not_found_cnt, found_cnt = permutations_for_lemma_verb(
                lemma, hypo.min_depth(), hypo.name())
            # 1. Total hits for the current synset (not all synsets have more than 1 synonym, but in case they do, add all hits together)
            total_hits += lemma_hits
            # 2. Total hits for the current synset including the hits of all of THIS synsets children (the children recursion only goes as far as the desired end-level)
            total_hits_for_current_synset += lemma_hits
            # 3. The total count of password variations that were not found in the HIBP password file
            not_found += not_found_cnt
            # 4. The total count of password variations that were found in the HIBP password file
            found += found_cnt
            # 5. The count of password variations for THIS synset that were not found in the HIBP password file
            not_found_for_current_synset += not_found_cnt
            # 6. The count of password variations for THIS synset that were found in the HIBP password file
            found_for_current_synset += found_cnt
        # Create this synset in the database and save its relatives (hypernym and hyponyms)
        mongo.store_synset_with_relatives_verb(hypo, curr_root_syn.name())
        # Recursive execution of this function with the new parent synset (of which we will in turn determine its children) set to be this child.
        hits_below, not_found_below, found_below = recurse_verbs_from_root(
            root_syn=hypo)

        # Add the sum of all hits below the current synset to the hits list of the current synset so
        # below hits are automatically included (not included in the terminal output, we separate both these
        # numbers into total_hits and hits_below so we can distinguish how many hits we found below and how
        # many were produced by the current synset).
        # Works because of... recursion
        total_hits_for_current_synset += hits_below
        not_found_for_current_synset += not_found_below
        found_for_current_synset += found_below
        # Update the synset with these stats
        mongo.update_synset_with_stats_verb(
            hypo, hits_below, not_found_below, found_below, total_hits, found_cnt, not_found_cnt)
        total_base_lemmas += 1

    return total_hits_for_current_synset, not_found_for_current_synset, found_for_current_synset


def option_lookup_passwords():
    """"
    Lookup the passwords in the pwned passwords list.
    """
    init()
    signal.signal(signal.SIGINT, sigint_handler)
    clear_terminal()

    mongo.purge_noun()
    log_ok("Deleted old MongoDB noun collections...")

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
        hits, not_found, found = permutations_for_lemma(
            root_lemma, choice_root_syn.min_depth(), choice_root_syn.name())
        first_level_hits += hits
        first_level_not_found += not_found
        first_level_found += found

    log_ok("Processing WordNet subtrees...")
    # Store this synset including all of its hyponyms.
    # By emitting the parent parameter, we declare this synset the root
    # We will only declare entity.n.01 as root since it is the actual root object of the wordnet tree
    if choice_root_syn.name() == "entity.n.01":
        mongo.store_synset_with_relatives(choice_root_syn, parent="root")
    else:
        # If we run the script starting from somewhere within the wordnet,
        # we still need to find its parent (hypernym). Therefore, we call hypernyms()
        # on the synset and check if one of the returned hypernyms already exists
        # in our database. If it does, we connect it by setting this synset's parent
        # to the found parent. Note that the first occurence of the hypernym
        # will be specified its parent (even if there might be more valid hypernyms existing in
        # the database)
        root_hypernyms = choice_root_syn.hypernyms()
        root_hypernym = None
        for hypernym in root_hypernyms:
            if mongo.db_wn.count_documents({"id": hypernym.name()}) == 0:
                continue
            else:
                root_hypernym = hypernym
        if root_hypernym is None:
            log_err(
                "Could not find a single hypernym of [%s] in the database to link to" % choice_root_syn.name())
            log_err("\t Hypernyms for [%s]: %s" % (
                choice_root_syn.name(), choice_root_syn.hypernyms()))
            sys.exit(0)
        mongo.store_synset_with_relatives(
            choice_root_syn, parent=root_hypernym.name())
    hits_below, not_found_below, found_below = recurse_nouns_from_root(
        root_syn=choice_root_syn, start_depth=choice_root_syn.min_depth(), rel_depth=args.dag_depth)

    # Update this root synset with its respective stats
    mongo.update_synset_with_stats(choice_root_syn, hits_below, not_found_below,
                                   found_below, first_level_hits, first_level_found, first_level_not_found)
    # mongo.update_synset_with_stats(choice_root_syn, hits_below, not_found_below,
    #                                found_below, hits, found, not_found)
    # we processed the subtrees, since we are going to reverse
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
    cleanup()

    # Append the dict with the root synset after


def option_verb_wordnet():
    """
    Args handler to lookup verbs from the wordnet.
    """
    init()
    signal.signal(signal.SIGINT, sigint_handler)
    clear_terminal()

    mongo.purge_verb()
    log_ok("Deleted old MongoDB verb collections...")

    started_time = get_curr_time()
    global glob_started_time
    glob_started_time = started_time

    # Will contain all synsets starting at level 0
    lvl_0_synsets = []
    lvl_0_synsets_labels = []
    global wn_verbs_check_map

    # Get all verb synsets and init the wn_verbs_check_map dict with each verb synset as key and initialized with the 0 value.
    # While recursing over the WordNet, we will gradually set each dictionary record to 1 to signify that we have processed this synset. After we finished the recursion, we know which synset are still unprocessed
    # by searching in the dict for all records still set to 0.
    for syn in list(wn.all_synsets("v")):
        # Store all synset names
        # We will init all dict values with 0. They are set to 1 once they have been processed by the recursion
        wn_verbs_check_map[syn.name()] = 0
        # Filter all synsets out that start on the level 0 (root of the wordnet synset verb "tree")
        if syn.min_depth() == 0:
            lvl_0_synsets.append(syn)
            lvl_0_synsets_labels.append(syn.name())

    log_ok("Synsets starting at Level 0: %d" % len(lvl_0_synsets))

    global total_base_lemmas
    global synset_cnt
    log_ok("Processing level 0 verb synsets...")
    # Before starting the actual recursion, we need to process all synsets on level 0 (recursion method always looks up the passed synsets hyponyms and not the synset itself)
    finish_cnt = 0
    lvl_0_len = len(lvl_0_synsets)
    lvl_0_perm_values = {}
    for syn in lvl_0_synsets:
        synset_cnt += 1
        # Contains the sum of the lemmas in case a synset consists of more than one lemma
        first_level_hits = 0
        first_level_not_found = 0
        first_level_found = 0
        # Set the dict entry to 1 to signify that we have "touched" this synset via the recursion
        wn_verbs_check_map[syn.name()] = 1

        # Create the synset in the database
        mongo.store_synset_with_relatives_verb(syn, parent="root")

        for syn_lemma in syn.lemma_names():
            total_base_lemmas += 1
            hits, not_found, found = permutations_for_lemma_verb(
                syn_lemma, syn.min_depth(), syn.name())
            first_level_hits += hits
            first_level_not_found += not_found
            first_level_found += found

        # Store these values for later when we need to update the lvl 0 synset stats
        o = {
            "first_level_hits": first_level_hits,
            "first_level_not_found": first_level_not_found,
            "first_level_found": first_level_found
        }
        lvl_0_perm_values[syn.name()] = o

        finish_cnt += 1
        log_ok("[%d/%d] Finished: %s" % (finish_cnt, lvl_0_len, syn.name()))

    log_status("Test 'root syns' OK")

    log_ok("Processing verb synset subtrees...")
    for syn in lvl_0_synsets:
        # Start the recursion
        hits_below, not_found_below, found_below = recurse_verbs_from_root(syn)

        # After the recursion is finished the function returns the hits from the child synsets we
        # started the recursion from. We can now update the lvl 0 synsets with the hits of their respective
        # children and subchildren and so on.
        hits = lvl_0_perm_values.get(syn.name(), {}).get("first_level_hits", 0)
        found = lvl_0_perm_values.get(
            syn.name(), {}).get("first_level_found", 0)
        not_found = lvl_0_perm_values.get(
            syn.name(), {}).get("first_level_not_found", 0)
        mongo.update_synset_with_stats_verb(
            syn, hits_below, not_found_below, found_below, hits, found, not_found)

    log_status("Test 'tree recursion' OK")

    # After we finished the recursion, check still unprocessed synsets, i.e. those in the wn_verbs_check_map with their value still set to 0
    not_found_check_map = []  # Contains all synsets that still need to be processed
    for k, v in wn_verbs_check_map.items():
        if v == 0:
            not_found_check_map.append(k)

    # Lookup the rest of the synsets
    log_ok("Processing verb synsets not iterated over by recursion...")
    finish_cnt = 0
    total_other_syn_len = len(not_found_check_map)

    for item in not_found_check_map:
        syn = wn.synset(item)

        total_hits = 0
        not_found = 0
        found = 0

        # Will be populated with stats after the lookup has been finished
        parent = ""
        if syn.hypernyms() == []:
            parent = "no_parent"
            log_status("{}, parent={}".format(syn.name(), syn.hypernyms()))
        else:
            parent = syn.hypernyms()[0].name()
            log_status("{}, parent={}".format(syn.name(), syn.hypernyms()))

        mongo.store_synset_with_relatives_verb(syn, parent=parent)

        for syn_lemma in syn.lemma_names():
            lemma_hits, not_found_cnt, found_cnt = permutations_for_lemma_verb(
                syn_lemma, syn.min_depth(), syn.name())
            total_hits += lemma_hits
            not_found += not_found_cnt
            found += found_cnt

        # Update the manually "crawled" synsets with their respective hits
        mongo.update_synset_with_stats_verb(
            syn, 0, 0, 0, total_hits, found, not_found)

        # Determine to which lvl 0 synset this synset belongs and add the hits of this synset to its
        # respective lvl 0 synset

        # Get the hypernyms and check which lvl 0 synset is found in the root path (hypernyms_path() returns all hypernyms until the root synset is reached)
        linked_lvl0_syn = "no_linked_lvl0_syn"
        hypernym_paths_labels = [
            ss.name() for hyper_lists in syn.hypernym_paths() for ss in hyper_lists]
        for lvl0 in lvl_0_synsets_labels:
            if lvl0 in hypernym_paths_labels:
                log_ok("Root parent for {} is {}".format(syn.name(), lvl0))
                linked_lvl0_syn = lvl0
                break

        # Add total_hits, found and not_found to the lvl0 synset the current synset is indirectly linked to (we update the respective level 0 synset since
        # we now know that the current synset is an indirect child of the determined lvl 0 synset)
        mongo.add_values_to_existing_verb(
            linked_lvl0_syn, total_hits, found, not_found)

        finish_cnt += 1
        log_status("[%d/%d] %s" %
                   (finish_cnt, total_other_syn_len, syn.name()))

    log_ok("Finished!")


def option_adjective_wordnet():
    """
    Args handler to lookup adjectives from the wordnet.
    """
    init()
    signal.signal(signal.SIGINT, sigint_handler)
    clear_terminal()

    mongo.purge_adjective()
    log_ok("Deleted old MongoDB adjective collections...")

    started_time = get_curr_time()
    global glob_started_time
    glob_started_time = started_time
    global total_base_lemmas
    finish_cnt = 0

    # Since the adjectives are represented as a flat list, iterating over it is fairly easy
    total_synsets = len(list(wn.all_synsets("a")))
    for syn in list(wn.all_synsets("a")):
        syn_hits = 0
        syn_not_found = 0
        syn_found = 0

        mongo.store_synset_with_relatives_adjective(syn, parent="root")

        for syn_lemma in syn.lemma_names():
            total_base_lemmas += 1
            lemma_hits, lemma_not_found, lemma_found = permutations_for_lemma_adjective(
                syn_lemma, syn.min_depth(), syn.name())
            syn_hits += lemma_hits
            syn_not_found += lemma_not_found
            syn_found += lemma_found

        mongo.update_synset_with_stats_adjective(
            syn, 0, 0, 0, syn_hits, syn_found, syn_not_found)

        # Progress indicator
        finish_cnt += 1
        log_ok("[%d/%d]Finished: %s,\tHits: %d, Found: %d, Not Found: %d" % (
            finish_cnt, total_synsets, syn.name(), syn_hits, syn_found, syn_not_found))
    log_ok("Finished!")


def option_adverb_wordnet():
    """
    Args handler to lookup adverbs from the wordnet.
    """
    init()
    signal.signal(signal.SIGINT, sigint_handler)
    clear_terminal()

    mongo.purge_adverb()
    log_ok("Deleted old MongoDB adverb collections...")

    started_time = get_curr_time()
    global glob_started_time
    glob_started_time = started_time
    global total_base_lemmas
    finish_cnt = 0

    # Since the adverbs are represented as a flat list, iterating over it is fairly easy
    total_synsets = len(list(wn.all_synsets("r")))
    for syn in list(wn.all_synsets("r")):
        syn_hits = 0
        syn_not_found = 0
        syn_found = 0

        mongo.store_synset_with_relatives_adverb(syn, parent="root")

        for syn_lemma in syn.lemma_names():
            total_base_lemmas += 1
            lemma_hits, lemma_not_found, lemma_found = permutations_for_lemma_adverb(
                syn_lemma, syn.min_depth(), syn.name())
            syn_hits += lemma_hits
            syn_not_found += lemma_not_found
            syn_found += lemma_found

        mongo.update_synset_with_stats_adverb(
            syn, 0, 0, 0, syn_hits, syn_found, syn_not_found)

        # Progress indicator
        finish_cnt += 1
        log_ok("[%d/%d]Finished: %s,\tHits: %d, Found: %d, Not Found: %d" % (
            finish_cnt, total_synsets, syn.name(), syn_hits, syn_found, syn_not_found))
    log_ok("Finished!")


def permutations_for_lemma(lemma, depth, source):
    """
    Applies a set of permutators to a given lemma (string) to generate possible password combinations.
    Return:
    - total_hits: The sum of all hits for all generated passwords from this lemma. Hits for a password is the number after the colon (:) in the HIBP password file, else 0.
    - not_found_cnt: The number of generated passwords that were not found in the HIBP password file (i.e. the passwords with 0 hits)
    - found_cnt: The number of generated passwords that were found in the HIBP password file (i.e. the passwords with > 0 hits)
    """

    total_hits = 0
    not_found_cnt = 0
    found_cnt = 0
    all_permutations = []
    for combination_handler in combinator.all:
        # Generate all permutations
        permutations = combination_handler(lemma, permutator.all)
        if args.verbose:
            log_status("Permutations for [%s]: %d" %
                       (lemma, len(permutations)))
        if permutations == None:
            continue
        # Combinators always return a list of permutations
        if type(permutations) == list:
            for p in permutations:
                if args.verbose:
                    log_status("Looking up [%s]" % p["name"])
                trans_hits = lookup(p["name"], depth, source, lemma)
                if args.root_syn_name:
                    # Store each permutations under this lemma object in the database
                    o = {
                        "name": p["name"],
                        "occurrences": trans_hits,
                        "synset": source,
                        "word_base": lemma,
                        "permutator": p["permutator"],
                        "depth": depth,
                        "tag": ILL_TAG
                    }

                    # all_permutations.append(
                    #     mongo.new_permutation_for_lemma(p["name"], trans_hits))
                    all_permutations.append(o)

                if args.from_lists:
                    mongo.store_tested_pass_lists(
                        p["name"], trans_hits, source, lemma, p["permutator"])
                total_hits += trans_hits
                if trans_hits == 0:
                    not_found_cnt += 1
                else:
                    found_cnt += 1
        else:
            if args.verbose:
                log_status("Looking up [%s]" % permutations["name"])
            trans_hits = lookup(permutations["name"], depth, source, lemma)
            if args.root_syn_name:
                o = {
                    "name": permutations["name"],
                    "occurrences": trans_hits,
                    "synset": source,
                    "word_base": lemma,
                    "permutator": permutations["permutator"],
                    "depth": depth,
                    "tag": ILL_TAG
                }
                # all_permutations.append(
                #     mongo.new_permutation_for_lemma(permutations["name"], trans_hits))
                all_permutations.append(o)

            if args.from_lists:
                mongo.store_tested_pass_lists(
                    permutations["name"], trans_hits, source, lemma, p["permutator"])

            if trans_hits == 0:
                not_found_cnt += 1
            else:
                found_cnt += 1
            total_hits += trans_hits

    if args.root_syn_name:
        permutations_for_lemma = {
            "word_base": lemma,
            "permutations": all_permutations,
            "total_permutations": len(all_permutations),
            "total_hits": total_hits,
            "synset": source
        }
        mongo.store_permutations_for_lemma(permutations_for_lemma)

    return total_hits, not_found_cnt, found_cnt


def permutations_for_lemma_verb(lemma, depth, source):
    """
    Applies a set of permutators to a given lemma (string) to generate possible password combinations.
    Return:
    - total_hits: The sum of all hits for all generated passwords from this lemma. Hits for a password is the number after the colon (:) in the HIBP password file, else 0.
    - not_found_cnt: The number of generated passwords that were not found in the HIBP password file (i.e. the passwords with 0 hits)
    - found_cnt: The number of generated passwords that were found in the HIBP password file (i.e. the passwords with > 0 hits)
    """

    total_hits = 0
    not_found_cnt = 0
    found_cnt = 0
    all_permutations = []

    for combination_handler in combinator.all:
        # Generate all permutations
        permutations = combination_handler(lemma, permutator.all)
        if args.verbose:
            log_status("Permutations for [%s]: %d" %
                       (lemma, len(permutations)))
        if permutations == None:
            continue
        # Combinators always return a list of permutations
        # Unwrap all permutations and append to all_permutations
        if type(permutations) == list:
            for p in permutations:
                if args.verbose:
                    log_status("Looking up [%s]" % p["name"])
                trans_hits = lookup(p["name"], depth, source, lemma)
                # Store each permutations under this lemma object in the database
                # new_permutation_for_lemma() returns a new JSON object with the fields permutation, occurrences and tag
                # All permutations of a lemma will be stored for each lemma

                o = {
                    "name": p["name"],
                    "occurrences": trans_hits,
                    "synset": source,
                    "word_base": lemma,
                    "permutator": p["permutator"],
                    "depth": depth,
                    "tag": ILL_TAG
                }

                # all_permutations.append(
                #     mongo.new_permutation_for_lemma(p["name"], trans_hits))
                all_permutations.append(o)
                total_hits += trans_hits
                if trans_hits == 0:
                    not_found_cnt += 1
                else:
                    found_cnt += 1
        else:
            if args.verbose:
                log_status("Looking up [%s]" % permutations["name"])
            trans_hits = lookup(permutations["name"], depth, source, lemma)

            o = {
                "name": permutations["name"],
                "occurrences": trans_hits,
                "synset": source,
                "word_base": lemma,
                "permutator": permutations["permutator"],
                "depth": depth,
                "tag": ILL_TAG
            }

            # all_permutations.append(
            #     mongo.new_permutation_for_lemma(permutations["name"], trans_hits))
            all_permutations.append(o)

            if trans_hits == 0:
                not_found_cnt += 1
            else:
                found_cnt += 1
            total_hits += trans_hits

    # Assemble JSON object that is going to be stored in the database
    permutations_for_lemma = {
        "word_base": lemma,
        "permutations": all_permutations,
        "total_permutations": len(all_permutations),
        "total_hits": total_hits,
        "synset": source
    }

    # store_permutations_for_lemma_verb() has 2 main functions:
    # 1. Store the JSON object in wn_lemma_permutations_verb (lemma and each of its permutations, total hits and corresponding synset)
    # 2. Store each permutation in passwords_wn_verb (permutation name, hits, word base, corresponding synset)
    mongo.store_permutations_for_lemma_verb(permutations_for_lemma)

    return total_hits, not_found_cnt, found_cnt


def permutations_for_lemma_adjective(lemma, depth, source):
    """
    Applies a set of permutators to a given lemma (string) to generate possible password combinations.
    Return:
    - total_hits: The sum of all hits for all generated passwords from this lemma. Hits for a password is the number after the colon (:) in the HIBP password file, else 0.
    - not_found_cnt: The number of generated passwords that were not found in the HIBP password file (i.e. the passwords with 0 hits)
    - found_cnt: The number of generated passwords that were found in the HIBP password file (i.e. the passwords with > 0 hits)
    """

    total_hits = 0
    not_found_cnt = 0
    found_cnt = 0
    all_permutations = []

    for combination_handler in combinator.all:
        # Generate all permutations
        permutations = combination_handler(lemma, permutator.all)
        if args.verbose:
            log_status("Permutations for [%s]: %d" %
                       (lemma, len(permutations)))
        if permutations == None:
            continue
        # Combinators always return a list of permutations
        # Unwrap all permutations and append to all_permutations
        if type(permutations) == list:
            for p in permutations:
                if args.verbose:
                    log_status("Looking up [%s]" % p["name"])
                trans_hits = lookup(p["name"], depth, source, lemma)
                # Store each permutations under this lemma object in the database
                # new_permutation_for_lemma() returns a new JSON object with the fields permutation, occurrences and tag
                # All permutations of a lemma will be stored for each lemma

                o = {
                    "name": p["name"],
                    "occurrences": trans_hits,
                    "synset": source,
                    "word_base": lemma,
                    "permutator": p["permutator"],
                    "tag": ILL_TAG
                }

                # all_permutations.append(
                #     mongo.new_permutation_for_lemma(p["name"], trans_hits))
                all_permutations.append(o)
                total_hits += trans_hits
                if trans_hits == 0:
                    not_found_cnt += 1
                else:
                    found_cnt += 1
        else:
            if args.verbose:
                log_status("Looking up [%s]" % permutations["name"])
            trans_hits = lookup(permutations["name"], depth, source, lemma)

            o = {
                "name": permutations["name"],
                "occurrences": trans_hits,
                "synset": source,
                "word_base": lemma,
                "permutator": permutations["permutator"],
                "tag": ILL_TAG
            }

            # all_permutations.append(
            #     mongo.new_permutation_for_lemma(permutations["name"], trans_hits))
            all_permutations.append(o)

            if trans_hits == 0:
                not_found_cnt += 1
            else:
                found_cnt += 1
            total_hits += trans_hits

    # Assemble JSON object that is going to be stored in the database
    permutations_for_lemma = {
        "word_base": lemma,
        "permutations": all_permutations,
        "total_permutations": len(all_permutations),
        "total_hits": total_hits,
        "synset": source
    }

    # store_permutations_for_lemma_verb() has 2 main functions:
    # 1. Store the JSON object in wn_lemma_permutations_verb (lemma and each of its permutations, total hits and corresponding synset)
    # 2. Store each permutation in passwords_wn_verb (permutation name, hits, word base, corresponding synset)
    mongo.store_permutations_for_lemma_adjective(permutations_for_lemma)

    return total_hits, not_found_cnt, found_cnt


def permutations_for_lemma_adverb(lemma, depth, source):
    """
    Applies a set of permutators to a given lemma (string) to generate possible password combinations.
    Return:
    - total_hits: The sum of all hits for all generated passwords from this lemma. Hits for a password is the number after the colon (:) in the HIBP password file, else 0.
    - not_found_cnt: The number of generated passwords that were not found in the HIBP password file (i.e. the passwords with 0 hits)
    - found_cnt: The number of generated passwords that were found in the HIBP password file (i.e. the passwords with > 0 hits)
    """

    total_hits = 0
    not_found_cnt = 0
    found_cnt = 0
    all_permutations = []

    for combination_handler in combinator.all:
        # Generate all permutations
        permutations = combination_handler(lemma, permutator.all)
        if args.verbose:
            log_status("Permutations for [%s]: %d" %
                       (lemma, len(permutations)))
        if permutations == None:
            continue
        # Combinators always return a list of permutations
        # Unwrap all permutations and append to all_permutations
        if type(permutations) == list:
            for p in permutations:
                if args.verbose:
                    log_status("Looking up [%s]" % p["name"])
                trans_hits = lookup(p["name"], depth, source, lemma)
                # Store each permutations under this lemma object in the database
                # new_permutation_for_lemma() returns a new JSON object with the fields permutation, occurrences and tag
                # All permutations of a lemma will be stored for each lemma

                o = {
                    "name": p["name"],
                    "occurrences": trans_hits,
                    "synset": source,
                    "word_base": lemma,
                    "permutator": p["permutator"],
                    "tag": ILL_TAG
                }

                # all_permutations.append(
                #     mongo.new_permutation_for_lemma(p["name"], trans_hits))
                all_permutations.append(o)
                total_hits += trans_hits
                if trans_hits == 0:
                    not_found_cnt += 1
                else:
                    found_cnt += 1
        else:
            if args.verbose:
                log_status("Looking up [%s]" % permutations["name"])
            trans_hits = lookup(permutations["name"], depth, source, lemma)

            o = {
                "name": permutations["name"],
                "occurrences": trans_hits,
                "synset": source,
                "word_base": lemma,
                "permutator": permutations["permutator"],
                "tag": ILL_TAG
            }

            # all_permutations.append(
            #     mongo.new_permutation_for_lemma(permutations["name"], trans_hits))
            all_permutations.append(o)

            if trans_hits == 0:
                not_found_cnt += 1
            else:
                found_cnt += 1
            total_hits += trans_hits

    # Assemble JSON object that is going to be stored in the database
    permutations_for_lemma = {
        "word_base": lemma,
        "permutations": all_permutations,
        "total_permutations": len(all_permutations),
        "total_hits": total_hits,
        "synset": source
    }

    # store_permutations_for_lemma_verb() has 2 main functions:
    # 1. Store the JSON object in wn_lemma_permutations_verb (lemma and each of its permutations, total hits and corresponding synset)
    # 2. Store each permutation in passwords_wn_verb (permutation name, hits, word base, corresponding synset)
    mongo.store_permutations_for_lemma_adverb(permutations_for_lemma)

    return total_hits, not_found_cnt, found_cnt


def lookup(permutation, depth, source, word_base):
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

    # Return occurrences in order to be able to subsume them for each class.
    global total_hits_sum
    total_hits_sum += occurrences
    return occurrences


def append_with_hits(lemma, total_hits, below_hits, not_found, not_found_below, found, found_below):
    """
    Deprecated.
    """
    global hits_for_lemmas
    res_set = [lemma, total_hits, below_hits,
               not_found, not_found_below, found, found_below]
    if lemma.name() in hits_for_lemmas:
        hits_for_lemmas[lemma.name()][1] += total_hits
    else:
        hits_for_lemmas[lemma.name()] = res_set


def prompt_synset_choice(root_synsets):
    """
    If a start synset (-s) name returns more than one possible synset, prompt the user for a choice.
    """
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
    nltk.download("wordnet")
    sys.exit(0)


def option_draw_graph():
    """
    Draw the graph.
    """
    from wn_graph import draw_graph
    draw_graph(args.root_syn_name, args.dag_depth)


def option_permutate_from_lists():
    """
    Iterate over a list containing base words. Apply permutators on each word to create different variants. Then look them up.
    """
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

    dir_txt_content = get_txt_files_from_dir(args.from_lists)
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
        # Check if a ill document for this list name already exists
        if mongo.db_lists.count_documents({"filename": pass_list}) > 0:
            log_status(
                "%s already exists in database, will append results to this document" % pass_list)
        else:
            # Create new document "frame"
            mongo.init_word_list_object(pass_list)

        if args.verbose:
            log_status("Processing: %s" % pass_list)
        try:
            pass_file = open("%s/%s" % (args.from_lists, pass_list))
            curr_pass_list = pass_file.readlines()
            pass_file.close()
        except Exception as e:
            log_err("Failed to open file '%s'" % pass_list)
            # Continue with next file instead of terminating the script
            continue
        if args.verbose:
            log_status("Read all entries for: %s" % pass_list)
        for password_base in curr_pass_list:
            if password_base[0] == "#" or password_base == "" or password_base == " " or password_base == "\n":
                if args.verbose:
                    log_status("[%s] is a non-lemma. Skipping!" %
                               password_base)
                continue
            else:
                password_base = remove_control_characters(password_base)
                if args.verbose:
                    log_status(
                        "Creating permutations for [%s]" % password_base)
                total_base_lemmas += 1
                total_hits, not_found_cnt, found_cnt = permutations_for_lemma(
                    password_base, 0, pass_list)
                append_list_lemma_to_list(
                    pass_list, password_base, total_hits, found_cnt, not_found_cnt)
                if args.verbose:
                    log_status("Finished Lemma [%s]" % password_base)

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

            # Append the finished lemma to the ill collection
            mongo.append_lemma_to_wl(password_base, total_hits,
                                     found_cnt, not_found_cnt, pass_list, tag=ILL_TAG)

        finished_lists += 1

    # if args.subsume_for_classes:
    #     create_classification_for_lists(dir_txt_content)
        # _write_lists_summary_to_result_file(opts)
    print()
    cleanup()


def create_classification_for_lists(word_lists=None):
    """
    Use the data stored in the database to create a classification (and summary).
    """
    # If no word list was passed, e.g. if this function was not called by another function, we need to get our list names from a directory
    if word_lists is None:
        # We use the -l parameter to pass a destination directory containing the lists
        word_lists = get_txt_files_from_dir(args.from_lists)
        if len(word_lists) == 0:
            log_err(
                "Could not find any text files in %s to create classifications from" % args.from_lists)
            sys.exit(0)
        # We only need to manually create the summary file if this function is not called from "permutate_from_lists".
        # When this function is called first, it already created the file handles, so we don't need to do that again
        _init_file_handles(ILL_TAG, of_summary=True)

    _write_to_summary_file("File created: %s" % ILL_TAG)
    _write_to_summary_file("")

    if args.top == None:
        # limit = 0 does not limit the query
        query_limit = 0
    else:
        query_limit = args.top

    if args.classify_lists == "all":
        # Iterate over each word list stored in the database
        for filename in word_lists:
            doc = mongo.db_lists.find_one({"filename": filename})
            if doc is None:
                continue
            all_lemmas = doc["lemmas"]
            if len(all_lemmas) == 0:
                _write_to_summary_file("\t <no lemmas stored for this list>")
            # Get the total sum of hits of all hits for all permutations for this list
            total_occurrences_list = 0
            for lemma in all_lemmas:
                total_occurrences_list += lemma["occurrences"]
            all_lemmas = sorted(
                all_lemmas, key=lambda k: k["occurrences"], reverse=True)
            _write_to_summary_file("***%s (Total occurrences: %s)" %
                                   (filename, format_number(total_occurrences_list)))
            _write_to_summary_file("")
            # Iterate over each lemma of each list
            for lemma in all_lemmas:
                _write_to_summary_file("\t+ %s" % (lemma["name"]))
                _write_to_summary_file(
                    "\t|-Total Occurrences: %s" % format_number(lemma["occurrences"]))
                _write_to_summary_file(
                    "\t|-Generated Permutations: %s" % (format_number(lemma["found_cnt"] + lemma["not_found_cnt"])))
                _write_to_summary_file(
                    "\t|-Found Permutations: %s" % format_number(lemma["found_cnt"]))
                _write_to_summary_file(
                    "\t|-Not Found Permutations: %s" % format_number(lemma["not_found_cnt"]))
                _write_to_summary_file("\t|-Occurrences in this list: {:.2f}%".format(
                    lemma["occurrences"] / total_occurrences_list * 100))
                _write_to_summary_file("")
            _write_to_summary_file("")
        log_ok("Classification written to the summary file.")
    elif args.classify_lists == "sort_password_desc":
        for password in mongo.db_pws_lists.find().sort("occurrences", pymongo.DESCENDING).limit(query_limit):
            print("{}\t{}".format(password["occurrences"], password["name"]))
    elif args.classify_lists == "sort_list_desc":
        for l in mongo.db_lists.find().sort("total_hits", pymongo.DESCENDING).limit(query_limit):
            print("{}\t{}".format(l["total_hits"], l["filename"]))
    else:
        log_err("Unrecognized classification option [%s]" % args.classify_wn)


def create_complete_classification_for_wn():
    # Check if we have synsets to iterate over
    if mongo.db_wn.count_documents({}) == 0:
        log_err("No synsets found in database. Nothing to process.")
        sys.exit(0)

    _init_file_handles(ILL_TAG, of_summary=True)
    # Get the root object
    tree_root = mongo.db_wn.find_one({"parent": "root"})

    _write_to_summary_file("File created: %s" % ILL_TAG)
    _write_to_summary_file("")

    if args.top == None:
        # limit = 0 does not limit the query
        query_limit = 0
    else:
        query_limit = args.top

    if args.classify_wn == "sort_synset_desc":
        # Sort all stored synsets based on their total_hits field (so their hits as well as their hyponym hits) in descending order
        for synset in mongo.db_wn.find().sort("total_hits", pymongo.DESCENDING):
            # o = wn.synset(synset["id"])
            print("{}\t\t{}".format(synset["total_hits"], synset["id"]))
    elif args.classify_wn == "sort_lemma_desc":
        # Sort all lemmas (word bases) based on their hits in descending order

        for lemma in mongo.db_wn_lemma_permutations.find().sort("total_hits", pymongo.DESCENDING).limit(query_limit):
            print("{}\t\t{}".format(lemma["total_hits"], lemma["word_base"]))
    elif args.classify_wn == "sort_password_desc":
        for password in mongo.db_pws_wn.find().sort("occurrences", pymongo.DESCENDING).limit(query_limit):
            print("{}\t{}".format(
                password["occurrences"], password["name"], password["synset"]))
    else:
        log_err("Unrecognized classification option [%s]" % args.classify_wn)


def append_list_lemma_to_list(list_name, lemma, total_hits, found_count, not_found_count):
    """
    Deprecated.
    """
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


def plot_data():
    """
    Create plots with the previously generated data.
    """
    import plots
    # evaluate the arguments and pack them into a dictionary
    opts = {}
    if not args.top:
        opts["top"] = None
    else:
        opts["top"] = args.top

    if not args.from_lists:
        opts["ref_list"] = None
    else:
        opts["ref_list"] = args.from_lists

    if not args.dag_depth:
        opts["depth"] = None
    else:
        opts["depth"] = args.dag_depth

    if not args.start_level:
        opts["start_level"] = 0
    else:
        opts["start_level"] = args.start_level

    if not args.dict_id:
        opts["dict_id"] = "null"
    else:
        opts["dict_id"] = args.dict_id

    if not args.pass_db_path:
        opts["pass_db_path"] = "null"
    else:
        opts["pass_db_path"] = args.pass_db_path

    if not args.pw_type:
        opts["pw_type"] = "null"
    else:
        opts["pw_type"] = args.pw_type

    # Bar diagram of the top N passwords of the WordNet
    # Y axis displayed as logartihmic scale with base 10
    if args.plot == "wn_passwords_bar":
        plots.wn_top_passwords_bar(opts)

    # Bar diagram of the top N passwords of all ref lists
    elif args.plot == "lists_passwords_bar":
        plots.lists_top_passwords_bar(opts)

    # Bar diagram of the top N passwords of a given ref list
    elif args.plot == "list_top_n_passwords_bar":
        plots.list_top_n_passwords_bar(opts)

    # Bar diagram of the origin lists of the top N passwords of all ref lists
    # NOTE Interesting comparisons: --top: 10/100/1000 with vastly different results
    elif args.plot == "lists_passwords_origin_bar":
        plots.lists_top_password_origin_bar(opts)

    # NOTE Not working as intended
    # Line diagram of the top N passwords of the WordNet
    elif args.plot == "wn_passwords_line":
        plots.wn_top_passwords_line(opts)

    # NOTE Not working as intended
    elif args.plot == "lists_passwords_line":
        plots.lists_top_passwords_line(opts)

    # Marked the top 1 and top 1000 password of the WordNet as well as some
    # words in between
    # NOTE Ugly
    elif args.plot == "top_1k_wn":
        plots.wn_top_1k(opts)

    # NOTE Ugly
    elif args.plot == "top_1k_wn_bar":
        plots.wn_top_1k_bar(opts)

    # Deprecated.
    # Mix of a bar and line graph.
    # The line graph displays the top 1000 WordNet passwords.
    # The bar graph displays the top N (--top) lemmas of the specified reference word list (-l)
    # "all" value for the -l parameter will determine the top passwords for all lists, not just one specific list
    elif args.plot == "wn_line_list_categories":
        plots.wn_line_plot_categories(opts)

    # Display the top N levels (starting at 0) of the WordNet as a pie chart
    elif args.plot == "wn_display":
        plots.wn_display(opts)

    # Display the distribution of all permutations of a password "class" as a pie chart
    elif args.plot == "perm_dist":
        plots.lists_plot_permutations(opts)

    # Deprecated
    # Display the top N (--top) passwords of a misc list as a line graph
    # The list must have been indexed/looked up in the password liste beforehand (--misc_list <name>).
    # The lookup will not create perform any permutations. It is implied, that each respective list already contains the necessary permutations
    elif args.plot == "misc_lists_line":
        plots.plot_misc_lists(opts)

    # Bar diagram of the top N passwords of a given ref list
    elif args.plot == "misc_lists_top_n_passwords_bar":
        plots.misc_lists_top_n_passwords_bar(opts)

    # Overlay two misc lists as a line graph (dotted and bold).
    # The two lists to be overlayed must be looked up beforehand and will be specified with the -l param:
    # -l <list1>,<list2>
    elif args.plot == "misc_lists_overlay":
        plots.plot_overlay_two_misc_lists(opts)

    # Same as above but overlay one misc list with the top N (--top) passwords of the WordNet
    elif args.plot == "wn_misc_lists_overlay":
        plots.plot_overlay_wn_misc_list(opts)

    # Deprecated
    # Draw the the top 1000 passwords of the WordNet as a line graph. The top 1k will
    # be determined based on the occurrences of the lemmas including all their permutations
    # Then draw a bar graph showing where in the line graph the reference list top N passwords are
    # located
    elif args.plot == "wn_list_comp_perm":
        plots.wn_line_plot_categories(opts)

    # Deprecated
    # Draw the the top 1000 passwords of the WordNet as a line graph. The top 1k will
    # be determined by the single password mutations of the WordNet
    # Then draw a bar graph showing where in the line graph the reference list top N passwords are
    # located
    elif args.plot == "wn_list_comp_no_perm":
        plots.wn_ref_list_comparison(opts)

    # Draw a pie chart of the WordNet hierarchy and determine the width of the slices by the occurrences of the synset resp. lemmas and permutations with the
    # ability to specify a start level
    # TODO Print out some examples for the level d+1 so they can be manually added to the graph
    elif args.plot == "wn_display_occurrences":
        plots.wn_display_occurrences(opts)

    # Bar plot the top N synsets (with its permutations) based on their total hits.
    elif args.plot == "wn_bar_top_n":
        plots.wn_bar_top_n(opts)

    # Bar plot the top N password lists (with its permutations) based on their total hits.
    # The ref lists are specified as self-crafted lists not downloaded from the internet.
    elif args.plot == "ref_list_bar_top_n":
        plots.ref_list_bar_top_n(opts)

    # Bar plot the top N misc password lists (no permutations, since we assume these lists already contain certain permutations) based on their total hits.
    # The misc lists are specified as lists freely available on the internet.
    elif args.plot == "misc_list_bar_top_n":
        plots.misc_list_bar_top_n(opts)

    # Bar plot the top N ref list word_bases based on its group buckets total hits (including its permutations)
    # NOT WORKING AS INTENDED
    elif args.plot == "ref_list_words_bar_top_n":
        plots.ref_list_words_top_n(opts)

    # Bar chart with multiple X's comparing the top N passwords of the WordNet and a
    # given ref word list
    elif args.plot == "wn_ref_list_top_n_pass_comp_bar":
        plots.wn_ref_list_top_n_pass_comp_bar(opts)

    # Bar chart with multiple X's comparing the top N passwords of the WordNet and a
    # given misc word list
    elif args.plot == "wn_misc_list_top_n_pass_comp_bar":
        plots.wn_misc_list_top_n_pass_comp_bar(opts)

    # Bar chart with multiple X's comparing the top N passwords of two different word lists.
    elif args.plot == "ref_ref_list_top_n_pass_comp_bar":
        plots.ref_ref_list_top_n_pass_comp_bar(opts)

    # Bar chart with multiple X's comparing the top N passwords of two misc lists.
    elif args.plot == "misc_misc_list_top_n_pass_comp_bar":
        plots.misc_misc_list_top_n_pass_comp_bar(opts)

    # Bar chart with multiple X's comparing the top N passwords of a ref list and a misc list.
    elif args.plot == "ref_misc_list_top_n_pass_comp_bar":
        plots.ref_misc_list_top_n_pass_comp_bar(opts)

    # Bar chart with multiple X's comparing a different dictionary with WordNet.
    elif args.plot == "dict_wn_top_n_pass_comp_bar":
        plots.dict_wn_top_n_pass_comp_bar(opts)

    # Bar chart with multiple X's comparing a different dictionary with a ref list.
    # TODO
    elif args.plot == "dict_ref_list_top_n_pass_comp_bar":
        plots.dict_ref_list_top_n_pass_comp_bar(opts)

    # Bar chart with multiple X's comparing a different dictionary with a misc list.
    elif args.plot == "dict_misc_list_top_n_pass_comp_bar":
        plots.dict_misc_list_top_n_pass_comp_bar(opts)

    # Bar chart with multiple X's comparing a different dictionary with another dictionary.
    elif args.plot == "dict_dict_top_n_pass_comp_bar":
        plots.dict_dict_top_n_pass_comp_bar(opts)

    # Bar chart comparing the different WordNet parts of speech (noun, verb, adjective, adverb)
    elif args.plot == "wn_comp_all_pos":
        plots.wn_comp_all_pos(opts)

    # Compare the total hits of everything. WordNet, Ref Lists, Misc Lists, Alt. Dicts etc.
    elif args.plot == "comp_all":
        plots.comp_all(opts)

    # Plot the stats for the WordNet, especially thee hits per password. The expected output is going to be a value
    elif args.plot == "wn_stats":
        pass

    # Plot the coverage for all WordNet PoS
    # This means that for each PoS we determine how many passwords were found (occurrences > 0)
    elif args.plot == "wn_coverage":
        plots.wn_coverage(opts)

    else:
        log_err("Unrecognized plotting option option [%s]" % args.plot)


def get_stats():
    """
    Print some stats about the data.
    """
    opts = {}
    if not args.top:
        opts["top"] = None
    else:
        opts["top"] = args.top

    if args.stats == "wordnet":
        # Display the hits per password rate
        # sum_all_passes / count_all_passes = hits_per_pass
        stats.wordnet(opts)

    elif args.stats == "ref_lists":
        stats.ref_lists()

    elif args.stats == "misc_lists":
        stats.misc_lists()
    else:
        log_err(
            "Parameter not recognized. Please consult the documentation and try again")
        return


def option_lookup_ref_lists():
    """
    Iterate over a passwords list containing passwords. No further permutators applied. We use the passwords as is and simply look them up
    and store them in the database.
    """
    signal.signal(signal.SIGINT, sigint_handler)
    if args.top == None:
        list_read_limit = None
    else:
        list_read_limit = args.top
    if not os.path.isfile(args.misc_list):
        log_err("Not a file")
        return
    if not args.misc_list.endswith(".txt"):
        log_err("Not a .txt file")
        return

    # Open word list
    log_ok("Reading word list %s..." % args.misc_list)
    try:
        word_list = open(args.misc_list)
        words = word_list.readlines()
    except Exception as e:
        log_err("Failed to open word list")
        return
    # Close after reading
    word_list.close()
    # Try to count lines (or at least give approximation)
    try:
        word_count = subprocess.check_output(
            ["wc", "-l", "{0}".format(args.misc_list)])
    except CalledProcessError as e:
        log_err(
            "Could not count lines for destination file! % s" % e)
    word_count = int(word_count.decode(
        "utf-8").strip("\n").strip("\r").lstrip().split(" ")[0])
    log_ok("Words to lookup: %d" % int(word_count))
    progress_count = 0
    non_passwords = 0
    if os.sep in args.misc_list:
        # Split by the OS separator
        word_list_name = args.misc_list.split(os.sep)[-1]
    else:
        word_list_name = args.misc_list
    # Generate collection suffix from misc list name
    # We imply that the collection does not exists yet
    # Make it lowercase
    wl_name = args.misc_list.lower()
    # Remove .txt (4 chars)
    wl_name = wl_name[:-4]
    # Strip path prefix
    wl_name = wl_name.split("/")[-1]

    for word in words:
        if list_read_limit:
            if progress_count >= list_read_limit:
                log_ok("Read limit of %d reached. Stopping." % list_read_limit)
                return
        progress_count += 1
        # Skip comments and empty lines
        if word[0] == "#" or word == "" or word == " " or word == "\n":
            non_passwords += 1
            log_status("[%d/%d] <skipping>" % (progress_count, word_count))
            continue
        cleaned_word = remove_control_characters(word)
        result = _lookup_in_hash_file(hash_sha1(cleaned_word))
        if not result:
            result_num = 0
        else:
            result_num = int(result.split(":")[1])
        success = mongo.store_tested_pass_misc_list(
            wl_name, cleaned_word, result_num, word_list_name)
        log_status("[%d/%d] %s (%d)" %
                   (progress_count, word_count, cleaned_word, result_num))
    log_ok("Finished. %d actual words, %d non-words (empty lines, comments, etc.)" %
           (progress_count-non_passwords, non_passwords))


def option_lookup_new_dict():
    """
    Iterate over a dictionary. Dictionary are basically treated the same as word lists. However, we still logically seperate them from each other. 
    Apply permutators on each word to create different variants. Then look them up.
    """
    signal.signal(signal.SIGINT, sigint_handler)
    if not os.path.isfile(args.dict_source):
        log_err("%s is not a file" % args.dict_source)
        return

    # Open dictionary
    log_ok("Opening dictionary %s..." % args.dict_source)
    try:
        word_list = open(args.dict_source)
        words = word_list.readlines()
    except Exception as e:
        log_err("Failed to open dictionary")
        return
    # Close after reading
    word_list.close()
    # Try to count lines (or at least give approximation)
    try:
        word_count = subprocess.check_output(
            ["wc", "-l", "{0}".format(args.dict_source)])
    except CalledProcessError as e:
        log_err(
            "Could not count lines for destination file! % s" % e)
    word_count = int(word_count.decode(
        "utf-8").strip("\n").strip("\r").lstrip().split(" ")[0])
    log_ok("No. of words to permutate: %d" % int(word_count))

    def lookup_perm(perm):
        result = _lookup_in_hash_file(hash_sha1(perm))
        if not result:
            result_num = 0
        else:
            result_num = int(result.split(":")[1])
        return result_num

    # We create a separate collection for each dictionary we process. Tread carefully!
    mongo_coll = mongo.db["passwords_dicts_{}".format(args.dict_id)]

    def store_dict_perm(perm, hits, word_base, permutator, source, tag):
        o = {
            "name": perm,
            "occurrences": hits,
            "source": source,
            "word_base": word_base,
            "permutator": permutator,
            "tag": tag
        }

        try:
            mongo_coll.insert_one(o)
        except Exception as e:
            return False, e
        return True, None

    tag = get_curr_time_str()
    started_time = get_curr_time()
    total_base_lemmas = 0
    non_passwords = 0
    tested_passwords = 0

    for word in words:
        # Skip comments and empty lines
        if word[0] == "#" or word == "" or word == " " or word == "\n":
            non_passwords += 1
            log_status("<skipping> (control character)")
            continue
        # Clean the word from control chars
        cleaned_word = remove_control_characters(word)

        # Create permutations for a given base word
        for combination_handler in combinator.all:
            total_base_lemmas += 1
            permutations = combination_handler(cleaned_word, permutator.all)
            # Special case if no permutation could be created
            if permutations == None:
                continue
            elif type(permutations) == list:
                for item in permutations:
                    tested_passwords += 1
                    hit_result = lookup_perm(item["name"])
                    # Store in db...
                    insert_status, ex = store_dict_perm(
                        item["name"], hit_result, cleaned_word, item["permutator"], args.dict_source, tag)
                    if not insert_status:
                        log_err("Error inserting '{}': {}".format(
                            item["name"], ex))
                    # else:
                        # log_ok("%s  %d  %s" %
                        # (item["name"], hit_result, item["permutator"]))
            else:
                tested_passwords += 1
                hit_result = lookup_perm(item["name"])
                log_ok("%s  %d  %s" %
                       (item["name"], hit_result, item["permutator"]))
                # Store in db...
                insert_status, ex = store_dict_perm(
                    item["name"], hit_result, cleaned_word, item["permutator"], args.dict_source, tag)
                if not insert_status:
                    log_err("Error inserting '{}': {}".format(
                        item["name"], ex))
                # else:
                #     log_ok("%s  %d  %s" %
                #         (item["name"], hit_result, item["permutator"]))

        # Display progress
        curr_time = get_curr_time()
        time_diff = curr_time - started_time
        curr_lemma_time = time_diff.seconds / total_base_lemmas
        remaining_lemmas = word_count - total_base_lemmas
        remaining_time_est = remaining_lemmas * curr_lemma_time
        clear_terminal()
        log_status("Processing dictionary: {0}\nProcessed Base Words (approx.): {1}/{2}\nTested Passwords: {3}\nCurrent Word Base: {4}\nElapsed Time (seconds): {5:.2f}\nEstimated Remaining Time (m/h): {6:.2f}/{7:.2f}\nCurrent Average Time per Lemma (s): {8:.2f}\n".format(
            args.dict_source,
            total_base_lemmas,
            word_count,
            tested_passwords,
            cleaned_word,
            time_diff.seconds,
            remaining_time_est / 60,
            remaining_time_est / 60 / 60,
            curr_lemma_time))

        continue

    clear_terminal()
    curr_time = get_curr_time()
    time_diff = curr_time - started_time
    log_ok("Finished. \nActual Word Bases Processed: {0}\nControl Characters: {1}\nTook: {2}s/{3}m".format(
        total_base_lemmas,
        non_passwords,
        time_diff.seconds,
        time_diff.minutes))


if __name__ == "__main__":
    if args.dl_wordnet:
        _download_wordnet()

    if args.extensive:
        log_ok("WARNING: You set the -e (--extensive) flag writes EVERY tested password to a seperate file. " +
               "Note that this is going to slow down the script a lot, since file I/O is slow. This flag can increase " +
               "the overall runtime of the script by a factor of 20-25 (and even more).")
        if args.skip_warning:
            pass
        else:
            log_status("ENTER to continue.")
            temp = input()

    if args.lookup_utility:
        log_status("NOTE: Make sure you have sgrep installed and added to PATH.")
        print()
        print()

    from nltk.corpus import wordnet as wn

    # WordNet graph
    if args.draw_dag:
        # Evaluate command line parameters
        if args.dag_depth is None or args.root_syn_name is None:
            log_err("Missing parameters.")
            parser.print_usage()
            sys.exit(0)
        option_draw_graph()
    # Lookup words from self-created lists
    elif args.classify_lists:
        # if args.from_lists is None:
        #     log_err("Missing parameters.")
        #     sys.exit(0)
        create_classification_for_lists()
    elif args.classify_wn:
        create_complete_classification_for_wn()
    elif args.from_lists and not args.plot:
        option_permutate_from_lists()
    elif args.plot:
        plot_data()
    elif args.stats:
        get_stats()
    elif args.misc_list:
        option_lookup_ref_lists()
    elif args.wn_pos:
        if args.wn_pos == "v":
            option_verb_wordnet()
        elif args.wn_pos == "a":
            option_adjective_wordnet()
        elif args.wn_pos == "r":
            option_adverb_wordnet()
        elif args.wn_pos == "n":
            option_lookup_passwords()
    else:
        # Evaluate command line parameters
        if args.wn:
            if args.pass_db_path is None or args.dag_depth is None or args.root_syn_name is None:
                log_err("Missing parameters.")
                parser.print_usage()
                sys.exit(0)
            option_lookup_passwords()
        elif args.dict_source:
            if args.dict_id:
                option_lookup_new_dict()
            else:
                log_err(
                    "No dict ID. Please specify an ID using only characters with the --dict-id parameter.")
                sys.exit(0)
        else:
            log_err("Unrecognized option.")
