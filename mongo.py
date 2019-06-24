from pymongo import MongoClient
from helper import get_curr_time

mongo = MongoClient("mongodb://localhost:27017")
db = mongo["passwords"]
db_ill = db["ill"]
db_wn = db["wn_synsets"]
db_pws_wn = db["passwords_wn"]
db_pws_lists = db["passwords_lists"]


def store_tested_pass_lists(name, occurrences, source):
    """
    Save permutation to the "lists" collection
    """
    o = {
        "name": name,
        "occurrences": occurrences,
        "source": source
    }
    try:
        db_pws_lists.insert_one(o)
    except Exception as e:
        return False
    return True


def store_tested_pass_wn(name, occurrences, source):
    """
    Save permutation to the "wn" (WordNet) collection
    """
    o = {
        "name": name,
        "occurrences": occurrences,
        "source": source
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
        "lemmas": []
    }
    try:
        db_ill.insert_one(o)
    except Exception as e:
        return False


def append_lemma_to_wl(lemma, occurrences, found_cnt, not_found_count, wl, tag="NOT_TAGGED"):
    """
    Insert a processed lemma to the "ill" collection. Checks if a lemma with the same name already exists.
    """
    # Check if the lemma already exists in the list
    if db_ill.count_documents({"filename": wl, "lemmas.name": lemma}) > 0:
        return
    o = {
        "name": lemma,
        "occurrences": occurrences,
        "total_cnt": found_cnt + not_found_count,
        "found_cnt": found_cnt,
        "not_found_cnt": not_found_count,
        "tag": tag
    }
    db_ill.update_one({"filename": wl}, {"$push": {"lemmas": o}})


def clear_mongo():
    db_ill.remove({})
    db_pws_wn.remove({})
    db_pws_lists.remove({})
    db_wn.remove({})


def store_synset_with_relatives(synset, parent="root"):
    # TODO Check if this synset already exists.
    # If it does, check differences (same parent/childs? If not, update with the newest values)
    # if db_wn.count_documents({""})
    childs = []
    for child in synset.hyponyms():
        childs.append(child.name())
    o = {
        "id": synset.name(),
        "level": synset.min_depth(),
        "parent": parent,
        "childs": childs
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
    }
    db_wn.update_one({"id": synset.name()}, {"$set": o})
