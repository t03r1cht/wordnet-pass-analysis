import random
from utilitybelt import change_charset

LEET_TRANSLATION_SIMPLE_FROM = "AaBbEeIiOo"
LEET_TRANSLATION_SIMPLE_TO = "4488331100"
LEET_TRANS_TABLE_SIMPLE = str.maketrans(
    LEET_TRANSLATION_SIMPLE_FROM, LEET_TRANSLATION_SIMPLE_TO)


def translator_registrar():
    """Decorator to register translation handlers
    """
    translation_registry = []

    def registrar(func):
        translation_registry.append(func)
        return func
    registrar.all = translation_registry
    return registrar


translator = translator_registrar()


@translator
def no_translator_translator(lemma):
    """Return the lemma as is. Required because we want to also 
    search for occurences of the original lemma.
    """
    return lemma


@translator
def casing_translator(lemma):
    """Return the lemma in uppercase.
    """
    return lemma.upper()


@translator
def leet_translator(lemma):
    """Returns a list of leet translations of the lemma.
    """

    return lemma.translate(LEET_TRANS_TABLE_SIMPLE)

@translator
def yob_translator(lemma):
    """Returns a list of lemmas with years of birth appended (1950-2019).
    """
    return ["%s%d" % (lemma, yob) for yob in range(1950, 2019+1)]