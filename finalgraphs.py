import mongo
from helper import log_err, log_ok, log_status
import helper
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import numpy as np
from textwrap import wrap
import sys
from os import path
import pymongo
from nltk.corpus import wordnet as wn
import duplicates
from tabulate import tabulate
from combinators import combinator, combinator_registrar
from permutators import permutator, permutator_registrar
from helper import get_curr_time, get_curr_time_str
import argparse
import hashlib
from subprocess import CalledProcessError
import subprocess
import duplicates
import re


parser = argparse.ArgumentParser(
    description="Password hash anaylsis using WordNet and the HaveIBeenPwned database.")
parser.add_argument("-p", "--pass-database", type=str,
                    help="Path to the HIBP password database.", dest="pass_db_path")
parser.add_argument("-t", "--lookup-utility", action="store_true",
                    help="If set, use sgrep instead of the look utility.", dest="lookup_utility")
parser.add_argument("-x", "--hibp", type=str,
                    help="Path to the HIBP top X sorted file.", dest="hibp")
args = parser.parse_args()

# Progress pad: https://pad.riseup.net/p/q5Qvgib36rkzQiWZE3uE

# Ignore deprecation warnings:
# py.exe -Wignore::DeprecationWarning .\finalgraphs.py

pwned_pw_amount = 551509767
ILL_TAG = get_curr_time_str()


def main():
    # =============================================================================================================================================
    #
    #  Calculate average permutations per lemma
    #
    # avg = avg_permutations_lemma("wordnet_n")
    # log_ok("Average permutations per lemma for Wordnet nouns: %d" % (avg))  # 224
    # avg = avg_permutations_lemma("wordnet_v")
    # log_ok("Average permutations per lemma for Wordnet verbs: %d" % (avg))  # 222
    # avg = avg_permutations_lemma("wordnet_adj")
    # log_ok("Average permutations per lemma for Wordnet adjectives: %d" %
    #        (avg))  # 221
    # avg = avg_permutations_lemma("wordnet_adv")
    # log_ok("Average permutations per lemma for Wordnet adverbs: %d" % (avg))  # 222
    # =============================================================================================================================================
    #
    # Calculate the number of hits (efficiency) as well as the percentage of hits (coverage)
    #

    # Spartenlisten

    # pw_hits, pct_hits = calculate_efficiency("list", source_name="01_en_office_supplies.txt", include_perms=False)
    # log_ok("01_en_office_supplies.txt (w/o permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))
    # pw_hits, pct_hits = calculate_efficiency("list", source_name="01_en_office_supplies.txt", include_perms=True)
    # log_ok("01_en_office_supplies.txt (w/ permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))
    
    # pw_hits, pct_hits = calculate_efficiency("list", source_name="02_en_office_brands.txt", include_perms=False)
    # log_ok("02_en_office_brands.txt (w/o permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))
    # pw_hits, pct_hits = calculate_efficiency("list", source_name="02_en_office_brands.txt", include_perms=True)
    # log_ok("02_en_office_brands.txt (w/ permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))

    # pw_hits, pct_hits = calculate_efficiency("list", source_name="03_keyboard_patterns.txt", include_perms=False)
    # log_ok("03_keyboard_patterns.txt.txt (w/o permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))
    # pw_hits, pct_hits = calculate_efficiency("list", source_name="03_keyboard_patterns.txt", include_perms=True)
    # log_ok("03_keyboard_patterns.txt.txt (w/ permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))

    # pw_hits, pct_hits = calculate_efficiency("list", source_name="05_en_financial_brands.txt", include_perms=False)
    # log_ok("05_en_financial_brands.txt (w/o permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))
    # pw_hits, pct_hits = calculate_efficiency("list", source_name="05_en_financial_brands.txt", include_perms=True)
    # log_ok("05_en_financial_brands.txt (w/ permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))

    # pw_hits, pct_hits = calculate_efficiency("list", source_name="06_en_cities.txt", include_perms=False)
    # log_ok("06_en_cities.txt (w/o permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))
    # pw_hits, pct_hits = calculate_efficiency("list", source_name="06_en_cities.txt", include_perms=True)
    # log_ok("06_en_cities.txt (w/ permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))

    # pw_hits, pct_hits = calculate_efficiency("list", source_name="07_first_names.txt", include_perms=False)
    # log_ok("07_first_names.txt (w/o permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))
    # pw_hits, pct_hits = calculate_efficiency("list", source_name="07_first_names.txt", include_perms=True)
    # log_ok("07_first_names.txt (w/ permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))

    # pw_hits, pct_hits = calculate_efficiency("list", source_name="08_last_names.txt", include_perms=False)
    # log_ok("08_last_names.txt (w/o permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))
    # pw_hits, pct_hits = calculate_efficiency("list", source_name="08_last_names.txt", include_perms=True)
    # log_ok("08_last_names.txt (w/ permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))

    # pw_hits, pct_hits = calculate_efficiency("list", source_name="09_en_countries.txt", include_perms=False)
    # log_ok("09_en_countries.txt (w/o permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))
    # pw_hits, pct_hits = calculate_efficiency("list", source_name="09_en_countries.txt", include_perms=True)
    # log_ok("09_en_countries.txt (w/ permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))

    # pw_hits, pct_hits = calculate_efficiency("list", source_name="10_automobile.txt", include_perms=False)
    # log_ok("10_automobile.txt (w/o permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))
    # pw_hits, pct_hits = calculate_efficiency("list", source_name="10_automobile.txt", include_perms=True)
    # log_ok("10_automobile.txt (w/ permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))

    # pw_hits, pct_hits = calculate_efficiency("list", source_name="11_software_names.txt", include_perms=False)
    # log_ok("11_software_names.txt (w/o permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))
    # pw_hits, pct_hits = calculate_efficiency("list", source_name="11_software_names.txt", include_perms=True)
    # log_ok("11_software_names.txt (w/ permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))

    # pw_hits, pct_hits = calculate_efficiency("list", source_name="12_tech_brands.txt", include_perms=False)
    # log_ok("12_tech_brands.txt (w/o permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))
    # pw_hits, pct_hits = calculate_efficiency("list", source_name="12_tech_brands.txt", include_perms=True)
    # log_ok("12_tech_brands.txt (w/ permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))

    # pw_hits, pct_hits = calculate_efficiency("list", source_name="13_en_fruit.txt", include_perms=False)
    # log_ok("13_en_fruit.txt (w/o permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))
    # pw_hits, pct_hits = calculate_efficiency("list", source_name="13_en_fruit.txt", include_perms=True)
    # log_ok("13_en_fruit.txt (w/ permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))

    # pw_hits, pct_hits = calculate_efficiency("list", source_name="14_en_drinks.txt", include_perms=False)
    # log_ok("14_en_drinks.txt (w/o permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))
    # pw_hits, pct_hits = calculate_efficiency("list", source_name="14_en_drinks.txt", include_perms=True)
    # log_ok("14_en_drinks.txt (w/ permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))

    # pw_hits, pct_hits = calculate_efficiency("list", source_name="15_en_food.txt", include_perms=False)
    # log_ok("15_en_food.txt (w/o permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))
    # pw_hits, pct_hits = calculate_efficiency("list", source_name="15_en_food.txt", include_perms=True)
    # log_ok("15_en_food.txt (w/ permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))

    # pw_hits, pct_hits = calculate_efficiency("list", source_name="99_unsortiert.txt", include_perms=False)
    # log_ok("99_unsortiert.txt (w/o permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))
    # pw_hits, pct_hits = calculate_efficiency("list", source_name="99_unsortiert.txt", include_perms=True)
    # log_ok("99_unsortiert.txt (w/ permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))

    # Misc Lists
    
    # pw_hits, pct_hits = calculate_efficiency("misc_list", source_name="10-million-password-list-top-500", include_perms=True)
    # log_ok("10-million-password-list-top-500 (w/ permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))

    # pw_hits, pct_hits = calculate_efficiency("misc_list", source_name="100k-most-used-passwords-ncsc", include_perms=True)
    # log_ok("100k-most-used-passwords-ncsc (w/ permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))

    # pw_hits, pct_hits = calculate_efficiency("misc_list", source_name="10k-most-common", include_perms=True)
    # log_ok("10k-most-common (w/ permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))

    # pw_hits, pct_hits = calculate_efficiency("misc_list", source_name="cirt-default-passwords", include_perms=True)
    # log_ok("cirt-default-passwords (w/ permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))

    # pw_hits, pct_hits = calculate_efficiency("misc_list", source_name="common-passwords-win", include_perms=True)
    # log_ok("common-passwords-win (w/ permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))

    # pw_hits, pct_hits = calculate_efficiency("misc_list", source_name="lizard-squad", include_perms=True)
    # log_ok("lizard-squad (w/ permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))

    # pw_hits, pct_hits = calculate_efficiency("misc_list", source_name="milw0rm-dictionary", include_perms=True)
    # log_ok("milw0rm-dictionary (w/ permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))

    # pw_hits, pct_hits = calculate_efficiency("misc_list", source_name="top-20-common-ssh-passwords", include_perms=True)
    # log_ok("top-20-common-ssh-passwords (w/ permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))

    # pw_hits, pct_hits = calculate_efficiency("misc_list", source_name="twitter-banned", include_perms=True)
    # log_ok("twitter-banned (w/ permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))

    # pw_hits, pct_hits = calculate_efficiency("misc_list", source_name="xato-net-10-million-passwords", include_perms=True)
    # log_ok("xato-net-10-million-passwords (w/ permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))

    # pw_hits, pct_hits = calculate_efficiency("misc_list", source_name="xato-net-10-million-passwords-100000", include_perms=True)
    # log_ok("xato-net-10-million-passwords-100000 (w/ permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))

    # Dicts

    # pw_hits, pct_hits = calculate_efficiency("dict", source_name="american-english", include_perms=False)
    # log_ok("american-english (w/o permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))
    # pw_hits, pct_hits = calculate_efficiency("dict", source_name="american-english", include_perms=True)
    # log_ok("american-english (w/ permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))

    # pw_hits, pct_hits = calculate_efficiency("dict", source_name="british-english", include_perms=False)
    # log_ok("british-english (w/o permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))
    # pw_hits, pct_hits = calculate_efficiency("dict", source_name="british-english", include_perms=True)
    # log_ok("british-english (w/ permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))

    # pw_hits, pct_hits = calculate_efficiency("dict", source_name="cracklib-small", include_perms=False)
    # log_ok("cracklib-small (w/o permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))
    # pw_hits, pct_hits = calculate_efficiency("dict", source_name="cracklib-small", include_perms=True)
    # log_ok("cracklib-small (w/ permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))
    
    # Wordnet
    # pw_hits, pct_hits = calculate_efficiency("wordnet_n", include_perms=False)
    # log_ok("Wordnet nouns (w/o permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))
    # pw_hits, pct_hits = calculate_efficiency("wordnet_n", include_perms=True)
    # log_ok("Wordnet nouns (w/ permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))

    # pw_hits, pct_hits = calculate_efficiency("wordnet_v", include_perms=False)
    # log_ok("Wordnet verbs (w/o permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))
    # pw_hits, pct_hits = calculate_efficiency("wordnet_v", include_perms=True)
    # log_ok("Wordnet verbs (w/ permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))

    # pw_hits, pct_hits = calculate_efficiency(
    #     "wordnet_adj", include_perms=False)
    # log_ok("Wordnet adjectives (w/o permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))
    # pw_hits, pct_hits = calculate_efficiency("wordnet_adj", include_perms=True)
    # log_ok("Wordnet adjectives (w/ permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))

    # pw_hits, pct_hits = calculate_efficiency(
    #     "wordnet_adv", include_perms=False)
    # log_ok("Wordnet adverbs (w/o permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))
    # pw_hits, pct_hits = calculate_efficiency("wordnet_adv", include_perms=True)
    # log_ok("Wordnet adverbs (w/ permutations):\n\tPassword hits: {}\n\tPercentage hits: {}%".format(pw_hits, round(pct_hits*100, 5)))
    # =============================================================================================================================================
    #
    # Plot the wordnet coverage for all parts of speech (with and without permutations)
    #
    # wordnet_coverage(include_perms=False)
    # wordnet_coverage(include_perms=True)
    # =============================================================================================================================================
    #
    # Locate the top n passwords from a category list on the top n passwords of the HIBP file
    #
    # locate_topn_list_pws_hibp("01_en_office_supplies.txt", top=10, include_perms=False)
    # locate_topn_list_pws_hibp("01_en_office_supplies.txt", top=10, include_perms=True)
    # locate_topn_list_pws_hibp("02_en_office_brands.txt", top=10, include_perms=False)
    # locate_topn_list_pws_hibp("02_en_office_brands.txt", top=10, include_perms=True)
    # locate_topn_list_pws_hibp("03_keyboard_patterns.txt", top=10, include_perms=False)
    # locate_topn_list_pws_hibp("03_keyboard_patterns.txt", top=10, include_perms=True)
    # locate_topn_list_pws_hibp("05_en_financial_brands.txt", top=10, include_perms=False)
    # locate_topn_list_pws_hibp("05_en_financial_brands.txt", top=10, include_perms=True)
    # locate_topn_list_pws_hibp("06_en_cities.txt", top=10, include_perms=False)
    # locate_topn_list_pws_hibp("06_en_cities.txt", top=10, include_perms=True)
    # locate_topn_list_pws_hibp("07_first_names.txt", top=10, include_perms=False)
    # locate_topn_list_pws_hibp("07_first_names.txt", top=10, include_perms=True)
    # locate_topn_list_pws_hibp("08_last_names.txt", top=10, include_perms=False)
    # locate_topn_list_pws_hibp("08_last_names.txt", top=10, include_perms=True)
    # locate_topn_list_pws_hibp("09_en_countries.txt", top=10, include_perms=False)
    # locate_topn_list_pws_hibp("09_en_countries.txt", top=10, include_perms=True)
    # locate_topn_list_pws_hibp("10_automobile.txt", top=10, include_perms=False)
    # locate_topn_list_pws_hibp("10_automobile.txt", top=10, include_perms=True)
    # locate_topn_list_pws_hibp("11_software_names.txt", top=10, include_perms=False)
    # locate_topn_list_pws_hibp("11_software_names.txt", top=10, include_perms=True)
    # locate_topn_list_pws_hibp("12_tech_brands.txt", top=10, include_perms=False)
    # locate_topn_list_pws_hibp("12_tech_brands.txt", top=10, include_perms=True)
    # locate_topn_list_pws_hibp("13_en_fruit.txt", top=10, include_perms=False)
    # locate_topn_list_pws_hibp("13_en_fruit.txt", top=10, include_perms=True)
    # locate_topn_list_pws_hibp("14_en_drinks.txt", top=10, include_perms=False)
    # locate_topn_list_pws_hibp("14_en_drinks.txt", top=10, include_perms=True)
    # locate_topn_list_pws_hibp("15_en_food.txt", top=10, include_perms=False)
    # locate_topn_list_pws_hibp("15_en_food.txt", top=10, include_perms=True)
    # =============================================================================================================================================
    #
    # Print a list with the top n passwords of the wordnet (with and without permutations)
    #
    # print("Nouns")
    # print_top_lemmas("n", 20, include_perms=False)
    # print()
    # print("Nouns")
    # print_top_lemmas("n", 20, include_perms=True, no_numbers=True)
    # print()
    # print("Verbs")
    # print_top_lemmas("v", 20, include_perms=False)
    # print()
    # print("Verbs")
    # print_top_lemmas("v", 20, include_perms=True, no_numbers=True)
    # print()
    # print("Adjectives")
    # print_top_lemmas("adj", 20, include_perms=False)
    # print()
    # print("Adjectives")
    # print_top_lemmas("adj", 20, include_perms=True, no_numbers=True)
    # print()
    # print("Adverbs")
    # print_top_lemmas("adv", 20, include_perms=False)
    # print()
    # print("Adverbs")
    # print_top_lemmas("adv", 20, include_perms=True, no_numbers=True)
    # print()
    # # =============================================================================================================================================
    #
    # Print top n synsets for each level (sorted by total_hits)
    #
    # top_classes_per_level("noun", 10)
    # top_classes_per_level("verb", 10)
    # # =============================================================================================================================================
    #
    # Print top n synsets for each level (sorted by this_hits)
    #
    # top_classes_per_level_this("noun", 10)
    # top_classes_per_level_this("verb", 10)
    # =============================================================================================================================================
    #
    # Locate the top n passwords from a category list on the top n passwords of the Wordnet
    #
    locate_topn_list_pws_wn("01_en_office_supplies.txt", top=10, include_perms=False, wn_lim=2000)
    locate_topn_list_pws_wn("01_en_office_supplies.txt", top=10, include_perms=True, wn_lim=2000)
    locate_topn_list_pws_wn("02_en_office_brands.txt", top=10, include_perms=False, wn_lim=2000)
    locate_topn_list_pws_wn("02_en_office_brands.txt", top=10, include_perms=True, wn_lim=2000)
    locate_topn_list_pws_wn("03_keyboard_patterns.txt", top=10, include_perms=False, wn_lim=2000)
    locate_topn_list_pws_wn("03_keyboard_patterns.txt", top=10, include_perms=True, wn_lim=2000)
    locate_topn_list_pws_wn("05_en_financial_brands.txt", top=10, include_perms=False, wn_lim=2000)
    locate_topn_list_pws_wn("05_en_financial_brands.txt", top=10, include_perms=True, wn_lim=2000)
    locate_topn_list_pws_wn("06_en_cities.txt", top=10, include_perms=False, wn_lim=2000)
    locate_topn_list_pws_wn("06_en_cities.txt", top=10, include_perms=True, wn_lim=2000)
    locate_topn_list_pws_wn("07_first_names.txt", top=10, include_perms=False, wn_lim=2000)
    locate_topn_list_pws_wn("07_first_names.txt", top=10, include_perms=True, wn_lim=2000)
    locate_topn_list_pws_wn("08_last_names.txt", top=10, include_perms=False, wn_lim=2000)
    locate_topn_list_pws_wn("08_last_names.txt", top=10, include_perms=True, wn_lim=2000)
    locate_topn_list_pws_wn("09_en_countries.txt", top=10, include_perms=False, wn_lim=2000)
    locate_topn_list_pws_wn("09_en_countries.txt", top=10, include_perms=True, wn_lim=2000)
    locate_topn_list_pws_wn("10_automobile.txt", top=10, include_perms=False, wn_lim=2000)
    locate_topn_list_pws_wn("10_automobile.txt", top=10, include_perms=True, wn_lim=2000)
    locate_topn_list_pws_wn("11_software_names.txt", top=10, include_perms=False, wn_lim=2000)
    locate_topn_list_pws_wn("11_software_names.txt", top=10, include_perms=True, wn_lim=2000)
    locate_topn_list_pws_wn("12_tech_brands.txt", top=10, include_perms=False, wn_lim=2000)
    locate_topn_list_pws_wn("12_tech_brands.txt", top=10, include_perms=True, wn_lim=2000)
    locate_topn_list_pws_wn("13_en_fruit.txt", top=10, include_perms=False, wn_lim=2000)
    locate_topn_list_pws_wn("13_en_fruit.txt", top=10, include_perms=True, wn_lim=2000)
    locate_topn_list_pws_wn("14_en_drinks.txt", top=10, include_perms=False, wn_lim=2000)
    locate_topn_list_pws_wn("14_en_drinks.txt", top=10, include_perms=True, wn_lim=2000)
    locate_topn_list_pws_wn("15_en_food.txt", top=10, include_perms=False, wn_lim=2000)
    locate_topn_list_pws_wn("15_en_food.txt", top=10, include_perms=True, wn_lim=2000)    
    # =============================================================================================================================================
    #
    # Print stats for the all parts of speech of the Wordnet
    #
    # overview_wn()
    # =============================================================================================================================================
    #
    # Double bar diagram to compare the efficiency with the number of lemmas
    #
    # compare_hits_to_permutations("list", include_perms=True, sort_by="quota")
    # compare_hits_to_permutations("list", include_perms=True, sort_by="quota", top=3)
    # compare_hits_to_permutations("list", include_perms=True, sort_by="total_lemmas")
    # compare_hits_to_permutations("list", include_perms=True, sort_by="password_hits")
    # compare_hits_to_permutations("wordnet", include_perms=True, sort_by="quota")
    # compare_hits_to_permutations("wordnet", include_perms=True, sort_by="total_lemmas")
    # compare_hits_to_permutations("wordnet", include_perms=True, sort_by="password_hits")
    # =============================================================================================================================================
    #
    # Plot the dictionary coverage of the HIBP database (with and without permutations)
    #
    # dictionary_coverage(include_perms=False)
    # dictionary_coverage(include_perms=True)
    # =============================================================================================================================================
    #
    # Plot the list coverage of the HIBP database (with and without permutations)
    #
    # list_coverage(include_perms=False)
    # list_coverage(include_perms=True)
    # =============================================================================================================================================
    #
    # Plot the password list coverage of the HIBP database (with and without permutations)
    #
    # password_list_coverage()
    # =============================================================================================================================================
    #
    # Plot the percentage for the top synsets of a level in relationship to the total sum of this_hits of their levels
    #
    # display_pct_synsets_on_level("n", top=30, level=3)
    # display_pct_synsets_on_level("v", top=5, level=6)
    # =============================================================================================================================================
    #
    # Display the permutators of the top X passwords of a password source
    #
    # top_passwords_permutators("wn_n", top=10000)
    # top_passwords_permutators("wn_v", top=10000)
    # top_passwords_permutators("wn_adj", top=10000)
    # top_passwords_permutators("wn_adv", top=10000)
    # top_passwords_permutators("list", source_name="07_first_names.txt", top=10000)
    # top_passwords_permutators("list", source_name="13_en_fruit.txt", top=10000)
    # top_passwords_permutators("dict", source_name="cracklib-small", top=10000)
    # top_passwords_permutators("dict", source_name="american-english", top=10000)
    # =============================================================================================================================================
    #
    # Lookup pure numbers as passwords.
    #
    # lookup_number_sequences()
    # =============================================================================================================================================
    #
    # Plot top X number passwords
    # topn_numbers(3)
    # topn_numbers(10)
    # topn_numbers(20)
    #
    # =============================================================================================================================================
    #
    # Plot the top X passwords of a wordnet part of speech generated by a number synset.
    #
    # top_passwords_wn_numbers(pos="n", top=10)
    # top_passwords_wn_numbers(pos="v", top=10)
    # top_passwords_wn_numbers(pos="adj", top=10)
    # top_passwords_wn_numbers(pos="adv", top=10)
    # =============================================================================================================================================
    #
    # Print/plot the coverage of a list/misc_list/dictionary on all parts of speeches of the wordnet
    #
    # list_wn_coverage("list", "07_first_names.txt")
    # list_wn_coverage("misc_list", "lizard-squad")
    # list_wn_coverage("dict", "cracklib-small")
    pass


