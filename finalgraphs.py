def avg_permutations_lemma(base):
    """
    Calculate the average permutations per lemma.
    Base: either wordnet or lists
    """
    pass

def locate_topn_list_pws_wn(list_name):
    """
    Mark the top N passwords of a given list within the top N passwords of the wordnet.
    On the X axis, mark each 50th step.
    """
    top_n_wn = 1000
    pass

def calculate_efficiency(base):
    """
    The efficiency is a number/percentage that indicates how many
    passwords of a given password source were found in collection 1, disregarding the 
    actual number of occurrences.
    Efficiency = Sum(occurrences > 0)
    """
    pass

def calculate_performance(base):
    """
    The performance is the total sum of occurrences for a password source.
    """
    pass

def topn_passwords_hibp(n):
    """
    Return the top N passwords of the HIBP hash list (list must be sorted by prevalence).
    """
    pass