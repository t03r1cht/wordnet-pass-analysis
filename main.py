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

# pip installation über py binary: py -m pip install nltk

words = [
    "ham",
    "meatballs",
    "apple",
    "bacon",
    "ham",
]

total_processed = 0


def lookup_password():
    pwned_pass_list = "E:\\HIBP Passwords\\pwned-passwords-sha1-ordered-by-count-v4.txt"
    hashed_pw = hashlib.sha1("test".encode("utf-8")).hexdigest()
    try:
        result = subprocess.check_output(
            ["findstr", "/i", hashed_pw, pwned_pass_list], shell=True)
    except CalledProcessError:
        return
    str_result = result.decode("utf-8").strip("\n").strip("\r")
    print(str_result.split(":"))


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
    os.system("clear") if platform.system() == "Linux" else os.system("cls")

def update_stats(current, finished):
    clear_terminal()
    print()
    print()
    # print(int(get_shell_width() / 2) * "+=")
    c_t = get_curr_time()
    print("  WordNet Password Analysis // Time: %s" % c_t)
    # print("%s".center(get_shell_width() - len(c_t)) % c_t)
    # print(int(get_shell_width() / 2) * "+=")
    print()
    print("  Processing: \t%s" % current)
    print("  Finished: \t%d" % finished)
    print()


def recurse_nouns_from_root(root_syn, until_level=0):
    if root_syn.min_depth() == until_level:
            # print("Reached depth: %d" % until_level)
            return
    curr_root_syn = root_syn
    for hypo in curr_root_syn.hyponyms():
        # print("{0}({2}){1}".format(hypo.min_depth() * "  ", hypo.lemma_names(), hypo.min_depth()))
        for lemma in hypo.lemma_names():
            hashed_lemma = hash_sha1(lemma)
            global total_processed
            total_processed += 1
            update_stats(current="%s / %s" % (lemma, hashed_lemma), finished=total_processed)
        recurse_nouns_from_root(root_syn=hypo, until_level=until_level)



def analyze_root_hypernyms(loops=100):
    synsets = list(wn.all_synsets("n"))[100:100+loops]
    for syn in synsets:
        hyper_path = [s.name() for s in syn.hypernym_paths()[0]]
        print("  %s path: %s" % (syn.name(), hyper_path))

def hash_sha1(s):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()

if __name__ == "__main__":
    # root_synset = wn.synset("entity.n.01")
    # print(root_synset.name())
    # r_h = [hyponym for hyponym in root_synset.hyponyms()]
    # second_lvl_r_h = [print("hyponyms for {0} [{1}]: {2}\n".format(sec_hyponym.name(), sec_hyponym.min_depth(), len(sec_hyponym.hyponyms()))) for first_hyponym in root_synset.hyponyms()
    #                   for sec_hyponym in first_hyponym.hyponyms()]
    init()
    signal.signal(signal.SIGINT, sigint_handler)

    clear_terminal()
    print()
    # new_str = ""
    # for w in words:
    #     sys.stdout.flush()
    #     # new_str = "processing word: %s %s %s %s" % (
    #     #     Back.GREEN, Fore.RED, w, Style.RESET_ALL)
    #     new_str = "processing word: %s" % (w)
    #     cols, _ = shutil.get_terminal_size((80, 20))
    #     sys.stdout.write(new_str.ljust(cols - len(new_str), " "))
    #     sys.stdout.write("\r")
    #     time.sleep(random.random())
    # sys.stdout.write("%s... Done!\n" % new_str)

    # cnt = 0
    # total_len = len(list(wn.all_synsets("n")))
    # for synset in list(wn.all_synsets("n"))[:100]:
    #     refresh_stats(total=total_len, current_syn=synset.name(), finished=cnt)
    #     cnt += 1


    # synset = wn.synset("entity.n.01")
    # print(synset.min_depth())
    # print("synset: {0}, lemmas: {1}".format(synset.name(), synset.lemma_names()))
    # hyponyms = synset.hyponyms()
    # for hn in hyponyms:
    #     print("  synset: {0}, lemmas: {1}, depth: {3} hypernyms: {2}".format(hn.name(), hn.lemma_names(), hn.hypernyms(), hn.min_depth()))
    #     for hn1 in hn.hyponyms():
    #             print("    synset: {0}, lemmas: {1}, depth: {3} hypernyms: {2}".format(hn1.name(), hn1.lemma_names(), hn1.hypernyms(), hn1.min_depth()))




    # len_noun = len(list(wn.all_synsets("n")))
    # len_verb = len(list(wn.all_synsets("v")))
    # len_adj = len(list(wn.all_synsets("a")))
    # len_adv = len(list(wn.all_synsets("r")))
    # len_all_sum = len_noun + len_verb + len_adj + len_adv
    # len_all = len(list(wn.all_synsets()))

    # print("len.noun: %d" % len_noun)
    # print("len.verb: %d" % len_verb)
    # print("len.adj: %d" % len_adj)
    # print("len.adv: %d" % len_adv)
    # print("len.all: %d-%d" % (len_all_sum, len_all))


    recurse_nouns_from_root(wn.synset("entity.n.01"), 2)


    print()