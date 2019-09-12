
def digit_singlechar():
    f = []
    chars = "abcdefghijklmnopqrstuvwxyz"
    nums = [str(i) for i in list(range(101))]
    for c in chars:
        f.append(c)
    f.extend(nums)
    return f
