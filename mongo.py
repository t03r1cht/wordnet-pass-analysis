from pymongo import MongoClient
from helper import get_curr_time, get_curr_time_str

mongo = MongoClient("mongodb://localhost:27017")
db = mongo["passwords"]
db_lists = db["lists"]
db_wn = db["wn_synsets"]
db_pws_wn = db["passwords_wn"]
db_wn_lemma_permutations = db["wn_lemma_permutations"]
db_pws_lists = db["passwords_lists"]

TAG = get_curr_time_str()


def store_tested_pass_lists(name, occurrences, source, word_base):
    """
    Save permutation to the "lists" collection
    """
    o = {
        "name": name,
        "occurrences": occurrences,
        "source": source,
        "word_base": word_base,
        "tag": TAG
    }
    try:
        db_pws_lists.insert_one(o)
    except Exception as e:
        return False
    return True


def store_tested_pass_wn(name, occurrences, source, word_base):
    """
    Save permutation to the "wn" (WordNet) collection
    """
    o = {
        "name": name,
        "occurrences": occurrences,
        "synset": source,
        "word_base": word_base,
        "tag": TAG
    }
    try:
        db_pws_wn.insert_one(o)
    except Exception as e:
        return False
    return True


def init_word_list_object(filename):
    """
    Create an initial object to store processed lemmas.
    """
    o = {
        "filename": filename,
        "created": get_curr_time(),
        "lemmas": [],
        "tag": TAG
    }
    try:
        db_lists.insert_one(o)
    except Exception as e:
        return False


def append_lemma_to_wl(lemma, occurrences, found_cnt, not_found_count, wl, tag="NOT_TAGGED"):
    """
    Insert a processed lemma to the "ill" collection. Checks if a lemma with the same name already exists.
    """
    # Check if the lemma already exists in the list
    if db_lists.count_documents({"filename": wl, "lemmas.name": lemma}) > 0:
        return
    o = {
        "name": lemma,
        "occurrences": occurrences,
        "total_cnt": found_cnt + not_found_count,
        "found_cnt": found_cnt,
        "not_found_cnt": not_found_count,
        "tag": TAG
    }
    db_lists.update_one({"filename": wl}, {"$push": {"lemmas": o}})


def clear_mongo():
    db_lists.remove({})
    db_pws_wn.remove({})
    db_pws_lists.remove({})
    db_wn.remove({})
    db_wn_lemma_permutations.remove({})


def store_permutations_for_lemma(permutations):
    # In case it already exists
    if db_wn_lemma_permutations.count_documents({"word_base": permutations["word_base"]}) > 0:
        return
    db_wn_lemma_permutations.insert_one(permutations)
    # Also store each separate permutation so we can search for the most popular permutations
    for p in permutations["permutations"]:
        store_tested_pass_wn(p["permutation"], p["occurrences"],
                             permutations["synset"], permutations["word_base"])


def new_permutation_for_lemma(permutation, occurrences):
    o = {
        "permutation": permutation,
        "occurrences": occurrences,
        "tag": TAG
    }
    return o


def store_synset_with_relatives(synset, parent="root"):
    # Check if this synset already exists.
    if db_wn.count_documents({"id": synset.name()}) > 0:
        return

    childs = []
    for child in synset.hyponyms():
        childs.append(child.name())
    o = {
        "id": synset.name(),
        "level": synset.min_depth(),
        "parent": parent,
        "childs": childs,
        "tag": TAG
    }
    db_wn.insert_one(o)


def update_synset_with_stats(synset, hits_below, not_found_below, found_below, this_hits, this_found, this_not_found):
    o = {
        "total_hits": this_hits + hits_below,
        "hits_below": hits_below,
        "this_hits": this_hits,
        "not_found_below": not_found_below,
        "found_below": found_below,
        "this_found_cnt": this_found,
        "this_not_found_cnt": this_not_found,
        "this_permutations": this_found + this_not_found,
        "below_permutations": found_below + not_found_below,
        "tag": TAG
    }
    db_wn.update_one({"id": synset.name()}, {"$set": o})
