from nltk.corpus import wordnet as wn

total_cnt = 0
known_keys = {}
diff_key_cnt = 0
key_exists_cnt = 0
check_map = {}
check_map_not_found_cnt = 0
# TODO Create map: put all from all_synsets in a dict, mark them with value 1 if the recursion has iterated over the key
# Get the diff (keys with value still 0 that have not been touched by the recursion)


def main():

    lvl_0_synsets = []
    lvl_0_synsets_labels = []

    for syn in list(wn.all_synsets("v")):
        # Store all synset names and check which ones haven't been touched by
        # the recursion
        check_map[syn.name()] = 0
        if syn.min_depth() == 0:
            lvl_0_synsets.append(syn)
            lvl_0_synsets_labels.append(syn.name())

    print("Synsets starting at Level 0: ", len(lvl_0_synsets))

    for syn in lvl_0_synsets:
        rec(syn, None)

    not_found_check_map = []
    for k, v in check_map.items():
        if v == 0:
            not_found_check_map.append(k)

    print("WN Verb len: ", len(list(wn.all_synsets("v"))))
    print("Counted: ", len(known_keys.keys()))
    print("diff_key_cnt: ", diff_key_cnt)
    print("key_exists_cnt: ", key_exists_cnt)
    print("check_map_not_found_cnt: ", check_map_not_found_cnt)
    print("Diff not found by recursion: ", len(not_found_check_map))

    print()
    print()
    print()
    print()

    # Get the diff synsets
    for item in not_found_check_map:
        syn = wn.synset(item)
        # print(syn.name(), syn.min_depth(), syn.hypernyms(), syn.hyponyms(), syn.lemma_names())
        hypernym_paths_labels = [syn.name() for hyper_lists in syn.hypernym_paths() for syn in hyper_lists]
        found_lvl0_in_hypernyms = []
        for lvl0 in lvl_0_synsets_labels:
            if lvl0 in hypernym_paths_labels:
                found_lvl0_in_hypernyms.append(lvl0)

        print(syn.name(), syn.min_depth(), "LVL 0 PARENTS:", found_lvl0_in_hypernyms)
        print()


def rec(syn, parent):
    global total_cnt
    global known_keys
    global diff_key_cnt
    global key_exists_cnt
    global check_map_not_found_cnt

    total_cnt += 1

    # Flag syn name in check_map for found (1)
    if syn.name() in check_map:
        check_map[syn.name()] = 1
    else:
        print("Not found in check_map: ", syn.name())
        check_map_not_found_cnt += 1

    if syn.name() in known_keys:
        key_exists_cnt += 1
        print("")
        print(syn.name(), "already exists")
        print("Existing: Key=", syn.name(), "Value=", known_keys[syn.name()])
        print("New: Key=", syn.name(), "Value=", parent)
        # If the new value is the same as the existing value
        if known_keys[syn.name()] == parent:
            print("Values are the same!")
        else:
            print("Values are different, old={}, new={}".format(
                known_keys[syn.name()], parent))
            diff_key_cnt += 1
    known_keys[syn.name()] = parent
    hypos = syn.hyponyms()

    # print("level: ", syn.min_depth())
    if hypos == []:
        pass
        # print(syn.name(), "has no hypos")
    else:
        if not parent:
            pass
            # print(syn, "(parent: None) has", len(hypos),
            #       "hyponyms:", [x.name() for x in hypos])
        else:
            pass
            # print(syn, "(parent: ", parent.name(), ") has", len(
            #     hypos), "hyponyms:", [x.name() for x in hypos])
        for hypo in hypos:
            rec(hypo, syn)


if __name__ == "__main__":
    main()
