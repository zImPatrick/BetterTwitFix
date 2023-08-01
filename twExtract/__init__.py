import yt_dlp
from yt_dlp.extractor import twitter
import uuid
import json
import requests
import re
import random
from . import twExtractError
import urllib.parse
from configHandler import config
bearer="Bearer AAAAAAAAAAAAAAAAAAAAAPYXBAAAAAAACLXUNDekMxqa8h%2F40K4moUkGsoc%3DTYfbDKbT3jJPCEVnMYqilB28NHfOPqkca3qaAxGfsyKCs0wRbw"
v2Bearer="Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
guestToken=None
pathregex = r"\w{1,15}\/(status|statuses)\/(\d{2,20})"
userregex = r"^https?:\/\/(?:www\.)?twitter\.com\/(?:#!\/)?@?([^/?#]*)(?:[?#/].*)?$"
userIDregex = r"\/i\/user\/(\d+)"

v2Features='{"longform_notetweets_inline_media_enabled":true,"super_follow_badge_privacy_enabled":true,"longform_notetweets_rich_text_read_enabled":true,"super_follow_user_api_enabled":true,"super_follow_tweet_api_enabled":true,"android_graphql_skip_api_media_color_palette":true,"creator_subscriptions_tweet_preview_api_enabled":true,"freedom_of_speech_not_reach_fetch_enabled":true,"creator_subscriptions_subscription_count_enabled":true,"tweetypie_unmention_optimization_enabled":true,"longform_notetweets_consumption_enabled":true,"subscriptions_verification_info_enabled":true,"blue_business_profile_image_shape_enabled":true,"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":true,"super_follow_exclusive_tweet_notifications_enabled":true}'
v2graphql_api="2OOZWmw8nAtUHVnXXQhgaA"

def getGuestToken():
    global guestToken
    if guestToken is None:
        r = requests.post("https://api.twitter.com/1.1/guest/activate.json", headers={"Authorization":bearer})
        guestToken = json.loads(r.text)["guest_token"]
    return guestToken

def extractStatus_token(url):
    # get tweet ID
    m = re.search(pathregex, url)
    if m is None:
        raise twExtractError.TwExtractError(400, "Extract error")
    twid = m.group(2)
    if config["config"]["workaroundTokens"] == None:
        raise twExtractError.TwExtractError(400, "Extract error (no tokens defined)")
    # get tweet
    tokens = config["config"]["workaroundTokens"].split(",")
    for authToken in tokens:
        try:
            csrfToken=str(uuid.uuid4()).replace('-', '')
            tweet = requests.get("https://api.twitter.com/1.1/statuses/show/" + twid + ".json?tweet_mode=extended&cards_platform=Web-12&include_cards=1&include_reply_count=1&include_user_entities=0", headers={"Authorization":bearer,"Cookie":f"auth_token={authToken}; ct0={csrfToken}; ","x-twitter-active-user":"yes","x-twitter-auth-type":"OAuth2Session","x-twitter-client-language":"en","x-csrf-token":csrfToken,"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0"})
            output = tweet.json()
            if "errors" in output:
                # try another token
                continue
        except Exception as e:
            continue
        return output
    raise twExtractError.TwExtractError(400, "Extract error")

def extractStatus_guestToken(url):
    # get tweet ID
    m = re.search(pathregex, url)
    if m is None:
        return extractStatus_token(url)
    twid = m.group(2)
    # get guest token
    guestToken = getGuestToken()
    # get tweet
    tweet = requests.get("https://api.twitter.com/1.1/statuses/show/" + twid + ".json?tweet_mode=extended&cards_platform=Web-12&include_cards=1&include_reply_count=1&include_user_entities=0", headers={"Authorization":bearer, "x-guest-token":guestToken})
    output = tweet.json()
    if "errors" in output:
        # pick the first error and create a twExtractError
        error = output["errors"][0]
        raise twExtractError.TwExtractError(error["code"], error["message"])
    return output

def extractStatus_syndication(url):
    # https://github.com/mikf/gallery-dl/blob/46cae04aa3a113c7b6bbee1bb468669564b14ae8/gallery_dl/extractor/twitter.py#L1784
    m = re.search(pathregex, url)
    if m is None:
        raise twExtractError.TwExtractError(400, "Extract error")
    twid = m.group(2)
    tweet = requests.get("https://cdn.syndication.twimg.com/tweet-result?id=" + twid)
    
    
    if tweet.status_code == 404 or tweet.status_code == 403:
        raise twExtractError.TwExtractError(404, "Tweet not found")
    output = tweet.json()
    if "errors" in output:
        # pick the first error and create a twExtractError
        error = output["errors"][0]
        raise twExtractError.TwExtractError(error["code"], error["message"])
    
    # change returned data to match the one from the other methods
    output['full_text'] = output['text']
    output['user']['profile_image_url'] = output['user']['profile_image_url_https']
    output['retweet_count']=0
    if 'mediaDetails' in output:
        output['extended_entities'] = {'media':output['mediaDetails']}
        for media in output['extended_entities']['media']:
            media['media_url'] = media['media_url_https']
    if 'quoted_tweet' in output:
        output['quoted_status'] = output['quoted_tweet']
        quotedID=output['quoted_tweet']['id_str']
        quotedScreenName=output['quoted_tweet']['user']['screen_name']
        output['quoted_status_permalink'] = {'expanded':f"https://twitter.com/{quotedScreenName}/status/{quotedID}"}

    #output['user']['']

    return output

