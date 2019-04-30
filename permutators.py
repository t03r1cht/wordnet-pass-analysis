import random
from utilitybelt import change_charset

LEET_TRANSLATION_SIMPLE_FROM = "AaBbEeIiOo"
LEET_TRANSLATION_SIMPLE_TO = "4488331100"
LEET_TRANS_TABLE_SIMPLE = str.maketrans(
    LEET_TRANSLATION_SIMPLE_FROM, LEET_TRANSLATION_SIMPLE_TO)


def permut_registrar():
    """Decorator to register permutation handlers
    """
    permut_registry = []

    def registrar(func):
        permut_registry.append(func)
        return func
    registrar.all = permut_registry
    return registrar


permutator = permut_registrar()


@permutator
def no_permutator_permutator(lemma):
    """Return the lemma as is. Required because we want to also 
    search for occurences of the original lemma.
    """
    return lemma


@permutator
def casing_permutator(lemma):
    """Return the lemma in uppercase.
    """
    return lemma.upper()


@permutator
def leet_permutator(lemma):
    """Returns a list of leet permutations of the lemma.
    """

    return lemma.translate(LEET_TRANS_TABLE_SIMPLE)