# ====================== Wrappers ======================

def identify_and_store_missing_verbs():
    """
    Identify all missing verbs and store them in wn_synsets_verbs_missing
    """
    # NOTE Important: create indexes! db.coll.createIndex({"id":1})
    # total synsets should: 13767
    # total synsets in passwords: 7422
    # total synsets in synsets: 13767
    # diff synsets - passwords: 13767 - 7422 = 6345

    password_synset = []
    synsets_in_pws = mongo.db["passwords_wn_verb"].distinct("synset")
    i = 0
    for ss in synsets_in_pws:
        password_synset.append(ss)
        i += 1

    # contains all synsets that were not in passwords_wn_verb/lemma_permutations
    not_found = []
    for ss in wn.all_synsets("v"):
        if ss.name() not in password_synset:
            o = {
                "name": ss.name(),
                "lemmas": ss.lemma_names(),
                "depth": ss.min_depth()
            }
            not_found.append(o)

    # we need to look up all synsets from not_found again and put them in passwords_wn_verb and wn_lemma_permutations_verb
    # links already exists (no need to store again in wn_synsets_verb)
    synset_cnt = 0
    lemma_cnt = 0
    for k, ss in enumerate(not_found):
        # create permutations
        print(k, "Looking up: %s" % ss["name"])
        synset_cnt += 1
        for lemma in ss["lemmas"]:
            lemma_cnt += 1
            lemma = lemma.lower()
            # will be stored in passwords_wn_noun
            # store all permutations in passwords_wn_verb
            # bundle all permutations in wn_lemma_permutations_verb
            total_hits, not_found_cnt, found_cnt = permutations_for_lemma(
                lemma, ss["depth"], ss["name"], "v")
            print("\tLemma: {}, Total Hits: {}, Not Found: {}, Found: {}".format(
                lemma, total_hits, not_found_cnt, found_cnt))
    print()
    print()
    print()
    print("Looked up synsets:", synset_cnt)
    print("Looked up lemmas:", lemma_cnt)
    return

    # check which synsets from wn_synsets_verb are not in passwords_wn_verb
    not_found_in_passwords = 0
    not_found_in_passwords_list = []
    synsets_in_synset = mongo.db["wn_synsets_verb"].find()
    for ss in synsets_in_synset:
        if ss["id"] not in password_synset:
            o = {
                "name": ss["id"],
                "level": ss["level"],
                "parent": ss["parent"]
            }
            not_found_in_passwords_list.append(o)
            not_found_in_passwords += 1
    for k, v in enumerate(not_found_in_passwords_list):
        print(k, v)
    print("Synsets in passwords", len(password_synset))
    print("Synsets from wn_synsets_verb not found in passwords",
          not_found_in_passwords)


