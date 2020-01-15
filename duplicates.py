from nltk.corpus import wordnet as wn
import mongo
import sys
from helper import format_number

dups_map = {}
first_occurrence_dups = []
ignore_dups = {}
total_subtractions = 0


def main():
    if eval_arg(sys.argv[1], "update"):
        if eval_arg(sys.argv[2], "noun"):
            if eval_arg(sys.argv[3], "by_lemmas"):
                update_by_lemmas_noun()
            elif eval_arg(sys.argv[3], "by_hits"):
                update_by_hits_noun()
            elif eval_arg(sys.argv[3], "root_ss"):
                update_by_root_ss()
            else:
                print("Unknown argument for <update> <noun>")
        elif eval_arg(sys.argv[2], "verb"):
            if eval_arg(sys.argv[3], "by_lemmas"):
                update_by_lemmas_verb()
            elif eval_arg(sys.argv[3], "by_hits"):
                update_by_hits_verb()
        else:
            pass
    elif eval_arg(sys.argv[1], "duplicates"):
        if eval_arg(sys.argv[2], "noun"):
            sum_without_dups("noun")
        if eval_arg(sys.argv[2], "verb"):
            sum_without_dups("verb")
    else:
        print("Unknown argument")
    return
    # nohup nice -n -20 python3 main.py -p $PW_LIST -s "entity" -d 100 -t --wn-type="n" &
    # init_first_occurrences_dups() must be called before init_ignore_dups(), since init_ignore_dups() creates the "inverse" list to init_first_occurrences_dups()
    init_first_occurrences_dups()
    init_ignore_dups()
    # For each password, check if this password is in the list of keys of the above dict. If it is, we know our password permutation is a duplicate
    # We then check if the password we are looking is the lowest duplicate in the wordnet
    # if password.synset == map[password_perm]["synset"]: add the occurrences of this password to the total sum, else: continue (dont add, because we already have it added somewhere below)

    # Determine the lowest level we can start from
    # We will start at the bottom and work our way up to the root synset
    all_levels = mongo.db_wn.distinct("level")
    lowest_level = max(all_levels)
    """
    Problem
    die summen von unten nach oben stimmen noch nicht. wenn man die summen der total_hits der schichten
    n-1 addiert ergeben diese eine andere summe als der wert hits_below der schicht n
    """
    # 1.
    # for i in reversed(range(lowest_level+1)):
    #     fix_this_hits(i)

    # 2.
    # for i in reversed(range(lowest_level+1)):
    #     update_hits(i)
    # return

    # 3.
    # for i in reversed(range((lowest_level+1))):
    #     sum_with_dups(i)

    # total_hits = 0
    # total_iters = 0
    # for i in reversed(range((lowest_level+1))):
    #     hits, iters = sum_all(i)
    #     total_hits += hits
    #     total_iters += iters
    #     print("Hits for level {}: {} (with {} synsets)".format(i, hits, iters))

    # print()
    # print()
    # print("Total hits:", total_hits)
    # print("Total iters:", total_iters)

    for i in reversed(range((lowest_level+1))):
        sum_without_dups_noun(i)
    # print("Total subtractions:", total_subtractions)


def eval_arg(arg, s):
    """
    Argument evaluation. Only for visual separation. Nothing special here.
    """
    return arg == s


def get_lowest_level_wn(mode):
    """
    Get the current lowest level in the wordnet tree.
    "mode" defines from which part of speech the lowest level should be returned from.
    """
    if mode not in ["noun", "verb"]:
        print("init_first_occurrences_dups(): invalid mode:", mode)
        return
    coll_table = {
        "noun": "wn_synsets_noun",
        "verb": "wn_synsets_verb",
    }
    coll_name = coll_table[mode]

    all_levels = mongo.db[coll_name].distinct("level")
    lowest_level = max(all_levels)
    return lowest_level


def update_by_lemmas_noun():
    """
    Wrapper
    """
    lowest_level = get_lowest_level_wn("noun")
    for i in reversed(range(lowest_level+1)):
        fix_this_hits_noun(i)


