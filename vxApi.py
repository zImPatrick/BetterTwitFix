import html
from datetime import datetime
from configHandler import config
from utils import stripEndTCO

def getApiResponse(tweet,include_txt=False,include_rtf=False):
    tweetL = tweet["legacy"]
    if "user_result" in tweet["core"]:
        userL = tweet["core"]["user_result"]["result"]["legacy"]
    elif "user_results" in tweet["core"]:
        userL = tweet["core"]["user_results"]["result"]["legacy"]
    media=[]
    media_extended=[]
    hashtags=[]
    communityNote=None
    oldTweetVersion = False
    #editedTweet=False
    try:
        if "birdwatch_pivot" in tweet:
            if 'summary' in tweet["birdwatch_pivot"]["note"]:
                communityNote=tweet["birdwatch_pivot"]["note"]["summary"]["text"]
            elif 'subtitle' in tweet["birdwatch_pivot"] and 'text' in tweet["birdwatch_pivot"]["subtitle"]:
                communityNote=tweet["birdwatch_pivot"]["subtitle"]["text"]
    except:
        pass
    
    try:
        if "edit_control" in tweet and "edit_tweet_ids" in tweet["edit_control"]:
            #if len(tweet["edit_control"]['initial_tweet_id']) > 1:
            #    editedTweet = True
            lastEditID = tweet["edit_control"]["edit_tweet_ids"][-1]
            if lastEditID != tweet["rest_id"]:
                oldTweetVersion = True
    except:
        pass


    if "extended_entities" in tweetL:
        if "media" in tweetL["extended_entities"]:
            tmedia=tweetL["extended_entities"]["media"]
            for i in tmedia:
                extendedInfo={}
                if "video_info" in i:
                    # find the highest bitrate
                    best_bitrate = -1
                    besturl=""
                    for j in i["video_info"]["variants"]:
                        if j['content_type'] == "video/mp4" and '/hevc/' not in j["url"] and j['bitrate'] > best_bitrate:
                            besturl = j['url']
                            best_bitrate = j['bitrate']
                    if "?tag=" in besturl:
                        besturl = besturl[:besturl.index("?tag=")]
                    media.append(besturl)
                    extendedInfo["url"] = besturl
                    extendedInfo["type"] = "video"
                    if (i["type"] == "animated_gif"):
                        extendedInfo["type"] = "gif"
                    altText = None
                    extendedInfo["size"] = {"width":i["original_info"]["width"],"height":i["original_info"]["height"]}
                    if "ext_alt_text" in i:
                        altText=i["ext_alt_text"]
                    if "duration_millis" in i["video_info"]:
                        extendedInfo["duration_millis"] = i["video_info"]["duration_millis"]
                    else:
                        extendedInfo["duration_millis"] = 0
                    extendedInfo["thumbnail_url"] = i["media_url_https"]
                    extendedInfo["altText"] = altText
                    media_extended.append(extendedInfo)
                else:
                    media.append(i["media_url_https"])
                    extendedInfo["url"] = i["media_url_https"]
                    altText=None
                    if "ext_alt_text" in i:
                        altText=i["ext_alt_text"]
                    extendedInfo["altText"] = altText
                    extendedInfo["type"] = "image"
                    extendedInfo["size"] = {"width":i["original_info"]["width"],"height":i["original_info"]["height"]}
                    extendedInfo["thumbnail_url"] = i["media_url_https"]
                    media_extended.append(extendedInfo)

        if "hashtags" in tweetL["entities"]:
            for i in tweetL["entities"]["hashtags"]:
                hashtags.append(i["text"])

    #include_txt = request.args.get("include_txt", "false")
    #include_rtf = request.args.get("include_rtf", "false") # for certain types of archival software (i.e Hydrus)

    if include_txt == True or include_txt == "true" or (include_txt == "ifnomedia" and len(media)==0):
        txturl = config['config']['url']+"/"+userL["screen_name"]+"/status/"+tweet["rest_id"]+".txt"
        media.append(txturl)
        media_extended.append({"url":txturl,"type":"txt"})
    if include_rtf == True or include_rtf == "true" or (include_rtf == "ifnomedia" and len(media)==0): 
        rtfurl = config['config']['url']+"/"+userL["screen_name"]+"/status/"+tweet["rest_id"]+".rtf"
        media.append(rtfurl)
        media_extended.append({"url":rtfurl,"type":"rtf"})

    qrtURL = None
    if 'quoted_status_id_str' in tweetL:
        qrtURL = "https://twitter.com/i/status/" + tweetL['quoted_status_id_str']

    if 'possibly_sensitive' not in tweetL:
        tweetL['possibly_sensitive'] = False

    twText = html.unescape(tweetL["full_text"])

    if 'entities' in tweetL and 'urls' in tweetL['entities']:
        for eurl in tweetL['entities']['urls']:
            if "/status/" in eurl["expanded_url"] and eurl["expanded_url"].startswith("https://twitter.com/"):
                twText = twText.replace(eurl["url"], "")
            else:
                twText = twText.replace(eurl["url"],eurl["expanded_url"])
    twText = stripEndTCO(twText)

    # check if all extended media are the same type
    sameMedia = False
    if len(media_extended) > 1:
        sameMedia = True
        for i in media_extended:
            if i["type"] != media_extended[0]["type"]:
                sameMedia = False
                break
    else:
        sameMedia = True

    combinedMediaUrl = None
    if len(media_extended) > 0 and sameMedia and media_extended[0]["type"] == "image" and len(media) > 1:
        host=config['config']['url']
        combinedMediaUrl = f'{host}/rendercombined.jpg?imgs='
        for i in media:
            combinedMediaUrl += i + ","
        combinedMediaUrl = combinedMediaUrl[:-1]

    pollData = None
    card = None
    if 'card' in tweet and 'legacy' in tweet['card'] and tweet['card']['legacy']['name'].startswith("poll"):
        card = tweet['card']['legacy']
    elif 'card' in tweet and 'binding_values' in tweet['card']:
        card = tweet['card']

    if card != None:
        cardName = card['name']
        pollData={} # format: {"options":["name":"Option 1 Name","votes":5,"percent":50]}
        pollData["options"] = []
        totalVotes = 0
        bindingValues = card['binding_values']
        pollValues = {}
        for i in bindingValues:
            key = i["key"]
            value = i["value"]
            etype = value["type"]
            if etype == "STRING":
                pollValues[key] = value["string_value"]
            elif etype == "BOOLEAN":
                pollValues[key] = value["boolean_value"]
        for i in range(1,5):
            if f"choice{i}_label" in pollValues:
                option = {}
                option["name"] = pollValues[f"choice{i}_label"]
                option["votes"] = int(pollValues[f"choice{i}_count"])
                totalVotes += option["votes"]
                pollData["options"].append(option)
        for i in pollData["options"]:
            i["percent"] = round((i["votes"]/totalVotes)*100,2)
        

    apiObject = {
        "text": twText,
        "likes": tweetL["favorite_count"],
        "retweets": tweetL["retweet_count"],
        "replies": tweetL["reply_count"],
        "date": tweetL["created_at"],
        "user_screen_name": html.unescape(userL["screen_name"]),
        "user_name": userL["name"],
        "user_profile_image_url": userL["profile_image_url_https"],
        "tweetURL": "https://twitter.com/"+userL["screen_name"]+"/status/"+tweet["rest_id"],
        "tweetID": tweet["rest_id"],
        "conversationID": tweetL["conversation_id_str"],
        "mediaURLs": media,
        "media_extended": media_extended,
        "possibly_sensitive": tweetL["possibly_sensitive"],
        "hashtags": hashtags,
        "qrtURL": qrtURL,
        "communityNote": communityNote,
        "allSameType": sameMedia,
        "hasMedia": len(media) > 0,
        "combinedMediaUrl": combinedMediaUrl,
        "pollData": pollData,
    }
    try:
        apiObject["date_epoch"] = int(datetime.strptime(tweetL["created_at"], "%a %b %d %H:%M:%S %z %Y").timestamp())
    except:
        pass

    return apiObject