from pymongo import MongoClient
from helper import get_curr_time, get_curr_time_str

# MONGO_ADDR = "192.168.56.102"
# MONGO_ADDR = "192.168.171.3"
# MONGO_ADDR = "localhost"
MONGO_ADDR = "141.87.21.180"
mongo = MongoClient("mongodb://{}:27017".format(MONGO_ADDR))

db = mongo["passwords"]
db_lists = db["lists"]

db_wn = db["wn_synsets_noun"]
db_wn_verb = db["wn_synsets_verb"]
db_wn_adjective = db["wn_synsets_adjective"]
db_wn_adverb = db["wn_synsets_adverb"]

db_pws_wn = db["passwords_wn_noun"]
db_pws_wn_verb = db["passwords_wn_verb"]
db_pws_wn_adjective = db["passwords_wn_adjective"]
db_pws_wn_adverb = db["passwords_wn_adverb"]
db_pws_lists = db["passwords_lists"]
db_pws_misc_lists = db["passwords_misc_lists"]
db_pws_dicts = db["passwords_dicts"]

db_wn_lemma_permutations = db["wn_lemma_permutations_noun"]
db_wn_lemma_permutations_verb = db["wn_lemma_permutations_verb"]
db_wn_lemma_permutations_adjective = db["wn_lemma_permutations_adjective"]
db_wn_lemma_permutations_adverb = db["wn_lemma_permutations_adverb"]


TAG = get_curr_time_str()


def store_tested_pass_lists(name, occurrences, source, word_base, permutator=""):
    """
    Save permutation to the "lists" collection
    """
    o = {
        "name": name,
        "occurrences": occurrences,
        "source": source,
        "word_base": word_base,
        "permutator": permutator,
        "tag": TAG
    }
    try:
        db_pws_lists.insert_one(o)
    except Exception:
        return False
    return True


def store_tested_pass_wn(name, occurrences, source, word_base, permutator=""):
    """
    Save permutation to the "wn" (WordNet) collection
    """
    o = {
        "name": name,
        "occurrences": occurrences,
        "synset": source,
        "word_base": word_base,
        "permutator": permutator,
        "tag": TAG
    }
    try:
        db_pws_wn.insert_one(o)
    except Exception:
        return False
    return True


def store_tested_pass_wn_verb(name, occurrences, source, word_base, permutator=""):
    """
    Save permutation to the "wn" (WordNet) collection
    """
    o = {
        "name": name,
        "occurrences": occurrences,
        "synset": source,
        "word_base": word_base,
        "permutator": permutator,
        "tag": TAG
    }
    try:
        db_pws_wn_verb.insert_one(o)
    except Exception:
        return False
    return True


def store_tested_pass_misc_list(collection_suffix, name, occurrences, source):
    """
    Store a misc list passwords.
    """
    o = {
        "name": name,
        "occurrences": occurrences,
        "source": source,
        "tag": TAG
    }

    try:
        db["passwords_misc_lists_%s" % collection_suffix].insert_one(o)
    except Exception:
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
        "total_hits": 0,
        "tag": TAG
    }
    try:
        db_lists.insert_one(o)
    except Exception:
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
    # Also increment the lists total hits by the number of occurrences of this lemma
    db_lists.update_one({"filename": wl}, {
                        "$inc": {"total_hits": occurrences}})


def purge_verb():
    """
    Drop all wordnet verb collections.
    """
    db_wn_verb.drop()
    db_pws_wn_verb.drop()
    db_wn_lemma_permutations_verb.drop()


def purge_adjective():
    """
    Drop all wordnet adjective collections.
    """
    db_wn_adjective.drop()
    db_pws_wn_adjective.drop()
    db_wn_lemma_permutations_adjective.drop()


def purge_adverb():
    """
    Drop all wordnet adverb collections.
    """
    db_wn_adverb.drop()
    db_pws_wn_adverb.drop()
    db_wn_lemma_permutations_adverb.drop()


def purge_noun():
    """
    Drop all wordnet noun collections.
    """
    db_wn.drop()
    db_pws_wn.drop()
    db_wn_lemma_permutations.drop()


def store_permutations_for_lemma(permutations):
    """
    For each lemma, store all of its permutations. The "permutations" key is basically a group of records in the passwords_wn_noun collection.
    """
    # In case it already exists
    if db_wn_lemma_permutations.count_documents({"word_base": permutations["word_base"]}) > 0:
        return
    db_wn_lemma_permutations.insert_one(permutations)
    # Replace with bulk insert. Should generally increase performance
    try:
        db_pws_wn.insert_many(permutations["permutations"])
    except Exception:
        return False
    return True





def store_permutations_for_lemma_verb(permutations):
    """
    For each lemma, store all of its permutations. The "permutations" key is basically a group of records in the passwords_wn_verb collection.
    """
   # In case it already exists
    if db_wn_lemma_permutations_verb.count_documents({"word_base": permutations["word_base"]}) > 0:
        return
    db_wn_lemma_permutations_verb.insert_one(permutations)
    # Replace with bulk insert. Should generally increase performance
    try:
        db_pws_wn_verb.insert_many(permutations["permutations"])
    except Exception:
        return False
    return True


