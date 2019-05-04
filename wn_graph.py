import networkx as nx
import matplotlib as mpl
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout
import random
import pydot
from nltk.corpus import wordnet as wn


# To install pygraphviz on windows use the pre-built python binaries/wheel:
# https://github.com/CristiFati/Prebuilt-Binaries/tree/master/Windows/PyGraphviz

def draw_graph(root_syn_name, max_depth):
    """
    Draw a directed acyclic graph representing the WordNet.

    root_syn_name: The synset the drawing will start from.
    max_depth: the level until which this function should draw the graph.
    """
    G = nx.DiGraph()
    root_synsets = wn.synsets(root_syn_name)
    if len(root_synsets) == 0:
        print("  No synset found for: %s" % root_syn_name)
        return

    # If multiple synsets were found, prompt the user to choose which one to use.
    if len(root_synsets) > 1:
        print("  Multiple synset were found. Please choose: ")
        for elem in range(len(root_synsets)):
            print("    [%d] %s" % (elem, root_synsets[elem]))
        choice = input("Your choice [0-%d]: " % ((len(root_synsets)-1)))
        try:
            int_choice = int(choice)
        except ValueError:
            print("Invalid choice: %s" % choice)
            return
        if int_choice < 0 or int_choice > len(root_synsets) - 1:
            print("Invalid choice: %s" % choice)
            return
        # Make the choice the new root synset from we will start our recursion.
        choice_root_syn = root_synsets[int_choice]
    else:
        choice_root_syn = root_synsets[0]

    # print(choice_root_syn.hyponyms())
    # return
    # Create the first node in the digraph
    G.add_node(choice_root_syn.name())
    _recurse_nouns_from_root(G, root_syn=choice_root_syn,
                             start_depth=choice_root_syn.min_depth(), rel_depth=max_depth)
    print("len G: %d" % len(G))
    pos = hierarchy_pos(G, choice_root_syn.name())
    # labels = nx.get_node_attributes(G, 'depth')
    # nx.draw(G, pos=pos, with_labels=True, labels=labels)
    nx.draw(G, pos=pos, with_labels=True)

    plt.title("WordNet")
    plt.show()


def _recurse_nouns_from_root(G, root_syn, start_depth, rel_depth=0):
    """
    Iterate over the entire WordNet starting from root_syn and running until a total of rel_depth layers were processed.
    """
    # If the current depth in the DAG is reached, do not continue to iterate this path.
    if (root_syn.min_depth() - start_depth) >= rel_depth:
        return
    curr_root_syn = root_syn
    for hypo in curr_root_syn.hyponyms():
        # Add the new synset as a node to the digraph
        G.add_node(hypo.name())
        # Create the edge between this synset and its hypernym
        G.add_edge(root_syn.name(), hypo.name())
        # Execute the function again with the new root synset being each hyponym we just found.
        _recurse_nouns_from_root(
            G, root_syn=hypo, start_depth=start_depth, rel_depth=rel_depth)


def hierarchy_pos(G, root, levels=None, width=1., height=1.):
    '''If there is a cycle that is reachable from root, then this will see infinite recursion.
       G: the graph
       root: the root node
       levels: a dictionary
               key: level number (starting from 0)
               value: number of nodes in this level
       width: horizontal space allocated for drawing
       height: vertical space allocated for drawing'''
    TOTAL = "total"
    CURRENT = "current"

    def make_levels(levels, node=root, currentLevel=0, parent=None):
        """Compute the number of nodes for each level
        """
        if not currentLevel in levels:
            levels[currentLevel] = {TOTAL: 0, CURRENT: 0}
        levels[currentLevel][TOTAL] += 1
        neighbors = G.neighbors(node)
        for neighbor in neighbors:
            if not neighbor == parent:
                levels = make_levels(levels, neighbor, currentLevel + 1, node)
        return levels

    def make_pos(pos, node=root, currentLevel=0, parent=None, vert_loc=0):
        dx = 1/levels[currentLevel][TOTAL]
        left = dx/2
        pos[node] = ((left + dx*levels[currentLevel][CURRENT])*width, vert_loc)
        levels[currentLevel][CURRENT] += 1
        neighbors = G.neighbors(node)
        for neighbor in neighbors:
            if not neighbor == parent:
                pos = make_pos(pos, neighbor, currentLevel +
                               1, node, vert_loc-vert_gap)
        return pos
    if levels is None:
        levels = make_levels({})
    else:
        levels = {l: {TOTAL: levels[l], CURRENT: 0} for l in levels}
    vert_gap = height / (max([l for l in levels])+1)
    return make_pos({})
