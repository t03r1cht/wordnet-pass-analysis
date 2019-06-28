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
    # Create a sequence from 0 - len(labels) - 1 (will be the x coordinates)
    index = np.arange(len(labels))
    # index (0..99) are the indices for the labels array
    # occurrences are the height of each tick on the x axis (so the occurrences on the y axis)
    plt.bar(index, occurrences)
    plt.xlabel('Password', fontsize=10)
    plt.ylabel('Occurrences', fontsize=10)
    # mark each tick on the x axis using the index to place each element of the labels list
    # we can "map" the index list to the label list and also represent each label x coordinate with it
    plt.xticks(index, labels, fontsize=7, rotation=90)
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


def wn_top_passwords_line(opts):
    labels = []
    occurrences = []
    for password in mongo.db_pws_wn.find().sort("occurrences", pymongo.DESCENDING).limit(opts["top"]):
        labels.append(password["name"])
        occurrences.append(password["occurrences"])
    # plt.vlines(x=labels, ymin=0, ymax=100000, color="r")
    # plt.axvline(x=1, color="c", linestyle="-")
    f, ax = plt.subplots(1)
    ax.plot(labels, occurrences, "b.-")

    xticks = [0, 1, round(len(labels)/2) - 1,
              round(len(labels)/2) + 1, len(labels)-1]
    indices = np.arange(len(labels))
    plt.xticks(indices, labels, fontsize=7, rotation=90)
    # plt.xticks(rotation=70)
    ax.set_ylim(bottom=0)
    # https://stackoverflow.com/questions/38172903/plot-vertical-lines-from-datapoints-to-zero-axis-in-python?rq=1
    # Give the y axis a fourth more space based off the highest occurrences value so we can still properly display the occurences with the vertical lines
    ax.set_ylim([0, occurrences[0] + occurrences[0] / 4])
    # Plot the WordNet passwords
    for index in indices:
        ax.plot([index, index], [index, occurrences[index]], color="blue")
        ax.annotate(occurrences[index],
                    xy=(index, occurrences[index]),
                    xytext=(0, 30),
                    # with offset pixels, we can specify that the values from xytext are handles as pixels and not as plot points
                    textcoords="offset pixels",
                    rotation=90)
    plt.xlabel("Passwords")
    plt.ylabel("Occurrences")
    plt.title("Top %d WordNet Passwords" % opts["top"])
    plt.show(f)

def lists_top_passwords_line(opts):
    labels = []
    occurrences = []
    for password in mongo.db_pws_lists.find().sort("occurrences", pymongo.DESCENDING).limit(opts["top"]):
        labels.append(password["name"])
        occurrences.append(password["occurrences"])
    # plt.vlines(x=labels, ymin=0, ymax=100000, color="r")
    # plt.axvline(x=1, color="c", linestyle="-")
    f, ax = plt.subplots(1)
    ax.plot(labels, occurrences, "b.-")

    xticks = [0, 1, round(len(labels)/2) - 1,
              round(len(labels)/2) + 1, len(labels)-1]
    indices = np.arange(len(labels))
    plt.xticks(indices, labels, fontsize=7, rotation=90)
    # plt.xticks(rotation=70)
    ax.set_ylim(bottom=0)
    # https://stackoverflow.com/questions/38172903/plot-vertical-lines-from-datapoints-to-zero-axis-in-python?rq=1
    # Give the y axis a fourth more space based off the highest occurrences value so we can still properly display the occurences with the vertical lines
    ax.set_ylim([0, occurrences[0] + occurrences[0] / 4])
    # Plot the WordNet passwords
    for index in indices:
        ax.plot([index, index], [index, occurrences[index]], color="blue")
        ax.annotate(occurrences[index],
                    xy=(index, occurrences[index]),
                    xytext=(0, 30),
                    # with offset pixels, we can specify that the values from xytext are handles as pixels and not as plot points
                    textcoords="offset pixels",
                    rotation=90)
    plt.xlabel("Passwords")
    plt.ylabel("Occurrences")
    plt.title("Top %d Word List Passwords" % opts["top"])
    plt.show(f)

def test_plot(opts):
    wn_labels = []
    wn_occurrences = []
    for password in mongo.db_pws_wn.find().sort("occurrences", pymongo.DESCENDING).limit(opts["top"]):
        wn_labels.append(password["name"])
        wn_occurrences.append(password["occurrences"])
    list_labels = []
    list_occurrences = []
    for password in mongo.db_pws_lists.find().sort("occurrences", pymongo.DESCENDING).limit(opts["top"]):
        list_labels.append(password["name"])
        list_occurrences.append(password["occurrences"])
    # plt.vlines(x=wn_labels, ymin=0, ymax=100000, color="r")
    # plt.axvline(x=1, color="c", linestyle="-")
    f, ax = plt.subplots(1)
    ax.plot(wn_labels, wn_occurrences, "b.-")

    xticks = [0, 1, round(len(wn_labels)/2) - 1,
              round(len(wn_labels)/2) + 1, len(wn_labels)-1]
    plt.xticks(xticks, wn_labels, fontsize=7, rotation=30)
    # plt.xticks(rotation=70)
    ax.set_ylim(bottom=0)
    # https://stackoverflow.com/questions/38172903/plot-vertical-lines-from-datapoints-to-zero-axis-in-python?rq=1
    # Give the y axis a fourth more space based off the highest wn_occurrences value so we can still properly display the occurences with the vertical lines
    ax.set_ylim([0, wn_occurrences[0] + wn_occurrences[0] / 4])
    # Plot the WordNet passwords
    for index in xticks:
        ax.plot([index, index], [index, wn_occurrences[index]], color="blue")
        ax.annotate(wn_occurrences[index],
                    xy=(index, wn_occurrences[index]),
                    xytext=(0, 30),
                    # with offset pixels, we can specify that the values from xytext are handles as pixels and not as plot points
                    textcoords="offset pixels",
                    rotation=90)
    # Plot some word list passwords
    # xticks_lists = [2, 3, 4]
    # for index in xticks_lists:
    #     ax.plot([index, index], [index, list_occurrences[index]], color="blue")
    #     ax.annotate(list_occurrences[index],
    #                 xy=(index, list_occurrences[index]),
    #                 xytext=(0, 30),
    #                 # with offset pixels, we can specify that the values from xytext are handles as pixels and not as plot points
    #                 textcoords="offset pixels",
    #                 rotation=90)

    plt.xlabel("Passwords")
    plt.ylabel("Occurrences")
    plt.title("Top %d WordNet Passwords" % opts["top"])
    plt.show(f)