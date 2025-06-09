"""
A script to process a dictionary file of VESUM and convert it to dict.cc format for inflections.

For documentation on tags selected, see:
https://github.com/brown-uk/dict_uk/blob/master/doc/tags.txt
"""

USAGE = "Usage: python convert.py <adj|noun|verb> <filename>"
from itertools import islice
from sys import argv
from collections import defaultdict

def main():
    if len(argv) != 3:
        print(USAGE)
        return

    selectors = {
        'noun': Nouns(),
        'verb': Verbs(),
        'adj': Adjectives(),
    }
    if argv[1] not in selectors:
        print(USAGE)
        return

    selector = selectors[argv[1]]
    
    with open(argv[2]) as dict_uk:
        for line in dict_uk:
            line = line.strip()
            lexem, lemma, tags = line.split(' ')
            tags = set(tags.split(':'))

            if {'bad', 'rare', 'arch', 'alt'}.intersection(tags):
                continue # skip errorneous, rare, achaic and non-normative forms

            selector.add(lexem, lemma, tags)

    selector.print()

class Selector:
    def __init__(self):
        self.words = defaultdict(dict)

    def print(self):
        for lemma, forms in self.words.items():
            print(self.format(lemma, forms))

class Nouns(Selector):
    def add(self, lexem, lemma, tags):
        if 'noun' not in tags:
            return
        if 'p' not in tags and 'v_rod' in tags: # take singular genitive
            self.words[lemma]['gen.sg'] = lexem
        if 'p' in tags and 'v_naz' in tags: # and plural nominative
            self.words[lemma]['pl'] = lexem

    def format(self, lemma, forms):
        return f"{lemma} | {forms.get('gen.sg', '-')} | {forms.get('pl', '-')}"

class Adjectives(Selector):
    def add(self, lexem, lemma, tags):
        if 'adj' not in tags:
            return
        if 'compc' in tags or 'comps' in tags:
            return # only basic form (skip comparatives & superlatives)
        if 'v_naz' not in tags:
            return # only nominative
        if 'long' in tags:
            return # skip long forms, they sound a bit too formal & archaic

        for form in ['m', 'n', 'f', 'p']:
            if form not in tags:
                continue
            self.words[lemma][form] = lexem

    def format(self, lemma, forms):
        return f"{forms.get('m', '-')} | {forms.get('n', '-')} | {forms.get('f', '-')} | {forms.get('p', '-')}"

class Verbs(Selector):
    def add(self, lexem, lemma, tags):
        if 'verb' not in tags:
            return

        if tags == {'verb', 'imperf', 'inf'}:
            self.words[lemma]['imperf_inf'] = lexem
        elif tags == {'verb', 'imperf', 'pres', 's', '1'}:
            self.words[lemma]['present.1p.sg'] = lexem
        elif tags == {'verb', 'imperf', 'past', 'm'}:
            self.words[lemma]['past'] = lexem

        elif tags == {'verb', 'perf', 'inf'}:
            self.words[lemma]['perf_inf'] = lexem
        elif tags == {'verb', 'perf', 'futr', 's', '1'}:
            self.words[lemma]['future.1p.sg'] = lexem
        elif tags == {'verb', 'perf', 'past', 'm'}:
            self.words[lemma]['past'] = lexem

    def format(self, lemma, forms):
        if 'imperf_inf' in forms:
            return f"{lemma} | {forms.get('present.1p.sg', '-')} | {forms.get('past', '-')}"
        elif 'perf_inf' in forms:
            return f"{lemma} | {forms.get('future.1p.sg', '-')} | {forms.get('past', '-')}"

if __name__ == "__main__":
    main()
