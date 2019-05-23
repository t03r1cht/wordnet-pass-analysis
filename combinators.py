

DISABLED_PERMUTATORS = [
    "no_permutator",
    "year_long",
    "number",
    "num_seq_suffix",
    "num_seq_prefix",
    "special_chars_suffix",
    "special_chars_prefix",
]


def combinator_registrar():
    """
    Decorator to register combination handlers
    """
    combination_registry = []

    def registrar(func):
        combination_registry.append(func)
        return func
    registrar.all = combination_registry
    return registrar


combinator = combinator_registrar()


@combinator
def no_combinations(lemma, permutator_registry):
    ret_list = []
    for permutator in permutator_registry:
        perm = permutator(lemma)
        if perm == None:
            continue
        elif type(perm) == list:
            for p in perm:
                if p != None:
                    ret_list.append(p)
        else:
            if perm != None:
                ret_list.append(perm)
    return ret_list


@combinator
def cxc(lemma, permutator_registry):
    ret_list = []
    for permutation_handler in permutator_registry:
        trans = permutation_handler(lemma)
        # Create a list with all permutators except me (the current iteration of all permutatos (see outer loop))
        exc_me = []
        for c in permutator_registry:
            # If a function name is the same as myself, skip, since that would produce a combination
            # with myself
            if c.__name__ != permutation_handler.__name__:
                exc_me.append(c)
        # Call other permutators with the return value of the current permutator
        current_base_permutation = trans  # We already created the permutation above
        for permutator in exc_me:
            if permutation_handler.__name__ in DISABLED_PERMUTATORS:
                continue
            if current_base_permutation == None:
                continue
            elif type(current_base_permutation) == list:
                # If one of the permutators returned a list of permutations
                for p in current_base_permutation:
                    comb_perm = permutator(p)
                    if comb_perm != None:
                        ret_list.append(comb_perm)
            else:  # If the permutator returned a single permutation
                comb_perm = permutator(current_base_permutation)
                if comb_perm != None:
                    ret_list.append(comb_perm)
    return ret_list
