from nltk.corpus import wordnet as wn
import mongo

dups_map = {}
first_occurrence_dups = []
ignore_dups = {}
total_subtractions = 0


def main():
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

    idee:
    rekursion ändern? summierung anders machen?
    BESSERE DEBUG NACHRICHTEN um alles nachvollziehen zu können
    """
    # 1.
    # for i in reversed(range(lowest_level+1)):
    #     fix_this_hits(i)

    # 2.
    # for i in reversed(range(lowest_level+1)):
    #     update_hits(i)

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
        sum_without_dups(i)
    # print("Total subtractions:", total_subtractions)


def fix_this_hits(level):
    # TODO
    # laufen lassen (setzt neue this_hits werte)
    # andere funktion (die this_hits werte addiert und zu parent(hits_below) schreibt)
    # werte erneut überprüfen

    # Iterate over all synsets
    # For each synset, lookup in wn_lemma_permutations, for all entries get the permutations.occurrences
    # values and add them together

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


def update_hits(level):
    query_set = mongo.db_wn.find({"level": level})
    for s in query_set:
        mongo.update_synset_hits(s["id"])


def sum_all(level):
    total_hits = 0
    i = 0
    query_set = mongo.db_wn.find({"level": level})
    for s in query_set:
        total_hits += s["this_hits"]
        i += 1
    return total_hits, i


def sum_with_dups(sum_level):
    # Sum all total hits starting from the lowest level up to the root node
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


def sum_without_dups(sum_level):
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
                    print("Propagating changes to hits to synsets on the parent root path...")
                    propagate(sub_sum, start_parent_synset)
                    continue                 
                    # total_hits -= sub[1]
                    # total_subtractions += sub[1]
            else:
                pass
        # If we finished identifying the duplicates, we need to update the parent synset with the according numbers
        # hits_below = this.total_hits
        # total_hits = hits_below + this.total_hits
        # cd ~/dump && mongorestore --drop
        # this_hits, hits_below = mongo.update_synset_noun_add_hits(
        #     item["_id"], total_hits)
        # print("Updated synset {}: sub -{} -> reason: duplicate {} (origin: {})".format(
        #     item["_id"],
        #     sub[1],
        #     sub[0],
        #     synset_id
        # ))

def propagate(subtractions_total, start_parent):
    """
    Subtract subtractions_total from each synset starting at start_parent from its hits_below value
    Do this until and including the root synset (entity.n.01)
    """
    # Get hypernym paths
    hp = wn.synset(start_parent).hypernym_paths()
    # Shortest hypernym path sp
    sp_idx = 0
    sp = hp[sp_idx]
    for i,v in enumerate(hp):
        if len(v) < len(sp):
            sp_idx = i
            sp = hp[sp_idx]
    # Remove the current object from the list (the current synset id is the last item in the list)
    del(sp[-1])
    # For each item (synset ID) in sp, do the following
    print("Root path for {}: {}".format(start_parent, list(reversed([x.name() for x in sp]))))
    for ssid in reversed(sp):
    # 1. Subtract subtractions_total from hits_below ($inc -subtractions_total)
        mongo.subtract_from_hits_below(ssid.name(), subtractions_total)
    # 2. Update total_hits (total_hits = hits_below + this_hits)
        total_hits, total_hits_old = mongo.update_synset_hits(ssid.name())
        print("\tUpdated {} total_hits: {} -> {}".format(ssid, total_hits_old, total_hits))
    print()

    # TODO Test
    # WordNet nouns neu durchlaufen lassen, combinators beschränken (vllt auf die ersten 3)
    # Test propagation with bigger data base
    # mongorestore --db mydbname --collection mycollection dump/mydbname/mycollection.bson


def initDupsMap():
    # Build a duplicate map
    # This map contains a list of known duplicates including the number of the lowest level one of the duplicates occurs in.
    # We imply that we subsume all the hits starting from the bottom of the WordNet all the way to the root node. This means, we do not allow any duplicates
    # under the root node (other than if we start subsuming from somewhere in the middle of the Wordnet. In that case, we don't care about duplicates possibly occurring in sibling sub-trees),
    # which means we do not allow any duplicates AT ALL.
    # MongoDB Find duplicates: db.getCollection('passwords_wn_noun').aggregate([{"$match": {"occurrences": {"$gt": 0}}}, {"$group": {_id: "$name", sum: {"$sum": 1}}}, {"$match": {"sum": {"$gt": 1}}}, {"$sort": {"sum": -1}}], { allowDiskUse: true })
    # MongoDB Count number of duplicates: db.getCollection('passwords_wn_noun').aggregate([{"$match": {"occurrences": {"$gt": 0}}}, {"$group": {_id: "$name", sum: {"$sum": 1}}}, {"$match": {"sum": {"$gt": 1}}}, {"$sort": {"sum": -1}}, {"$group": {_id: null, count: {"$sum": 1}}}], { allowDiskUse: true })
    # MongoDB Show clustered duplicates with synset origin: db.getCollection('passwords_wn_noun').aggregate([ { "$match": { "occurrences": { "$gt": 0 } } }, { "$group": { "_id": "$name", "sum": { "$sum": 1 }, "results": { "$push": { "name": "$name", "occurrences": "$occurrences", "word_base": "$word_base", "synset": "$synset", "level": "$depth", "permutator": "$permutator" } } } }, { "$match": { "sum": { "$gt": 1 } } }, { "$sort": { "sum": -1 } } ], {"allowDiskUse": true})
    dup_query = mongo.db_pws_wn.aggregate([
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
        o = {
            "name": "",
            "occurrences": 0,
            "synset": "",
            "level": 0,
        }
        # Initialize with the first object
        idx = 0
        min_depth = dup["results"][0]["level"]
        # From the set of found duplicates, we want to find the duplicate the lowest in the tree
        for index, value in enumerate(dup["results"]):
            # > means lower in the tree (tree levels go from 0..n)
            if value["level"] > min_depth:
                min_depth = value["level"]
                idx = index

        results = dup["results"]
        o["name"] = results[idx]["name"]
        o["occurrences"] = results[idx]["occurrences"]
        o["synset"] = results[idx]["synset"]
        o["level"] = results[idx]["level"]
        # Store in dict of dicts containing the lowest duplicates. The outer key for the dict is the password
        # permutation
        dups_map[o["name"]] = o

    print("Duplicate map created. Length: %d items" % len(dups_map.items()))


def init_first_occurrences_dups():
    dup_query = mongo.db_pws_wn.aggregate([
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
        o = {
            "name": "",
            "occurrences": 0,
            "synset": "",
            "level": 0,
        }
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


def init_ignore_dups():
    """
    The goal of this function is to cluster duplicates for all synsets
    """
    dup_query = mongo.db_pws_wn.aggregate([
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
            # If this synset is already know to the first_occurrence_dups list we must not append it to this map
            if synset in first_occurrence_dups:
                continue
            # Check if there are already duplicates registered to the current synset
            if synset in ignore_dups.keys():  # We append the current duplicate to the existing list
                ignore_dups[synset].append(
                    (dup_result["name"], dup_result["occurrences"]))
            else:  # Create a new list under the key of the synset of the current duplicate
                ignore_dups[synset] = [
                    (dup_result["name"], dup_result["occurrences"])]

    print("Ignore Duplicate list created. Length: %d items" %
          len(ignore_dups.items()))


def isDuplicate(password_perm, synset):
    """
    This function receives a password permutation and decides, whether the hits of the passed password can be added to the total sum.
    This happens by firstly checking if the password is found in the duplicate map dups_map. If it is found, we want to find out if the password
    is the lowest in the Wordnet tree. We do that by comparing the origin synset of the passed password with the synset associated with the actual lowest duplicate.
    If both are the same, we return true. That means, that we add the hits of the password to the total sum we are currently computing. Any same duplicate of the same password
    that comes after the check (which returned true) will in the following always return false, so the hits for a respective password are added only once.

    Special duplicate cases we need to check:
    - Does the synset contain duplicates?
    - If yes, how many?

    """
    if password_perm not in dups_map.keys():
        return True  # Not a duplicate
    elif synset != dups_map[password_perm]["synset"]:
        return False  # Not the lowest password if the synsets don't match. So it won't get added to the overall sum
    else:
        return True  # We covered the special cases before


def check_dups():
    # Plan: Suche nach Duplikaten. Wäre zu viel, wenn alles mit allem verglichen werden müsste,
    # daher Vorüberlegung: welche Permutatoren können überhaupt Duplikate erzeugen?
    # Anschließend wird jedes Passwort erneut in der DB gesucht. Wenn Hits > 1 gibt es ein Duplikat.
    # Nun müssen wir allerdings prüfen, ob das aktuell geprüfte Passwort mit dem Duplikat auf einem Weg liegt. Wenn das Duplikat
    # zB zu einem ganz anderen Subtree gehört, zählen wir es nicht als tatsächliches Duplikat. Es wird in dem Fall nicht in die Duplikatsliste aufgenommen
    #
    # Ist das gefundene Duplikat von einem niedrigen Level (in dem Baum als höher als das Passwort, das wir aktuell prüfen)
    # addieren wir das aktuelle Passwort zu der Summe hinzu.
    #
    # Permutators that might potentially produce duplicate passwords (basically any permutator, that adds or detracts characters to a string)
    # no_permutator
    # strip_vowel
    # duplicate
    # reverse

    pass


if __name__ == "__main__":
    main()