def identify_and_store_missing_nouns():
    """
    Identify all missing nouns and store them in wn_synsets_noun_missing
    """
    # Nouns
    # Found: 74374
    # Not found: 7741
    # Total: 82115
    # Total (supposed): 82115
    # Not found len: 7741
    # NOTE Important: create indexes! db.coll.createIndex({"id":1})
    # mongo.db["wn_synsets_noun_missing"].drop()
    not_found_ss = []
    cnt = 0
    cnt_missing = 0
    for i in list(wn.all_synsets("n")):
        res = mongo.db["wn_synsets_noun"].find({"id": i.name()}).limit(1)
        cnt += 1
        l = len(list(res))
        if l == 0:
            cnt_missing += 1
            print(cnt, l, i.name())
            o = {
                "name": i.name(),
                "depth": i.min_depth(),
                "lemmas": i.lemma_names(),
            }
            not_found_ss.append(o)
            print(o)
        else:
            print(cnt, l)

    print()
    print()
    print()
    print()
    res = mongo.db["wn_synsets_noun_missing"].insert_many(not_found_ss)
    actual_nouns = 74374
    found_missing_nouns = len(not_found_ss)
    total_nouns_supposed = 82115
    total_nouns_actual = actual_nouns + found_missing_nouns
    print("Count missing:", cnt_missing)
    print("Count missing (list len):", found_missing_nouns)
    print("Should be:", total_nouns_supposed)  # Diff found: 7741
    print("Is:", total_nouns_actual)


def lookup_and_insert_missing_nouns():
    """
    For each noun in wn_synsets_noun_missing permutate and lookup the lemmas. Store in the respective collections. Insert missing synsets in wn_synsets_noun
    """
    # mongo.db["wn_lemma_permutations_noun_test"].drop()
    # mongo.db["passwords_wn_noun_test"].drop()
    # mongo.db["wn_synsets_noun_test"].drop()
    # mongo.db["wn_synsets_noun_staging_test"].drop()
    # mongo.db["wn_synsets_noun_staging"].drop()

    # cnt = i + 500  # target delta
    # synsets that have either a parent or childs
    # hyp_or_hyper = [1110, 1616, 1620, 1698, 1699, 1700, 2320, 2332, 2426, 2436, 3494, 3530,
    #                 3532, 3539, 3749, 3896, 3897, 3898, 3899, 4065, 4066, 4072, 4180, 4198, 4346, 4347]
    # begin stage 1
    i = 0
    missing_synsets = mongo.db["wn_synsets_noun_missing"].find()
    for ss in missing_synsets:
        syn = wn.synset(ss["name"])
        # iterate over each lemma and permutate
        print(i, ss["name"])
        syn_total_hits = 0
        syn_not_found = 0
        syn_found = 0
        for lemma in ss["lemmas"]:
            lemma = lemma.lower()
            # will be stored in passwords_wn_noun
            total_hits, not_found_cnt, found_cnt = permutations_for_lemma(
                lemma, ss["depth"], ss["name"], "n")
            syn_total_hits += total_hits
            syn_not_found += not_found_cnt
            syn_found += found_cnt
            print("\t", lemma, "Total hits:", total_hits,
                  "Not found:", not_found_cnt, "Found:", found_cnt)
        # store frame for synsets in wn_synsets_noun
        mongo.store_synset_without_relatives_noun(
            syn, ss["depth"], syn_total_hits, syn_not_found, syn_found)
        i += 1
    print("Looked up %d noun synsets" % i)
    return  # end stage 1

    # first, we must copy all missing synsets to wn_synsets_noun
    # one of the missing synsets might be the parent of another missing synset,
    # so when the child of a missing synset gets iterated before its parent (and the parent was
    # not copied to wn_synsets_noun yet), there will be no link.
    # hence, we copy all missing synsets first, then create the links between them
    missing_synsets_staging = mongo.db["wn_synsets_noun_staging"].find()
    copy_cnt = 0
    i = 1
    for ss in missing_synsets_staging:
        my_id = ss["id"]
        print(i, my_id)
        # change staging_to_prod to 1
        # copy us to wn_synsets_noun
        ss["staging_to_prod"] = 1
        res = mongo.db["wn_synsets_noun"].insert_one(ss)
        print("\tInsert to wn_synsets_noun", res.inserted_id)
        # update in wn_synsets_noun_staging
        # mark that we have been linked to our parent and copied to wn_synsets_noun
        res = mongo.db["wn_synsets_noun_staging"].update_one(
            {"id": my_id},
            {"$set": {"staging_to_prod": 1}}
        )
        print("\tUpdate to wn_synsets_noun_staging", res.modified_count)
        copy_cnt += 1
        i += 1

    print("Copied %d synsets to wn_synsets_noun" % copy_cnt)
    print()
    print()
    print()

    # after we have permutated and inserted, iterate over the missing ones again,
    # determine their parents/children and insert them. some children are inserted
    # before their parents, so we would get an error if we tried to link a
    # children to a yet non-existent parent

    # count how many missing synsets have parents and need to be linked to them (in the sense of appending the missing synset to the parents childs list)
    required_links_cnt = mongo.db["wn_synsets_noun_staging"].count_documents(
        {"parent": {"$nin": ["no_parent"]}})

    i = 1
    update_cnt = 0
    update_stats_cnt = 0
    # we keep track of a total sum of all stats of our missing synsets, so in the end we can create a second entity.n.01 synset
    # that also includes the values of our missing synsets (the synsets that are neither directly or indirectly connected to the actual entity.n.01 but we still
    # want to consider in our statistics, so we add the missing synset values to a second entity.n.01 object)
    total_this_hits = 0
    total_this_found_cnt = 0
    total_this_not_found_cnt = 0
    total_this_permutations = 0

    missing_synsets_staging = mongo.db["wn_synsets_noun_staging"].find()
    for ss in missing_synsets_staging:
        parent_id = ss["parent"]
        my_id = ss["id"]
        if parent_id != "no_parent":
            print(i, my_id)
            # append this synset to the children list of the parent synset
            # childs arrays get built here. no need to determine childs from the nltk package.
            # if you have a parent, you will be appended to your parents childs array
            result = mongo.db["wn_synsets_noun"].update_one(
                {"id": parent_id},
                {"$push": {"childs": my_id}})
            update_cnt += 1
            print("\tAppended {} to {} (matched={}, modified={})".format(
                my_id, parent_id, result.matched_count, result.modified_count))
            # The other thing we do is add our total_hits, this_found_cnt, this_not_found_cnt, this_permutations,
            # below_permutations, hits_below, not_found_below and found_below to the stats of our parent to
            # upkeep the stats from below
            my_total_hits = ss["total_hits"]
            my_this_hits = ss["this_hits"]
            my_this_found_cnt = ss["this_found_cnt"]
            my_this_not_found_cnt = ss["this_not_found_cnt"]
            my_this_permutations = ss["this_permutations"]
            my_below_permutations = ss["below_permutations"]
            my_total_permutations = my_this_permutations + my_below_permutations
            my_hits_below = ss["hits_below"]
            my_not_found_below = ss["not_found_below"]
            my_found_below = ss["found_below"]
            my_total_found = my_this_found_cnt + my_found_below
            my_total_not_found = my_this_not_found_cnt + my_not_found_below

            # keep track of total_* stats for entity.n.01 #2
            total_this_hits += my_this_hits
            total_this_found_cnt += my_this_found_cnt
            total_this_not_found_cnt += my_this_not_found_cnt
            total_this_permutations += my_this_permutations

            result = mongo.db["wn_synsets_noun"].update_one(
                {"id": parent_id},
                {"$inc": {
                    "total_hits": my_total_hits,
                    "hits_below": my_total_hits,
                    "found_below": my_total_found,
                    "not_found_below": my_total_not_found,
                    "below_permutations": my_total_permutations,
                }})
            print("\tUpdated hits of parent {}: {}".format(
                parent_id, result.modified_count))
            update_stats_cnt += 1

        i += 1
    print("Updated the childs/links of %d parent synsets (%d missing synsets required were required to be linked)" % (
        update_cnt, required_links_cnt))

    # create entity.n.01_2
    # we sum the hits of the missing synsets directly onto entity.n.01 because the missing synsets have no direct or indirect association with entity.n.01
    # therefore, we imply a hypothetical connection in order to include the missing synsets hits with the other synsets and use them for our statistics
    entity_orig = mongo.db["wn_synsets_noun"].find_one({"id": "entity.n.01"})
    # create a new dict that is going to be entity.n.01_2
    new_entity = {}
    new_entity["childs"] = entity_orig["childs"]
    new_entity["level"] = entity_orig["level"]
    new_entity["parent"] = entity_orig["parent"]
    new_entity["this_permutations"] = entity_orig["this_permutations"]
    new_entity["this_hits"] = entity_orig["this_hits"]
    new_entity["this_not_found_cnt"] = entity_orig["this_not_found_cnt"]
    new_entity["this_found_cnt"] = entity_orig["this_found_cnt"]
    new_entity["total_hits"] = entity_orig["total_hits"] + total_this_hits
    new_entity["id"] = "entity.n.01_2"
    new_entity["tag"] = entity_orig["tag"]
    new_entity["found_below"] = entity_orig["found_below"] + \
        total_this_found_cnt
    new_entity["below_permutations"] = entity_orig["below_permutations"] + \
        total_this_permutations
    new_entity["not_found_below"] = entity_orig["not_found_below"] + \
        total_this_not_found_cnt
    new_entity["hits_below"] = entity_orig["hits_below"] + total_this_hits

    res = mongo.db["wn_synsets_noun"].insert_one(new_entity)
    print()
    print()
    print("Inserted new entity.n.01_2: {}".format(res.inserted_id))

    # print overview
    print()
    print()
    print()
    print()
    print("Sum counts for missing synsets:")
    print("\ttotal_this_hits", total_this_hits)
    print("\ttotal_this_found_cnt", total_this_found_cnt)
    print("\ttotal_this_not_found_cnt", total_this_not_found_cnt)
    print("\ttotal_this_permutations", total_this_permutations)


# ====================== Implementations ======================


def avg_permutations_lemma(base):
    """
    Calculate the average permutations per lemma.
    Base: either wordnet or lists
    """
    coll_name = ""
    if base == "wordnet_n":
        coll_name = "wn_lemma_permutations_noun"
    elif base == "wordnet_v":
        coll_name = "wn_lemma_permutations_verb"
    elif base == "wordnet_adj":
        coll_name = "wn_lemma_permutations_adjective"
    elif base == "wordnet_adv":
        coll_name = "wn_lemma_permutations_adverb"
    else:
        log_err("Invalid base")
        return 0

    perm_cnt = 0
    perms_total = 0
    for perms in mongo.db[coll_name].find():
        perm_cnt += 1
        perms_total += len(perms["permutations"])
        print("%d / %d" % (perm_cnt, perms_total), end="\r")

    return perms_total / perm_cnt


