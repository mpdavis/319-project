def print_match(match, participants=None):
    if match:
        ps = ""
        if participants:
            for p in participants:
                ps += "%s, " % p
        return "<Model id=%s, round=%s, status=%s, participants=%s>" % (match.key().id(),
                                                                        match.round,
                                                                        match.status,
                                                                        ps)
    return None


def print_participant(p):
    if p:
        return "<Participant name=%s, seed=%s, score=%s, uuid=%s>" % (p.name,
                                                                      p.seed,
                                                                      p.score,
                                                                      p.uuid)
    return None


#TODO: Write unittests for this function
def determine_bracket(m):
    """
    This function generates a nested list representing the bracket.
    Algorithm based off a question Max asked in StackOverflow
    stackoverflow.com/questions/13792213/algorithm-for-generating-a-bracket-model-list-in-python
    :param m: The number of participants.
    :return: The list representing all or part of the bracket, depending on the recursion.
    Example: m=8 arr= [[[1,8],[4,5]],[[2,7],[3,6]]]
    """
    def divide(arr, depth, m):
        if len(complements) <= depth:
            complements.append(2 ** (depth + 2) + 1)
        complement = complements[depth]
        for i in range(2):
            if complement - arr[i] <= m:
                arr[i] = [arr[i], complement - arr[i]]
                divide(arr[i], depth + 1, m)

    arr = [1, 2]
    complements = []
    divide(arr, 0, m)
    return arr