def update_by_root_ss():
    """
    Due to the nature of the duplicate removal code, the this_hits value for the root synset
    never gets update. Therefore, we have to manually call it. It computes the this_hits
    value based on its hits_below and total_hits value.
    """
    res = mongo.update_synset_this_hits("entity.n.01")
    print("Updated: %s -> %s" %
          (format_number(res["this_hits_old"]), format_number(res["this_hits_new"])))
    print("Updated: %s -> %s" %
          (format_number(res["hits_below_old"]), format_number(res["hits_below_new"])))
    print("Updated: %s -> %s" %
          (format_number(res["total_hits_old"]), format_number(res["total_hits_new"])))


def update_by_lemmas_verb():
    """
    Wrapper
    """
    lowest_level = get_lowest_level_wn("verb")
    for i in reversed(range(lowest_level+1)):
        fix_this_hits_verb(i)


def update_by_hits_noun():
    """
    Wrapper
    """
    lowest_level = get_lowest_level_wn("noun")
    for i in reversed(range(lowest_level+1)):
        update_hits_noun(i)


def update_by_hits_verb():
    """
    Wrapper
    """
    lowest_level = get_lowest_level_wn("verb")
    for i in reversed(range(lowest_level+1)):
        update_hits_verb(i)


def fix_this_hits_noun(level):
    """
    Update total_hits value for all noun synsets using the sum of hits from wn_lemma_permutations
    """
    # This is the new this_hits value for the synsets in wn_synsets_noun
    query_set = mongo.db_wn.find({"level": level})
    for s in query_set:
        this_hits_synset = 0
        lemma_query = mongo.db_wn_lemma_permutations.find({"synset": s["id"]})
        for l in lemma_query:
            for perms in l["permutations"]:
                this_hits_synset += perms["occurrences"]
        print(s["id"], this_hits_synset)
        mongo.db_wn.update(
            {"id": s["id"]},
            {
                "$set": {
                    "this_hits": this_hits_synset
                }
            }
        )


def fix_this_hits_verb(level):
    """
    Update total_hits value for all verb synsets using the sum of hits from wn_lemma_permutations
    """
    # This is the new this_hits value for the synsets in wn_synsets_noun
    query_set = mongo.db_wn_verb.find({"level": level})
    for s in query_set:
        this_hits_synset = 0
        lemma_query = mongo.db_wn_lemma_permutations_verb.find(
            {"synset": s["id"]})
        for l in lemma_query:
            for perms in l["permutations"]:
                this_hits_synset += perms["occurrences"]
        print(s["id"], this_hits_synset)
        mongo.db_wn_verb.update(
            {"id": s["id"]},
            {
                "$set": {
                    "this_hits": this_hits_synset
                }
            }
        )


def update_hits_noun(level):
    """
    Update total_hits value for all noun synsets using this_hits and hits_below
    """
    query_set = mongo.db_wn.find({"level": level})
    for s in query_set:
        mongo.update_synset_hits(s["id"])


def update_hits_verb(level):
    """
    Update total_hits value for all verb synsets using this_hits and hits_below
    """
    query_set = mongo.db_wn_verb.find({"level": level})
    for s in query_set:
        mongo.update_synset_hits_verb(s["id"])


def sum_all(level):
    """
    Sum the this_hits values for nouns per level.
    """
    total_hits = 0
    i = 0
    query_set = mongo.db_wn.find({"level": level})
    for s in query_set:
        total_hits += s["this_hits"]
        i += 1
    return total_hits, i


def sum_with_dups(sum_level):
    """
    Sum total_hits starting from the lowest level up to the root node
    Note: Duplicates are not removed.
    """
    # Start at level sum_level and group by parents
    curr_level_synset_parent_groups = mongo.db_wn.aggregate([
        {"$match": {"level": sum_level}},  # filter by lowest level
        {"$group": {
            "_id": "$parent",  # group by the parent synsets
            "sum_total_hits": {
                "$sum": "$total_hits"
            },
            "sum_this_hits": {
                "$sum": "$this_hits"
            },
            "sum_hits_below": {
                "$sum": "$hits_below"
            },
            "childs": {
                "$push": {
                    "synset": "$id",
                    "this_hits": "$this_hits",
                    "hits_below": "$hits_below",
                    "total_hits": "$total_hits"
                }
            }
        }}
    ])
    # For each group, retrieve this_hits and hits_below for each synset and sum
    for item in curr_level_synset_parent_groups:
        sum_total_hits = item["sum_total_hits"]
        sum_this_hits = item["sum_this_hits"]
        sum_hits_below = item["sum_hits_below"]
        # Write total_hits to parent(hits_below)
        mongo.update_synset_noun_set_hits_below(item["_id"], sum_total_hits)
        print("Updated synset {}: set hits_below={}".format(
            item["_id"], sum_total_hits))
        # Update synsets of the current level in case their hits_below values were changed from lower levels in a previous iteration
        for c in item["childs"]:
            total_hits_new, total_hits_old = mongo.update_synset_hits(
                c["synset"])


