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


parser = argparse.ArgumentParser(
    description="Password hash anaylsis using WordNet and the HaveIBeenPwned database.")
parser.add_argument("-p", "--pass-database", type=str,
                    help="Path to the HIBP password database.", dest="pass_db_path")
parser.add_argument("-t", "--lookup-utility", action="store_true",
                    help="If set, use sgrep instead of the look utility.", dest="lookup_utility")
args = parser.parse_args()

# Progress pad: https://pad.riseup.net/p/q5Qvgib36rkzQiWZE3uE

# Rausfiltern von arabischen Zahlen (0-99)
# db.getCollection('passwords_wn_noun').find({"$and": [{"permutator": "no_permutator"},{"word_base": {"$nin": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "11"]}}, {"occurrences": {"$gt":0}}]}).count()
# amount of passwords in the password database

# Ignore deprecation warnings:
# py.exe -Wignore::DeprecationWarning .\finalgraphs.py

pwned_pw_amount = 551509767
ILL_TAG = get_curr_time_str()


# Nouns
# Found: 74374
# Not found: 7741
# Total: 82115
# Total (supposed): 82115
# Not found len: 7741

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


def main():

    # =============================================================================================================================================
    #
    #  Calculate average permutations per lemma
    #
    # avg = avg_permutations_lemma("wordnet_n")
    # log_ok("Average permutations per lemma for Wordnet nouns: %d" % (avg))  # 225
    # avg = avg_permutations_lemma("wordnet_v")
    # log_ok("Average permutations per lemma for Wordnet verbs: %d" % (avg))  # 223
    # avg = avg_permutations_lemma("wordnet_adj")
    # log_ok("Average permutations per lemma for Wordnet adjectives: %d" %
    #        (avg))  # 221
    # avg = avg_permutations_lemma("wordnet_adv")
    # log_ok("Average permutations per lemma for Wordnet adverbs: %d" % (avg))  # 222
    # =============================================================================================================================================
    #
    # Calculate the number of hits (efficiency) as well as the percentage of hits (coverage)
    #
    # pw_hits, pct_hits = calculate_efficiency("wordnet_n", include_perms=False)
    # log_ok("Wordnet nouns (w/o permutations):\n\tPassword hits: {}\n\tPercentage hits: {}".format(pw_hits, pct_hits*100))
    # pw_hits, pct_hits = calculate_efficiency("wordnet_n", include_perms=True)
    # log_ok("Wordnet nouns (w/ permutations):\n\tPassword hits: {}\n\tPercentage hits: {}".format(pw_hits, pct_hits*100))

    # pw_hits, pct_hits = calculate_efficiency("wordnet_v", include_perms=False)
    # log_ok("Wordnet verbs (w/o permutations):\n\tPassword hits: {}\n\tPercentage hits: {}".format(pw_hits, pct_hits*100))
    # pw_hits, pct_hits = calculate_efficiency("wordnet_v", include_perms=True)
    # log_ok("Wordnet verbs (w/ permutations):\n\tPassword hits: {}\n\tPercentage hits: {}".format(pw_hits, pct_hits*100))

    # pw_hits, pct_hits = calculate_efficiency(
    #     "wordnet_adj", include_perms=False)
    # log_ok("Wordnet adjectives (w/o permutations):\n\tPassword hits: {}\n\tPercentage hits: {}".format(pw_hits, pct_hits*100))
    # pw_hits, pct_hits = calculate_efficiency("wordnet_adj", include_perms=True)
    # log_ok("Wordnet adjectives (w/ permutations):\n\tPassword hits: {}\n\tPercentage hits: {}".format(pw_hits, pct_hits*100))

    # pw_hits, pct_hits = calculate_efficiency(
    #     "wordnet_adv", include_perms=False)
    # log_ok("Wordnet adverbs (w/o permutations):\n\tPassword hits: {}\n\tPercentage hits: {}".format(pw_hits, pct_hits*100))
    # pw_hits, pct_hits = calculate_efficiency("wordnet_adv", include_perms=True)
    # log_ok("Wordnet adverbs (w/ permutations):\n\tPassword hits: {}\n\tPercentage hits: {}".format(pw_hits, pct_hits*100))
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
    # print_top_lemmas("n", 20, include_perms=True)
    # print()
    # print("Verbs")
    # print_top_lemmas("v", 20, include_perms=False)
    # print()
    # print("Verbs")
    # print_top_lemmas("v", 20, include_perms=True)
    # print()
    # print("Adjectives")
    # print_top_lemmas("adj", 20, include_perms=False)
    # print()
    # print("Adjectives")
    # print_top_lemmas("adj", 20, include_perms=True)
    # print()
    # print("Adverbs")
    # print_top_lemmas("adv", 20, include_perms=False)
    # print()
    # print("Adverbs")
    # print_top_lemmas("adv", 20, include_perms=True)
    # print()
    # # =============================================================================================================================================
    #
    # Print top n synsets for each level
    #
    # top_classes_per_level("noun", 10)
    # top_classes_per_level("verb", 10)
    # =============================================================================================================================================
    #
    # Locate the top n passwords from a category list on the top n passwords of the Wordnet
    #
    locate_topn_list_pws_wn("12_tech_brands.txt", top=20, include_perms=False)
    # locate_topn_list_pws_wn("12_tech_brands.txt", top=20, include_perms=True)
    # =============================================================================================================================================
    #
    # Print stats for the all parts of speech of the Wordnet
    #
    # overview_wn()
    pass


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


