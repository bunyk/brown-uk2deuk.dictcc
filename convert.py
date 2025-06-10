"""
A script to process a dictionary file of VESUM and convert it to dict.cc format for inflections.

For documentation on tags selected, see:
https://github.com/brown-uk/dict_uk/blob/master/doc/tags.txt
"""

USAGE = "Usage: python convert.py <adj|noun|verb> <filename>"
from itertools import islice
import sys
from collections import defaultdict

def main():
    if len(sys.argv) != 3:
        print(USAGE)
        return

    selectors = {
        'noun': Nouns(),
        'verb': Verbs(),
        'adj': Adjectives(),
    }
    if sys.argv[1] not in selectors:
        print(USAGE)
        return

    selector = selectors[sys.argv[1]]
    
    with open(sys.argv[2]) as dict_uk:
        for line in dict_uk:
            line = line.strip()
            lexem, lemma, tags = line.split(' ')
            tags = set(tags.split(':'))

            if {'bad', 'rare', 'arch', 'alt', 'subst'}.intersection(tags):
                continue # skip errorneous, rare, achaic, non-normative and substandard forms

            selector.add(lexem, lemma, tags)

    selector.print()

class Selector:
    def __init__(self):
        self.words = defaultdict(dict)

    def print(self):
        for lemma, forms in self.words.items():
            for k, v in forms.items():
                if isinstance(v, set):
                    forms[k] = ' / '.join(sorted(v))
            print(self.format(lemma, forms))

    def add_form(self, lemma, form, lexem, variants=False):
        if form not in self.words[lemma]:
            self.words[lemma][form] = lexem
            return
        if self.words[lemma][form] != lexem:
            if variants:
                if isinstance(self.words[lemma][form], str):
                    self.words[lemma][form] = {self.words[lemma][form]}
                self.words[lemma][form].add(lexem)
            else:
                print(f"Warning: {lemma} already has form {form} with value {self.words[lemma][form]}, but trying to set it to {lexem}", file=sys.stderr)
            return

class Nouns(Selector):
    def add(self, lexem, lemma, tags):
        if 'noun' not in tags:
            return
        if tags.intersection({'lname', 'pname'}):
            return # skip last and paternal names
        if 'p' not in tags and 'v_rod' in tags: # take singular genitive
            self.add_form(lemma, 'gen.sg', lexem, variants=True)
        if 'p' in tags and 'v_naz' in tags: # and plural nominative
            self.add_form(lemma, 'pl', lexem, variants=True)

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
        if 'long' in tags or 'short' in tags:
            return # skip long and short forms, they sound a bit too sofisticated

        for form in ['m', 'n', 'f', 'p']:
            if form not in tags:
                continue
            self.add_form(lemma, form, lexem)

    def format(self, lemma, forms):
        return f"{forms.get('m', '-')} | {forms.get('n', '-')} | {forms.get('f', '-')} | {forms.get('p', '-')}"

class Verbs(Selector):
    def add(self, lexem, lemma, tags):
        if 'verb' not in tags:
            return

        if tags == {'verb', 'imperf', 'inf'}:
            self.add_form(lemma, 'imperf_inf', lexem)
        elif tags == {'verb', 'imperf', 'pres', 's', '1'}:
            self.add_form(lemma, 'present.1p.sg', lexem, variants=True)
        elif tags == {'verb', 'imperf', 'past', 'm'}:
            self.add_form(lemma, 'past', lexem, variants=True)

        elif tags == {'verb', 'perf', 'inf'}:
            self.add_form(lemma, 'perf_inf', lexem)
        elif tags == {'verb', 'perf', 'futr', 's', '1'}:
            self.add_form(lemma, 'future.1p.sg', lexem, variants=True)
        elif tags == {'verb', 'perf', 'past', 'm'}:
            self.add_form(lemma, 'past', lexem, variants=True)

    def format(self, lemma, forms):
        if 'imperf_inf' in forms:
            return f"{lemma} | {forms.get('present.1p.sg', '-')} | {forms.get('past', '-')}"
        elif 'perf_inf' in forms:
            return f"{lemma} | {forms.get('future.1p.sg', '-')} | {forms.get('past', '-')}"

if __name__ == "__main__":
    main()