def extractStatusV2(url):
    # get tweet ID
    m = re.search(pathregex, url)
    if m is None:
        raise twExtractError.TwExtractError(400, "Extract error")
    twid = m.group(2)
    if config["config"]["workaroundTokens"] == None:
        raise twExtractError.TwExtractError(400, "Extract error (no tokens defined)")
    # get tweet
    tokens = config["config"]["workaroundTokens"].split(",")
    for authToken in tokens:
        try:
            csrfToken=str(uuid.uuid4()).replace('-', '')
            vars = json.loads('{"includeTweetImpression":true,"includeHasBirdwatchNotes":false,"includeEditPerspective":false,"rest_ids":["x"],"includeEditControl":true,"includeCommunityTweetRelationship":true,"includeTweetVisibilityNudge":true}')
            vars['rest_ids'][0] = str(twid)
            tweet = requests.get(f"https://twitter.com/i/api/graphql/{v2graphql_api}/TweetResultsByIdsQuery?variables={urllib.parse.quote(json.dumps(vars))}&features={urllib.parse.quote(v2Features)}", headers={"Authorization":v2Bearer,"Cookie":f"auth_token={authToken}; ct0={csrfToken}; ","x-twitter-active-user":"yes","x-twitter-auth-type":"OAuth2Session","x-twitter-client-language":"en","x-csrf-token":csrfToken,"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0"})
            if tweet.status_code == 429:
                # try another token
                continue
            try:
                rateLimitRemaining = tweet.headers.get("x-rate-limit-remaining")
                print(f"Twitter Token Rate limit remaining: {rateLimitRemaining}")
            except: # for some reason the header is not always present
                pass
            output = tweet.json()
            
            if "errors" in output:
                # try another token
                continue
            entries=output['data']['tweet_results']
            tweetEntry=None
            for entry in entries:
                result = entry['result']
                if '__typename' in result and result['__typename'] == 'TweetWithVisibilityResults':
                    result=result['tweet']
                if 'rest_id' in result and result['rest_id'] == twid:
                    tweetEntry=result
                    break
            tweet=tweetEntry
        except Exception as e:
            continue
        return tweet
    raise twExtractError.TwExtractError(400, "Extract error")

def extractStatusV2Legacy(url):
    tweet = extractStatusV2(url)
    if 'errors' in tweet or 'legacy' not in tweet:
        raise twExtractError.TwExtractError(400, "Extract error")
    tweet['legacy']['user'] = tweet["core"]["user_result"]["result"]["legacy"]
    tweet['legacy']['user']['profile_image_url'] = tweet['legacy']['user']['profile_image_url_https']
    if 'card' in tweet:
        tweet['legacy']['card'] = tweet['card']['legacy']
    if 'extended_entities' in tweet['legacy']:
        tweet['legacy']['extended_entities'] = {'media':tweet['legacy']['extended_entities']['media']}
        for media in tweet['legacy']['extended_entities']['media']:
            media['media_url'] = media['media_url_https']
    if 'tweet_card' in tweet:
        tweet['legacy']['card'] = tweet['tweet_card']['legacy']
    return tweet['legacy']

def extractStatus(url):
    methods=[extractStatus_syndication,extractStatusV2Legacy]
    for method in methods:
        try:
            return method(url)
        except twExtractError.TwExtractError as e:
            continue
    raise twExtractError.TwExtractError(400, "Extract error")

def extractUser(url):
    useId=True
    m = re.search(userIDregex, url)
    if m is None:
        m = re.search(userregex, url)
        if m is None:
            raise twExtractError.TwExtractError(400, "Invalid URL")
        else:
            useId=False
    screen_name = m.group(1)
    # get user
    tokens = config["config"]["workaroundTokens"].split(",")
    for authToken in tokens:
        try:
            csrfToken=str(uuid.uuid4()).replace('-', '')
            reqHeaders = {"Authorization":bearer,"Cookie":f"auth_token={authToken}; ct0={csrfToken}; ","x-twitter-active-user":"yes","x-twitter-auth-type":"OAuth2Session","x-twitter-client-language":"en","x-csrf-token":csrfToken,"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0"}
            if not useId:
                user = requests.get(f"https://api.twitter.com/1.1/users/show.json?screen_name={screen_name}",headers=reqHeaders)
            else:
                user = requests.get(f"https://api.twitter.com/1.1/users/show.json?user_id={screen_name}",headers=reqHeaders)
            output = user.json()
            if "errors" in output:
                # pick the first error and create a twExtractError
                error = output["errors"][0]
                raise twExtractError.TwExtractError(error["code"], error["message"])
            return output
        except Exception as e:
            continue
    raise twExtractError.TwExtractError(400, "Extract error")

#def extractUserByID(id):
    

def lambda_handler(event, context):
    if ("queryStringParameters" not in event):
        return {
            "statusCode": 400,
            "body": "Invalid request."
        }
    url = event["queryStringParameters"].get("url","")
    return {
        'statusCode': 200,
        'body': extractStatus(url)
    }