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

NUM_SUFFIXES = [
    "123",
    "1234",
    "12345",
    "123456",
    "1234567",
    "12345678",
    "123456789",
    "1234567890",
]

SPECIAL_CHARS_SUFFIXES = [
    "!",
    "@",
    "#",
    "$",
    "%",
    "^",
    "&",
    "*",
    "?",
    ".",
    ",",
    "-"
    "_",
    "+",
]

PADDING_CHARS = [
    "_",
    "-",
    ".",
    ",",
    "#",
    "*",
    "+",
]

VOWELS = [
    "A",
    "a",
    "E",
    "e",
    "I",
    "i",
    "O",
    "o",
    "U",
    "u",
]


def permutator_registrar():
    """
    Decorator to register permutation handlers
    """
    permutation_registry = []

    def registrar(func):
        permutation_registry.append(func)
        return func
    registrar.all = permutation_registry
    return registrar


permutator = permutator_registrar()


@permutator
def no_permutator(lemma):
    """
    Return the lemma as is. Required because we want to also 
    search for occurences of the original lemma.
    """
    return lemma


@permutator
def casing_(lemma):
    """
    Return the lemma in uppercase.
    """
    return lemma.upper()


@permutator
def leet(lemma):
    """
    Returns a list of leet permutations of the lemma.
    """

    return lemma.translate(LEET_TRANS_TABLE_SIMPLE)


@permutator
def year_long(lemma):
    """
    Returns a list of lemmas with years of birth appended (1950-2019).
    """
    return ["%s%d" % (lemma, yob) for yob in range(1950, 2019+1)]


@permutator
def number(lemma):
    """
    Returns a list of lemmas with years of birth appended (0-100).
    """
    return ["%s%d" % (lemma, num) for num in range(100)]


@permutator
def strip_vowel(lemma):
    """
    Remove all vowels of a lemma.
    """
    perm = lemma.translate(REMOVE_VOWELS)
    if perm is None or len(perm) == 0:
        return lemma
    return perm


@permutator
def sc_cc(lemma):
    """
    Snake case to camel case, e.g. john_wayne -> JohnWayne or john_wayne -> johnWayne
    """
    perm_list = []
    split_array = []

    if "_" in lemma:
        split_array = lemma.split("_")
    elif "-" in lemma:
        split_array = lemma.split("-")
    elif "." in lemma:
        split_array = lemma.split(".")
    else:
        return None
    # CamelCase
    cap = [p.capitalize() for p in split_array]
    perm_list.append("".join(cap))
    # camelCase
    cap = [p.capitalize() for p in split_array]
    # After everything has been capitalized, lowercase the first word
    cap[0] = cap[0].lower()
    perm_list.append("".join(cap))

    return perm_list


@permutator
def separator(lemma):
    """
    Composite lemmas in WordNet are always separated by the underscore "_". Replace it by spaces, hyphens, dots etc.
    """
    perm_list = []
    if "_" in lemma:
        perm_list.append(lemma.replace("_", "-"))
        perm_list.append(lemma.replace("_", "."))
        perm_list.append(lemma.replace("_", ","))
        perm_list.append(lemma.replace("_", "#"))
        perm_list.append(lemma.replace("_", "+"))
        perm_list.append(lemma.replace("_", "*"))
        perm_list.append(lemma.replace("_", " "))
        return perm_list
    else:
        return None


@permutator
def uppercase_index_char(lemma):
    """
    Make the first char of the lemma upper case.
    """
    return lemma.capitalize()


@permutator
def num_seq_suffix(lemma):
    """
    Append common number sequence suffixes like 123 to the lemma.
    """
    return ["%s%s" % (lemma, suffix) for suffix in NUM_SUFFIXES]


@permutator
def num_seq_prefix(lemma):
    """
    Append common number sequence suffixes like 123 to the beginning of the lemma.
    """
    return ["%s%s" % (prefix, lemma) for prefix in NUM_SUFFIXES]


@permutator
def special_chars_suffix(lemma):
    """
    Append special characters to the lemma.
    """
    return ["%s%s" % (lemma, suffix) for suffix in SPECIAL_CHARS_SUFFIXES]


@permutator
def special_chars_prefix(lemma):
    """
    Append special characters to the beginning of the lemma.
    """
    return ["%s%s" % (prefix, lemma) for prefix in SPECIAL_CHARS_SUFFIXES]


@permutator
def duplicate(lemma):
    """
    Duplicates the lemma.
    """
    return "%s%s" % (lemma, lemma)


@permutator
def pad_with_characters(lemma):
    """
    Separate each character in the lemma with an underscore, e.g. h_e_l_l_o (dot, hyphen, hash etc.).
    """
    perm_list = []
    for padding_char in PADDING_CHARS:
        perm = ""
        for c in lemma:
            perm += "%s%s" % (c, padding_char)
        # Remove trailing padding char
        # Take substring until length of the string (excluding the trailing padding char)
        perm_list.append(perm[:len(perm)-1])
    return perm_list


@permutator
def reverse(lemma):
    """
    Reverse the lemma.
    """
    return lemma[::-1]


@permutator
def upper_vowels(lemma):
    """
    Make vowels uppercase, e.g. hEllO.
    """
    perm = ""
    for char in lemma:
        if char in VOWELS:
            perm += char.upper()
        else:
            perm += char
    return perm


@permutator
def upper_non_vowels(lemma):
    """
    Make everything except vowels uppercase, e.g. HeLLo.
    """
    perm = ""
    for char in lemma:
        if char not in VOWELS:
            perm += char.upper()
        else:
            perm += char
    return perm

# X x X combination
