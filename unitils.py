def pair_diff(a, b):
    return list(map(lambda x: x[0] - x[1], zip(a, b)))


def pair_sum(a, b):
    return list(map(lambda x: x[0] + x[1], zip(a, b)))



