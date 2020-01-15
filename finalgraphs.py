import mongo
from helper import log_err, log_ok, log_status
import helper
import matplotlib.pyplot as plt
import numpy as np
from textwrap import wrap


# amount of passwords in the password database
pwned_pw_amount = 551509767


def main():
    # =============================================================================================================================================
    #
    #  Calculate average permutations per lemma
    #
    # avg = avg_permutations_lemma("wordnet_n")
    # log_ok("Average permutations per lemma for Wordnet nouns: %d" % (avg))
    # avg = avg_permutations_lemma("wordnet_v")
    # log_ok("Average permutations per lemma for Wordnet verbs: %d" % (avg))
    # avg = avg_permutations_lemma("wordnet_adj")
    # log_ok("Average permutations per lemma for Wordnet adjectives: %d" % (avg))
    # avg = avg_permutations_lemma("wordnet_adv")
    # log_ok("Average permutations per lemma for Wordnet adverbs: %d" % (avg))
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
    wordnet_coverage(include_perms=False)
    wordnet_coverage(include_perms=True)


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


def locate_topn_list_pws_wn(list_name):
    """
    Mark the top N passwords of a given list within the top N passwords of the wordnet.
    On the X axis, mark each 50th step.
    """
    top_n_wn = 1000
    pass


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


def calculate_performance(base):
    """
    The performance is the total sum of occurrences for a password source.
    """
    pass


def topn_passwords_hibp(n):
    """
    Return the top N passwords of the HIBP hash list (list must be sorted by prevalence).
    """
    pass


def wordnet_coverage(include_perms=False):
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

    plt.yscale("log", basey=10)

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


if __name__ == "__main__":
    main()
