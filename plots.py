import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import mongo
from mongo import db_wn
import pymongo
from helper import log_err, format_number, log_status, log_ok
import operator
from hpie import HPie, stringvalues_to_pv
from nltk.corpus import wordnet as wn

# https://github.com/klieret/pyplot-hierarchical-pie


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
                    xytext=(0, 40),
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
                    xytext=(0, 40),
                    # with offset pixels, we can specify that the values from xytext are handles as pixels and not as plot points
                    textcoords="offset pixels",
                    rotation=90)
    plt.xlabel("Passwords")
    plt.ylabel("Occurrences")
    plt.title("Top %d Word List Passwords" % opts["top"])
    plt.show(f)


def wn_top_1k(opts):
    labels = []
    occurrences = []
    i = 0
    for password in mongo.db_pws_wn.find().sort("occurrences", pymongo.DESCENDING).limit(1000):
        labels.append("%s (#%s)" % (password["name"], i+1))
        occurrences.append(password["occurrences"])
        i += 1

    # Get top 10 from some list
    ref_labels = []
    ref_occs = []
    for password in mongo.db_pws_lists.find({"source": "12_tech_brands.txt"}).sort("occurrences", pymongo.DESCENDING).limit(10):
        ref_labels.append("%s" % (password["name"]))
        ref_occs.append(password["occurrences"])

    f, ax = plt.subplots(1)
    # Plot the base line
    ax.plot(labels, occurrences, "-")

    # Create an index for the labels. These values are the coordinates for the x axis where the reference values will be drawn in another color
    # (1 and 1000 of the Wordnet will be blue and sorted and in between these two ticks will be the reference values, also sorted and in red, so they
    # will be surrounded by the blue ticks. Since index 0 and 999 is already occupied by the WordNet ticks, we need corrdinates from in between)
    # ref_xticks = np.arange(1, len(ref_labels))
    # plt.xticks(ref_xticks, ref_labels, fontsize=7, rotation=30)
    # plt.xticks([500], ["blabla"], fontsize=7, rotation=30)

    # only create ticks for the first and last rank (index 0 and 999)
    xticks = [0, 999]
    xtick_labels = []
    for tick in xticks:
        xtick_labels.append(labels[tick])

    # Merge the two lists
    for i in range(len(ref_labels)):
        xticks.append((i + 1) * 50)
        xtick_labels.append(ref_labels[i])

    plt.xticks(xticks, xtick_labels, fontsize=7, rotation=90)
    indices = np.arange(len(labels))

    # Find the biggest absolute value of occurrences. This value plus 1/4 of it will be used as length for the Y axis
    max_val_base = occurrences[0]
    max_val_ref = ref_occs[0]
    if max_val_base >= max_val_ref:
        max_val = max_val_base
    else:
        max_val = max_val_ref
    # Set the fixed Y axis height to 125% of the highest value found in either ref_occs or occurrences
    ax.set_ylim([0, max_val + max_val / 4])
    for index in xticks[:2]:
        # the first array is the xy_from, second is xy_to value, so we basically draw a simple vertical line
        ax.plot([index, index], [index, occurrences[index]], color="blue")
        ax.annotate(occurrences[index],
                    xy=(index, occurrences[index]),
                    xytext=(0, 30),
                    # with offset pixels, we can specify that the values from xytext are handles as pixels and not as plot points
                    textcoords="offset pixels",
                    rotation=90)
    for index in range(len(xticks[2:])):
        # the first array is the xy_from, second is xy_to value, so we basically draw a simple vertical line
        ax.plot([(index+1)*50, (index+1)*50],
                [(index+1)*50, ref_occs[index]], color="black")
        ax.annotate(ref_occs[index],
                    xy=((index+1)*50, ref_occs[index]),
                    xytext=(0, 30),
                    # with offset pixels, we can specify that the values from xytext are handles as pixels and not as plot points
                    textcoords="offset pixels",
                    rotation=90)
    plt.xlabel("Passwords by Occurrences")
    plt.ylabel("Occurrences")
    plt.title("Top 1000 Word List Passwords")
    black_patch = mpatches.Patch(
        color="black", label="Ref data set occurrences")
    blue_patch = mpatches.Patch(color="blue", label="WordNet occurrences")
    plt.legend(handles=[black_patch, blue_patch], loc="best")
    plt.show(f)


