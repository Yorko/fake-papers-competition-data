import argparse
import json
import random

import nltk
import scispacy
import spacy
from nltk.corpus import wordnet
from scispacy.linking import EntityLinker

parser = argparse.ArgumentParser()
parser.add_argument("input")
parser.add_argument("concepts")
parser.add_argument("output")
parser.add_argument("--umls", action="store_true")
parser.add_argument("--walk", action="store_true")
parser.add_argument("--word", action="store_true")
parser.add_argument("--entity", action="store_true")

args = parser.parse_args()

nlp = spacy.load("en_core_sci_lg")
nlp.add_pipe("scispacy_linker", config={"resolve_abbreviations": True, "linker_name": "umls"})

POS = {"NOUN": "n", "ADV": "r", "ADJ": "a", "VERB": "v"}

print("loading")
with open("tree.json") as inf:
    c2ptree = json.load(inf)
    p2ctree = {}
    for c in c2ptree:
        v = set(c2ptree[c])
        c2ptree[c] = v
        for p in v:
            l = p2ctree.setdefault(p, set())
            l.add(c)

with open(args.concepts) as inf:
    concepts = {}
    for l in inf:
        p = l.strip().split("\t")
        li = concepts.setdefault(p[2], [])
        li.append(p[0])
print("loaded")


def getsyns(word, pos):
    synonyms = []
    pos = POS[pos]
    for syn in wordnet.synsets(word, pos):
        for l in syn.lemmas():
            synonyms.append(l.name())
    return synonyms


SELECTION_RATE = 0.1

PICK_PARENT = 0.5
KEEP_WALKING = 0.1


def walk(cid):
    parents = c2ptree.get(cid)
    children = p2ctree.get(cid)
    if parents is not None and random.random() < PICK_PARENT:
        p = random.choice(list(parents))
        if random.random() < KEEP_WALKING:
            return walk(p)
        else:
            return p
    elif children is not None:
        p = random.choice(list(children))
        if random.random() < KEEP_WALKING:
            return walk(p)
        else:
            return p

    return None


def switchConcept(word, ws, pos, start_char, end_char, spans):
    for s, e, c in spans:
        if start_char >= s and end_char <= e:
            if len(c) > 0:
                if start_char == s:
                    if args.walk:
                        o = walk(c[0][0])
                        if o is None:
                            return random.choice(concepts[c[0][0]]) + ws
                        else:
                            return random.choice(concepts[o]) + ws
                    else:
                        return random.choice(concepts[c[0][0]]) + ws
                    # return "X"+ws
                else:
                    return ""
            else:
                return word + ws
    return word + ws


def switch(word, pos):
    r = random.random()

    if r < SELECTION_RATE:
        syns = [w for w in getsyns(word, pos) if w != word]
        if len(syns) == 0:
            return word
        else:
            return random.choice(syns).replace("_", " ")
    return word


def overlap(start_char, end_char, spans):
    for s, e, c in spans:
        if start_char >= s and end_char <= e:
            return True
    return False


with open(args.input) as inf:
    docs = json.load(inf)

TAGS = ["ADJ", "NOUN", "ADV", "VERB"]
with open(args.output, "w") as outf:
    res = []
    for d in docs:
        orig = d["origPara"]
        doc = nlp(orig)
        # print(doc.ents)
        # for e in doc.ents:
        # 	print(e._.kb_ents)
        # exit()

        spans = [(e.start_char, e.end_char, e._.kb_ents) for e in doc.ents]
        # for t in doc:
        # 	t.text="AA"
        # 	print(t.text,t.pos_,t.tag_)
        if args.word:
            res.append(
                {
                    "origPara": orig,
                    "switched": "".join(
                        [
                            i
                            for l in [
                                [switch(t.text, t.pos_) if t.pos_ in TAGS else t.text, t.whitespace_] for t in doc
                            ]
                            for i in l
                        ]
                    ),
                }
            )
        elif args.entity:
            res.append(
                {
                    "origPara": orig,
                    "switched": "".join(
                        [
                            i
                            for l in [
                                [
                                    switch(t.text, t.pos_)
                                    if overlap(t.idx, t.idx + len(t), spans) and t.pos_ in TAGS
                                    else t.text,
                                    t.whitespace_,
                                ]
                                for t in doc
                            ]
                            for i in l
                        ]
                    ),
                }
            )
        elif args.umls:
            res.append(
                {
                    "origPara": orig,
                    "switched": "".join(
                        [
                            i
                            for l in [
                                [switchConcept(t.text, t.whitespace_, t.pos_, t.idx, t.idx + len(t), spans)]
                                for t in doc
                            ]
                            for i in l
                        ]
                    ),
                }
            )
        # linker = nlp.get_pipe("scispacy_linker")
        # for umls_ent in entity._.kb_ents:

    json.dump(res, outf)
