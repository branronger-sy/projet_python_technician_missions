import sys
sys.path.append("/tmp")
import os
os.environ.setdefault("MPLCONFIGDIR", "/tmp")
import csv
import math
import matplotlib.pyplot as plt

def chargertech(fic):
    techs = []
    with open(fic, 'r') as f:
        lect = csv.DictReader(f)
        for l in lect:
            techs.append({
                'id': l['id'],
                'x': int(l['x']),
                'y': int(l['y']),
                'competences': l['competences'].split('|')
            })
    return techs

def chargermiss(fic):
    miss = []
    with open(fic, 'r') as f:
        lect = csv.DictReader(f)
        for l in lect:
            miss.append({
                'id': l['id'],
                'x': int(l['x']),
                'y': int(l['y']),
                'competence': l['competence']
            })
    return miss

def compat(t, m):
    return m['competence'] in t['competences']

def dist(t, m):
    dx = t['x'] - m['x']
    dy = t['y'] - m['y']
    return math.sqrt(dx**2 + dy**2)

def glouton(techs, miss):
    aff = {}
    pris = set()
    tot = 0
    for m in miss:
        top = None
        dmin = float('inf')
        for t in techs:
            if t['id'] in pris:
                continue
            if not compat(t, m):
                continue
            d = dist(t, m)
            if d < dmin:
                dmin = d
                top = t
        if top is not None:
            aff[m['id']] = top['id']
            pris.add(top['id'])
            tot += dmin
    return aff, tot

def exact(techs, miss):
    bestaff = {}
    bestcout = float('inf')
    maxnb = 0
    cur = {}
    pris = set()

    def backtrack(idx, cout):
        nonlocal bestaff, bestcout, maxnb
        nb = len(cur)
        if nb + (len(miss) - idx) < maxnb:
            return
        if idx == len(miss):
            if nb > maxnb or (nb == maxnb and cout < bestcout):
                maxnb = nb
                bestcout = cout
                bestaff = cur.copy()
            return
        m = miss[idx]
        for t in techs:
            tid = t['id']
            if tid in pris:
                continue
            if not compat(t, m):
                continue
            d = dist(t, m)
            cur[m['id']] = tid
            pris.add(tid)
            backtrack(idx + 1, cout + d)
            del cur[m['id']]
            pris.remove(tid)
        backtrack(idx + 1, cout)

    backtrack(0, 0)
    return bestaff, bestcout

def tracer(techs, miss, aff):
    for t in techs:
        plt.plot(t['x'], t['y'], 'bo')
        plt.text(t['x'] + 0.1, t['y'], t['id'], color='blue')
    for m in miss:
        plt.plot(m['x'], m['y'], 'ro')
        plt.text(m['x'] + 0.1, m['y'], m['id'], color='red')
    if aff:
        for mid, tid in aff.items():
            m = next(x for x in miss if x['id'] == mid)
            t = next(x for x in techs if x['id'] == tid)
            plt.plot([t['x'], m['x']], [t['y'], m['y']], 'g--')
    plt.grid(True)
    plt.savefig("test.png")
    plt.show()

def verif(techs, miss, aff):
    if aff:
        u = len(set(aff.values())) == len(aff)
        c = True
        for mid, tid in aff.items():
            m = next(x for x in miss if x['id'] == mid)
            t = next(x for x in techs if x['id'] == tid)
            if not compat(t, m):
                c = False
        print("verif unicite et compat :", u and c)

    mfake = [{'id': 'Mfake', 'x': 0, 'y': 0, 'competence': 'inconnue'}]
    r1, _ = exact(techs, mfake)
    print("verif competence absente :", len(r1) == 0)

    tfake = techs[:1]
    r2, _ = exact(tfake, miss)
    print("verif techs insuffisants :", len(r2) <= len(tfake))

    r3, c3 = exact(techs, [])
    print("verif zero mission :", r3 == {} and c3 == 0)

techs = chargertech("techniciens.csv")
miss = chargermiss("missions.csv")

print(techs)
print(miss)

resg, coutg = glouton(techs, miss)
print("glouton :", resg, coutg)

rese, coute = exact(techs, miss)
print("exact :", rese, coute)

verif(techs, miss, rese)

tracer(techs, miss, rese)
