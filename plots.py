import matplotlib.pyplot as plt
import numpy as np
import mongo
import pymongo


def wn_top_passwords_bar(opts):
    labels = []
    occurrences = []
    for password in mongo.db_pws_wn.find().sort("occurrences", pymongo.DESCENDING).limit(opts["top"]):
        labels.append(password["name"])
        occurrences.append(password["occurrences"])
    index = np.arange(len(labels))
    plt.bar(index, occurrences)
    plt.xlabel('Password', fontsize=10)
    plt.ylabel('Occurrences', fontsize=10)
    plt.xticks(index, labels, fontsize=7, rotation=30)
    plt.title('Top %d WordNet Passwords' % opts["top"])
    plt.show()

def lists_top_passwords_bar(opts):
    labels = []
    occurrences = []
    for password in mongo.db_pws_lists.find().sort("occurrences", pymongo.DESCENDING).limit(opts["top"]):
        labels.append(password["name"])
        occurrences.append(password["occurrences"])
    index = np.arange(len(labels))
    plt.bar(index, occurrences)
    plt.xlabel('Password', fontsize=10)
    plt.ylabel('Occurrences', fontsize=10)
    plt.xticks(index, labels, fontsize=7, rotation=30)
    plt.title('Top %d Word List Passwords' % opts["top"])
    plt.show()
