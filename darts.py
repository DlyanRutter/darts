from collections import defaultdict

singles = [e for e in range(21)] + [25]
points = set(m*s for s in singles for m in (1,2,3) if m*s != 75)
doubles = set(2*s for s in singles)
ordered_points = [0] + sorted(points, reverse=True)
clockwise = "20 1 18 4 13 6 10 15 2 17 3 19 7 16 8 11 14 9 12 5".split()
counter = clockwise.reverse()
targets = set(str(s+r) for r in clockwise for s in 'SDT') | set(['SB', 'DB'])

def name(d, double=False):
    """Given an int, d, return the name of a target that scores d. If double
    is true, the name must start with 'D', otherwise, prefer the order 'S',
    then 'T', then 'D'"""
    return ('OFF' if d == 0 else
            'DB' if d == 50 else
            q
            'SB' if d == 25 else
            'D'+str(d//2) if (d in doubles and double) else
            'S'+str(d) if d in singles else
            'T'+str(d//3) if (d % 3 == 0) else
            'D'+str(d//2))

def double_out(total):
    """Return a shortest possible list of targets that add to total,
    where the length <= 3 and the final element is a double.
    If there is no solution, return None."""
    for dart1 in ordered_points:
        for dart2 in ordered_points:
            dart3 = total - dart1 - dart2
            if dart3 in doubles:
                solution = [name(dart1), name(dart2), name(dart3, 'D')]
                return [e for e in solution if e != 'OFF']
    return None

def test_double_out():
    "Test the double_out function."
    assert double_out(170) == ['T20', 'T20', 'DB']
    assert double_out(171) == None
    assert double_out(100) in (['T20', 'D20'], ['DB', 'DB'])
    return 'Tests pass'

print test_double_out()

""" triple string misses go to a single ring"
double misses: .5 to single, .5 off board"
thin single is 1/5 as likely as thick single
1/2 thick misses go to double and 1/2 to triple
1/4 single bull misses go to DB and 3/4 to single"
DB miss rate is 3*miss rate, 2/3 to single and 1/3 to SB
1/2 miss rate goes colockwise, 1/2 counterclockwise
sections are list 1 to 20
aim for SB or DB then section can be any of all 20
missing a single section is equally likely to go to all singles"""

def ring_outcome(target, miss):
    "Return a probability distribution of [(ring, probability)] pairs."
    hit = 1.0 - miss
    r = target[0]
    if target == 'DB': 
        miss = min(3*miss, 1.)
        hit = 1. - miss
        return [('DB', hit), ('SB', miss/3.), ('S', 2./3.*miss)]
    elif target == 'SB': 
        return [('SB', hit), ('DB', miss/4.), ('S', 3/4.*miss)]
    elif r == 'S':
        return [(r, 1.0 - miss/5.), ('D', miss/10.), ('T', miss/10.)]
    elif r == 'D': 
        return [(r, hit), ('S', miss/2), ('OFF', miss/2)]
    elif r == 'T': 
        return [(r, hit), ('S', miss)]

def section_outcome(target, miss):
    "Return a probability distribution of [(section, probability)] pairs."
    hit = 1.0 - miss
    if target == 'DB' or target == 'SB':
        misses = [(s, miss/20) for s in clockwise]
    else:
        i = clockwise.index(target[1:])
        misses = [(clockwise[i-1], miss/2),
                  (clockwise[(i+1)%20], miss/2)]
    return  [(target[1:], hit)] + misses

def Target(ring, section):
    "Construct a target name from a ring and section."
    if ring == 'OFF':
        return 'OFF'
    elif ring in ('SB', 'DB'):
        return ring if (section == 'B') else ('S' + section)
    else:
        return ring + section
       
def outcome(target, miss):
    """Returns the outcome of aiming at a target with a given miss ratio. The
    possible outcomes are represented in a dictionary of the target's name and
    the combined probabilities of hitting its section and ring number."""
    results = defaultdict(float)
    for (ring, ringP) in ring_outcome(target, miss):
        for (sect, sectP) in section_outcome(target, miss):
            if ring == 'S' and sect.endswith('B'):
                for s in clockwise:
                    results[Target(ring, s)] += round(((ringP * sectP) / 20), 5)
            else:
                results[Target(ring, sect)] += round((ringP * sectP), 5)
    return dict(results)


def same_outcome(dict1, dict2):
    "Two states are the same if all corresponding sets of locs are the same."
    return all(abs(dict1.get(key, 0) - dict2.get(key, 0)) <= 0.0001
               for key in set(dict1) | set(dict2))

def best_target(miss):
    "Return the target that maximizes the expected score."
    return max(targets, key=lambda t: expected_value(t, miss))

def expected_value(target, miss):
    "The expected score of aiming at target with a given miss ratio."
    return sum([y for (e,y) in value_dict(target, miss).items()])
    
def value_dict(target, miss):
    """A dictionary of each target name and the score of hitting it with
    probability factored in"""
    removeable = [('S',1),('D', 2), ('T', 3)]
    newdict = {}
    for (target_name, probability) in outcome(target, miss).items():
        for (letter, points) in removeable:
            if letter == 'SB': newdict['SB'] = miss * 25
            elif letter == 'DB': newdict['DB'] = miss * 50
            else:
                result = [float(i) for i in target_name if i.isdigit()]
                for letterless in result:
                    if letter in target_name:
                         value = points * letterless
                         newdict[target_name] = probability * value
 #   print value
    return dict(newdict)

def all_targets(miss):
    clockwise = "20 1 18 4 13 6 10 15 2 17 3 19 7 16 8 11 14 9 12 5".split()
    targets = set(str(s+r) for r in clockwise for s in 'SDT') | set(['SB', 'DB'])
    new = []
    for e in targets:
        done = expected_value(e, miss)
        new.append(done)
    print new



#print outcome('SB', 0.2).items()
print expected_value('T19', 0.2)
print value_dict('T20', 0.2)
#    {'S9': 0.016, 'S8': 0.016, 'S3': 0.016, 'S2': 0.016, 'S1': 0.016,
#     'DB': 0.04, 'S6': 0.016, 'S5': 0.016, 'S4': 0.016, 'S20': 0.016,
#     'S19': 0.016, 'S18': 0.016, 'S13': 0.016, 'S12': 0.016, 'S11': 0.016,
#     'S10': 0.016, 'S17': 0.016, 'S16': 0.016, 'S15': 0.016, 'S14': 0.016,
#     'S7': 0.016, 'SB': 0.64})
#print value_dict('S9', 0.2)
print best_target(0.0)