def sum_without_dups(mode):
    """
    Wrapper
    """
    lowest_level = get_lowest_level_wn(mode)
    init_first_occurrences_dups(mode)
    init_ignore_dups(mode)
    for i in reversed(range((lowest_level+1))):
        if mode == "noun":
            sum_without_dups_noun(i)
        elif mode == "verb":
            sum_without_dups_verb(i)
        else:
            print("sum_without_dups(): invalid mode:", mode)
            return


def sum_without_dups_noun(sum_level):
    """
    Sum the total_hits for the noun wordnet tree bottom-up. Duplicates are ignore in the way that only
    the first occurrence of a duplicate is included in the total sum. All further duplicates (so at a lower level, since we are working bottom-up),
    will be ignored in the sum.
    
    We approach some kind of inverted method here. The sums have already been computed when we looked the passwords up. However, duplicates were not considered in that process.
    So what we are supposed to do now is identify duplicates (and the synsets that generated them) and subtract the duplicate's hits that were erroneously added the value of the total sum.
    Important note: It is not enough to only subtract the hits values from the directly attached parent synset (hypernym). The subtractions propagate from a level all the way to the top.
    Suppose we have to subtract the value 25 at level 5. This means we have to subtract the same value not only on level 5 but all the way to level 0, since a synset on level N always contains
    a hits_below value, which subsumes the hit values from all of its (in)directly attached children nodes.
    """
    # Has internal hierarchy
    # Return all synsets of the specified level but grouped by their parents. For each parent group, we store the total hits sum of this parent synsets children as well as the IDs of the children
    # text _id: Parent
    # int sum: Hits sum of all child synsets of parent
    # list childs: ID of the child synsets
    lowest_level_grps = mongo.db_wn.aggregate([
        {"$match": {"level": sum_level}},  # filter by lowest level
        {"$group": {
            "_id": "$parent",  # group by the parent synsets
            "sum": {
                # sum the hits of only the current synsets (including lemmas), disregarding possible hits below this synset
                # "$sum": "$this_hits"
                "$sum": "$total_hits"
            },
            "childs": {
                "$push": {
                    "synset": "$id"
                }
            }
        }}
    ])

    global total_subtractions
    for item in lowest_level_grps:
        total_hits = item["sum"]
        total_hits_old = total_hits
        orig_sum = total_hits
        # print(
        #     "Checking for child-password-duplicates for parent '{}'".format(item["_id"]))
        for synset in item["childs"]:
            synset_id = synset["synset"]
            # This synset contains duplicates, however these duplicates are the first occuring ones in the Wordnet, so we add them to the total_hits
            if synset_id in first_occurrence_dups:
                pass
            # This synset contains duplicates and these duplicates are not the first occuring ones. This means we need to subtract the hits for the
            # duplicate passwords from total_hits (they already occurred somewhen earlier, in that case the above case evaluated to true)
            elif synset_id in ignore_dups.keys():
                subtracts = ignore_dups[synset_id]
                # A synset may contain more than one duplicate
                # [(pw, 100), (pw2, 200)]
                sub_sum = 0
                for sub in subtracts:
                    # Add the total subtractions
                    # Propagate total subtractions from this synsets parents up to the root synset and update
                    # the hit values for each synset we subtracted from
                    sub_sum += sub[1]
                    start_parent_synset = item["_id"]
                    print(
                        "Propagating changes to hits to synsets on the parent root path... (-%s)" % (format_number(sub_sum)))
                    propagate_noun(sub_sum, start_parent_synset)
                    continue
            else:
                pass
        # If we finished identifying the duplicates, we need to update the parent synset with the according numbers
        # hits_below = this.total_hits
        # total_hits = hits_below + this.total_hits
        # cd ~/dump && mongorestore --drop


