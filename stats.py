import mongo
import mongo_filter
import pymongo
from helper import log_ok, log_err


def wordnet():
    # We want to exclude the non-alphanumerical and single character lemmas
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
            "$limit": 3
        }
    ]
    for item in mongo.db_pws_wn.aggregate(aggregate_query):
        log_ok(item["name"])
