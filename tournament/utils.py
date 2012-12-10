def print_match(match):
    if match:
        return "<Model id=%s, round=%s, status=%s>" % (match.key().id(), match.round, match.status)
    return None

def print_participant(p):
    if p:
        return "<Participant name=%s, seed=%s, score=%s, uuid=%s>" % (p.name, p.seed, p.score, p.uuid)
    return None
