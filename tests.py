from nltk.corpus import wordnet as wn
import nltk


# wordnet ids:
# n = noun
# v = verb
# a = adjectives
# r = adverbs
# s = adverb satellites


if __name__ == "__main__":
        # download corpus
    # nltk.download("wordnet")

    # get synsets for word and print synonyms, definition and examples
    # synset = wn.synsets("good")
    # for s in synset:
    #     print("%s lemmas[%s]\ndefinition[%s]\nexample[%s]" %
    #           (s, s.lemmas(), s.definition(), s.examples()))

    # specific synset with gloss and example
    # synset = wn.synset("chair.n.01")
    # print("synset[%s]\ndefinition[%s]\nexample[%s]" %
    #       (synset, synset.definition(), synset.examples()))

    # get the paths from the current synset to the root lemma
    # synset = wn.synset("chair.n.01")
    # print(synset.hypernym_paths())

    # synset = wn.synset("boat.n.01")
    # print("%s lemmas[%s] %s" % (synset, synset.lemmas(), synset.definition()))
    # for hypo in synset.hyponyms():
    #     print("[%s] lemmas: %s" % (hypo.name(), [lemma.name()
    #                                              for lemma in hypo.lemmas()]))
    # print("root hyponyms: %s" % synset.root_hypernyms())

    # synset = wn.synsets("boat", wn.NOUN)
    # print("ADJ-good: %s" % synset)

    # get the parts the lemma is comprised of
    # synset = wn.synset("ship.n.01")
    # print(synset.part_meronyms())

    # get the substances the lemma is comprised of
    # synset = wn.synset("tree.n.01")
    # print(synset.substance_meronyms())

    # get what the lemma is a part of
    # synset = wn.synset("atom.n.01")
    # print("atom.n.01 part_holonyms", synset.part_holonyms())

    # get what the lemma is a substance of
    # synset = wn.synset("hydrogen.n.01")
    # print("hydrogen.n.01 substance_holonyms", synset.substance_holonyms())

    # get entailments (folgebeziehungen) of verbs
    # synset = wn.synset("drink.v.01")
    # print(synset.entailments())

    # get the lowest common hypernyms of 2 words
    # synset1 = wn.synset("car.n.01")
    # synset2 = wn.synset("garbage_truck.n.01")
    # print(synset1.lowest_common_hypernyms(synset2))

    # get the depth of a word in the wordnet tree
    # entity is the root element of WordNet
    # print(wn.synset("entity.n.01").min_depth())
    # print(wn.synset("car.n.01").min_depth())
    # print(wn.synset("chair.v.01").min_depth())

    # synset1 = wn.synset("garbage_truck.n.01")
    # synset2 = wn.synset("truck.n.01")
    # print(synset1.wup_similarity(synset2))

    # start wordnet browser
    # nltk.app.wordnet()
    
    pass
