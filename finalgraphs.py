import mongo
from helper import log_err, log_ok, log_status

# amount of passwords in the password database
pwned_pw_amount = 551509767

def main():
    #
    # Calculate average permutations per lemma
    # avg = avg_permutations_lemma("wordnet_n")
    # log_ok("Average permutations per lemma for Wordnet nouns: %d" % (avg))
    # avg = avg_permutations_lemma("wordnet_v")
    # log_ok("Average permutations per lemma for Wordnet verbs: %d" % (avg))
    # avg = avg_permutations_lemma("wordnet_adj")
    # log_ok("Average permutations per lemma for Wordnet adjectives: %d" % (avg))
    # avg = avg_permutations_lemma("wordnet_adv")
    # log_ok("Average permutations per lemma for Wordnet adverbs: %d" % (avg))
    #
    # Calculate the number of hits (efficiency) as well as the percentage of hits (coverage)
    pw_hits, pct_hits = calculate_efficiency("wordnet_n", include_perms=False)
    log_ok("Wordnet nouns (w/o permutations):\n\tPassword hits: {}\n\tPercentage hits: {}".format(pw_hits, pct_hits*100))
    pw_hits, pct_hits = calculate_efficiency("wordnet_n", include_perms=True)
    log_ok("Wordnet nouns (w/ permutations):\n\tPassword hits: {}\n\tPercentage hits: {}".format(pw_hits, pct_hits*100))

    pw_hits, pct_hits = calculate_efficiency("wordnet_v", include_perms=False)
    log_ok("Wordnet verbs (w/o permutations):\n\tPassword hits: {}\n\tPercentage hits: {}".format(pw_hits, pct_hits*100))
    pw_hits, pct_hits = calculate_efficiency("wordnet_v", include_perms=True)
    log_ok("Wordnet verbs (w/ permutations):\n\tPassword hits: {}\n\tPercentage hits: {}".format(pw_hits, pct_hits*100))

    pw_hits, pct_hits = calculate_efficiency("wordnet_adj", include_perms=False)
    log_ok("Wordnet adjectives (w/o permutations):\n\tPassword hits: {}\n\tPercentage hits: {}".format(pw_hits, pct_hits*100))
    pw_hits, pct_hits = calculate_efficiency("wordnet_adj", include_perms=True)
    log_ok("Wordnet adjectives (w/ permutations):\n\tPassword hits: {}\n\tPercentage hits: {}".format(pw_hits, pct_hits*100))

    pw_hits, pct_hits = calculate_efficiency("wordnet_adv", include_perms=False)
    log_ok("Wordnet adverbs (w/o permutations):\n\tPassword hits: {}\n\tPercentage hits: {}".format(pw_hits, pct_hits*100))
    pw_hits, pct_hits = calculate_efficiency("wordnet_adv", include_perms=True)
    log_ok("Wordnet adverbs (w/ permutations):\n\tPassword hits: {}\n\tPercentage hits: {}".format(pw_hits, pct_hits*100))

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
                {"occurrences": {"$gt":1}}
            ]
        }
    else:
        query = {
            "occurrences": {"$gt":1}
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

if __name__ == "__main__":
    main()