def wordnet_coverage(include_perms=False):
    f, ax = plt.subplots(1)
    total_sum = []

    if not include_perms:
        query = {
            "$and": [
                {"permutator": "no_permutator"},
                {"occurrences": {"$gt": 0}}
            ]
        }
    else:
        query = {
            "occurrences": {"$gt": 0}
        }

    # Get coverage for
    query_result_n = mongo.db_pws_wn.find(query).count()
    total_sum.append({
        "type": "wordnet",
        "name": "WordNet Nouns",
        "sum": query_result_n
    })

    query_result_v = mongo.db_pws_wn_verb.find(query).count()
    total_sum.append({
        "type": "wordnet",
        "name": "WordNet Verbs",
        "sum": query_result_v
    })

    query_result_adj = mongo.db_pws_wn_adjective.find(query).count()
    total_sum.append({
        "type": "wordnet",
        "name": "WordNet Adjectives",
        "sum": query_result_adj
    })

    query_result_adv = mongo.db_pws_wn_adverb.find(query).count()
    total_sum.append({
        "type": "wordnet",
        "name": "WordNet Adverbs",
        "sum": query_result_adv
    })
    if include_perms:
        log_ok("Note: including permutations")
    else:
        log_ok("Note: excluding permutations")
    sorted_sums = sorted(total_sum, key=lambda k: k["sum"], reverse=True)
    for k, v in enumerate(sorted_sums):
        pct_cvg = round((v["sum"] / pwned_pw_amount) * 100, 5)
        log_ok("({}) {}, {}, {} %".format(
            k, v["name"], helper.format_number(v["sum"]), pct_cvg))

    sorted_l = ["-\n".join(wrap(x["name"], 10)) for x in sorted_sums]
    sorted_o = [x["sum"] for x in sorted_sums]

    # Plot as bar
    N = len(sorted_l)
    ind = np.arange(N)
    width = 0.35

    plt.bar(ind, sorted_o, width,
            label="Password Collections", color="black")

    # plt.yscale("log", basey=10)

    plt.ylabel("Total Hits")
    plt.xlabel("Password Source")
    if include_perms:
        plt.title(
            "Wordnet Coverage of the HIBP passwords (including password variants)", fontdict={'fontsize': 10})
    else:
        plt.title(
            "Wordnet Coverage of the HIBP passwords (excluding password variants)", fontdict={'fontsize': 10})

    plt.xticks(ind, sorted_l, fontsize=7)
    plt.legend(loc="best")

    plt.show()


def dictionary_coverage(include_perms=False):
    f, ax = plt.subplots(1)
    total_sum = []

    if not include_perms:
        query = {
            "$and": [
                {"permutator": "no_permutator"},
                {"occurrences": {"$gt": 0}}
            ]
        }
    else:
        query = {
            "occurrences": {"$gt": 0}
        }

    # Get coverage for each dictionary
    query_result_ae = mongo.db["passwords_dicts_american-english"].find(
        query).count()
    total_sum.append({
        "type": "dictionary",
        "name": "Unix/American English",
        "sum": query_result_ae
    })

    query_result_be = mongo.db["passwords_dicts_british-english"].find(
        query).count()
    total_sum.append({
        "type": "dictionary",
        "name": "Unix/British English",
        "sum": query_result_be
    })

    query_result_cs = mongo.db["passwords_dicts_cracklib-small"].find(
        query).count()
    total_sum.append({
        "type": "dictionary",
        "name": "Unix/Cracklib Small",
        "sum": query_result_cs
    })

    if include_perms:
        log_ok("Note: including permutations")
    else:
        log_ok("Note: excluding permutations")
    sorted_sums = sorted(total_sum, key=lambda k: k["sum"], reverse=True)
    for k, v in enumerate(sorted_sums):
        pct_cvg = round((v["sum"] / pwned_pw_amount) * 100, 5)
        log_ok("({}) {}, {}, {} %".format(
            k, v["name"], helper.format_number(v["sum"]), pct_cvg))

    # sorted_l = ["-\n".join(wrap(x["name"], 10)) for x in sorted_sums]
    sorted_l = [x["name"] for x in sorted_sums]
    sorted_o = [x["sum"] for x in sorted_sums]

    # Plot as bar
    N = len(sorted_l)
    ind = np.arange(N)
    width = 0.35

    plt.bar(ind, sorted_o, width,
            label="Dictionaries", color="black")

    # plt.yscale("log", basey=10)

    plt.ylabel("Total Hits")
    plt.xlabel("Password Source")
    if include_perms:
        plt.title(
            "Dictionary Coverage of the HIBP passwords (including password variants)", fontdict={'fontsize': 10})
    else:
        plt.title(
            "Dictionary Coverage of the HIBP passwords (excluding password variants)", fontdict={'fontsize': 10})

    plt.xticks(ind, sorted_l, fontsize=7)
    plt.legend(loc="best")

    plt.show()


def list_coverage(include_perms=False):
    f, ax = plt.subplots(1)
    total_sum = []

    labels = {
        "07_first_names.txt": "First Names",
        "09_en_countries.txt": "Countries",
        "01_en_office_supplies.txt": "Office Supplies",
        "06_en_cities.txt": "Cities",
        "13_en_fruit.txt": "Fruit",
        "08_last_names.txt": "Last Name",
        "10_automobile.txt": "Automobile",
        "12_tech_brands.txt": "Tech Brands",
        "03_keyboard_patterns.txt": "Keyboard Patterns",
        "15_en_food.txt": "Food",
        "02_en_office_brands.txt": "Office Brands",
        "14_en_drinks.txt": "Drinks",
        "05_en_financial_brands.txt": "Financial Brands",
        "11_software_names.txt": "Software Names",
    }
    all_lists = []
    lists_result = mongo.db["lists"].find()
    for res in lists_result:
        all_lists.append(res["filename"])
    # for each lists get the efficiency as well as the total number of lemmas (with or without permutations)
    for list_name in all_lists:
        # skip 99_unsortiert.txt
        if list_name == "99_unsortiert.txt":
            continue
        # query to get the total amount of lemmas
        if include_perms:
            query = {
                "$and": [
                    {"source": list_name},
                ]
            }
        else:
            query = {
                "$and": [
                    {"source": list_name},
                    {"permutator": "no_permutator"}
                ]
            }
        total_lemmas = mongo.db["passwords_lists"].count_documents(query)
        # query to get the passwords with hits > 0 (efficiency)
        if include_perms:
            query = {
                "$and": [
                    {"source": list_name},
                    {"occurrences": {"$gt": 0}}
                ]
            }
        else:
            query = {
                "$and": [
                    {"source": list_name},
                    {"permutator": "no_permutator"},
                    {"occurrences": {"$gt": 0}}
                ]
            }
        password_hits = mongo.db["passwords_lists"].count_documents(query)
        o = {
            "name": labels[list_name],
            "type": "list",
            "sum": password_hits
        }
        total_sum.append(o)

    if include_perms:
        log_ok("Note: including permutations")
    else:
        log_ok("Note: excluding permutations")
    sorted_sums = sorted(total_sum, key=lambda k: k["sum"], reverse=True)
    for k, v in enumerate(sorted_sums):
        pct_cvg = round((v["sum"] / pwned_pw_amount) * 100, 5)
        log_ok("({}) {}, {}, {} %".format(
            k, v["name"], helper.format_number(v["sum"]), pct_cvg))

    # sorted_l = ["-\n".join(wrap(x["name"], 10)) for x in sorted_sums]
    sorted_l = [x["name"] for x in sorted_sums]
    sorted_o = [x["sum"] for x in sorted_sums]

    # Plot as bar
    N = len(sorted_l)
    ind = np.arange(N)
    width = 0.35

    plt.bar(ind, sorted_o, width,
            label="Category List", color="black")

    # plt.yscale("log", basey=10)

    plt.ylabel("Total Hits")
    plt.xlabel("Password Source")
    if include_perms:
        plt.title(
            "Category List Coverage of the HIBP passwords (including password variants)", fontdict={'fontsize': 10})
    else:
        plt.title(
            "Category List Coverage of the HIBP passwords (excluding password variants)", fontdict={'fontsize': 10})

    plt.xticks(ind, sorted_l, fontsize=7, rotation=90)
    plt.legend(loc="best")

    plt.show()


def password_list_coverage():
    f, ax = plt.subplots(1)
    total_sum = []
    all_lists = []
    lists_result = mongo.db["lists"].find()
    for res in mongo.db.collection_names():
        # for some lists that blow the rest out of proportion, we can exclude them
        # if res == "passwords_misc_lists_xato-net-10-million-passwords":
        #     continue
        if res.startswith("passwords_misc_lists_"):
            all_lists.append(res)
    # for each lists get the efficiency as well as the total number of lemmas (with or without permutations)
    # query to get the total amount of lemmas
    for list_name in all_lists:
        total_lemmas = mongo.db[list_name].count_documents({})
        # query to get the passwords with hits > 0 (efficiency)
        password_hits = mongo.db[list_name].count_documents(
            {"occurrences": {"$gt": 0}})
        o = {
            "name": list_name.replace("passwords_misc_lists_", ""),
            "type": "misc_list",
            "sum": password_hits
        }
        total_sum.append(o)

    sorted_sums = sorted(total_sum, key=lambda k: k["sum"], reverse=True)
    for k, v in enumerate(sorted_sums):
        pct_cvg = round((v["sum"] / pwned_pw_amount) * 100, 5)
        log_ok("({}) {}, {}, {} %".format(
            k, v["name"], helper.format_number(v["sum"]), pct_cvg))

    # sorted_l = ["-\n".join(wrap(x["name"], 10)) for x in sorted_sums]
    sorted_l = [x["name"] for x in sorted_sums]
    sorted_o = [x["sum"] for x in sorted_sums]
    # Plot as bar
    N = len(sorted_l)
    ind = np.arange(N)
    width = 0.35
    plt.bar(ind, sorted_o, width,
            label="Password List", color="black")
    # plt.yscale("log", basey=10)
    plt.ylabel("Total Hits")
    plt.xlabel("Password Source")
    plt.title("Category List Coverage of the HIBP passwords (excluding password variants)",
              fontdict={'fontsize': 10})

    plt.xticks(ind, sorted_l, fontsize=7, rotation=90)
    plt.legend(loc="best")

    plt.show()