def wordnet_coverage(top_hibp=1000, include_perms=False):
    f, ax = plt.subplots(1)

    # Contains all sum results. Will be used to create the bar plot in the end
    # Structure:
    #   type: misc,ref,etc
    #   name: source_name
    #   sum: sum
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
        log_ok("(%d)\t%s\t%s\t%s" %
               (k, v["type"], v["name"], helper.format_number(v["sum"])))

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


def locate_topn_list_pws_hibp(list_name, top=10, include_perms=False):
    """
    Mark the top N passwords of a given list within the top N passwords of the wordnet.
    On the X axis, mark each 50th step.
    """
    hibp_limit = 2000
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
    fname = sys.argv[1]
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
                    fontsize="x-small",
                    ha="center", va='bottom')
        i += 1

    # Draw the line plot
    ax.plot(np.arange(len(hibp_labels)), hibp_occs, "-", color="black")
    # Also print the pw list (for manual labelling)
    for k, v in enumerate(pw_list):
        log_ok("{} - {}".format(k, v))
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


def print_top_lemmas(pos, top, include_perms=False):
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
            "occurrences": {"$gt": 0}
        }

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
    top_with_buf = top * 4
    res_list = []
    known_names = []
    query_res = mongo.db[coll_name].find(query).sort(
        "occurrences", pymongo.DESCENDING).limit(top_with_buf)
    for item in query_res:
        if item["name"] in known_names:
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


def calculate_efficiency(base, include_perms=False):
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
    else:
        log_err("Invalid base")
        return 0

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


def examples_duplicates():
    """
    Print some examples for duplicates.
    MongoDB Find duplicates: db.getCollection('passwords_wn_noun').aggregate([{"$match": {"occurrences": {"$gt": 0}}}, {"$group": {_id: "$name", sum: {"$sum": 1}}}, {"$match": {"sum": {"$gt": 1}}}, {"$sort": {"sum": -1}}], { allowDiskUse: true })
    MongoDB Count number of duplicates: db.getCollection('passwords_wn_noun').aggregate([{"$match": {"occurrences": {"$gt": 0}}}, {"$group": {_id: "$name", sum: {"$sum": 1}}}, {"$match": {"sum": {"$gt": 1}}}, {"$sort": {"sum": -1}}, {"$group": {_id: null, count: {"$sum": 1}}}], { allowDiskUse: true })
    MongoDB Show clustered duplicates with synset origin: db.getCollection('passwords_wn_noun').aggregate([ { "$match": { "occurrences": { "$gt": 0 } } }, { "$group": { "_id": "$name", "sum": { "$sum": 1 }, "results": { "$push": { "name": "$name", "occurrences": "$occurrences", "word_base": "$word_base", "synset": "$synset", "level": "$depth", "permutator": "$permutator" } } } }, { "$match": { "sum": { "$gt": 1 } } }, { "$sort": { "sum": -1 } } ], {"allowDiskUse": true})    """
    pass


