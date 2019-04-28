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


def get_shell_width():
    cols, _ = shutil.get_terminal_size((80, 20))
    return cols


def get_curr_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def refresh_stats(total, current_syn, finished):
    os.system("clear") if platform.system() == "Linux" else os.system("cls")
    print()
    print()
    print(int(get_shell_width() / 2) * "+=")
    c_t = get_curr_time()
    print("%s".center(get_shell_width() - len(c_t)) % c_t)
    print(int(get_shell_width() / 2) * "+=")
    print()
    print("  Current: \t%s" % current_syn)
    print("  Progress: \t%d / %d" % (finished, total))
    print("  Finished: \t%d" % finished)
    print("  Total: \t%d" % total)
    print()


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

    cnt = 0
    total_len = len(list(wn.all_synsets("n")))
    for synset in list(wn.all_synsets("n"))[:100]:
        refresh_stats(total=total_len, current_syn=synset.name(), finished=cnt)
        cnt += 1