def sum_without_dups_verb(sum_level):
    """
    Sum the total_hits for the noun wordnet tree bottom-up. Duplicates are ignore in the way that only
    the first occurrence of a duplicate is included in the total sum. All further duplicates (so at a lower level, since we are working bottom-up),
    will be ignored in the sum.
    
    We approach some kind of inverted method here. The sums have already been computed when we looked the passwords up. However, duplicates were not considered in that process.
    So what we are supposed to do now is identify duplicates (and the synsets that generated them) and subtract the duplicate's hits that were erroneously added the value of the total sum.
    Important note: It is not enough to only subtract the hits values from the directly attached parent synset (hypernym). The subtractions propagate from a level all the way to the top.
    Suppose we have to subtract the value 25 at level 5. This means we have to subtract the same value not only on level 5 but all the way to level 0, since a synset on level N always contains
    a hits_below value, which subsumes the hit values from all of its (in)directly attached children nodes.
    """
    # Has internal hierarchy
    # Return all synsets of the specified level but grouped by their parents. For each parent group, we store the total hits sum of this parent synsets children as well as the IDs of the children
    # text _id: Parent
    # int sum: Hits sum of all child synsets of parent
    # list childs: ID of the child synsets
    lowest_level_grps = mongo.db_wn_verb.aggregate([
        {"$match": {"level": sum_level}},  # filter by lowest level
        {"$group": {
            "_id": "$parent",  # group by the parent synsets
            "sum": {
                # sum the hits of only the current synsets (including lemmas), disregarding possible hits below this synset
                # "$sum": "$this_hits"
                "$sum": "$total_hits"
            },
            "childs": {
                "$push": {
                    "synset": "$id"
                }
            }
        }}
    ])

    global total_subtractions
    for item in lowest_level_grps:
        if not item["_id"] == "root":
            pass
        else:
            # If we reached the end (tree top), we branch into this code
            print("Reached the top (level 0), will now subtract from the root nodes...")
            for c in item["childs"]:
                sid = c["synset"]
                # If the synset ID is found in the dictionary, we subtract the duplicate hits from the current
                # synset. Since we are at the top, we don't need to propagate the changes
                if sid in ignore_dups.keys():
                    print("Not first occurrence. Subtracting from current synset:", sid)
                    # Sum all the values, so we can save some database accesses and increase performance, even if
                    # by just a little
                    total_dups = 0
                    for d in ignore_dups[sid]:
                        print("\t", d)
                        total_dups += d[1]
                    print("\ttotal:", total_dups)
                    # Subtract
                    mongo.subtract_from_this_hits_verb(sid, total_dups)
                    # We need to update total_hits since we have modified this_hits
                    total_hits_c, total_hits_old_c = mongo.update_synset_hits_verb(
                        sid)
                    print("\t\tUpdate:", total_hits_old_c, " -> ", total_hits_c)
                else:
                    continue
            print("Finished!")
            return

        total_hits = item["sum"]
        total_hits_old = total_hits
        orig_sum = total_hits
        for synset in item["childs"]:
            synset_id = synset["synset"]
            # This synset contains duplicates, however these duplicates are the first occuring ones in the Wordnet, so we add them to the total_hits
            if synset_id in first_occurrence_dups:
                pass
            # This synset contains duplicates and these duplicates are not the first occuring ones. This means we need to subtract the hits for the
            # duplicate passwords from total_hits (they already occurred somewhen earlier, in that case the above case evaluated to true)
            elif synset_id in ignore_dups.keys():
                subtracts = ignore_dups[synset_id]
                # A synset may contain more than one duplicate
                # [(pw, 100), (pw2, 200)]
                sub_sum = 0
                for sub in subtracts:
                    # Add the total subtractions
                    # Propagate total subtractions from this synsets parents up to the root synset and update
                    # the hit values for each synset we subtracted from
                    sub_sum += sub[1]
                    start_parent_synset = item["_id"]
                    print(
                        "Propagating changes to hits to synsets on the parent root path... (-%s)" % (format_number(sub_sum)))
                    print(start_parent_synset)
                    continue
                    propagate_verb(sub_sum, start_parent_synset)
                    continue
            else:  # Synset contains no duplicates, hence, no action
                pass


