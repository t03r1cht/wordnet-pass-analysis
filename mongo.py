from pymongo import MongoClient
from helper import get_curr_time

mongo = MongoClient("mongodb://localhost:27017")
db = mongo["passwords"]
db_ill = db["ill"]
db_pws_wn = db["passwords_wn"]
db_pws_lists = db["passwords_lists"]


def store_tested_pass_lists(name, occurrences):
    """
    Save permutation to the "lists" collection
    """
    o = {
        "name": name,
        "occurrences": occurrences
    }
    try:
        db_pws_lists.insert_one(o)
    except Exception as e:
        return False
    return True


def store_tested_pass_wn(name, occurrences):
    """
    Save permutation to the "wn" (WordNet) collection
    """
    o = {
        "name": name,
        "occurrences": occurrences
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
