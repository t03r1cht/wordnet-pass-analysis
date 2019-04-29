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

parser = argparse.ArgumentParser(description="Password hash anaylsis using WordNet and the HaveIBeenPwned database")
parser.add_argument("-p", "--pass-database", type=str, required=True, help="Path to the HIBP password database", dest="pass_db_path")
parser.add_argument("-d", "--depth", type=int, required=True, help="Depth in the DAG", dest="dag_depth")
args = parser.parse_args()

total_processed = 0
started = ""
outfile_name = "results.txt"
outfile_f = open(outfile_name, "w+")

def lookup_password():
    pwned_pass_list = "E:\\HIBP Passwords\\pwned-passwords-sha1-ordered-by-count-v4.txt"
    hashed_pw = hashlib.sha1("test".encode("utf-8")).hexdigest()
    


def sigint_handler(sig, frame):
    print()
    print("Caught Ctrl+C, shutting down...")
    sys.exit(0)


def get_shell_width():
    cols, _ = shutil.get_terminal_size((80, 20))
    return cols


def get_curr_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def clear_terminal():
    os.system("clear") if platform.system() == "Linux" or platform.system() == "Darwin" else os.system("cls")

def update_stats(current, finished):
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
    """Wrapper for _lookup_in_hash_file
    """
    occurrences = _lookup_in_hash_file(hash)
    if occurrences is None:
        return 0
    else: 
        return int(occurrences.split(":")[1])


def _lookup_in_hash_file(hash):
    try:
        result = subprocess.check_output(["look", "-f", hash, args.pass_db_path])
    except CalledProcessError as e:
        print(e)
        return None
    return result.decode("utf-8").strip("\n").strip("\r")
        


def analyze_root_hypernyms(loops=100):
    synsets = list(wn.all_synsets("n"))[100:100+loops]
    for syn in synsets:
        hyper_path = [s.name() for s in syn.hypernym_paths()[0]]
        print("  %s path: %s" % (syn.name(), hyper_path))

def hash_sha1(s):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


def recurse_nouns_from_root(root_syn, max_depth=0):
    """Iterates over each hyponym synset until the desired depth in the DAG is reached. 

    For each level of hyponyms in the DAG, this function will unpack each lemma of each 
    synset of said depth level, which can be confusing when looking at results.txt.

    Each indented set of lemmas is the sum of all unpacked lemmas of each synset of the current graph level.
    """
    if root_syn.min_depth() == max_depth:
            return
    curr_root_syn = root_syn
    for hypo in curr_root_syn.hyponyms():
        for lemma in hypo.lemma_names():
            hashed_lemma = hash_sha1(lemma)
            occurrences = lookup_pass(hashed_lemma)
            global total_processed
            total_processed += 1
            _write_result_to_results_file(lemma, hypo.min_depth(), occurrences)
            update_stats(current="%s / %d" % (lemma, occurrences), finished=total_processed)
        recurse_nouns_from_root(root_syn=hypo, max_depth=max_depth)



def _write_result_to_results_file(lemma_name, lemma_depth, occurrences):
    """Wrapper for the _write_results_file() function
    """
    _write_to_results_file("%s%s %d" % (lemma_depth * "  ", lemma_name, occurrences))

def _write_to_results_file(s):
    outfile_f.write("%s\n" % s)


if __name__ == "__main__":
    init()
    signal.signal(signal.SIGINT, sigint_handler)
    clear_terminal()
    nltk.download("wordnet")
    print()
    started_time = get_curr_time()

    root_syn = wn.synset("entity.n.01")
    for root_lemma in root_syn.lemma_names():
        _write_result_to_results_file(root_lemma, root_syn.min_depth(), lookup_pass(hash_sha1(root_lemma)))
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