def propagate_noun(subtractions_total, start_parent):
    """
    Subtract subtractions_total from each synset starting at start_parent from its hits_below value
    Do this until and including the root synset (entity.n.01)
    """
    # Get hypernym paths
    hp = wn.synset(start_parent).hypernym_paths()
    # Shortest hypernym path sp
    sp_idx = 0
    sp = hp[sp_idx]
    for i, v in enumerate(hp):
        if len(v) < len(sp):
            sp_idx = i
            sp = hp[sp_idx]
    # Remove the current object from the list (the current synset id is the last item in the list)
    del(sp[-1])
    # For each item (synset ID) in sp, do the following
    print("Root path for {}: {}".format(
        start_parent, list(reversed([x.name() for x in sp]))))
    for ssid in reversed(sp):
        # 1. Subtract subtractions_total from hits_below ($inc -subtractions_total)
        mongo.subtract_from_hits_below(ssid.name(), subtractions_total)
        # 2. Update total_hits (total_hits = hits_below + this_hits)
        total_hits, total_hits_old = mongo.update_synset_hits(ssid.name())
        print("\tUpdated {} total_hits: {} -> {}".format(ssid,
                                                         total_hits_old, total_hits))
    print()
    # mongorestore --db mydbname --collection mycollection dump/mydbname/mycollection.bson


def propagate_verb(subtractions_total, start_parent):
    """
    Subtract subtractions_total from each synset starting at start_parent from its hits_below value
    Do this until and including the root synset (entity.n.01)
    """
    # Get hypernym paths
    # If our parent is "root" that means we are a synset on level 0. In this case, there is no path
    # we can propagate the changes to. Hence we only need to subtract the duplicate hits from ourself
    if start_parent == "root":
        print("Reached root - nothing to propagate further. Subtracting from myself...")
        mongo.subtract_from_hits_below_verb()
        return
    hp = wn.synset(start_parent).hypernym_paths()
    # Shortest hypernym path sp
    sp_idx = 0
    sp = hp[sp_idx]
    for i, v in enumerate(hp):
        if len(v) < len(sp):
            sp_idx = i
            sp = hp[sp_idx]
    # Remove the current object from the list (the current synset id is the last item in the list)
    del(sp[-1])
    # For each item (synset ID) in sp, do the following
    print("Root path for {}: {}".format(
        start_parent, list(reversed([x.name() for x in sp]))))
    for ssid in reversed(sp):
        # 1. Subtract subtractions_total from hits_below ($inc -subtractions_total)
        mongo.subtract_from_hits_below_verb(ssid.name(), subtractions_total)
        # 2. Update total_hits (total_hits = hits_below + this_hits)
        total_hits, total_hits_old = mongo.update_synset_hits_verb(ssid.name())
        print("\tUpdated {} total_hits: {} -> {}".format(ssid,
                                                         total_hits_old, total_hits))
    print()


def init_first_occurrences_dups(mode):
    """
    Create a list containing the IDs of synsets containing first occurrences of a password.
    "First" meaning the lowest duplicate in the tree, since our iterations begins from the bottom and not from the top.
    We use this dictionary to check whether a synset we are currently processing contains a duplicate password. If the synset_id is found in this
    dictionary, the synset contains a duplicate and is the first occurrence of exactly this duplicate password. Therefore, we allow the number of 
    its occurrences to be added to the this_hits value. This in turn means, we take no further action, since its hits were already added to the total
    sum when it was looked up/generated from permutation. However, if it is a duplicate that is not the first one to occur in our bottom-up iteration,
    we explicitly subtract its hits from the this_hits of the current synset as well as propagate the changes to the root path. The updated hits value
    of the current synset (in)directly affects the hits_below and total_hits value of its hypernyms. Therefore, we need to iterate over the root path
    starting from this synset and subtract its number of hits from the hits_below and total_hits values of its hypernyms.
    """
    if mode not in ["noun", "verb"]:
        print("init_first_occurrences_dups(): invalid mode:", mode)
        return
    coll_table = {
        "noun": "passwords_wn_noun",
        "verb": "passwords_wn_verb",
    }
    coll_name = coll_table[mode]
    dup_query = mongo.db[coll_name].aggregate([
        {
            "$match": {
                "occurrences": {"$gt": 0}
            }
        },
        {
            "$group": {
                "_id": "$name",
                "sum": {
                    "$sum": 1
                },
                "results": {
                    "$push": {
                        "name": "$name",
                        "occurrences": "$occurrences",
                        "word_base": "$word_base",
                        "synset": "$synset",
                        "level": "$depth",
                    }
                }
            }
        },
        {
            "$match": {
                "sum": {"$gt": 1}
            }
        },
        {
            "$sort": {"sum": -1}
        }
    ], allowDiskUse=True)

    for dup in dup_query:
        # Initialize with the first object
        idx = 0
        min_depth = dup["results"][0]["level"]
        # From the set of found duplicates, we want to find the duplicate the lowest in the tree
        for index, value in enumerate(dup["results"]):
            # > means lower in the tree (tree levels go from 0..n)
            if value["level"] > min_depth:
                min_depth = value["level"]
                idx = index
        synset_id = dup["results"][idx]["synset"]
        if synset_id in first_occurrence_dups:
            pass
        else:
            first_occurrence_dups.append(synset_id)

    print("First Occurrences Duplicate list created. Length: %d items" %
          len(first_occurrence_dups))