def locate_topn_list_pws_hibp(list_name, top=10, include_perms=False, hipb_lim=1000):
    """
    Mark the top N passwords of a given list within the top N passwords of the wordnet.
    On the X axis, mark each 50th step.
    """
    hibp_limit = hipb_lim
    # Get top n from some list
    pw_list = []
    if include_perms:
        query = {
            "source": list_name
        }
    else:
        query = {
            "$and": [
                {"source": list_name},
                {"permutator": "no_permutator"}
            ]
        }

    known_names = []
    for item in mongo.db_pws_lists.find(query).sort("occurrences", pymongo.DESCENDING).limit(top * 10):
        # since we query a bit more records than we actually need, stop the iteration when our list has the desired length
        if len(known_names) == top:
            break
        # check for duplicate hits (generate by different permutators)
        if item["name"] in known_names:
            continue
        # enforce policy: min. 3 chars
        if len(item["name"]) < 3:
            continue
        known_names.append(item["name"])
        o = {"name": item["name"],
             "occurrences": item["occurrences"],
             "permutator": item["permutator"]}
        pw_list.append(o)

    # get the top n passwords from the sorted HIBP list
    # We use a precompiled text file with the top 2000 passwords
    fname = args.hibp
    if not path.exists(fname):
        log_err("Path %s does not exist" % fname)
        return
    cnt = 0
    hibp_labels = []
    hibp_occs = []
    with open(fname) as f:
        for line in f:
            if cnt == hibp_limit:
                break
            # parse lines and put into the lists required to plot the data
            label = line.replace("\n", "").split(":")[0]
            occs = line.replace("\n", "").split(":")[1]
            hibp_labels.append(label)
            hibp_occs.append(int(occs))
            cnt += 1

    new_occs_inserted = [{"orig": x, "list": -1} for x in hibp_occs]
    new_labels_inserted = [{"orig": x, "list": None} for x in hibp_labels]

    idx_behind_last_wn = len(hibp_labels)
    xcoords_bar = []

    for item in pw_list:
        occs = item["occurrences"]
        # Determine first if this elements occs are lower than the last wn element. If thats the case, append it behind the last wn element
        if occs < hibp_occs[-1]:
                # If the current item occurrences was lower than the last wordnet element, append it with the index last_wn + 1 and increment this counter
                # xcoords_bar.append(idx_behind_last_wn)
            new_occs_inserted.append({"orig": -1, "list": occs})
            new_labels_inserted.append({"orig": "", "list": item["name"]})
            idx_behind_last_wn += 1
        else:
            # At this point we know the current elements occs are not lower than the last wn element
            # Now we just need to find out where (within the first and last wn element frame) it will be drawn
            for idx, wn_occs in enumerate(hibp_occs):
                # Run until occs is NOT lower than wn_occs
                if occs < wn_occs:
                    pass
                elif occs >= wn_occs:

                    # cut_wn_occs is stored from most to least occurrences, so if val a is bigger than the current value from cut_wn_occs it must automatically
                    # be bigger than the rest of the list (since it is ordererd in a decending order)
                    # Before we insert, there may already be an element that was previously compared against the same element, so we need to determine if we insert before or
                    # after this index
                    if new_occs_inserted[idx]["list"] < occs:
                        # The current occs value is bigger than what is already in there
                        new_occs_inserted.insert(
                            idx, {"orig": -1, "list": occs})
                        new_labels_inserted.insert(
                            idx, {"orig": "", "list": item["name"]})
                    else:
                        # If the value is bigger, we insert occs after this index
                        new_occs_inserted.insert(
                            idx+1, {"orig": -1, "list": occs})
                        new_labels_inserted.insert(
                            idx+1, {"orig": "", "list": item["name"]})

                    break
                else:
                    pass

    # Transform the dict to a flat list. List dict items with orig = -1 are going to be 0 in the flattened list, else the "list" value
    flat_occs_inserted = []
    for x in new_occs_inserted:
        if x["list"] == -1:
            flat_occs_inserted.append(0)
        else:
            flat_occs_inserted.append(x["list"])
    # ... also transform the label list so we have a consistent mapping again (mind the zeros)
    flat_labels_inserted = []
    for x in new_labels_inserted:
        if x["list"] == None:
            flat_labels_inserted.append("")
        else:
            flat_labels_inserted.append(x["list"])

   # Check lengths (the next step will raise an exception if the lengths of both flat lists are not equal since we want to merge them into a dict)
    if len(flat_labels_inserted) != len(flat_occs_inserted):
        log_err("Something went wrong while flattening the lists (lengths are not equal). flat_occs_inserted: %d, flat_labels_inserted: %d" % (
            len(flat_occs_inserted), len(flat_labels_inserted)))
        return

    # store labels with occs as keys
    labels_for_occs = {}
    for idx, val in enumerate(flat_occs_inserted):
        labels_for_occs[idx] = flat_labels_inserted[idx]

    # save 0 states in flat lists
    zero_pos = []
    flat_occs_inserted_no_zeros = []
    for idx, val in enumerate(flat_occs_inserted):
        if val == 0:
            zero_pos.append(idx)
        else:
            flat_occs_inserted_no_zeros.append(val)

    # sort lists
    sorted_no_zeros = sorted(flat_occs_inserted_no_zeros, reverse=True)
    log_status("Unsorted xcoords list: \n{}".format(flat_occs_inserted))

    # restore 0 states, i.e. insert zeros at the indices saved in the zero_pos list
    sorted_with_zeros = sorted_no_zeros[:]
    for idx in zero_pos:
        sorted_with_zeros.insert(idx, 0)

    log_status("Sorted xcoords list: \n{}".format(sorted_with_zeros))

    f, ax = plt.subplots(1)
    # Draw the bar plot
    rect1 = ax.bar(np.arange(len(sorted_with_zeros)),
                   sorted_with_zeros, alpha=0.7, color="gray", width=0.3)

    i = 0
    for rect in rect1:
        height = rect.get_height()
        ax.annotate('{}'.format(flat_labels_inserted[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(2*3, 3),  # use 3 points offset
                    textcoords="offset points",  # in both directions
                    rotation=90,
                    # fontsize="x-small",
                    fontsize=9,
                    ha="center", va='bottom')
        i += 1

    # Draw the line plot
    ax.plot(np.arange(len(hibp_labels)), hibp_occs, "-", color="black")
    # Also print the pw list (for manual labelling)
    for k, v in enumerate(pw_list):
        print("{} - {}".format(k+1, v))
    ax.set_yscale("log", basey=10)
    # ax.set_ylim(bottom=0)
    plt.ylim((pow(10, 0)))
    ax.set_xlim(left=0)
    ax.set_ylim([0, sorted_no_zeros[0] + sorted_no_zeros[0] / 4])
    plt.xlabel(
        "Top %s HaveIBeenPwned Passwords" % helper.format_number(hibp_limit))
    plt.ylabel("Occurrences")
    if not include_perms:
        plt.title("Top %d List Passwords (excl. variants)" % top)
    else:
        plt.title("Top %d List Passwords (incl. variants)" % top)
    blue_patch = mpatches.Patch(color="black", label="HIBP Top Passwords")
    red_patch = mpatches.Patch(
        color="gray", label=list_name)
    plt.legend(handles=[blue_patch, red_patch], loc="best")
    plt.show(f)


def print_top_lemmas(pos, top, include_perms=False, no_numbers=False):
    """
    Print a list with the top n lemmas including their hits
    """
    if not include_perms:
        query = {
            "$and": [
                {"permutator": "no_permutator"},
                {"occurrences": {"$gt": 0}}
            ]
        }
    else:
        query = {
            "$and": [
                {"occurrences": {"$gt": 0}}
            ]
        }

    if no_numbers:
        nums = [str(x) for x in range(101)]
        # exclude word_bases from 0 - 100
        no_numbers_in_base_query = {
            "word_base": {
                "$nin": nums,
            },
        }

        no_numbers_in_name_query = {
            "name": {
                "$nin": nums,
            },
        }

        query["$and"].append(no_numbers_in_base_query)
        query["$and"].append(no_numbers_in_name_query)

    coll_name = ""
    if pos == "n":
        coll_name = "passwords_wn_noun"
    elif pos == "v":
        coll_name = "passwords_wn_verb"
    elif pos == "adj":
        coll_name = "passwords_wn_adjective"
    elif pos == "adv":
        coll_name = "passwords_wn_adverb"
    else:
        log_err("Invalid PoS: %s" % pos)
        return

    # query a bit more, because we need to eliminate the duplicates
    top_with_buf = top * 10
    res_list = []
    known_names = []
    query_res = mongo.db[coll_name].find(query).sort(
        "occurrences", pymongo.DESCENDING).limit(top_with_buf)
    for item in query_res:
        if item["name"] in known_names:
            continue
        elif item["name"].isdigit():
            continue
        elif len(item["name"]) < 3:
            continue
        else:
            known_names.append(item["name"])
            res_list.append(item)
    if include_perms:
        log_ok("Note: including permutations")
    else:
        log_ok("Note: excluding permutations")
    for k, v in enumerate(res_list):
        if k == top:
            break
        print("(%d)     %s: %s" %
              (k+1, v["name"], helper.format_number(v["occurrences"])))


def calculate_efficiency(base, source_name="", include_perms=False):
    """
    The efficiency is a number/percentage that indicates how many
    passwords of a given password source were found in collection 1, disregarding the 
    actual number of occurrences.
    Efficiency = Sum(occurrences > 0)
    include_perms: If set to true, include permutations (not only no_permutator) when calculating the efficiency
    """
    coll_name = ""
    if base == "wordnet_n":
        coll_name = "passwords_wn_noun"
    elif base == "wordnet_v":
        coll_name = "passwords_wn_verb"
    elif base == "wordnet_adj":
        coll_name = "passwords_wn_adjective"
    elif base == "wordnet_adv":
        coll_name = "passwords_wn_adverb"
    elif base == "list":
        if source_name != "":
            coll_name = "passwords_lists"
        else:
            log_err("Invalid source_name")
    elif base == "misc_list":
        if source_name != "":
            coll_name = "passwords_misc_lists_%s" % source_name
        else:
            log_err("Invalid source_name")
    elif base == "dict":
        if source_name != "":
            coll_name = "passwords_dicts_%s" % source_name
        else:
            log_err("Invalid source_name")
    else:
        log_err("Invalid base")
        return 0

    if not include_perms:
        if base != "list":
            query = {
                "$and": [
                    {"permutator": "no_permutator"},
                    {"occurrences": {"$gt": 0}}
                ]
            }
        else:
            query = {
                "$and": [
                    {"source": source_name},
                    {"permutator": "no_permutator"},
                    {"occurrences": {"$gt": 0}}
                ]
            }

    else:
        if base != "list":
            query = {
                "occurrences": {"$gt": 0}
            }
        else:
            query = {
                "$and": [
                    {"occurrences": {"$gt": 0}},
                    {"source": source_name}
                ]
            }


    # the number of passwords with hits > 0, meaning they were a hit in the password database
    password_hits = mongo.db[coll_name].find(query).count()
    pct_hits = password_hits / pwned_pw_amount
    return password_hits, pct_hits


def interesting_classes():
    """
    Ab Level 6, Total Hits > 5 Mio: db.getCollection('wn_synsets_noun').find({"$and": [{"level": {"$gt":6}}, {"total_hits": {"$gt": 5000000}}]}).sort({"total_hits": -1})

    Animal: db.getCollection('wn_synsets_noun').find({"id": "animal.n.01"})

    Fruit: db.getCollection('wn_synsets_noun').find({"id": "edible_fruit.n.01"})

    Field Sports: db.getCollection('wn_synsets_noun').find({"parent": "field_game.n.01"}).sort({"total_hits": -1})

    Sport (general): db.getCollection('wn_synsets_noun').find({"parent": "sport.n.01"}).sort({"total_hits": -1})
    """
    pass


def top_classes_per_level(mode, top):
    """
    Return the top n classes per level.
    """
    lowest_level = duplicates.get_lowest_level_wn(mode)
    for i in range((lowest_level+1)):
        query = {
            "level": i
        }
        coll_name = ""
        if mode == "noun":
            coll_name = "wn_synsets_noun"
        elif mode == "verb":
            coll_name = "wn_synsets_verb"
        else:
            log_ok("Invalid mode")
            return
        query_result = mongo.db[coll_name].find(query).sort(
            "total_hits", pymongo.DESCENDING).limit(top)
        print("Top %d synset for level %d:" % (top, i))
        for k, v in enumerate(query_result):
            print("\t%d - %s: %s" %
                  (k+1, v["id"], helper.format_number(v["total_hits"])))
        print()

def top_classes_per_level_this(mode, top):
    """
    Return the top n classes per level.
    """
    lowest_level = duplicates.get_lowest_level_wn(mode)
    for i in range((lowest_level+1)):
        query = {
            "level": i
        }
        coll_name = ""
        if mode == "noun":
            coll_name = "wn_synsets_noun"
        elif mode == "verb":
            coll_name = "wn_synsets_verb"
        else:
            log_ok("Invalid mode")
            return
        query_result = mongo.db[coll_name].find(query).sort(
            "this_hits", pymongo.DESCENDING).limit(top)
        print("Top %d synset for level %d:" % (top, i))
        for k, v in enumerate(query_result):
            print("\t%d - %s: %s" %
                  (k+1, v["id"], helper.format_number(v["this_hits"])))
        print()


def examples_duplicates():
    """
    Print some examples for duplicates.
    MongoDB Find duplicates: db.getCollection('passwords_wn_noun').aggregate([{"$match": {"occurrences": {"$gt": 0}}}, {"$group": {_id: "$name", sum: {"$sum": 1}}}, {"$match": {"sum": {"$gt": 1}}}, {"$sort": {"sum": -1}}], { allowDiskUse: true })
    MongoDB Count number of duplicates: db.getCollection('passwords_wn_noun').aggregate([{"$match": {"occurrences": {"$gt": 0}}}, {"$group": {_id: "$name", sum: {"$sum": 1}}}, {"$match": {"sum": {"$gt": 1}}}, {"$sort": {"sum": -1}}, {"$group": {_id: null, count: {"$sum": 1}}}], { allowDiskUse: true })
    MongoDB Show clustered duplicates with synset origin: db.getCollection('passwords_wn_noun').aggregate([ { "$match": { "occurrences": { "$gt": 0 } } }, { "$group": { "_id": "$name", "sum": { "$sum": 1 }, "results": { "$push": { "name": "$name", "occurrences": "$occurrences", "word_base": "$word_base", "synset": "$synset", "level": "$depth", "permutator": "$permutator" } } } }, { "$match": { "sum": { "$gt": 1 } } }, { "$sort": { "sum": -1 } } ], {"allowDiskUse": true})    

    Examples: Duplicate, # of duplicates

    Nouns:
        C, 187
        pnt, 52
        line1970, 31
        LSD, 31

    Verb:
        run, 84
        cut, 82
        break64, 59
        make61, 49

    Adjective:
        dry, 64
        heavy2000, 27
        light28, 25
        open!, 21

    Adverbs:
        Only, 14
        w3ll, 13
        well123456, 13
        back1234, 6
    """
    pass


def locate_topn_list_pws_wn(list_name, top=10, include_perms=False, wn_lim=1000):
    """
    Mark the top N passwords of a given list within the top N passwords of the wordnet.
    On the X axis, mark each 50th step.
    """
    # Read the top wn_limit passwords generated from the WordNet
    wn_limit = wn_lim
    f, ax = plt.subplots(1)

    limit_val = top

    # Get top n from some list
    # Get top n from some list
    pw_list = []
    if include_perms:
        query = {
            "source": list_name
        }
    else:
        query = {
            "$and": [
                {"source": list_name},
                {"permutator": "no_permutator"}
            ]
        }

    known_names = []
    for item in mongo.db_pws_lists.find(query).sort("occurrences", pymongo.DESCENDING).limit(top * 10):
        # since we query a bit more records than we actually need, stop the iteration when our list has the desired length
        if len(known_names) == top:
            break
        # check for duplicate hits (generate by different permutators)
        if item["name"] in known_names:
            continue
        # enforce policy: min. 3 chars
        if len(item["name"]) < 3:
            continue
        known_names.append(item["name"])
        o = {"name": item["name"],
             "occurrences": item["occurrences"],
             "permutator": item["permutator"]}
        pw_list.append(o)


    # for item in mongo.db_pws_lists.find(query).sort("occurrences", pymongo.DESCENDING).limit(top):
    #     o = {"name": item["name"],
    #          "occurrences": item["occurrences"],
    #          "permutator": item["permutator"]}
    #     pw_list.append(o)

    labels = []
    occurrences = []

    # Get the top 1000 wordnet passwords (used as a reference for the word list passwords)
    # Problem: If we want to search over all WordNet passwords (ca. 26 million) we run out of RAM. So in order to just search the passwords we need to set a threshhold
    # for minimum occurrences of a password. Our goal is to find a threshhold that yields approximately 1000 passwords after having been cleaned (since we want to show the first 1k passwords for this graph).
    # By trial-and-error, this number was found with a threshhold of approximately 25000+ occurrences.
    # db.getCollection('passwords_wn').find({"occurrences": {"$gt": 25000}, "word_base": {"$nin": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0",]}}).sort({"occurrences": -1}).count() => 1296

    # find() criteria
    search_filter = {
        "occurrences": {"$gt":
                        2500
                        },
        "word_base": {"$nin": [
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "0",
        ]}
    }
    buf_len = wn_limit * 4
    top_wn_pws = mongo.db_pws_wn.find(search_filter).sort(
        "occurrences", pymongo.DESCENDING).limit(buf_len)
    for password in top_wn_pws:
        labels.append("%s" % (password["name"]))
        occurrences.append(password["occurrences"])

    # First we need to clean the labels, i.e. delete all passwords that are not at least 3 characters
    old_len = len(labels)
    cleaned_list_labels = []
    cleaned_list_occs = []
    known_pws = []
    cnt = 0
    for i in range(len(labels)):
        cnt += 1
        curr = labels[i]
        if curr in known_pws:  # Remove following duplicates
            log_err("Removed {}, reason: duplicate entry".format(curr))
        elif len(curr) < 3:  # Remove passwords with less than 3 characters
            log_err("Removed {}, reason: too short".format(curr))
        else:
            cleaned_list_labels.append(curr)
            cleaned_list_occs.append(occurrences[i])
            known_pws.append(curr)

    cut_wn_labels = cleaned_list_labels[:wn_limit]
    cut_wn_occs = cleaned_list_occs[:wn_limit]

    # Create a list that has the wn values but they are just for orientation/comparison of occurrences. The values of the "original" list are not going to used
    # for bar plotting. Instead, they will be saved under a key, that is ignored when drawing the bar plot.
    new_occs_inserted = [{"orig": x, "list": -1} for x in cut_wn_occs]
    new_labels_inserted = [{"orig": x, "list": None} for x in cut_wn_labels]

    # Insert the sorted word list items at the right x coords
    idx_behind_last_wn = len(cut_wn_labels)
    xcoords_bar = []

    for item in pw_list:
        occs = item["occurrences"]
        # Determine first if this elements occs are lower than the last wn element. If thats the case, append it behind the last wn element
        if occs < cut_wn_occs[-1]:
            # If the current item occurrences was lower than the last wordnet element, append it with the index last_wn + 1 and increment this counter
            # xcoords_bar.append(idx_behind_last_wn)
            new_occs_inserted.append({"orig": -1, "list": occs})
            new_labels_inserted.append({"orig": "", "list": item["name"]})
            idx_behind_last_wn += 1
        else:
            # At this point we know the current elements occs are not lower than the last wn element
            # Now we just need to find out where (within the first and last wn element frame) it will be drawn
            for idx, wn_occs in enumerate(cut_wn_occs):
                # Run until occs is NOT lower than wn_occs
                if occs < wn_occs:
                    pass
                elif occs >= wn_occs:

                    # cut_wn_occs is stored from most to least occurrences, so if val a is bigger than the current value from cut_wn_occs it must automatically
                    # be bigger than the rest of the list (since it is ordererd in a decending order)
                    # Before we insert, there may already be an element that was previously compared against the same element, so we need to determine if we insert before or
                    # after this index
                    if new_occs_inserted[idx]["list"] < occs:
                        # The current occs value is bigger than what is already in there
                        new_occs_inserted.insert(
                            idx, {"orig": -1, "list": occs})
                        new_labels_inserted.insert(
                            idx, {"orig": "", "list": item["name"]})
                    else:
                        # If the value is bigger, we insert occs after this index
                        new_occs_inserted.insert(
                            idx+1, {"orig": -1, "list": occs})
                        new_labels_inserted.insert(
                            idx+1, {"orig": "", "list": item["name"]})

                    break
                else:
                    pass

    # Transform the dict to a flat list. List dict items with orig = -1 are going to be 0 in the flattened list, else the "list" value
    flat_occs_inserted = []
    for x in new_occs_inserted:
        if x["list"] == -1:
            flat_occs_inserted.append(0)
        else:
            flat_occs_inserted.append(x["list"])
    # ... also transform the label list so we have a consistent mapping again (mind the zeros)
    flat_labels_inserted = []
    for x in new_labels_inserted:
        if x["list"] == None:
            flat_labels_inserted.append("")
        else:
            flat_labels_inserted.append(x["list"])

    # Check lengths (the next step will raise an exception if the lengths of both flat lists are not equal since we want to merge them into a dict)
    if len(flat_labels_inserted) != len(flat_occs_inserted):
        log_err("Something went wrong while flattening the lists (lengths are not equal). flat_occs_inserted: %d, flat_labels_inserted: %d" % (
            len(flat_occs_inserted), len(flat_labels_inserted)))
        return

    # store labels with occs as keys
    labels_for_occs = {}
    for idx, val in enumerate(flat_occs_inserted):
        labels_for_occs[idx] = flat_labels_inserted[idx]

    # save 0 states in flat lists
    zero_pos = []
    flat_occs_inserted_no_zeros = []
    for idx, val in enumerate(flat_occs_inserted):
        if val == 0:
            zero_pos.append(idx)
        else:
            flat_occs_inserted_no_zeros.append(val)

    # sort lists
    sorted_no_zeros = sorted(flat_occs_inserted_no_zeros, reverse=True)
    log_status("Unsorted xcoords list: \n{}".format(flat_occs_inserted))

    # restore 0 states, i.e. insert zeros at the indices saved in the zero_pos list
    sorted_with_zeros = sorted_no_zeros[:]
    for idx in zero_pos:
        sorted_with_zeros.insert(idx, 0)

    log_status("Sorted xcoords list: \n{}".format(sorted_with_zeros))

    # Draw the bar plot
    rect1 = ax.bar(np.arange(len(sorted_with_zeros)),
                   sorted_with_zeros, alpha=0.7, color="gray", width=0.3)

    i = 0
    for rect in rect1:
        height = rect.get_height()
        ax.annotate('{}'.format(flat_labels_inserted[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0*3, 3),  # use 3 points offset
                    textcoords="offset points",  # in both directions
                    rotation=90,
                    # fontsize="x-small",
                    fontsize=9,
                    ha="center", va='bottom')
        i += 1

    # Create the xticks for the wn 1 and 1000 labels
    # plt.xticks([0, wn_limit-1], [cut_wn_labels[0],
    #                              cut_wn_labels[wn_limit-1]])
    # Draw the line plot
    ax.plot(np.arange(len(cut_wn_labels)), cut_wn_occs, "-", color="black")
    # Also print the pw list (for manual labelling)
    for k, v in enumerate(pw_list):
        print("{} - {}".format(k+1, v))
    ax.set_yscale("log", basey=10)
    # ax.set_ylim(bottom=0)
    plt.ylim((pow(10, 0)))
    ax.set_xlim(left=0)
    ax.set_ylim([0, sorted_no_zeros[0] + sorted_no_zeros[0] / 4])
    # plt.ticklabel_format(style='plain', axis='y')
    plt.xlabel(
        "Top %s Wordnet Noun Passwords" % helper.format_number(wn_limit))
    plt.ylabel("Occurrences")
    if not include_perms:
        plt.title("Top %d List Passwords (excl. variants)" % top)
    else:
        plt.title("Top %d List Passwords (incl. variants)" % top)
    blue_patch = mpatches.Patch(color="black", label="Wordnet Top Passwords")
    red_patch = mpatches.Patch(
        color="gray", label=list_name)
    plt.legend(handles=[blue_patch, red_patch], loc="best")
    log_ok("Drawing plot...")
    plt.show(f)


def overview_wn():
    """
    Give a overview over the Wordnet (with all of its synsets, permutations and lemmas)

    PoS | Total Synsets | Total Lemmas | Permutations | Hits w/o perms | Hits w/ perms | Total occurrences w/o perms | Total occurrences w/ perms
    """
    vals = {}
    vals["n"] = {}
    vals["v"] = {}
    vals["adj"] = {}
    vals["adv"] = {}

    # Part of speech label
    vals["n"]["label"] = "Nouns"
    vals["v"]["label"] = "Verbs"
    vals["adj"]["label"] = "Adjectives"
    vals["adv"]["label"] = "Adverbs"

    # Total synsets
    print("1 Counting synsets...")
    res = mongo.db["wn_synsets_noun"].count()
    vals["n"]["total_synsets"] = res
    res = mongo.db["wn_synsets_verb"].count()
    vals["v"]["total_synsets"] = res
    res = mongo.db["wn_synsets_adjective"].count()
    vals["adj"]["total_synsets"] = res
    res = mongo.db["wn_synsets_adverb"].count()
    vals["adv"]["total_synsets"] = res
    print("1 Counting synsets... Finished!")

    # Total lemmas
    print("2 Counting lemmas...")
    res = mongo.db["wn_lemma_permutations_noun"].count()
    vals["n"]["total_lemmas"] = res
    res = mongo.db["wn_lemma_permutations_verb"].count()
    vals["v"]["total_lemmas"] = res
    res = mongo.db["wn_lemma_permutations_adjective"].count()
    vals["adj"]["total_lemmas"] = res
    res = mongo.db["wn_lemma_permutations_adverb"].count()
    vals["adv"]["total_lemmas"] = res
    print("2 Counting lemmas... Finished!")

    # Total permutations
    print("3 Counting passwords...")
    res = mongo.db["passwords_wn_noun"].count()
    vals["n"]["total_permutations"] = res
    res = mongo.db["passwords_wn_verb"].count()
    vals["v"]["total_permutations"] = res
    res = mongo.db["passwords_wn_adjective"].count()
    vals["adj"]["total_permutations"] = res
    res = mongo.db["passwords_wn_adverb"].count()
    vals["adv"]["total_permutations"] = res
    print("3 Counting passwords... Finished!")

    # Hits w/o permutations
    query_hits_no_perms = {
        "$and": [
            {"permutator": "no_permutator"},
            {"occurrences": {"$gt": 0}}
        ]
    }
    print("4 Counting passwords (no permutations)...")
    # create index, so we can boost the performance drastically
    res = mongo.db["passwords_wn_noun"].find(query_hits_no_perms).count()
    vals["n"]["hits_no_perms"] = res
    res = mongo.db["passwords_wn_verb"].find(query_hits_no_perms).count()
    vals["v"]["hits_no_perms"] = res
    res = mongo.db["passwords_wn_adjective"].find(query_hits_no_perms).count()
    vals["adj"]["hits_no_perms"] = res
    res = mongo.db["passwords_wn_adverb"].find(query_hits_no_perms).count()
    vals["adv"]["hits_no_perms"] = res
    print("4 Counting passwords (no permutations)... Finished!")

    # Hits w/ permutations
    query_hits_with_perms = {
        "$and": [
            {"occurrences": {"$gt": 0}}
        ]
    }
    print("5 Counting passwords (with permutations)...")
    res = mongo.db["passwords_wn_noun"].find(query_hits_with_perms).count()
    vals["n"]["hits_with_perms"] = res
    res = mongo.db["passwords_wn_verb"].find(query_hits_with_perms).count()
    vals["v"]["hits_with_perms"] = res
    res = mongo.db["passwords_wn_adjective"].find(
        query_hits_with_perms).count()
    vals["adj"]["hits_with_perms"] = res
    res = mongo.db["passwords_wn_adverb"].find(query_hits_with_perms).count()
    vals["adv"]["hits_with_perms"] = res
    print("5 Counting passwords (with permutations)... Finished!")

    # Total occurrences w/o permutations
    print("6 Counting password occurrences (no permutations)...")
    res = mongo.db["passwords_wn_noun"].aggregate([{"$match": {"permutator": "no_permutator"}}, {
                                                  "$group": {"_id": "tag", "sum": {"$sum": "$occurrences"}}}])
    for item in res:
        vals["n"]["occs_no_perms"] = item["sum"]
    res = mongo.db["passwords_wn_verb"].aggregate([{"$match": {"permutator": "no_permutator"}}, {
                                                  "$group": {"_id": "tag", "sum": {"$sum": "$occurrences"}}}])
    for item in res:
        vals["v"]["occs_no_perms"] = item["sum"]
    res = mongo.db["passwords_wn_adjective"].aggregate([{"$match": {"permutator": "no_permutator"}}, {
                                                       "$group": {"_id": "tag", "sum": {"$sum": "$occurrences"}}}])
    for item in res:
        vals["adj"]["occs_no_perms"] = item["sum"]
    res = mongo.db["passwords_wn_adverb"].aggregate([{"$match": {"permutator": "no_permutator"}}, {
                                                    "$group": {"_id": "tag", "sum": {"$sum": "$occurrences"}}}])
    for item in res:
        vals["adv"]["occs_no_perms"] = item["sum"]
    print("6 Counting password occurrences (no permutations)... Finished!")

    # Total occurrences w/ permutations
    print("7 Counting password occurrences (with permutations)...")
    res = mongo.db["passwords_wn_noun"].aggregate(
        [{"$group": {"_id": "tag", "sum": {"$sum": "$occurrences"}}}])
    for item in res:
        vals["n"]["occs_with_perms"] = item["sum"]

    res = mongo.db["passwords_wn_verb"].aggregate(
        [{"$group": {"_id": "tag", "sum": {"$sum": "$occurrences"}}}])
    for item in res:
        vals["v"]["occs_with_perms"] = item["sum"]

    res = mongo.db["passwords_wn_adjective"].aggregate(
        [{"$group": {"_id": "tag", "sum": {"$sum": "$occurrences"}}}])
    for item in res:
        vals["adj"]["occs_with_perms"] = item["sum"]

    res = mongo.db["passwords_wn_adverb"].aggregate(
        [{"$group": {"_id": "tag", "sum": {"$sum": "$occurrences"}}}])
    for item in res:
        vals["adv"]["occs_with_perms"] = item["sum"]
    print("7 Counting password occurrences (with permutations)... Finished!")

    rows = []
    for item in vals.values():
        row = []
        row.append(item["label"])
        row.append(item["total_synsets"])
        row.append(item["total_lemmas"])
        row.append(item["total_permutations"])
        row.append(item["hits_no_perms"])
        row.append(item["hits_with_perms"])
        row.append(item["occs_no_perms"])
        row.append(item["occs_with_perms"])
        rows.append(row)

    headers = [
        "PoS",
        "Synsets",
        "Lemmas",
        "Permutations",
        "Hits no perms",
        "Hits w. perms",
        "Occs. no perms",
        "Occs. w. perms"
    ]

    print()
    print()
    print(tabulate(rows, headers=headers))
    print()
    print()


def compare_hits_to_permutations(source, include_perms=False, sort_by="quota", top=0):
    """
    Double bar diagram. Left bar: efficiency, right bar: number of lemmas (with and without permutations)
    """
    allowed_sources = ["wordnet", "list"]
    if source not in allowed_sources:
        log_err("Source %s not recognized" % source)
        return

    allowed_sort_bys = ["quota", "total_lemmas", "password_hits"]
    if sort_by not in allowed_sort_bys:
        log_err("Sort by %s not recognized" % sort_by)
        return

    result_list = []

    if source == "list":
        labels = {
            "07_first_names.txt": "First Names",
            "09_en_countries.txt": "Countries",
            "01_en_office_supplies.txt": "Office Supplies",
            "06_en_cities.txt": "Cities",
            "13_en_fruit.txt": "Fruit",
            "08_last_names.txt": "Last Name",
            "10_automobile.txt": "Automobile",
            "12_tech_brands.txt": "Tech Brands",
            "03_keyboard_patterns.txt": "Keyboard Patterns",
            "15_en_food.txt": "Food",
            "02_en_office_brands.txt": "Office Brands",
            "14_en_drinks.txt": "Drinks",
            "05_en_financial_brands.txt": "Financial Brands",
            "11_software_names.txt": "Software Names",
        }
        all_lists = []
        lists_result = mongo.db["lists"].find()
        for res in lists_result:
            all_lists.append(res["filename"])
        # for each lists get the efficiency as well as the total number of lemmas (with or without permutations)
        for list_name in all_lists:
            # skip 99_unsortiert.txt
            if list_name == "99_unsortiert.txt":
                continue
            # query to get the total amount of lemmas
            if include_perms:
                query = {
                    "$and": [
                        {"source": list_name},
                    ]
                }
            else:
                query = {
                    "$and": [
                        {"source": list_name},
                        {"permutator": "no_permutator"}
                    ]
                }
            total_lemmas = mongo.db["passwords_lists"].count_documents(query)
            # query to get the passwords with hits > 0 (efficiency)
            if include_perms:
                query = {
                    "$and": [
                        {"source": list_name},
                        {"occurrences": {"$gt": 0}}
                    ]
                }
            else:
                query = {
                    "$and": [
                        {"source": list_name},
                        {"permutator": "no_permutator"},
                        {"occurrences": {"$gt": 0}}
                    ]
                }
            password_hits = mongo.db["passwords_lists"].count_documents(query)
            o = {
                "name": labels[list_name],
                "total_lemmas": total_lemmas,
                "password_hits": password_hits,
                # "quota": total_lemmas / password_hits
                "quota": round((password_hits / total_lemmas) * 100, 3)
            }
            result_list.append(o)
    elif source == "wordnet":
        labels = {
            "passwords_wn_noun": "Wordnet Nouns",
            "passwords_wn_adverb": "Wordnet Adverbs",
            "passwords_wn_verb": "Wordnet Verbs",
            "passwords_wn_adjective": "Wordnet Adjectives",
        }
        all_pos = []
        for res in mongo.db.collection_names():
            if res.startswith("passwords_wn_"):
                all_pos.append(res)
        for pos in all_pos:
            # query to get the total amount of lemmas
            if include_perms:
                query = {}
            else:
                query = {
                    "$and": [
                        {"permutator": "no_permutator"}
                    ]
                }
            total_lemmas = mongo.db[pos].count_documents(query)
            # query to get the passwords with hits > 0 (efficiency)
            if include_perms:
                query = {
                    "$and": [
                        {"occurrences": {"$gt": 0}}
                    ]
                }
            else:
                query = {
                    "$and": [
                        {"permutator": "no_permutator"},
                        {"occurrences": {"$gt": 0}}
                    ]
                }
            password_hits = mongo.db[pos].count_documents(query)
            o = {
                "name": labels[pos],
                "total_lemmas": total_lemmas,
                "password_hits": password_hits,
                # "quota": total_lemmas / password_hits
                "quota": round((password_hits / total_lemmas) * 100, 3)
            }
            result_list.append(o)

    else:
        return

    # if sort_by == "quota":
    #     # sort from lowest to highest since lower quotas are better than higher ones
    #     sorted_sums = sorted(
    #         result_list, key=lambda k: k[sort_by], reverse=False)
    # else:
    #     sorted_sums = sorted(
    #         result_list, key=lambda k: k[sort_by], reverse=True)
    sorted_sums = sorted(
        result_list, key=lambda k: k[sort_by], reverse=True)

    if top > 0:
        sorted_sums = sorted_sums[:top]
    wrapped_labels = ["-\n".join(wrap(x["name"], 10)) for x in sorted_sums]

    # print for visibility
    for k, v in enumerate(sorted_sums):
        print(k, v)

    list_password_hits = [x["password_hits"] for x in sorted_sums]
    list_total_lemmas = [x["total_lemmas"] for x in sorted_sums]
    N = len(sorted_sums)
    ind = np.arange(N)
    width = 0.35
    plt.bar(ind, list_total_lemmas, width, label="Total Lemmas", color="black")
    plt.bar(ind + width, list_password_hits, width,
            label="Efficiency", color="grey")

    plt.yscale("log", basey=10)

    plt.ylabel("Password Occurrences")
    plt.xlabel("Password Sources")
    if include_perms:
        label_tag = " (incl. permutations)"
    else:
        label_tag = " (excl. permutations)"
    if source == "list":
        plt.title(
            "Total Lemmas/Efficiency Comparison for Lists%s" % label_tag)
    else:
        plt.title(
            "Total Lemmas/Efficiency Comparison for the Wordnet%s" % label_tag)
    if source == "list":
        if top == 0:
            plt.xticks(ind + width / 2, wrapped_labels,
                       fontsize=7, rotation=90)
        else:
            # don't rotate so the labels look are not tilted
            plt.xticks(ind + width / 2, wrapped_labels, fontsize=7)
    else:
        plt.xticks(ind + width / 2, wrapped_labels, fontsize=7)
    plt.legend(loc="best")
    plt.show()


def display_pct_synsets_on_level(mode, top=5, level=0):
    """
    Display and print percentages of the top X synsets per level relative to the total amount of their levels.
    top: Top X synsets per level
    level: Draw a diagram with the top X synsets of the specified level. However print all levels
    """
    if top > 30:
        log_err("top max value is 30")
        return
    allowed_modes = ["n", "v"]
    if mode not in allowed_modes:
        log_err("Unrecognized mode %s" % mode)
        return
    if mode == "n":
        coll_name = "wn_synsets_noun"
        lowest_level = duplicates.get_lowest_level_wn("noun")
    elif mode == "v":
        coll_name = "wn_synsets_verb"
        lowest_level = duplicates.get_lowest_level_wn("verb")
    else:
        return
    labels = []
    occs = []
    # get lowest level and start from the lowest level
    for i in range((lowest_level+1)):
        query_total_sum = [
            {"$match": {
                "level": i
            }},
            {"$group": {
                "_id": "id",
                "sum": {
                    "$sum": "$total_hits"
                }
            }}
        ]
        # get the total hits
        res = mongo.db[coll_name].aggregate(query_total_sum)
        total_occs = list(res)[0]["sum"]
        # get the top X synsets of this level
        top_ss = mongo.db[coll_name].find({"$and": [{"level": i}, {"total_hits": {
                                          "$gt": 0}}]}).sort("total_hits", -1).limit(top)
        # calculate their percentage
        print("Level", i, "100% =", helper.format_number(total_occs))
        for ss in top_ss:
            try:
                total_hits = ss["total_hits"]
            except KeyError:
                total_hits = 0
            pct = round(total_hits / total_occs * 100, 2)
            if i == level:
                labels.append(ss["id"])
                occs.append(pct)
            print("\t", "{}%".format(pct),
                  ss["id"], helper.format_number(total_hits))
        print()

    # Plot as bar
    N = len(labels)
    ind = np.arange(N)
    width = 0.35
    plt.bar(ind, occs, width,
            label="Percentages", color="black")
    # plt.yscale("log", basey=10)
    plt.ylabel("Percentage (total occurrences) of the level [%]")
    plt.xlabel("Synset")
    plt.title("Top Synset Percentages for Level %d" % level,
              fontdict={'fontsize': 10})
    # at a certain top value, wrap and rotate the labels
    if top > 5:
        plt.xticks(ind, labels, fontsize=7, rotation=45)
    else:
        plt.xticks(ind, labels, fontsize=7)
    plt.legend(loc="best")

    plt.show()


def top_passwords_permutators(source, source_name="", top=1000):
    """
    Display the permutators of the top X passwords of a password source.
    Print the percentages.
    """
    source_map = {
        "wn_n": "passwords_wn_noun",
        "wn_v": "passwords_wn_verb",
        "wn_adj": "passwords_wn_adjective",
        "wn_adv": "passwords_wn_adverb",
        "list": "passwords_lists",
        "dict": "passwords_dicts_",
    }
    label_map = {
        "wn_n": "Wordnet Nouns",
        "wn_v": "Wordnet Verbs",
        "wn_adj": "Wordnet Adjectives",
        "wn_adv": "Wordnet Adverbs",
        "list": "Category List ",
        "dict": "Dictionary ",
    }
    requires_source_name = [
        "list",
        "dict",
    ]
    if source not in source_map.keys():
        log_err("Unrecognized source %s" % source)
        return

    if source in requires_source_name and source_name == "":
        log_err("Source %s requires additional source_name" % source)
        return
    # build the collection name
    if source_name != "" and source != "list":
        coll_name = "{}{}".format(source_map[source], source_name)
        print()
    else:
        coll_name = source_map[source]
    # get the top X passwords
    if source == "list":
        aggregate_query = [
            {"$match": {"occurrences": {"$gt": 1000}, "source": source_name}},
            {"$limit": top},
            {"$group": {"_id": "$permutator", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
    else:
        aggregate_query = [
            {"$match": {"occurrences": {"$gt": 1000}}},
            {"$limit": top},
            {"$group": {"_id": "$permutator", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
    labels = []
    count = []
    res = mongo.db[coll_name].aggregate(aggregate_query)
    for r in res:
        permutator = r["_id"]
        count_permutator = r["count"]
        labels.append(permutator)
        count.append(count_permutator)
        print("Permutator:", permutator, count_permutator)

    # Plot as bar
    N = len(labels)
    ind = np.arange(N)
    width = 0.35
    plt.bar(ind, count, width,
            label="Percentages", color="black")
    # plt.yscale("log", basey=10)
    plt.ylabel("# of passwords generated using permutator")
    plt.xlabel("Permutator")
    plt.title("Permutators of the Top {} Passwords of {}{}".format(top, label_map[source], source_name),
              fontdict={'fontsize': 10})
    plt.xticks(ind, labels, fontsize=7, rotation=45)
    plt.legend(loc="best")

    plt.show()


def lookup_number_sequences():
    """
    Generate numbers (from 0 - 9.999.999) and other number sequences and look them up.
    """
    # we don't include 1234567 (and every sequence below that) since it is smaller than 9.999.999 and therefore included below
    num_seq = []
    num_seq.append(str(12345678))
    num_seq.append(str(123456789))
    num_seq.append(str(1234567890))
    # start with 0
    num_seq.append("01")
    num_seq.append("012")
    num_seq.append("0123")
    num_seq.append("01234")
    num_seq.append("012345")
    num_seq.append("0123456")
    num_seq.append("012345678")
    num_seq.append("0123456789")
    # reverse (other numbers are already included below)
    num_seq.append("0987654321")
    num_seq.append(str(987654321))
    num_seq.append(str(87654321))
    # ends with zero (other numbers are already included below)
    num_seq.append(str(9876543210))
    num_seq.append(str(876543210))
    num_seq.append(str(76543210))

    # custom sequences
    for i in num_seq:
        hits = lookup_pass(hash_sha1(str(i)))
        print(i, hits)
        o = {
            "name": i,
            "occurrences": hits,
            "tag": ILL_TAG,
            "permutator": "custom_seq"
        }
        mongo.db_pws_numbers.insert_one(o)

    # 0 - 9.999.999
    for i in range(10000000):
        hits = lookup_pass(hash_sha1(str(i)))
        print(i, hits)
        o = {
            "name": i,
            "occurrences": hits,
            "tag": ILL_TAG,
            "permutator": "natural_nums"
        }
        mongo.db_pws_numbers.insert_one(o)

    print("Finished!")


def top_passwords_wn_numbers(pos, top=10):
    """
    Plot the top X noun passwords .
    """
    # create a list with all parent synsets whose children are related to numbers
    # use regex for numbers: /^\d+$/ (without quotation strings)
    allowed_pos = ["n", "v", "adj", "adv", ]
    if pos not in allowed_pos:
        log_err("Unrecognized part of speech: %s" % pos)
        return
    if pos == "n":
        coll_name = "passwords_wn_noun"
        print("Noun")
        title_pos = "Noun"
    elif pos == "v":
        coll_name = "passwords_wn_verb"
        print("Verb")
        title_pos = "Verb"
    elif pos == "adj":
        coll_name = "passwords_wn_adjective"
        print("Adjective")
        title_pos = "Adjective"
    elif pos == "adv":
        coll_name = "passwords_wn_adverb"
        print("Adverb")
        title_pos = "Adverb"
    else:
        return

    regex = re.compile("^\d+$", re.IGNORECASE)
    buf_len = top * 30
    known_names = []
    result_list = []
    res = mongo.db[coll_name].find({"name": regex}).sort(
        "occurrences", pymongo.DESCENDING).limit(buf_len)
    for r in res:
        if len(result_list) == top:
            break
        if r["name"] in known_names:
            continue
        else:
            known_names.append(r["name"])
            result_list.append(r)
    labels = []
    occs = []
    for k, v in enumerate(result_list):
        print(k, v["name"], helper.format_number(v["occurrences"]))
        labels.append(v["name"])
        occs.append(v["occurrences"])

    # Plot as bar
    N = len(labels)
    ind = np.arange(N)
    width = 0.35
    plt.bar(ind, occs, width,
            label="Occurrences", color="black")
    plt.yscale("log", basey=10)
    plt.ylabel("Occurrences")
    plt.xlabel("Password")
    plt.title("Top %d %s Wordnet Number-only Passwords" % (top, title_pos),
              fontdict={'fontsize': 10})
    # at a certain top value, wrap and rotate the labels
    if top > 5:
        plt.xticks(ind, labels, fontsize=7, rotation=45)
    else:
        plt.xticks(ind, labels, fontsize=7)
    plt.legend(loc="best")

    plt.show()


def list_wn_coverage(source, source_name):
    """
    Print/plot the coverage of a list/misc_list/dictionary on all parts of speeches of the wordnet
    It is critical to create an index (on the name field, since we lookup different passwords) beforehand to reduce search times dramastically

    db.coll.createIndex({"name":1})
    """
    allowed_sources = ["dict", "misc_list", "list"]
    if source not in allowed_sources:
        log_err("Unrecognized source: %s" % source)
        return

    if source == "list":
        coll_name = "passwords_lists"
    elif source == "dict":
        coll_name = "passwords_dicts_%s" % source_name
    elif source == "misc_list":
        coll_name = "passwords_misc_lists_%s" % source_name
    else:
        return

    pos_noun = "passwords_wn_noun"
    pos_verb = "passwords_wn_verb"
    pos_adjective = "passwords_wn_adjective"
    pos_adverb = "passwords_wn_adverb"

    # keep open cursor, ignore timeout
    if source == "list":
        query = {"source": source_name}
    else:
        query = {}

    tested = 0
    not_found = 0
    hits_noun = 0
    hits_verb = 0
    hits_adjective = 0
    hits_adverb = 0
    limit = 3000
    for pw in mongo.db[coll_name].find(query, no_cursor_timeout=True):
        # if tested == limit:
        #     break
        # look pw up in each pos
        if mongo.db[pos_noun].count_documents({"name": pw["name"]}) > 0:
            hits_noun += 1
        if mongo.db[pos_verb].count_documents({"name": pw["name"]}) > 0:
            hits_verb += 1
        if mongo.db[pos_adjective].count_documents({"name": pw["name"]}) > 0:
            hits_adjective += 1
        if mongo.db[pos_adverb].count_documents({"name": pw["name"]}) > 0:
            hits_adverb += 1

        print(hits_noun, hits_verb, hits_adjective, hits_adverb)

        print(tested, pw["name"])
        tested += 1

    print("Finished!")
    labels = []
    pcts = []
    res_list = []
    pct_noun = round((hits_noun / tested) * 100, 3)
    o = {
        "label": "Noun",
        "pct": pct_noun
    }
    res_list.append(o)

    pct_verb = round((hits_verb / tested) * 100, 3)
    o = {
        "label": "Verb",
        "pct": pct_verb
    }
    res_list.append(o)

    pct_adjective = round((hits_adjective / tested) * 100, 3)
    o = {
        "label": "Adjective",
        "pct": pct_adjective
    }
    res_list.append(o)

    pct_adverb = round((hits_adverb / tested) * 100, 3)
    o = {
        "label": "Adverb",
        "pct": pct_adverb
    }
    res_list.append(o)

    sorted_pcts = sorted(res_list, key=lambda k: k["pct"], reverse=True)

    labels = [x["label"] for x in sorted_pcts]
    pcts = [x["pct"] for x in sorted_pcts]

    print("Tested:", tested)
    print()
    print(source, source_name)
    print("Noun")
    print("  Found:", hits_noun)
    print("  Not found:", tested - hits_noun)
    print("  Coverage:", pct_noun, "%")
    print()
    print("Verb")
    print("  Found:", hits_verb)
    print("  Not found:", tested - hits_verb)
    print("  Coverage:", pct_verb, "%")
    print()
    print("Adjective")
    print("  Found:", hits_adjective)
    print("  Not found:", tested - hits_adjective)
    print("  Coverage:", pct_adjective, "%")
    print()
    print("Adverb")
    print("  Found:", hits_adverb)
    print("  Not found:", tested - hits_adverb)
    print("  Coverage:", pct_adverb, "%")

    # Plot as bar
    N = len(labels)
    ind = np.arange(N)
    width = 0.35
    plt.bar(ind, pcts, width,
            label="Percentages", color="black")
    plt.yscale("log", basey=10)
    plt.ylabel("Coverage [%]")
    plt.xlabel("Wordnet Part of Speech")
    plt.title("Coverage of %s of the Wordnet" %
              source_name, fontdict={'fontsize': 10})
    plt.xticks(ind, labels, fontsize=7)
    plt.legend(loc="best")

    plt.show()


def topn_numbers(top):
    """
    Plot the top X number passwords.
    """
    labels = []
    occs = []
    top_pws = mongo.db["passwords_numbers"].find({"occurrences": {"$gt": 100}}).sort(
        "occurrences", pymongo.DESCENDING).limit(top)
    for k, v in enumerate(top_pws):
        labels.append(v["name"])
        occs.append(v["occurrences"])
        print(k, v["name"], helper.format_number(v["occurrences"]))

    # Plot as bar
    N = len(labels)
    ind = np.arange(N)
    width = 0.35
    plt.bar(ind, occs, width,
            label="Percentages", color="black")
    plt.yscale("log", basey=10)
    plt.ylabel("Occurrences")
    plt.xlabel("Passwords")
    plt.title("Top %d Number Passwords" % top, fontdict={'fontsize': 10})
    if top < 5:
        plt.xticks(ind, labels, fontsize=7)
    else:
        plt.xticks(ind, labels, fontsize=7, rotation=45)
    plt.legend(loc="best")

    plt.show()

# ====================== Helper Functions ======================


def permutations_for_lemma(lemma, depth, source, mode):
    """
    Permutate a lemma.
    Mode: n, v, adj, adv. Controls where everything is stored
    """
    modes = [
        "n",
        "v",
        "adj",
        "adv"
    ]
    if mode not in modes:
        log_err("Invalid mode %s" % mode)
        return

    total_hits = 0
    not_found_cnt = 0
    found_cnt = 0
    all_permutations = []
    for combination_handler in combinator.all:
        # Generate all permutations
        permutations = combination_handler(lemma, permutator.all)
        if permutations == None:
            continue
        # Combinators always return a list of permutations
        if type(permutations) == list:
            for p in permutations:
                trans_hits = lookup(p["name"], depth, source, lemma)
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
                all_permutations.append(o)

                total_hits += trans_hits
                if trans_hits == 0:
                    not_found_cnt += 1
                else:
                    found_cnt += 1
        else:
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
            all_permutations.append(o)

            if trans_hits == 0:
                not_found_cnt += 1
            else:
                found_cnt += 1
            total_hits += trans_hits

    permutations_for_lemma = {
        "word_base": lemma,
        "permutations": all_permutations,
        "total_permutations": len(all_permutations),
        "total_hits": total_hits,
        "synset": source
    }

    if mode == "n":
        mongo.store_permutations_for_lemma_noun(permutations_for_lemma)
    if mode == "v":
        mongo.store_permutations_for_lemma_verb_missing(permutations_for_lemma)

    return total_hits, not_found_cnt, found_cnt


def lookup(permutation, depth, source, word_base):
    """
    Hashes the (translated) lemma and looks it up in  the HIBP password file.
    """
    # Hash and lookup translated lemma
    hashed_lemma = hash_sha1(permutation)
    occurrences = lookup_pass(hashed_lemma)
    return occurrences


def hash_sha1(s):
    """
    Hash the password.
    """
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


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


if __name__ == "__main__":
    # identify_and_store_missing_verbs()
    # lookup_and_insert_missing_nouns()
    # identify_and_store_missing_nouns()
    main()
    pass
