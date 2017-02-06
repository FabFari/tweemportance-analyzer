
def compare_positivity(v1, v2):
    p = 0
    #Assumes they have the same length
    n = len(v1)
    for i in range (0,n):
        p += v1[i]-v2[i]

    return p


def count_non_zero(v1):
    count = 0
    for i in v1:
        if i > 0:
            count += 1
    return count