def init_ignore_dups(mode):
    """
    This function produces a dictionary in the same manner as init_first_occurrences_dups(), however, it is the inverse of this dictionary. It contains all
    duplicate passwords that are not the first occurrences in the wordnet tree as well as their number of hits.
    Mapping: [key] -> [(pw1,100),(pw2,245),...]
    """
    if mode not in ["noun", "verb"]:
        print("init_first_occurrences_dups(): invalid mode:", mode)
        return
    coll_table = {
        "noun": "passwords_wn_noun",
        "verb": "passwords_wn_verb",
    }
    coll_name = coll_table[mode]
    dup_query = mongo.db[coll_name].aggregate([
        {
            "$match": {
                "occurrences": {"$gt": 0}
            }
        },
        {
            "$group": {
                "_id": "$name",
                "sum": {
                    "$sum": 1
                },
                "results": {
                    "$push": {
                        "name": "$name",
                        "occurrences": "$occurrences",
                        "word_base": "$word_base",
                        "synset": "$synset",
                        "level": "$depth",
                    }
                }
            }
        },
        {
            "$match": {
                "sum": {"$gt": 1}
            }
        },
        {
            "$sort": {"sum": -1}
        }
    ], allowDiskUse=True)

    for dup in dup_query:
        for dup_result in dup["results"]:
            o = []
            synset = dup_result["synset"]
            # If this synset is already known to the first_occurrence_dups list we must not append it to this map
            if synset in first_occurrence_dups:
                continue
            # Check if there are already duplicates registered to the current synset (one synset might produce multiple duplicates)
            if synset in ignore_dups.keys():  # We append the current duplicate to the existing list
                ignore_dups[synset].append(
                    (dup_result["name"], dup_result["occurrences"], dup_result["synset"]))
            else:  # Create a new list under the key of the synset of the current duplicate
                ignore_dups[synset] = [
                    (dup_result["name"], dup_result["occurrences"], dup_result["synset"])]

    print("Ignore Duplicate list created. Length: %d items" %
          len(ignore_dups.items()))


if __name__ == "__main__":
    main()
    # MongoDB Find duplicates: db.getCollection('passwords_wn_noun').aggregate([{"$match": {"occurrences": {"$gt": 0}}}, {"$group": {_id: "$name", sum: {"$sum": 1}}}, {"$match": {"sum": {"$gt": 1}}}, {"$sort": {"sum": -1}}], { allowDiskUse: true })
    # MongoDB Count number of duplicates: db.getCollection('passwords_wn_noun').aggregate([{"$match": {"occurrences": {"$gt": 0}}}, {"$group": {_id: "$name", sum: {"$sum": 1}}}, {"$match": {"sum": {"$gt": 1}}}, {"$sort": {"sum": -1}}, {"$group": {_id: null, count: {"$sum": 1}}}], { allowDiskUse: true })
    # MongoDB Show clustered duplicates with synset origin: db.getCollection('passwords_wn_noun').aggregate([ { "$match": { "occurrences": { "$gt": 0 } } }, { "$group": { "_id": "$name", "sum": { "$sum": 1 }, "results": { "$push": { "name": "$name", "occurrences": "$occurrences", "word_base": "$word_base", "synset": "$synset", "level": "$depth", "permutator": "$permutator" } } } }, { "$match": { "sum": { "$gt": 1 } } }, { "$sort": { "sum": -1 } } ], {"allowDiskUse": true})