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

# Rausfiltern von arabischen Zahlen (0-99)
# db.getCollection('passwords_wn_noun').find({"$and": [{"permutator": "no_permutator"},{"word_base": {"$nin": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "11"]}}, {"occurrences": {"$gt":0}}]}).count()
# amount of passwords in the password database
pwned_pw_amount = 551509767


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
    # locate_topn_list_pws_hibp("12_tech_brands.txt", top=10, include_perms=False)
    # locate_topn_list_pws_hibp("12_tech_brands.txt", top=20, include_perms=True)
    # =============================================================================================================================================
    #
    # Print a list with the top n passwords of the wordnet (with and without permutations)
    #
    # print_top_lemmas("n", 20, include_perms=False)
    # print()
    # print()
    # print_top_lemmas("n", 20, include_perms=True)
    # =============================================================================================================================================
    #
    # Print top n synsets for each level
    #
    top_classes_per_level("noun", 10)
    # top_classes_per_level("verb", 10)
    # =============================================================================================================================================
    #
    # Locate the top n passwords from a category list on the top n passwords of the Wordnet
    #
    # locate_topn_list_pws_wn("12_tech_brands.txt", top=20, include_perms=False)
    # locate_topn_list_pws_wn("12_tech_brands.txt", top=20, include_perms=True)


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

    plt.xticks(ind, sorted_l, rotation=45, fontsize=7)
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
    for item in mongo.db_pws_lists.find(query).sort("occurrences", pymongo.DESCENDING).limit(top):
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
                    xytext=(0*3, 3),  # use 3 points offset
                    textcoords="offset points",  # in both directions
                    rotation=90,
                    fontsize="x-small",
                    ha="center", va='bottom')
        i += 1

    # Draw the line plot
    ax.plot(np.arange(len(hibp_labels)), hibp_occs, "-", color="black")

    ax.set_ylim(bottom=0)
    ax.set_xlim(left=0)
    ax.set_ylim([0, sorted_no_zeros[0] + sorted_no_zeros[0] / 4])
    ax.set_yscale("log", basey=10)
    plt.xlabel(
        "Top 10 HaveIBeenPwned Passwords")
    plt.ylabel("Occurrences")
    plt.title("Top %d List Passwords" % top)
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
    top_with_buf = top * 2
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
        log_ok("(%d)     %s: %s" %
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
        log_ok("Top %d synset for level %d" % (top, i))
        for k, v in enumerate(query_result):
            log_ok("%d - %s: %s" %
                   (k+1, v["id"], helper.format_number(v["total_hits"])))
        log_ok("")


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

    for i in pw_list:
        print(i)
    return

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

    for password in mongo.db_pws_wn.find(search_filter).sort("occurrences", pymongo.DESCENDING):
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


def locate_topn_list_pws_wnold(opts):
    """
    Deprecated
    """
    # Read the top wn_limit passwords generated from the WordNet
    wn_limit = 1000
    f, ax = plt.subplots(1)

    limit_val = 20
    # We can set the number of top passwords with the --top flag
    if opts["top"]:
        if opts["top"] > 100:
            log_err("--top value too high. Select Value between 5 and 100")
            return
        limit_val = opts["top"]
    else:
        limit_val = 10

    ref_list = None
    if opts["ref_list"] == None:
        log_err(
            "No ref list specified. Use the -l flag to specify a list to use for passwords")
        return
    # ref_list == "alL" looks at all lists and not a specific one
    ref_list = opts["ref_list"]

    # Get top n from some list
    if ref_list == "all":
        # we exclude the keyboard patterns txt file since it has a lot of duplicates with 99_unsortiert
        all_word_lists_list = mongo.db_lists.find(
            {"filename": {"$nin": ["03_keyboard_patterns.txt"]}})
        lemma_list = []
        for item in list(all_word_lists_list):
            lemma_list.extend(item["lemmas"])

        pw_list = []
        for item in lemma_list:
            o = {"name": item["name"], "occurrences": item["occurrences"]}
            pw_list.append(o)
    else:
        word_lists = mongo.db_lists.find_one({"filename": ref_list})
        pw_list = word_lists["lemmas"]

    # We now need to sort the dictionary by "occurrences" in descending order
    # Contains all word bases ("lemmas") for a given list plus its occurrences
    # Cut the sorted result list based on the --top flag. --top defaults to 10
    sorted_o = sorted(pw_list, key=lambda k: k["occurrences"], reverse=True)[
        :limit_val]

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

    for password in mongo.db_pws_wn.find(search_filter).sort("occurrences", pymongo.DESCENDING):
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

    cut_wn_labels = cleaned_list_labels[:1000]
    cut_wn_occs = cleaned_list_occs[:1000]

    # Create a list that has the wn values but they are just for orientation/comparison of occurrences. The values of the "original" list are not going to used
    # for bar plotting. Instead, they will be saved under a key, that is ignored when drawing the bar plot.
    new_occs_inserted = [{"orig": x, "list": -1} for x in cut_wn_occs]
    new_labels_inserted = [{"orig": x, "list": None} for x in cut_wn_labels]

    # Insert the sorted word list items at the right x coords
    idx_behind_last_wn = len(cut_wn_labels)
    xcoords_bar = []

    for item in sorted_o:
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


if __name__ == "__main__":
    main()
