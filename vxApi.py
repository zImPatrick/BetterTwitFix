import html
from datetime import datetime
from configHandler import config

def getApiResponse(tweet,include_txt=False,include_zip=False):
    tweetL = tweet["legacy"]
    if "user_result" in tweet["core"]:
        userL = tweet["core"]["user_result"]["result"]["legacy"]
    elif "user_results" in tweet["core"]:
        userL = tweet["core"]["user_results"]["result"]["legacy"]
    media=[]
    media_extended=[]
    hashtags=[]
    communityNote=None
    try:
        if "birdwatch_pivot" in tweet:
            communityNote=tweet["birdwatch_pivot"]["note"]["summary"]["text"]
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
    #include_zip = request.args.get("include_zip", "false") # for certain types of archival software (i.e Hydrus)

    if include_txt == "true" or (include_txt == "ifnomedia" and len(media)==0):
        txturl = config['config']['url']+"/"+userL["screen_name"]+"/status/"+tweet["rest_id"]+".txt"
        media.append(txturl)
        media_extended.append({"url":txturl,"type":"txt"})
    if include_zip == "true" or (include_zip == "ifnomedia" and len(media)==0): 
        zipurl = config['config']['url']+"/"+userL["screen_name"]+"/status/"+tweet["rest_id"]+".zip"
        media.append(zipurl)
        media_extended.append({"url":zipurl,"type":"zip"})

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
        "communityNote": communityNote
    }
    try:
        apiObject["date_epoch"] = int(datetime.strptime(tweetL["created_at"], "%a %b %d %H:%M:%S %z %Y").timestamp())
    except:
        pass

    return apiObject