def store_permutations_for_lemma_adjective(permutations):
    """
    For each lemma, store all of its permutations. The "permutations" key is basically a group of records in the passwords_wn_adjective collection.
    """
    # In case it already exists
    if db_wn_lemma_permutations_adjective.count_documents({"word_base": permutations["word_base"]}) > 0:
        return
    db_wn_lemma_permutations_adjective.insert_one(permutations)
    # Replace with bulk insert. Should generally increase performance
    try:
        db_pws_wn_adjective.insert_many(permutations["permutations"])
    except Exception:
        return False
    return True


def store_permutations_for_lemma_adverb(permutations):
    """
    For each lemma, store all of its permutations. The "permutations" key is basically a group of records in the passwords_wn_adverb collection.
    """
    # In case it already exists
    if db_wn_lemma_permutations_adverb.count_documents({"word_base": permutations["word_base"]}) > 0:
        return
    db_wn_lemma_permutations_adverb.insert_one(permutations)
    # Also store each separate permutation so we can search for the most popular permutations
    # for p in permutations["permutations"]:
    #     store_tested_pass_wn_verb(p["permutation"], p["occurrences"],
    #                               permutations["synset"], permutations["word_base"])
    # Replace with bulk insert. Should generally increase performance
    try:
        db_pws_wn_adverb.insert_many(permutations["permutations"])
    except Exception:
        return False
    return True


def store_synset_with_relatives(synset, parent="root"):
    """
    Stores a frame in wn_synsets_noun and determines this synsets children and immediate parent.
    """
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


def store_synset_with_relatives_verb(synset, parent="root"):
    """
    Stores a frame in wn_synsets_verb and determines this synsets children and immediate parent.
    """
    # Check if this synset already exists.
    if db_wn_verb.count_documents({"id": synset.name()}) > 0:
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
    db_wn_verb.insert_one(o)


def store_synset_with_relatives_adjective(synset, parent="root"):
    """
    Stores a frame in wn_synsets_adjective and determines this synsets children and immediate parent.
    """
    # Check if this synset already exists.
    if db_wn_adjective.count_documents({"id": synset.name()}) > 0:
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
    db_wn_adjective.insert_one(o)


def store_synset_with_relatives_adverb(synset, parent="root"):
    """
    Stores a frame in wn_synsets_adverb and determines this synsets children and immediate parent.
    """
    # Check if this synset already exists.
    if db_wn_adverb.count_documents({"id": synset.name()}) > 0:
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
    db_wn_adverb.insert_one(o)


def update_synset_with_stats(synset, hits_below, not_found_below, found_below, this_hits, this_found, this_not_found):
    """
    Update a synset in wn_synsets_noun with new values.
    """
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


def update_synset_with_stats_verb(synset, hits_below, not_found_below, found_below, this_hits, this_found, this_not_found):
    """
    Update a synset in wn_synsets_verb with new values.
    """
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
    db_wn_verb.update_one({"id": synset.name()}, {"$set": o})


def update_synset_with_stats_adjective(synset, hits_below, not_found_below, found_below, this_hits, this_found, this_not_found):
    """
    Update a synset in wn_synsets_adjective with new values.
    """
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
    db_wn_adjective.update_one({"id": synset.name()}, {"$set": o})


def update_synset_with_stats_adverb(synset, hits_below, not_found_below, found_below, this_hits, this_found, this_not_found):
    """
    Update a synset in wn_synsets_adverb with new values.
    """
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
    db_wn_adverb.update_one({"id": synset.name()}, {"$set": o})


def add_values_to_existing_verb(id, total_hits, found, not_found):
    """
    Add/increment a verb with specific values.
    """
    db_wn_verb.update({"id": id}, {
        "$inc": {
            "hits_below": total_hits,
            "found_below": found,
            "not_found_below": not_found,
            # If the hits below were increased we also have to increase the value of total_hits (this_hits + below_hits)
            "total_hits": total_hits
        }
    })


def update_synset_noun_add_hits(synset_id, hits_below):
    """
    Update hits_below and total_hits of a noun.
    """
    # Get this_hits
    query_result = db_wn.find_one({"id": synset_id})
    this_hits = query_result["this_hits"]
    new_hits_below = hits_below
    new_total_hits = this_hits + new_hits_below
    # Update
    db_wn.update(
        {"id": synset_id},
        {"$set": {
            "hits_below": new_hits_below,
            "total_hits": new_total_hits
        }}
    )
    return this_hits, new_hits_below


def update_synset_noun_set_hits_below(synset_id, total_hits):
    """
    Update hits_below of a noun.
    """
    db_wn.update(
        {"id": synset_id},
        {"$set": {
            "hits_below": total_hits,
        }}
    )