def wn_top_1k_bar(opts):

    labels = []
    occurrences = []
    i = 0
    for password in mongo.db_pws_wn.find().sort("occurrences", pymongo.DESCENDING).limit(1000):
        labels.append("%s" % (password["name"]))
        occurrences.append(password["occurrences"])
        i += 1

    # Get top 10 from some list
    ref_labels = []
    ref_occs = []
    for password in mongo.db_pws_lists.find({"source": "12_tech_brands.txt"}).sort("occurrences", pymongo.DESCENDING).limit(20):
        ref_labels.append("%s" % (password["name"]))
        ref_occs.append(password["occurrences"])

    f, ax = plt.subplots(1)
    index = np.arange(len(labels))

    # Create the data lists
    indices = []
    # x coord 0 and 20 to show the first and last element of the WN top 1000
    indices.append(0)
    indices.append(20)
    # x coords for the values in between (1..19)
    # Split the list so it starts at the 1. index which is 1, since this is the first number we need instead of 0
    indices.extend(range(20)[1:])

    # Fill the data lists with data
    indices[0] = occurrences[0]
    indices[20] = occurrences[999]

    for i in range(19):
        # When i == 0 then ctr == 1. This way we never hit the first (0) and last (20) element
        # By incrementing ctr before actually using it, the last iteration will be 18+1 = 19 so the last
        # data element that is not alreay set by indices[20] = ...
        ctr = i + 1
        # We still use i to access the first 19 top elements of the ref list
        indices[ctr] = ref_occs[i]

    bar_colors = []
    for i in range(20):
        if i == 0 or i == 20:
            bar_colors.append("black")
        else:
            bar_colors.append("blue")

    xcoords = np.arange(len(indices))
    rect1 = ax.bar(xcoords, indices, color=bar_colors)

    # create labels for xticks
    xticks_labels = []
    xticks_labels.append(labels[0, labels[999]])
    # starting at index 1 since index 0 and 20 are set by the WN top 1 and 1000
    for i in range(20)[1:]:
        xticks_labels.append(ref_labels[i])
    xticks_labels.append(labels[999])
    print(labels[999])
    plt.xticks(np.arange(21), xticks_labels, rotation=45)
    autolabel(rect1, ax)

    # create patches to display in the legend for the graph
    black_patch = mpatches.Patch(
        color="black", label="WordNet #1 and #1000 of Top 1000 Passwords")
    blue_patch = mpatches.Patch(
        color="blue", label="Top 19 Passwords of Selected Word List")
    plt.legend(handles=[black_patch, blue_patch], loc="best")

    plt.ylabel("Occurrences")
    plt.xlabel("Password")
    plt.title("Word List Passwords")
    plt.show()
    return


