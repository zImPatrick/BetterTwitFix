import twitfix, cache, twExtract
from vx_testdata import *

def test_calcSyndicationToken():
    assert twExtract.calcSyndicationToken("1691389765483200513") == "43lnobuxzql"

def test_addToCache():
    cache.clearCache()
    twitfix.getTweetData(testTextTweet)
    twitfix.getTweetData(testVideoTweet)
    twitfix.getTweetData(testMediaTweet)
    twitfix.getTweetData(testMultiMediaTweet)
    #retrieve
    compareDict(testTextTweet_compare,cache.getVnfFromLinkCache(testTextTweet))
    compareDict(testVideoTweet_compare,cache.getVnfFromLinkCache(testVideoTweet))
    compareDict(testMediaTweet_compare,cache.getVnfFromLinkCache(testMediaTweet))
    compareDict(testMultiMediaTweet_compare,cache.getVnfFromLinkCache(testMultiMediaTweet))
    cache.clearCache()