import sys
import unicodedata
import re
import nltk

from collections import Counter
from pprint import pprint as pp
from glob import glob
try: reduce
except: from functools import reduce
try:    raw_input
except: raw_input = input
 

from nltk.corpus import stopwords
from nltk.stem.porter import *

def preprocess(text):
  preprocessedText = text.lower()
  preprocessedText = re.compile("[^\w']|_").sub(" ",text)

  stop = stopwords.words('english')
  data = [i for i in preprocessedText.split() if i not in stop]

  # Porter Stemmer
  stemmer = PorterStemmer()

  stemArray = []
  for word in data:
    stemArray.append(stemmer.stem(word))

  preprocessedText = ' '.join(stemArray)
  #print preprocessedText
  return preprocessedText
 
def parsetexts(fileglob='corpus*.txt'):
    texts, words = {}, set()
    for txtfile in glob(fileglob):
        with open(txtfile, 'r') as f:
            documentText = preprocess(f.read())
            txt = documentText.split()
            words |= set(txt)
            texts[txtfile.split('\\')[-1]] = txt
    return texts, words
 
def termsearch(terms): # Searches simple inverted index
    return reduce(set.intersection,
                  (invindex[term] for term in terms),
                  set(texts.keys()))
 
texts, words = parsetexts()
print('\nTexts')
pp(texts)
print('\nWords')
pp(sorted(words))
 
 
def termsearch(terms): # Searches full inverted index
    if not set(terms).issubset(words):
        return set()
    return reduce(set.intersection,
                  (set(x[0] for x in txtindx)
                   for term, txtindx in finvindex.items()
                   if term in terms),
                  set(texts.keys()) )
 
def phrasesearch(phrase):
    wordsinphrase = phrase.strip().strip('"').split()
    if not set(wordsinphrase).issubset(words):
        return set()
    #firstword, *otherwords = wordsinphrase # Only Python 3
    firstword, otherwords = wordsinphrase[0], wordsinphrase[1:]
    found = []
    for txt in termsearch(wordsinphrase):
        # Possible text files
        for firstindx in (indx for t,indx in finvindex[firstword]
                          if t == txt):
            # Over all positions of the first word of the phrase in this txt
            if all( (txt, firstindx+1 + otherindx) in finvindex[otherword]
                    for otherindx, otherword in enumerate(otherwords) ):
                found.append(txt)
    return found
 
 
finvindex = {word:set((txt, wrdindx)
                      for txt, wrds in texts.items()
                      for wrdindx in (i for i,w in enumerate(wrds) if word==w)
                      if word in wrds)
             for word in words}
print('\nFull Inverted Index')
pp({k:sorted(v) for k,v in finvindex.items()})
 
terms = []
for x in sys.argv[1:len(sys.argv)]:
  pre = preprocess(x)
  if pre != '':
    terms.append(preprocess(x))

if len(terms) > 0:
  print('\nTerm Search on full inverted index for: ' + repr(terms))
  pp(sorted(termsearch(terms)))
else:
  print ('\nNo results')
 
phrase = (' '.join(terms))
phrase = preprocess(phrase)
if phrase != '':
  phrase = ''.join(('"',phrase,'"'))
  print('\nPhrase Search for: ' + phrase)
  print(phrasesearch(phrase))
 
  # Show multiple match capability
  print('\nPhrase Search for: ' + phrase)
  ans = phrasesearch(phrase)
  print(ans)
  ans = Counter(ans)
  print('  The phrase is found most commonly in text: ' + repr(ans.most_common(1)[0][0]))