def wn_top_1k_bar_test(opts):
    limit_val = 20
    # We can set the number of top passwords with the --top flag
    if opts["top"]:
        if opts["top"] > 100:
            log_err("--top value too high. Select Value between 5 and 100")
            return
        limit_val = opts["top"]

    ref_list = None
    if opts["ref_list"] == None:
        log_err(
            "No ref list specified. Use the -l flag to specify a list to use for passwords")
        return
    # ref_list == "alL" looks at all lists and not a specific one
    ref_list = opts["ref_list"]

    labels = []
    occurrences = []
    i = 0
    for password in mongo.db_pws_wn.find().sort("occurrences", pymongo.DESCENDING).limit(1000):
        labels.append("%s" % (password["name"]))
        occurrences.append(password["occurrences"])
        i += 1

    # Get top 10 from some list
    ref_labels = []
    ref_occs = []
    if ref_list == "all":
        pw_list = mongo.db_pws_lists.find({}).sort(
            "occurrences", pymongo.DESCENDING).limit(limit_val)
    else:
        pw_list = mongo.db_pws_lists.find({"source": ref_list}).sort(
            "occurrences", pymongo.DESCENDING).limit(limit_val)

    for password in pw_list:
        ref_labels.append("%s" % (password["name"]))
        ref_occs.append(password["occurrences"])

    f, ax = plt.subplots(1)
    index = np.arange(len(labels))

    # Create the data lists
    indices = []
    # x coord 0 and 20 to show the first and last element of the WN top 1000
    indices.append(0)
    indices.append(limit_val)
    # x coords for the values in between (1..19)
    # Split the list so it starts at the 1. index which is 1, since this is the first number we need instead of 0
    indices.extend(range(limit_val)[1:])

    # Fill the data lists with data
    indices[0] = occurrences[0]
    indices[limit_val] = occurrences[999]

    for i in range(limit_val-1):
        # When i == 0 then ctr == 1. This way we never hit the first (0) and last (20) element
        # By incrementing ctr before actually using it, the last iteration will be 18+1 = 19 so the last
        # data element that is not alreay set by indices[20] = ...
        ctr = i + 1
        # We still use i to access the first 19 top elements of the ref list
        indices[ctr] = ref_occs[i]

    bar_colors = []
    for i in range(limit_val):
        if i == 0 or i == limit_val:
            bar_colors.append("black")
        else:
            bar_colors.append("blue")

    xcoords = np.arange(len(indices))
    rect1 = ax.bar(xcoords, indices, color=bar_colors)

    # create labels for xticks
    xticks_labels = []
    xticks_labels.append(labels[0])
    # starting at index 1 since index 0 and 20 are set by the WN top 1 and 1000
    for i in range(limit_val)[1:]:
        xticks_labels.append(ref_labels[i])
    xticks_labels.append(labels[999])
    plt.xticks(np.arange(limit_val+1), xticks_labels, rotation=45)
    autolabel(rect1, ax)

    # create patches to display in the legend for the graph
    black_patch = mpatches.Patch(
        color="black", label="WordNet #1 and #1000 of Top 1000 Passwords")
    blue_patch = mpatches.Patch(
        color="blue", label="Top %d Passwords of %s" % (limit_val, ref_list))
    plt.legend(handles=[black_patch, blue_patch], loc="best")

    plt.ylabel("Occurrences")
    plt.xlabel("Password")
    plt.title("Word List Passwords")
    plt.show()
    return


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


def autolabel(rects, ax, xpos="center"):
    ha = {'center': 'center', 'right': 'left', 'left': 'right'}
    offset = {'center': 0, 'right': 1, 'left': -1}

    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(offset[xpos]*3, 3),  # use 3 points offset
                    textcoords="offset points",  # in both directions
                    ha=ha[xpos], va='bottom')


def autolabel_custom(rects, ax, xpos="center"):
    ha = {'center': 'center', 'right': 'left', 'left': 'right'}
    offset = {'center': 0, 'right': 1, 'left': -1}

    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(offset[xpos]*3, 3),  # use 3 points offset
                    textcoords="offset points",  # in both directions
                    ha=ha[xpos], va='bottom')


def wn_line_plot_noteable_pws(opts):
    labels = []
    occurrences = []
    exclude_terms = {
        "word_base": {"$nin": [
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "0",
        ]}
    }

    for password in mongo.db_wn_lemma_permutations.find(exclude_terms).sort("total_hits", pymongo.DESCENDING).limit(39):
        labels.append("%s" % (password["word_base"]))
        occurrences.append(password["total_hits"])

    f, ax = plt.subplots(1)
    ax.plot(np.arange(len(labels)), occurrences, "-")
    plt.xticks([0, 38], [labels[0], labels[38]])

    ax.set_ylim(bottom=0)
    ax.set_xlim(left=0)
    plt.ticklabel_format(style='plain', axis='y')
    plt.xlabel("Passwords (including all of its permutations)")
    plt.ylabel("Occurrences")
    plt.title("Top %d WordNet Passwords" % opts["top"])
    plt.show(f)


