from nltk.corpus import wordnet as wn
import mongo


def main():
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
    check_dups()
    return
    main()
