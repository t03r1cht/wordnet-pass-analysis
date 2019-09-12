
def digit_singlechar():
    f = []
    chars = "abcdefghijklmnopqrstuvwxyz"
    nums = [str(i) for i in list(range(101))]
    for c in chars:
        f.append(c)
    f.extend(nums)
    return f

def digits():
    f = []
    nums = [str(i) for i in list(range(101))]
    f.extend(nums)
    f.extend(str(123))
    f.extend(str(1234))
    f.extend(str(12345))
    f.extend(str(123456))
    f.extend(str(1234567))
    f.extend(str(12345678))
    f.extend(str(123456789))
    f.extend(str(12345678900))
    
    return f