def wn_line_plot_categories(opts):
    wn_limit = 100
    f, ax = plt.subplots(1)

    limit_val = 20
    # We can set the number of top passwords with the --top flag
    if opts["top"]:
        if opts["top"] > 100:
            log_err("--top value too high. Select Value between 5 and 100")
            return
        limit_val = opts["top"]
    else:
        limit_val = 10

    ref_list = None
    if opts["ref_list"] == None:
        log_err(
            "No ref list specified. Use the -l flag to specify a list to use for passwords")
        return
    # ref_list == "alL" looks at all lists and not a specific one
    ref_list = opts["ref_list"]

    # Get top n from some list
    if ref_list == "all":
        # we exclude the keyboard patterns txt file since it has a lot of duplicates with 99_unsortiert
        all_word_lists_list = mongo.db_lists.find(
            {"filename": {"$nin": ["03_keyboard_patterns.txt"]}})
        lemma_list = []
        for item in list(all_word_lists_list):
            lemma_list.extend(item["lemmas"])

        pw_list = []
        for item in lemma_list:
            o = {"name": item["name"], "occurrences": item["occurrences"]}
            pw_list.append(o)
    else:
        word_lists = mongo.db_lists.find_one({"filename": ref_list})
        pw_list = word_lists["lemmas"]

    # We now need to sort the dictionary by "occurrences" in descending order
    # Contains all word bases ("lemmas") for a given list plus its occurrences
    # Cut the sorted result list based on the --top flag. --top defaults to 10
    sorted_o = sorted(pw_list, key=lambda k: k["occurrences"], reverse=True)[
        :limit_val]

    labels = []
    occurrences = []
    exclude_terms = {
        "word_base": {"$nin": [
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "0",
        ]}
    }

    # Get the top 1000 wordnet passwords (used as a reference for the word list passwords)
    for password in mongo.db_wn_lemma_permutations.find(exclude_terms).sort("total_hits", pymongo.DESCENDING).limit(wn_limit + 10):
        labels.append("%s" % (password["word_base"]))
        occurrences.append(password["total_hits"])
        # print(password["word_base"], password["total_hits"])

    # Get all passwords from the word lists as array so we can check if the top 1 or top 1000 password from the wordnet is contained in int
    # if it is contained, increment the top 1 and top 1000 index by one to create some kind of sliding window
    # the goal is to have a top 1 and 1000 password that is not contained by the word list passwords so they don't overlap on the boundaries
    wl_lemmas = [x["name"] for x in pw_list]

    i = 0
    while True:
        # Exit if bounds could not be found after 10 tries
        if i >= 10:
            log_err(
                "Too many duplicates in word list lemmas and WordNet. Could not determine left bound and right bound.")
            return
        # fitting boundaries are no numbers and contain more than 3 characters
        if labels[i] in wl_lemmas or labels[i].isdigit() or len(labels[i]) <= 3:
            log_err("Invalid left bound: %s (index: %d)" % (labels[i], i))
            pass
        elif labels[wn_limit-1+i] in wl_lemmas or labels[wn_limit-1+i].isdigit() or len(labels[wn_limit-1+i]) <= 3:
            log_err("Invalid right bound: %s (index: %d)" %
                    (labels[wn_limit-1+i], wn_limit-1+i))
            pass

        else:
            break
        i += 1

    # left boundary equal to labels[0] (or labels[0] + i in case sliding window) so the top 1 password
    l_bound = labels[i]

    # right boundary equal to labels[999] (or labels[999] + i in case sliding window) so the top 1000 password
    r_bound = labels[wn_limit-1+i]

    wn_pos_1_label = l_bound
    wn_pos_1_occs = occurrences[i]

    wn_pos_1000_label = r_bound
    wn_pos_1000_occs = occurrences[wn_limit-1+i]

    # We now need to trim the list to have the new left and right bound to be index 0 and 999 (for both the labels and the occurrences)
    cut_wn_labels = labels[i:wn_limit-1+i+1]
    cut_wn_occs = occurrences[i:wn_limit-1+i+1]

    # Create a list that has the wn values but they are just for orientation/comparison of occurrences. The values of the "original" list are not going to used
    # for bar plotting. Instead, they will be saved under a key, that is ignored when drawing the bar plot.
    new_occs_inserted = [{"orig": x, "list": -1} for x in cut_wn_occs]
    new_labels_inserted = [{"orig": x, "list": None} for x in cut_wn_labels]

    # Insert the sorted word list items at the right x coords
    idx_behind_last_wn = len(cut_wn_labels)
    xcoords_bar = []

    for item in sorted_o:
        occs = item["occurrences"]
        # Determine first if this elements occs are lower than the last wn element. If thats the case, append it behind the last wn element
        if occs < cut_wn_occs[-1]:
            # If the current item occurrences was lower than the last wordnet element, append it with the index last_wn + 1 and increment this counter
            # xcoords_bar.append(idx_behind_last_wn)
            new_occs_inserted.append({"orig": -1, "list": occs})
            new_labels_inserted.append({"orig": "", "list": item["name"]})
            idx_behind_last_wn += 1
        else:
            # At this point we know the current elements occs are not lower than the last wn element
            # Now we just need to find out where (within the first and last wn element frame) it will be drawn
            for idx, wn_occs in enumerate(cut_wn_occs):
                # Run until occs is NOT lower than wn_occs
                if occs < wn_occs:
                    pass
                elif occs >= wn_occs:

                    # cut_wn_occs is stored from most to least occurrences, so if val a is bigger than the current value from cut_wn_occs it must automatically
                    # be bigger than the rest of the list (since it is ordererd in a decending order)
                    # Before we insert, there may already be an element that was previously compared against the same element, so we need to determine if we insert before or
                    # after this index
                    if new_occs_inserted[idx]["list"] < occs:
                        # The current occs value is bigger than what is already in there
                        new_occs_inserted.insert(
                            idx, {"orig": -1, "list": occs})
                        new_labels_inserted.insert(
                            idx, {"orig": "", "list": item["name"]})
                    else:
                        # If the value is bigger, we insert occs after this index
                        new_occs_inserted.insert(
                            idx+1, {"orig": -1, "list": occs})
                        new_labels_inserted.insert(
                            idx+1, {"orig": "", "list": item["name"]})

                    break
                else:
                    pass

    # Transform the dict to a flat list. List dict items with orig = -1 are going to be 0 in the flattened list, else the "list" value
    flat_occs_inserted = []
    for x in new_occs_inserted:
        if x["list"] == -1:
            flat_occs_inserted.append(0)
        else:
            flat_occs_inserted.append(x["list"])
    # ... also transform the label list so we have a consistent mapping again (mind the zeros)
    flat_labels_inserted = []
    for x in new_labels_inserted:
        if x["list"] == None:
            flat_labels_inserted.append("")
        else:
            flat_labels_inserted.append(x["list"])

    # Check lengths (the next step will raise an exception if the lengths of both flat lists are not equal since we want to merge them into a dict)
    if len(flat_labels_inserted) != len(flat_occs_inserted):
        log_err("Something went wrong while flattening the lists (lengths are not equal). flat_occs_inserted: %d, flat_labels_inserted: %d" % (
            len(flat_occs_inserted), len(flat_labels_inserted)))
        return

    # store labels with occs as keys
    labels_for_occs = {}
    for idx, val in enumerate(flat_occs_inserted):
        labels_for_occs[idx] = flat_labels_inserted[idx]

    # save 0 states in flat lists
    zero_pos = []
    flat_occs_inserted_no_zeros = []
    for idx, val in enumerate(flat_occs_inserted):
        if val == 0:
            zero_pos.append(idx)
        else:
            flat_occs_inserted_no_zeros.append(val)

    # sort lists
    sorted_no_zeros = sorted(flat_occs_inserted_no_zeros, reverse=True)
    log_status("Unsorted xcoords list: \n{}".format(flat_occs_inserted))

    # restore 0 states, i.e. insert zeros at the indices saved in the zero_pos list
    sorted_with_zeros = sorted_no_zeros[:]
    for idx in zero_pos:
        sorted_with_zeros.insert(idx, 0)

    log_status("Sorted xcoords list: \n{}".format(sorted_with_zeros))

    # Draw the bar plot
    rect1 = ax.bar(np.arange(len(sorted_with_zeros)),
                   sorted_with_zeros, alpha=0.7, color="gray", width=0.3)

    i = 0
    for rect in rect1:
        height = rect.get_height()
        ax.annotate('{}'.format(flat_labels_inserted[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0*3, 3),  # use 3 points offset
                    textcoords="offset points",  # in both directions
                    rotation=90,
                    fontsize="x-small",
                    ha="center", va='bottom')
        i += 1

    # Create the xticks for the wn 1 and 1000 labels
    plt.xticks([0, wn_limit-1], [cut_wn_labels[0],
                                 cut_wn_labels[wn_limit-1]])
    # Draw the line plot
    ax.plot(np.arange(len(cut_wn_labels)), cut_wn_occs, "-", color="black")

    ax.set_ylim(bottom=0)
    ax.set_xlim(left=0)
    ax.set_ylim([0, sorted_no_zeros[0] + sorted_no_zeros[0] / 4])
    plt.ticklabel_format(style='plain', axis='y')
    plt.xlabel(
        "WordNet Top 1 and 1000 Passwords (including all of its permutations)")
    plt.ylabel("Occurrences")
    plt.title("Top %d Reference List Passwords" % limit_val)
    blue_patch = mpatches.Patch(color="black", label="WordNet occurrences")
    red_patch = mpatches.Patch(
        color="gray", label="Ref data set occurrences (incl permutations)")
    plt.legend(handles=[blue_patch, red_patch], loc="best")
    log_ok("Drawing plot...")
    plt.show(f)
    return


def wn_display(opts):
    limit_ss = 5
    limit_synsets_flag = 20
    limit_depth_flag = 20

    # control how deep you want to go in the wordnet hierarchy
    if opts["depth"]:
        if opts["depth"] > 18:
            log_err("-d value too high. Select Value between 1 and 18")
            return
        limit_depth_flag = opts["depth"]
    else:
        limit_depth_flag = 3

    if opts["top"]:
        limit_synsets_flag = opts["top"]
    else:
        limit_synsets_flag = 0  # 0 = no limit

    fix, ax = plt.subplots()

    # Get synsets from the database on the user-specified level
    # current max level is 18
    ss_for_level = db_wn.find(
        {"level": limit_depth_flag}).limit(limit_synsets_flag)

    # data_map contains the hierarchies, e.g. a/b/c: 1
    data_map = {}

    # fill the data map

    for ss_obj in ss_for_level:
        ss = wn.synset(ss_obj["id"])
        path_list = [x.lemma_names()[0] for x in ss.hypernym_paths()[0]]

        # create each patch, e.g. [a,b,c] => a, a/b, a/b/c
        for x in range(len(path_list)):
            sub_path_list = path_list[:x+1]
            sub_path = "/".join(sub_path_list)
            if sub_path not in data_map:
                data_map[sub_path] = 1


        ss_root_path = "/".join(path_list)
        data_map[ss_root_path] = 1
    
    
    # TODO wenn wir nur aus der datenbank diejenigen synsets des angegebenen levels holen, werden diejenigen nicht berücksichtigt, die auf levels weiter oben bereits
    # beendet werden (die hyponyme von thing.n.08 enden bereits auf level 2).
    # aus diesem grund muss vom angegebenen level zurück bis level 1 (exklusive 0) zurückgelaufen werden und dort auch alles gesucht werden. wenn diese bereits durch hierarchisch
    # untergeordnete pfade gezeichnet wurden, werden diese einfach übersprungen
    # create the paths for the paths between levels 1 and n-1
    for x in range(1, limit_depth_flag):
        ss_for_level = db_wn.find({"level": x}).limit(limit_synsets_flag)
        for ss_obj in ss_for_level:
            ss = wn.synset(ss_obj["id"])
            path_list = [x.lemma_names()[0] for x in ss.hypernym_paths()[0]]

            for x in range(len(path_list)):
                sub_path_list = path_list[:x+1]
                sub_path = "/".join(sub_path_list)
                if sub_path not in data_map:
                    data_map[sub_path] = 1


            ss_root_path = "/".join(path_list)
            data_map[ss_root_path] = 1

    
    data = stringvalues_to_pv(data_map)

    # If the whole graph should be filled out (not blank space on horizontal lines) only the hierarchically lowest elements can have the value 1, all other items need to be 0
    # data1 = stringvalues_to_pv({
    #     'ipsum':                      1,
    #     'ipsum/eirmod':               1,
    #     'ipsum/eirmod/dolor':         1,
    #     'lorem':                      1,
    #     'lorem/sadipscing/dolor':     1,
    #     'lorem/sadipscing/lorem':     1,
    #     'lorem/sadipscing/nonumy':    1,
    #     'lorem/eirmod':               1,
    #     'lorem/eirmod/lorem':         1,
    #     'lorem/sadipscing':           1,
    # })

    # ss = wn.synset("thing.n.08")
    # [Synset('thing.n.01'), Synset('thing.n.02'), Synset('thing.n.03'), Synset('thing.n.04'), Synset('thing.n.05'), 
    # Synset('matter.n.01'), Synset('thing.n.07'), Synset('thing.n.08'), Synset('thing.n.09'), Synset('thing.n.10'), 
    # Synset('thing.n.11'), Synset('thing.n.12')]
    # print(ss.hyponyms())
    # return

    # do the magic
    hp = HPie(data, ax, plot_center=True, 
        cmap=plt.get_cmap("hsv"),
        plot_minimal_angle=0,
        label_minimal_angle=1.5
    )

    hp.format_value_text = lambda value: None

    # set plot attributes
    hp.plot(setup_axes=True)
    ax.set_title('Hierarchical WordNet Structure')

    # save/show plot
    plt.show()
