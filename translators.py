import random

LEET_TRANSLATION_SIMPLE_FROM = "AaBbEeIiOoSs"
LEET_TRANSLATION_SIMPLE_TO = "448833110055"
LEET_TRANS_TABLE_SIMPLE = str.maketrans(
    LEET_TRANSLATION_SIMPLE_FROM, LEET_TRANSLATION_SIMPLE_TO)

REMOVE_VOWELS = {
    ord("a"): None,
    ord("A"): None,
    ord("e"): None,
    ord("E"): None,
    ord("i"): None,
    ord("I"): None,
    ord("o"): None,
    ord("O"): None,
    ord("u"): None,
    ord("U"): None,
}


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
def no_translator(lemma):
    """
    Return the lemma as is. Required because we want to also 
    search for occurences of the original lemma.
    """
    return lemma


@translator
def casing_(lemma):
    """
    Return the lemma in uppercase.
    """
    return lemma.upper()


@translator
def leet(lemma):
    """
    Returns a list of leet translations of the lemma.
    """

    return lemma.translate(LEET_TRANS_TABLE_SIMPLE)


@translator
def year_long(lemma):
    """
    Returns a list of lemmas with years of birth appended (1950-2019).
    """
    return ["%s%d" % (lemma, yob) for yob in range(1950, 2019+1)]


@translator
def number(lemma):
    """
    Returns a list of lemmas with years of birth appended (0-100).
    """
    return ["%s%d" % (lemma, num) for num in range(100)]


@translator
def strip_vowel(lemma):
    """
    Remove all vowels of a lemma.
    """
    perm = lemma.translate(REMOVE_VOWELS)
    if perm is None or len(perm) == 0:
        return lemma
    return perm


@translator
def sc_cc(lemma):
    """
    Snake case to camel case, e.g. john_wayne -> JohnWayne or john_wayne -> johnWayne
    """
    return lemma


@translator
def separator(lemma):
    """
    Lemmas in WordNet are always separated by the underscore "_". Replace it by spaces, hyphens, dots etc.
    """
    return lemma


@translator
def uppercase_index_char(lemma):
    """
    Make the first char of the lemma upper case.
    """
    return lemma


@translator
def num_seq_suffix(lemma):
    """
    Append common number sequence suffixes like 123 to the lemma.
    """
    return lemma


@translator
def num_seq_prefix(lemma):
    """
    Append common number sequence suffixes like 123 to the beginning of the lemma.
    """
    return lemma


@translator
def special_chars_suffix(lemma):
    """
    Append special characters to the lemma.
    """
    return lemma


@translator
def special_chars_prefix(lemma):
    """
    Append special characters to the beginning of the lemma.
    """
    return lemma


@translator
def duplicate(lemma):
    """
    Duplicates the lemma.
    """
    return lemma


@translator
def pad_with_characters(lemma):
    """
    Separate each character in the lemma with an underscore, e.g. h_e_l_l_o (dot, hyphen, hash etc.).
    """
    return lemma


@translator
def reverse(lemma):
    """
    Reverse the lemma.
    """
    return lemma


@translator
def upper_vowels(lemma):
    """
    Make vowels uppercase, e.g. hEllO.
    """
    return lemma


@translator
def upper_non_vowels(lemma):
    """
    Make everything except vowels uppercase, e.g. HeLLo.
    """
    return lemma
