import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import mongo
import pymongo
from helper import log_err
import operator


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
    # Get top 10 from some list
    if ref_list == "all":
        pw_list = mongo.db_lists.find_one({})
    else:
        pw_list = mongo.db_lists.find_one({"filename": ref_list})

    # We now need to sort the dictionary by "occurrences" in descending order
    # Contains all word bases ("lemmas") for a given list plus its occurrences
    o = pw_list["lemmas"]
    sorted_o = sorted(o, key=lambda k: k["occurrences"], reverse=True)

    # We now need to insert the reference passwords based on their occurrences
    ref_indices = []
    ref_labels = []
    ref_occs = []
    rev_occs = occurrences
    for pw in sorted_o:
        for idx, occ in enumerate(occurrences[::-1]):
            if pw["occurrences"] >= occ:
                print(pw["name"], "(", pw["occurrences"], ") is bigger than ", labels[idx], "(", occurrences[idx], ")")
            else:
                # If the name of the current word list lemma is the same as from the wordnet lemma, skip
                if pw["name"] == labels[idx]:
                    continue
                ref_indices.append(idx)
                ref_labels.append(pw["name"])
                ref_occs.append(pw["occurrences"])


    f, ax = plt.subplots(1)
    ax.plot(np.arange(len(labels)), occurrences, "-")
    rect1 = ax.bar([10, 20], [100000, 500000])

    # Label the bar diagram
    i = 0
    for rect in rect1:
        height = rect.get_height()
        ax.annotate('{}'.format(ref_labels[i]),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0*3, 3),  # use 3 points offset
                    textcoords="offset points",  # in both directions
                    ha="center", va='bottom')
        i += 1

    plt.xticks([0, 19, 38], [labels[0], labels[19], labels[38]])

    ax.set_ylim(bottom=0)
    ax.set_xlim(left=0)
    plt.ticklabel_format(style='plain', axis='y')
    plt.xlabel("Passwords (including all of its permutations)")
    plt.ylabel("Occurrences")
    plt.title("Top %d WordNet Passwords" % opts["top"])
    plt.show(f)
