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

# pip installation über py binary: py -m pip install nltk

parser = argparse.ArgumentParser(
    description="Password hash anaylsis using WordNet and the HaveIBeenPwned database")
parser.add_argument("-p", "--pass-database", type=str, required=True,
                    help="Path to the HIBP password database", dest="pass_db_path")
parser.add_argument("-d", "--depth", type=int, required=True,
                    help="Depth in the DAG", dest="dag_depth")
args = parser.parse_args()

total_processed = 0
started = ""
outfile_name = "results.txt"
outfile_f = open(outfile_name, "w+")
permut_handler = None


def sigint_handler(sig, frame):
    """Register the handler for the SIGINT signal.

    This is absolutely necessary to exit the program with Ctrl+C because a user easily misconfigure the 
    programe (i.e. -d > 4) for it to result in a combinatorial explosion because of its recursion.
    """
    print()
    print("Caught Ctrl+C, shutting down...")
    sys.exit(0)


def get_shell_width():
    """Return the number of colums in the current shell view.
    """
    cols, _ = shutil.get_terminal_size((80, 20))
    return cols


def get_curr_time():
    """Return the current time, nicely formatted as a string.
    """
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def clear_terminal():
    """Clear the terminal. This is required to properly display the stats while running.
    """
    os.system("clear") if platform.system(
    ) == "Linux" or platform.system() == "Darwin" else os.system("cls")


def update_stats(current, finished):
    """Print out the stats while the program is running.
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
    """Wrapper for _lookup_in_hash_file. Returns the occurrences of the 
    searched hash/password in the HIBP password file.
    """
    occurrences = _lookup_in_hash_file(hash)
    if occurrences is None:
        return 0
    else:
        return int(occurrences.split(":")[1])


def _lookup_in_hash_file(hash):
    """Implements actual file access.
    """
    try:
        result = subprocess.check_output(
            ["look", "-f", hash, args.pass_db_path])
    except CalledProcessError as e:
        return None
    return result.decode("utf-8").strip("\n").strip("\r")


def hash_sha1(s):
    """Hash the password.
    """
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


def recurse_nouns_from_root(root_syn, max_depth=0):
    """Iterates over each hyponym synset until the desired depth in the DAG is reached. 

    For each level of hyponyms in the DAG, this function will unpack each lemma of each 
    synset of said depth level, which can be confusing when looking at results.txt.

    Each indented set of lemmas is the sum of all unpacked lemmas of each synset of the current graph level.
    """

    # If the current depth in the DAG is reached, do not continue to iterate this path.
    if root_syn.min_depth() == max_depth:
        return
    curr_root_syn = root_syn
    for hypo in curr_root_syn.hyponyms():
        for lemma in hypo.lemma_names():
            # Apply a set of permutators to each lemma
            permutations_for_lemma(lemma)
            # hashed_lemma = hash_sha1(lemma)
            # occurrences = lookup_pass(hashed_lemma)
            # global total_processed
            # total_processed += 1
            # _write_result_to_results_file(lemma, hypo.min_depth(), occurrences)
            # update_stats(current="%s / %d" %
            #              (lemma, occurrences), finished=total_processed)
        # Execute the function again with the new root synset being each hyponym we just found.
        recurse_nouns_from_root(root_syn=hypo, max_depth=max_depth)


def permutations_for_lemma(lemma):
    """Compute all permutations by using the registered permutators.
    """
    for permut_handler in permutator.all:
        # The permutator returns the permutated lemma.
        permut = permut_handler(lemma)
        # Print the permutations to the result file.
        print("    ", permut)
        pass


def _permut_registrar():
    """Decorator to register permutation handlers
    """
    permut_registry = []

    def registrar(func):
        permut_registry.append(func)
        return func
    registrar.all = permut_registry
    return registrar


permutator = _permut_registrar()


@permutator
def casing_handler(lemma):
    return "PERMUTATOR_CASING_HANDLER %s" % lemma


def _write_result_to_results_file(lemma_name, lemma_depth, occurrences):
    """Wrapper for the _write_results_file() function
    """
    _write_to_results_file("%s%s %d" % (
        lemma_depth * "  ", lemma_name, occurrences))


def _write_to_results_file(s):
    outfile_f.write("%s\n" % s)


if __name__ == "__main__":
    init()
    signal.signal(signal.SIGINT, sigint_handler)
    clear_terminal()
    nltk.download("wordnet")
    print()
    started_time = get_curr_time()

    # print("handler: %s" % permutator.all)
    # for h in permutator.all:
    #     h("testString")

    root_syn = wn.synset("entity.n.01")
    for root_lemma in root_syn.lemma_names():
        _write_result_to_results_file(
            root_lemma, root_syn.min_depth(), lookup_pass(hash_sha1(root_lemma)))
        total_processed += 1

    recurse_nouns_from_root(root_syn=root_syn, max_depth=args.dag_depth)

    print()
    _write_to_results_file("")
    _write_to_results_file(40 * "=")
    _write_to_results_file("Starting Time: %s" % started_time)
    _write_to_results_file("Total lemmas processed: %d" % total_processed)
    finished_time = get_curr_time()
    print("  Finished: %s" % finished_time)
    _write_to_results_file("Finishing Time: %s" % finished_time)
    print()
    print("  Results written to %s" % outfile_name)
    outfile_f.close()
    print()
