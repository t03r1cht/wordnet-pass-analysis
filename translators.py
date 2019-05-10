import random

LEET_TRANSLATION_SIMPLE_FROM = "AaBbEeIiOo"
LEET_TRANSLATION_SIMPLE_TO = "4488331100"
LEET_TRANS_TABLE_SIMPLE = str.maketrans(
    LEET_TRANSLATION_SIMPLE_FROM, LEET_TRANSLATION_SIMPLE_TO)


def translator_registrar():
    """
    Decorator to register translation handlers
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
    """
    Return the lemma as is. Required because we want to also 
    search for occurences of the original lemma.
    """
    return lemma


@translator
def casing_translator(lemma):
    """
    Return the lemma in uppercase.
    """
    return lemma.upper()


@translator
def leet_translator(lemma):
    """
    Returns a list of leet translations of the lemma.
    """

    return lemma.translate(LEET_TRANS_TABLE_SIMPLE)


@translator
def yob_translator(lemma):
    """
    Returns a list of lemmas with years of birth appended (1950-2019).
    """
    return ["%s%d" % (lemma, yob) for yob in range(1950, 2019+1)]


@translator
def rem_vowel_translator(lemma):
    """
    Remove all vowels of a password.
    """
    return ""


@translator
def sc_cc_translator(lemma):
    """
    Snake case to camel case, e.g. john_wayne -> JohnWayne or john_wayne -> johnWayne
    """
    pass


@translator
def separator_translator(lemma):
    """
    Lemmas in WordNet are always separated by the underscore "_". Replace it by spaces, hyphens, dots etc.
    """
    pass


@translator
def uppercase_index_char(lemma):
    """
    Make the first char of the lemma upper case.
    """
    pass
