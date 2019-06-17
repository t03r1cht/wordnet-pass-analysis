import json
import jsonpickle


class WordList():

    def __init__(self):
        self.filename = ""
        self.lemmas_total = 0
        self.start_date = None
        self.end_date = None
        self.lemmas = []

    def add_lemma(self, o):
        self.lemmas.append(o)

    def write_to_file(self):
        # use jsonpickle.decode to recreate the python object from the json string
        with open("cache/" + self.filename + ".tmp", "w+") as f:
            json.dump(jsonpickle.encode(self), f)


class Lemma():
    def __init__(self):
        self.name = ""
        self.total_hits = 0
        self.searched = 0
        self.found = 0
        self.not_found = 0
