import mongo
import mongo_filter
import pymongo
import matplotlib.pyplot as plt
import numpy as np
from helper import log_ok, log_err, format_number
import collections
from operator import getitem


def wordnet():
    # We want to exclude the non-alphanumerical and single character lemmas
    exclude_filter = mongo_filter.digit_singlechar()
    aggregate_query1 = [
        {
            "$match": {
                "word_base": {
                    "$nin": exclude_filter
                }
            }
        },
        {
            "$group": {
                "_id": "$tag",
                "sum": {
                    "$sum": "$occurrences"
                }
            }
        }
    ]

    total_hits = 0
    for item in mongo.db_pws_wn.aggregate(aggregate_query1):
        log_ok("Total hits for timestamp '{}': {}".format(
            item["_id"], format_number(item["sum"])))
        total_hits += item["sum"]

    # Now that we have the total hits, we just need to get the number of total passwords (with the filter still applied)
    total_passwords = mongo.db_pws_wn.find(
        {"word_base": {"$nin": exclude_filter}}).count()
    log_ok("Total passwords generated with WordNet: {}".format(
        format_number(total_passwords)))
    log_ok("Note: Non-alphabetical and non-alphanumerical passwords have been excluded!")
    hpp = float(total_hits) / float(total_passwords)
    log_ok("Hits per password: {}".format(hpp))


def ref_lists():
    # Exclude non-alphabetical passwords/word bases
    exclude_filter = mongo_filter.digit_singlechar()
    aggregate_query = [
        {
            "$match": {
                "word_base": {
                    "$nin": exclude_filter
                }
            }
        },
        {
            "$group": {
                "_id": "$source",
                "sum": {
                    "$sum": "$occurrences"
                },
                "doc_count": {  # doc_count
                    "$sum": 1
                }
            }
        },
        {
            "$sort": {
                "sum": -1
            }
        }
    ]

    results = {}
    

    for item in mongo.db_pws_lists.aggregate(aggregate_query):
        hpp = float(item["sum"]) / float(item["doc_count"])
        results[item["_id"]] = {
            "hpp": hpp,
            "total_hits": item["sum"],
            "total_passwords": item["doc_count"]
        }
    sorted_o = collections.OrderedDict(sorted(results.items(), key=lambda x: getitem(x[1], "hpp"), reverse=True))

    hpp_list = []
    total_passwords_list = []
    names_list = []

    for item in sorted_o:
        list_name = item
        values = sorted_o[item]
        hpp_list.append(values["hpp"])
        total_passwords_list.append(values["total_passwords"])
        names_list.append(list_name)
        log_ok("Ref List: {},Total Passwords: {}, Total Hits: {}, Hits Per Password: {}".format(
            list_name,
            format_number(values["total_passwords"]),
            format_number(values["total_hits"]),
            values["hpp"]))

    log_ok("Note: Non-alphabetical and non-alphanumerical passwords have been excluded!")
    

    # And now also plot this
    f, ax = plt.subplots(1)
    xcoords = np.arange(len(names_list))
    width = 0.27
    hpps = ax.bar(xcoords, hpp_list, width, color="black")
    total_passes = ax.bar(xcoords+width, total_passwords_list, width, color="grey")
    plt.xticks(xcoords, names_list, rotation=45)
    plt.ylabel("Hits Per Password")
    plt.xlabel("Reference List")
    plt.title("Hits Per Password for Reference Lists")
    ax.legend((hpps, total_passes), ("Hits per Password", "Total Passwords"))
    ax.set_yscale("log", basey=10)
    plt.show()
    return