def locate_topn_list_pws_wn(list_name, top=10, include_perms=False):
    """
    Mark the top N passwords of a given list within the top N passwords of the wordnet.
    On the X axis, mark each 50th step.
    """
    # Read the top wn_limit passwords generated from the WordNet
    wn_limit = 1000
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
    for item in mongo.db_pws_lists.find(query).sort("occurrences", pymongo.DESCENDING).limit(top):
        o = {"name": item["name"],
             "occurrences": item["occurrences"],
             "permutator": item["permutator"]}
        pw_list.append(o)

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
                        25000
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
    buf_len = 1000 * 10
    top_wn_pws = mongo.db_pws_wn.find(search_filter).sort("occurrences", pymongo.DESCENDING).limit(buf_len)
    for password in top_wn_pws:
        labels.append("%s" % (password["name"]))
        occurrences.append(password["occurrences"])

    # First we need to clean the labels, i.e. delete all passwords that are not at least 3 characters
    old_len = len(labels)
    cleaned_list_labels = []
    cleaned_list_occs = []
    for i in range(len(labels)):
        curr = labels[i]
        if curr in labels[i+1:]:  # Remove following duplicates
            log_err("Removed {}, reason: duplicate entry".format(curr))
        elif len(curr) < 3:  # Remove passwords with less than 3 characters
            log_err("Removed {}, reason: too short".format(curr))
        else:
            cleaned_list_labels.append(curr)
            cleaned_list_occs.append(occurrences[i])
    
    print("LEN")
    print(len(cleaned_list_labels))
    print(len(cleaned_list_occs))
    return
    cut_wn_labels = cleaned_list_labels[:1000]
    cut_wn_occs = cleaned_list_occs[:1000]

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
                    fontsize="x-small",
                    ha="center", va='bottom')
        i += 1

    # Create the xticks for the wn 1 and 1000 labels
    plt.xticks([0, wn_limit-1], [cut_wn_labels[0],
                                 cut_wn_labels[wn_limit-1]])
    # Draw the line plot
    ax.plot(np.arange(len(cut_wn_labels)), cut_wn_occs, "-", color="black")

    ax.set_ylim(bottom=0)
    ax.set_xlim(left=0)
    ax.set_ylim([0, sorted_no_zeros[0] + sorted_no_zeros[0] / 4])
    ax.set_yscale("log", basey=10)
    # plt.ticklabel_format(style='plain', axis='y')
    plt.xlabel(
        "WordNet Top 1000 Generated Passwords")
    plt.ylabel("Occurrences")
    plt.title("Top %d Reference List Passwords" % limit_val)
    blue_patch = mpatches.Patch(color="black", label="WordNet occurrences")
    red_patch = mpatches.Patch(
        color="gray", label=ref_list)
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
    res = mongo.db["wn_synsets_noun"].count()
    vals["n"]["total_synsets"] = res
    res = mongo.db["wn_synsets_verb"].count()
    vals["v"]["total_synsets"] = res
    res = mongo.db["wn_synsets_adjective"].count()
    vals["adj"]["total_synsets"] = res
    res = mongo.db["wn_synsets_adverb"].count()
    vals["adv"]["total_synsets"] = res

    # Total lemmas
    res = mongo.db["wn_lemma_permutations_noun"].count()
    vals["n"]["total_lemmas"] = res
    res = mongo.db["wn_lemma_permutations_verb"].count()
    vals["v"]["total_lemmas"] = res
    res = mongo.db["wn_lemma_permutations_adjective"].count()
    vals["adj"]["total_lemmas"] = res
    res = mongo.db["wn_lemma_permutations_adverb"].count()
    vals["adv"]["total_lemmas"] = res

    # Total permutations
    res = mongo.db["passwords_wn_noun"].count()
    vals["n"]["total_permutations"] = res
    res = mongo.db["passwords_wn_verb"].count()
    vals["v"]["total_permutations"] = res
    res = mongo.db["passwords_wn_adjective"].count()
    vals["adj"]["total_permutations"] = res
    res = mongo.db["passwords_wn_adverb"].count()
    vals["adv"]["total_permutations"] = res

    # Hits w/o permutations
    query_hits_no_perms = {
        "$and": [
            {"permutator": "no_permutator"},
            {"occurrences": {"$gt": 0}}
        ]
    }
    res = mongo.db["passwords_wn_noun"].find(query_hits_no_perms).count()
    vals["n"]["hits_no_perms"] = res
    res = mongo.db["passwords_wn_verb"].find(query_hits_no_perms).count()
    vals["v"]["hits_no_perms"] = res
    res = mongo.db["passwords_wn_adjective"].find(query_hits_no_perms).count()
    vals["adj"]["hits_no_perms"] = res
    res = mongo.db["passwords_wn_adverb"].find(query_hits_no_perms).count()
    vals["adv"]["hits_no_perms"] = res

    # Hits w/ permutations
    query_hits_with_perms = {
        "$and": [
            {"occurrences": {"$gt": 0}}
        ]
    }
    res = mongo.db["passwords_wn_noun"].find(query_hits_with_perms).count()
    vals["n"]["hits_with_perms"] = res
    res = mongo.db["passwords_wn_verb"].find(query_hits_with_perms).count()
    vals["v"]["hits_with_perms"] = res
    res = mongo.db["passwords_wn_adjective"].find(
        query_hits_with_perms).count()
    vals["adj"]["hits_with_perms"] = res
    res = mongo.db["passwords_wn_adverb"].find(query_hits_with_perms).count()
    vals["adv"]["hits_with_perms"] = res

    # Total occurrences w/o permutations
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

    # Total occurrences w/ permutations
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
