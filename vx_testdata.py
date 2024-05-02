import os

# autogenerated from testgen.py
testTextTweet="https://twitter.com/jack/status/20"
testVideoTweet="https://twitter.com/pdxdylan/status/1540398733669666818"
testMediaTweet="https://twitter.com/pdxdylan/status/1534672932106035200"
testMultiMediaTweet="https://twitter.com/pdxdylan/status/1532006436703715331"
testQRTTweet="https://twitter.com/pdxdylan/status/1611477137319514129"
testQrtCeptionTweet="https://twitter.com/CatherineShu/status/585253766271672320"
testQrtVideoTweet="https://twitter.com/pdxdylan/status/1674561759422578690"
testNSFWTweet="https://twitter.com/kuyacoy/status/1581185279376838657"
testPollTweet="https://twitter.com/norm/status/651169346518056960"
testMixedMediaTweet="https://twitter.com/bigbeerfest/status/1760638922084741177"

testTextTweet_compare={'text': 'just setting up my twttr', 'date': 'Tue Mar 21 20:50:14 +0000 2006', 'tweetURL': 'https://twitter.com/jack/status/20', 'tweetID': '20', 'conversationID': '20', 'mediaURLs': [], 'media_extended': [], 'possibly_sensitive': False, 'hashtags': [], 'qrtURL': None, 'allSameType': True, 'hasMedia': False, 'combinedMediaUrl': None, 'pollData': None, 'date_epoch': 1142974214}
testVideoTweet_compare={'text': 'TikTok embeds on Discord/Telegram bait you with a fake play button, but to see the actual video you have to go to their website.\nAs a request from a friend, I made it so that if you add "vx" before "tiktok" on any link, it fixes that. https://t.co/QYpiVXUIrW', 'date': 'Fri Jun 24 18:17:31 +0000 2022', 'tweetURL': 'https://twitter.com/pdxdylan/status/1540398733669666818', 'tweetID': '1540398733669666818', 'conversationID': '1540398733669666818', 'mediaURLs': ['https://video.twimg.com/ext_tw_video/1540396699037929472/pu/vid/762x528/YxbXbT3X7vq4LWfC.mp4?tag=12'], 'media_extended': [{'url': 'https://video.twimg.com/ext_tw_video/1540396699037929472/pu/vid/762x528/YxbXbT3X7vq4LWfC.mp4?tag=12', 'type': 'video', 'size': {'width': 762, 'height': 528}, 'duration_millis': 13650, 'thumbnail_url': 'https://pbs.twimg.com/ext_tw_video_thumb/1540396699037929472/pu/img/l187Z6B9AHHxUKPV.jpg', 'altText': None}], 'possibly_sensitive': False, 'hashtags': [], 'qrtURL': None, 'allSameType': True, 'hasMedia': True, 'combinedMediaUrl': None, 'pollData': None, 'date_epoch': 1656094651}
testMediaTweet_compare={'text': 'oh.', 'date': 'Wed Jun 08 23:05:14 +0000 2022', 'tweetURL': 'https://twitter.com/pdxdylan/status/1534672932106035200', 'tweetID': '1534672932106035200', 'conversationID': '1534672673422381057', 'mediaURLs': ['https://pbs.twimg.com/media/FUxAt5LWUAMol0N.png'], 'media_extended': [{'url': 'https://pbs.twimg.com/media/FUxAt5LWUAMol0N.png', 'altText': None, 'type': 'image', 'size': {'width': 927, 'height': 534}, 'thumbnail_url': 'https://pbs.twimg.com/media/FUxAt5LWUAMol0N.png'}], 'possibly_sensitive': False, 'hashtags': [], 'qrtURL': None, 'allSameType': True, 'hasMedia': True, 'combinedMediaUrl': None, 'pollData': None, 'date_epoch': 1654729514}
testMultiMediaTweet_compare={'text': 'Released #Retro64 1.0.9. Besides a lot of internal bug-fixes, this adds quicksand blocks, fixes the rendering for the castle stairs block, and adds a new model, Sonic! \nhttps://github.com/Retro64Mod/Retro64Mod/releases/tag/1.18.2-1.0.9 https://t.co/CWZaw4hzyg', 'date': 'Wed Jun 01 14:29:32 +0000 2022', 'tweetURL': 'https://twitter.com/pdxdylan/status/1532006436703715331', 'tweetID': '1532006436703715331', 'conversationID': '1532006436703715331', 'mediaURLs': ['https://pbs.twimg.com/media/FULF9oxXwAMDI-C.png', 'https://pbs.twimg.com/media/FULGaHkWYAIBV5U.png', 'https://pbs.twimg.com/media/FULGiZnWQAMBRWl.png'], 'media_extended': [{'url': 'https://pbs.twimg.com/media/FULF9oxXwAMDI-C.png', 'altText': None, 'type': 'image', 'size': {'width': 507, 'height': 507}, 'thumbnail_url': 'https://pbs.twimg.com/media/FULF9oxXwAMDI-C.png'}, {'url': 'https://pbs.twimg.com/media/FULGaHkWYAIBV5U.png', 'altText': None, 'type': 'image', 'size': {'width': 396, 'height': 431}, 'thumbnail_url': 'https://pbs.twimg.com/media/FULGaHkWYAIBV5U.png'}, {'url': 'https://pbs.twimg.com/media/FULGiZnWQAMBRWl.png', 'altText': None, 'type': 'image', 'size': {'width': 399, 'height': 341}, 'thumbnail_url': 'https://pbs.twimg.com/media/FULGiZnWQAMBRWl.png'}], 'possibly_sensitive': False, 'hashtags': ['Retro64'], 'qrtURL': None, 'allSameType': True, 'hasMedia': True, 'combinedMediaUrl': 'https://vxtwitter.com/rendercombined.jpg?imgs=https://pbs.twimg.com/media/FULF9oxXwAMDI-C.png,https://pbs.twimg.com/media/FULGaHkWYAIBV5U.png,https://pbs.twimg.com/media/FULGiZnWQAMBRWl.png', 'pollData': None, 'date_epoch': 1654093772}
testQRTTweet_compare={'text': "vxTwitter has gotten a *ton* of usage recently, so I'd appreciate a donation to keep things running!\n", 'date': 'Fri Jan 06 21:37:43 +0000 2023', 'tweetURL': 'https://twitter.com/pdxdylan/status/1611477137319514129', 'tweetID': '1611477137319514129', 'conversationID': '1611476665821003776', 'mediaURLs': [], 'media_extended': [], 'possibly_sensitive': False, 'hashtags': [], 'qrtURL': 'https://twitter.com/i/status/1518309187515781125', 'allSameType': True, 'hasMedia': False, 'combinedMediaUrl': None, 'pollData': None, 'date_epoch': 1673041063}
testQrtCeptionTweet_compare={'text': 'Testing retweetception ', 'date': 'Tue Apr 07 01:32:26 +0000 2015', 'tweetURL': 'https://twitter.com/CatherineShu/status/585253766271672320', 'tweetID': '585253766271672320', 'conversationID': '585253766271672320', 'mediaURLs': [], 'media_extended': [], 'possibly_sensitive': False, 'hashtags': [], 'qrtURL': 'https://twitter.com/i/status/585253161260216320', 'allSameType': True, 'hasMedia': False, 'combinedMediaUrl': None, 'pollData': None, 'date_epoch': 1428370346}
testQrtVideoTweet_compare={'text': 'good', 'date': 'Thu Jun 29 23:33:29 +0000 2023', 'tweetURL': 'https://twitter.com/pdxdylan/status/1674561759422578690', 'tweetID': '1674561759422578690', 'conversationID': '1674561759422578690', 'mediaURLs': [], 'media_extended': [], 'possibly_sensitive': False, 'hashtags': [], 'qrtURL': 'https://twitter.com/i/status/1674197531301904388', 'allSameType': True, 'hasMedia': False, 'combinedMediaUrl': None, 'pollData': None, 'date_epoch': 1688081609}
testNSFWTweet_compare={'text': "ngl, I'm scared on finding out the cute Sprigatito's final evolution..\n\nso i had a bot generate it for me.... and I'm forever scarred https://t.co/itMay87vcS", 'date': 'Sat Oct 15 07:28:42 +0000 2022', 'tweetURL': 'https://twitter.com/kuyacoy/status/1581185279376838657', 'tweetID': '1581185279376838657', 'conversationID': '1581185279376838657', 'mediaURLs': ['https://pbs.twimg.com/media/FfF_gKwXgAIpnpD.jpg'], 'media_extended': [{'url': 'https://pbs.twimg.com/media/FfF_gKwXgAIpnpD.jpg', 'altText': None, 'type': 'image', 'size': {'width': 760, 'height': 926}, 'thumbnail_url': 'https://pbs.twimg.com/media/FfF_gKwXgAIpnpD.jpg'}], 'possibly_sensitive': False, 'hashtags': [], 'qrtURL': None, 'allSameType': True, 'hasMedia': True, 'combinedMediaUrl': None, 'pollData': None, 'date_epoch': 1665818922}
testPollTweet_compare={'text': 'I know when that hotline bling, that can only:', 'date': 'Mon Oct 05 22:57:25 +0000 2015', 'tweetURL': 'https://twitter.com/norm/status/651169346518056960', 'tweetID': '651169346518056960', 'conversationID': '651169346518056960', 'mediaURLs': [], 'media_extended': [], 'possibly_sensitive': False, 'hashtags': [], 'qrtURL': None, 'allSameType': True, 'hasMedia': False, 'combinedMediaUrl': None, 'pollData': {'options': [{'name': 'Mean one thing', 'votes': 124875, 'percent': 78.82}, {'name': 'Mean multiple things', 'votes': 33554, 'percent': 21.18}]}, 'date_epoch': 1444085845}
testMixedMediaTweet_compare={'text': 'Some of us here are definitely big nerds about beer, and could talk your ear off about it for days on end, but some of us are just "beer is nice"', 'date': 'Thu Feb 22 12:13:24 +0000 2024', 'tweetURL': 'https://twitter.com/bigbeerfest/status/1760638922084741177', 'tweetID': '1760638922084741177', 'conversationID': '1760638922084741177', 'mediaURLs': ['https://pbs.twimg.com/media/GG8LwfuWoAANKhs.jpg', 'https://video.twimg.com/tweet_video/GG8LwqWX0AAZch0.mp4'], 'media_extended': [{'url': 'https://pbs.twimg.com/media/GG8LwfuWoAANKhs.jpg', 'altText': None, 'type': 'image', 'size': {'width': 858, 'height': 960}, 'thumbnail_url': 'https://pbs.twimg.com/media/GG8LwfuWoAANKhs.jpg'}, {'url': 'https://video.twimg.com/tweet_video/GG8LwqWX0AAZch0.mp4', 'type': 'gif', 'size': {'width': 500, 'height': 500}, 'duration_millis': 0, 'thumbnail_url': 'https://pbs.twimg.com/tweet_video_thumb/GG8LwqWX0AAZch0.jpg', 'altText': None}], 'possibly_sensitive': False, 'hashtags': [], 'qrtURL': None, 'allSameType': False, 'hasMedia': True, 'combinedMediaUrl': None, 'pollData': None, 'date_epoch': 1708604004}

testUser="https://twitter.com/jack"
testUserID = "https://twitter.com/i/user/12"
testUserWeirdURLs=["https://twitter.com/jack?lang=en","https://twitter.com/jack/with_replies","https://twitter.com/jack/media","https://twitter.com/jack/likes","https://twitter.com/jack/with_replies?lang=en","https://twitter.com/jack/media?lang=en","https://twitter.com/jack/likes?lang=en","https://twitter.com/jack/"]
testTextTweet="https://twitter.com/jack/status/20"

tokens=os.getenv("VXTWITTER_WORKAROUND_TOKENS",None).split(',')

def compareDict(original,compare):
    for key in original:
        assert key in compare
        if type(compare[key]) is not dict:
            if (key == 'verified' or key== 'time') and compare[key]!=original[key]:
                continue # does not match as test data was from before verification changes
            assert compare[key]==original[key]
        else:
            compareDict(original[key],compare[key])