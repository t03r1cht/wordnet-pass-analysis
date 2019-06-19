import json
import jsonpickle
import os
from helper import log_err, log_status, log_ok
import sys


class WordList(object):

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
        with open("intermediate_lists/" + self.filename + ".ill", "w+") as f:
            json.dump(jsonpickle.encode(self), f)


class Lemma(object):
    def __init__(self):
        self.name = ""
        self.total_hits = 0
        self.searched = 0
        self.found = 0
        self.not_found = 0


def decode_from_ill_files():
    d_name = "intermediate_lists/"
    dir_content = os.listdir(d_name)
    if len(dir_content) == 0:
        log_err("%s is empty. Nothing to restore" % d_name)
        sys.exit(0)
    log_status("Restoring from %d .ill files" % (len(dir_content)))
    for ill_file in dir_content:
        with open(os.path.join(d_name, ill_file), "r") as f:
            ill_content = f.read()
            o = jsonpickle.decode(ill_content)
            log_status(o.lemmas_total)
    log_ok("Done")
