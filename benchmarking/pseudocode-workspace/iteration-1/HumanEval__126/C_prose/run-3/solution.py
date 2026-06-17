from collections import Counter


def is_sorted(lst):
    '''
    Given a list of numbers, return whether or not they are sorted
    in ascending order. If list has more than 1 duplicate of the same
    number, return False. Assume no negative numbers and only integers.
    '''
    if any(count > 2 for count in Counter(lst).values()):
        return False
    return all(lst[i] <= lst[i + 1] for i in range(len(lst) - 1))
