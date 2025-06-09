# brown-uk2deuk.dictcc
A set of tools to convert data of [brown-uk/dict_uk](https://github.com/brown-uk/dict_uk/) to [deuk.dict.cc](https://deuk.dict.cc/) inflections format.

Current data is based on the VESUM v6.6.5. (c) Рисін А., Старко В. Великий електронний словник української мови (ВЕСУМ). 2005-2025.

Many thanks for their generous permission to use their dictionary data for this project.

To get data yourself, clone this and dict_uk repositories:

```
git clone https://github.com/brown-uk/dict_uk.git
git clone https://github.com/bunyk/brown-uk2deuk.dictcc.git
```

Then build dict_uk according to it's instructions depending on your system. I did:

```
cd dict_uk
docker build -t brown-uk/dict_uk .
docker run -d --name dict_uk brown-uk/dict_uk /bin/bash
docker cp dict_uk:/src/out/ ./out
docker stop dict_uk
```

This will create `dict_uk/out/out/dict_corp_lt.txt` file looking like this:

```
а а conj:coord
...
millions more of similar lines
...
ящурні ящурний adj:p:v_kly
```

Format for each line of that file is (lexem, space, lexem, space, colon separated tags).

To generate inflections for nouns, adjectives and verbs, run the following commands:

```
# generate nouns in "nom.sg | gen.sg | pl" format:
python brown-uk2deuk.dictcc/convert.py noun dict_uk/out/out/dict_corp_lt.txt | tee brown-uk2deuk.dictcc/nouns.txt

# generate adjectives in "m | n | f | pl" format:
python brown-uk2deuk.dictcc/convert.py adj dict_uk/out/out/dict_corp_lt.txt | tee brown-uk2deuk.dictcc/adjectives.txt

# generate verbs in 
#   infinitive | present.1p.sg (imperfective verbs) | past
# or
#    infinitive | future.1p.sg (perfective verbs) | past
# formats, depending on the verb aspect:
python brown-uk2deuk.dictcc/convert.py verb dict_uk/out/out/dict_corp_lt.txt | tee brown-uk2deuk.dictcc/verbs.txt
```

Currently repository based on VESUM v6.6.5 contains this many entries:

```
   86110 adjectives.txt
  173000 nouns.txt
   27198 verbs.txt
  286308 total
```
