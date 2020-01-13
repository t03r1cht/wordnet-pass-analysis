
def digit_singlechar():
    """
    Returns a dictionary that is used as a filter for mongo queries to 
    exclude entries whose passwords consist of either only digits or are single characters.
    """
    f = []
    chars = "abcdefghijklmnopqrstuvwxyz"
    nums = [str(i) for i in list(range(101))]
    for c in chars:
        f.append(c)
    f.extend(nums)
    return f

def digits():
    """
    Returns a dictionary that is used as a filter for mongo queries to 
    exclude entries whose passwords consist of known number sequences.
    """
    f = []
    nums = [str(i) for i in list(range(101))]
    f.extend(nums)
    f.append(str(123))
    f.append(str(1234))
    f.append(str(12345))
    f.append(str(123456))
    f.append(str(1234567))
    f.append(str(12345678))
    f.append(str(123456789))
    f.append(str(1234567890))
    f.append(str(123)[::-1])
    f.append(str(1234)[::-1])
    f.append(str(12345)[::-1])
    f.append(str(123456)[::-1])
    f.append(str(1234567)[::-1])
    f.append(str(12345678)[::-1])
    f.append(str(123456789)[::-1])
    f.append(str(1234567890)[::-1])
    f.append(str(111))
    f.append(str(1111))
    f.append(str(11111))
    f.append(str(111111))
    f.append(str(1111111))
    f.append(str(11111111))
    f.append(str(111111111))
    f.append(str(1111111111))
    f.append(str(11111111111))
    f.append(str(111111111111))
    f.append(str(1111111111111))
    f.append("00")
    f.append("000")
    f.append("0000")
    f.append("00000")
    f.append("000000")
    f.append("0000000")
    f.append("00000000")
    f.append("000000000")
    f.append("0000000000")
    f.append("00000000000")

    return f