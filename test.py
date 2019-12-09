from nltk.corpus import wordnet as wn
import mongo


def main():
    # Build a duplicate map
    # This map contains a list of known duplicates including the number of the lowest level one of the duplicates occurs in.
    # We imply that we subsume all the hits starting from the bottom of the WordNet all the way to the root node. This means, we do not allow any duplicates
    # under the root node (other than if we start subsuming from somewhere in the middle of the Wordnet. In that case, we don't care about duplicates possibly occurring in sibling sub-trees),
    # which means we do not allow any duplicates AT ALL.
    # MongoDB Find duplicates: db.getCollection('passwords_wn_noun').aggregate([{"$match": {"occurrences": {"$gt": 0}}}, {"$group": {_id: "$name", sum: {"$sum": 1}}}, {"$match": {"sum": {"$gt": 1}}}, {"$sort": {"sum": -1}}], { allowDiskUse: true })
    # MongoDB Cound numer of duplicates: db.getCollection('passwords_wn_noun').aggregate([{"$match": {"occurrences": {"$gt": 0}}}, {"$group": {_id: "$name", sum: {"$sum": 1}}}, {"$match": {"sum": {"$gt": 1}}}, {"$sort": {"sum": -1}}, {"$group": {_id: null, count: {"$sum": 1}}}], { allowDiskUse: true })
    dups_map = {}
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
        for index,value in enumerate(dup["results"]):
            # > means lower in the tree (tree levels go from 0..n)
            if value["level"] > min_depth:
                min_depth = value["level"]
                idx = index
        
        results = dup["results"]
        o["name"] = results[idx]["name"]
        o["occurrences"] = results[idx]["occurrences"]
        o["synset"] = results[idx]["synset"]
        o["level"] = results[idx]["level"]
        print(o.values())
        # Store in dict of dicts containing the lowest duplicates. The outer key for the dict is the password
        # permutation

        # For each password, check if this password is in the list of keys of the above dict. If it is, we know our password permutation is a duplicate
        # We then check if the password we are looking is the lowest duplicate in the wordnet 
        # if password.synset == map[password_perm]["synset"]: add the occurrences of this password to the total sum, else: continue (dont add, because we already have it added somewhere below)

    return

    # Determine the lowest level we can start from
    # We will start at the bottom and work our way up to the root synset
    all_levels = mongo.db_wn.distinct("level")
    lowest_level = max(all_levels)
    # Get all synsets for this level, group by common parents and add the synset's hits together
    lowest_level_grps = mongo.db_wn.aggregate([
        {"$match": {"level": lowest_level}},  # filter by lowest level
        {"$group": {
            "_id": "$parent",  # group by the parent synsets
            "sum": {
                # sum the hits of only the current synsets (including lemmas), disregarding possible hits below this synset
                "$sum": "$this_hits"
            }
        }}
    ])
    for grouped_hits in lowest_level_grps:
        print(grouped_hits["_id"], grouped_hits["sum"])
    # Get all synsets for this level
    # For each synset, check its password permutations for possible duplicates. Found duplicates will be stored in found_dups
    synsets_lowest_lvl = mongo.db_wn.find({"level": lowest_level})
    for syn in synsets_lowest_lvl:
        found_dups = []
        perms = {}
        perms_for_syn = mongo.db_pws_wn.find({"synset": syn["id"]})
        for perm in perms_for_syn:
            pass
            # if perm["name"]
        print(syn["id"], syn["level"], cnt)


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