def update_synset_hits(synset_id):
    """
    Update total_hits of a noun by its current this_hits and hits_below values.
    """
    # Get this_hits
    doc = db_wn.find_one({"id": synset_id})
    total_hits_old = doc["total_hits"]
    this_hits = doc["this_hits"]
    hits_below = doc["hits_below"]
    total_hits = this_hits + hits_below
    db_wn.update(
        {"id": synset_id},
        {"$set": {
            "total_hits": total_hits,
        }}
    )
    return total_hits, total_hits_old


def update_synset_this_hits(synset_id):
    """
    Update this_hits and hits_below based on total_hits of this synsets childs.
    """
    # Get this_hits
    doc = db_wn.find_one({"id": synset_id})
    hits_below_parent = 0
    for c in doc["childs"]:
        c_ss = db_wn.find_one({"id": c})
        hits_below_parent += c_ss["total_hits"]
    this_hits_old = doc["this_hits"]
    total_hits = doc["total_hits"]
    hits_below = doc["hits_below"]
    this_hits_new = total_hits - hits_below_parent
    db_wn.update(
        {"id": synset_id},
        {"$set": {
            "this_hits": this_hits_new,
            "hits_below": hits_below_parent,
            "total_hits": this_hits_new + hits_below_parent,
        }}
    )
    ret = {
        "this_hits_old": this_hits_old,
        "this_hits_new": this_hits_new,
        "hits_below_old": hits_below,
        "hits_below_new": hits_below_parent,
        "total_hits_old": total_hits,
        "total_hits_new": this_hits_new + hits_below_parent,
    }
    return ret


def update_synset_hits_verb(synset_id):
    """
    Update the total_hits of a verb based on its this_hits and total_hits values.
    """
    # Get this_hits
    doc = db_wn_verb.find_one({"id": synset_id})
    total_hits_old = doc["total_hits"]
    this_hits = doc["this_hits"]
    hits_below = doc["hits_below"]
    total_hits = this_hits + hits_below
    db_wn_verb.update(
        {"id": synset_id},
        {"$set": {
            "total_hits": total_hits,
        }}
    )
    return total_hits, total_hits_old


def subtract_from_hits_below(ssid, value):
    """
    Subtract value from hits_below of a noun.
    """
    db_wn.update(
        {"id": ssid},
        {
            "$inc": {
                "hits_below": -value
            }
        }
    )


def subtract_from_this_hits_verb(ssid, value):
    """
    Subtract value from this_hits of a verb.
    """
    db_wn_verb.update(
        {"id": ssid},
        {
            "$inc": {
                "this_hits": -value
            }
        }
    )


def subtract_from_hits_below_verb(ssid, value):
    """
    Subtract value from hits_below of a verb.
    """
    db_wn_verb.update(
        {"id": ssid},
        {
            "$inc": {
                "hits_below": -value
            }
        }
    )

# ================ TEST AREA ================

def store_permutations_for_lemma_noun_test(permutations):
    """
    For each lemma, store all of its permutations. The "permutations" key is basically a group of records in the passwords_wn_noun collection.
    """
    # In case it already exists
    if db["wn_lemma_permutations_noun_test"].count_documents({"word_base": permutations["word_base"]}) > 0:
        return
    db["wn_lemma_permutations_noun_test"].insert_one(permutations)
    # Replace with bulk insert. Should generally increase performance
    try:
        db["passwords_wn_noun_test"].insert_many(permutations["permutations"])
    except Exception:
        return False
    return True


def store_synset_without_relatives_noun_test(synset, depth, this_total_hits, this_not_found_cnt, this_found_cnt):
    """
    Stores a frame in wn_synsets_noun and determines this synsets children and immediate parent.
    """
    # Check if this synset already exists.
    if db["wn_synsets_noun_staging_test"].count_documents({"id": synset.name()}) > 0:
        return
    # get parent
    parents = synset.hypernyms()
    if synset.hypernyms() == []:
        parent = "no_parent"
    else:
        parent = parents[0].name()
    o = {
        "id": synset.name(),
        # we need to initialize total_hits with this_hits at first so when we come to the stage 
        # where we update our parents, it requires that we have our total_hits already set, so we can
        # set the hits_below value of our parents
        "total_hits": this_total_hits,
        "hits_below": 0,
        "not_found_below": 0,
        "found_below": 0,
        "below_permutations": 0,
        "this_hits": this_total_hits,
        "this_not_found_cnt": this_not_found_cnt,
        "this_found_cnt": this_found_cnt,
        "this_permutations": this_not_found_cnt + this_found_cnt,
        "level": depth,
        "parent": parent,
        # "childs": childs,
        "childs": [],
        # is set to 1 once copied from staging to prod collection 
        # (after parent/child linking was successful)
        "staging_to_prod": 0,
        "tag": TAG
    }
    db["wn_synsets_noun_staging_test"].insert_one(o)