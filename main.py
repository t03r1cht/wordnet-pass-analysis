from nltk.corpus import wordnet as wn
import nltk
import hashlib
import timeit
import subprocess
from subprocess import CalledProcessError
import time
import curses
import sys
import random
import shutil
import signal
from colorama import init, Fore, Back, Style
import platform
import os
import datetime

words = [
    "ham",
    "meatballs",
    "apple",
    "bacon",
    "ham",
    "ham",
    "meatballs",
    "apple",
    "bacon",
    "ham",
    "ham",
    "meatballs",
    "apple",
    "bacon",
    "ham",
    "ham",
    "meatballs",
    "apple",
    "bacon",
    "ham",
]


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


def refresh_stats():
    os.system("clear") if platform.system() == "Linux" else os.system("cls")
    print("************************************************************")
    print("**************************  %s  *****************************" %
          datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("************************************************************")
    print()
    print("Processing: %s" % words[random.randint(0, len(words)-1)])
    print("Successful: %f" % random.random())
    print("Failed: %f" % random.random())
    print("Total: %f" % random.random())


if __name__ == "__main__":
    # root_synset = wn.synset("entity.n.01")
    # print(root_synset.name())
    # r_h = [hyponym for hyponym in root_synset.hyponyms()]
    # second_lvl_r_h = [print("hyponyms for {0} [{1}]: {2}\n".format(sec_hyponym.name(), sec_hyponym.min_depth(), len(sec_hyponym.hyponyms()))) for first_hyponym in root_synset.hyponyms()
    #                   for sec_hyponym in first_hyponym.hyponyms()]
    init()
    signal.signal(signal.SIGINT, sigint_handler)

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

    for w in words:
        refresh_stats()
        time.sleep(random.random())
