#!/usr/bin/env python

# http://katazen.blogspot.com/2014/04/006-python-cookbook-01-09-finding-common.html
# http://katazen.blogspot.com/2014/04/006-python-cookbook-01-12-most.html

# http://stackoverflow.com/questions/743806/split-string-into-a-list-in-python
# http://www.saltycrane.com/blog/2007/09/how-to-sort-python-dictionary-by-keys/

from collections import Counter

def parseText2TokenList(stringin):
  for i in stringin.split():
    i = i.strip(';,.\'').lower()
    yield i

def dumpTokenBy_TopN_CountAtLeastM(listin, topN, countM):
  for (key, value) in Counter(listin).most_common(topN):
    if value >= countM:
      yield (key, value)
  
def sumValueByKeyOnDict(dicta, dictb):
  dictOut = dict()
  for i in dicta.keys():
    if dictb.has_key(i):
      dictOut[i] = dicta[i] + dictb[i]
    else:
      dictOut[i] = dicta[i]
  for i in dictb.keys():
    if not dicta.has_key(i):
      dictOut[i] = dictb[i]
  return dictOut

if __name__ == "__main__":
  
  articalText1 = """As a news aggregator site, Google uses its own software to
  determine which stories to show from the online news sources it watches.
  Human editorial input does come into the system, however, in choosing
  exactly which sources Google News will pick from. This is where some of
  the controversy over Google News originates, when some news sources are
  included when visitors feel they don't deserve it, and when other news 
  sources are excluded when visitors feel they ought to be included.
  For examples, see the above mentions of Indymedia, or National Vanguard."""
  
  articalText2 = """The actual list of sources is not known outside of Google.
   The stated information from Google is that it watches more than 4,500
  English-language news sites. In the absence of a list, many independent
  sites have come up with their own ways of determining Google's news sources
  , as in the chart below."""
  
  print "---------- run 1: select top 10, shows 3 times at least"
  art1WordList = list(parseText2TokenList(articalText1))
  art1TopToken = dict(dumpTokenBy_TopN_CountAtLeastM(art1WordList, 10, 3))
  print art1TopToken
  
  print "---------- run 2: select top 10, shows 3 times at least"
  art2WordList = list(parseText2TokenList(articalText2))
  art2TopToken = dict(dumpTokenBy_TopN_CountAtLeastM(art2WordList, 10, 3))
  print art2TopToken
  
  print "---------- Sum"
  artSum = sumValueByKeyOnDict(art1TopToken, art2TopToken)
  print artSum
  
  # dump for post-process
  print "---------- CSV"
  for key, value in reversed(sorted(artSum.iteritems(), key=lambda (k,v): (v,k))):
    print "%s,%s" % (key, value)