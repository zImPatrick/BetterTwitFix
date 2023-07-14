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

v2Features='{"rweb_lists_timeline_redesign_enabled":true,"responsive_web_graphql_exclude_directive_enabled":true,"verified_phone_label_enabled":false,"creator_subscriptions_tweet_preview_api_enabled":true,"responsive_web_graphql_timeline_navigation_enabled":true,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,"tweetypie_unmention_optimization_enabled":true,"responsive_web_edit_tweet_api_enabled":true,"graphql_is_translatable_rweb_tweet_is_translatable_enabled":true,"view_counts_everywhere_api_enabled":true,"longform_notetweets_consumption_enabled":true,"responsive_web_twitter_article_tweet_consumption_enabled":false,"tweet_awards_web_tipping_enabled":false,"freedom_of_speech_not_reach_fetch_enabled":true,"standardized_nudges_misinfo":true,"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":true,"longform_notetweets_rich_text_read_enabled":true,"longform_notetweets_inline_media_enabled":true,"responsive_web_media_download_video_enabled":false,"responsive_web_enhance_cards_enabled":false}'
v2graphql_api="NmCeCgkVlsRGS1cAwqtgmw"
v2fieldToggles='{"withAuxiliaryUserLabels":false,"withArticleRichContentState":false}'

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
    
    
    if tweet.status_code == 404:
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
            vars = json.loads('{"focalTweetId":"x","referrer":"messages","with_rux_injections":false,"includePromotedContent":true,"withCommunity":true,"withQuickPromoteEligibilityTweetFields":true,"withBirdwatchNotes":true,"withVoice":true,"withV2Timeline":true}')
            vars['focalTweetId'] = str(twid)
            tweet = requests.get(f"https://twitter.com/i/api/graphql/{v2graphql_api}/TweetDetail?variables={urllib.parse.quote(json.dumps(vars))}&features={urllib.parse.quote(v2Features)}&fieldToggles={urllib.parse.quote(v2fieldToggles)}", headers={"Authorization":v2Bearer,"Cookie":f"auth_token={authToken}; ct0={csrfToken}; ","x-twitter-active-user":"yes","x-twitter-auth-type":"OAuth2Session","x-twitter-client-language":"en","x-csrf-token":csrfToken,"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0"})
            if tweet.status_code == 429:
                # try another token
                continue
            output = tweet.json()
            if "errors" in output:
                # try another token
                continue
            entries=output['data']['threaded_conversation_with_injections_v2']['instructions'][0]['entries']
            tweetEntry=None
            for entry in entries:
                if 'entryId' in entry and entry['entryId'] == "tweet-"+twid:
                    tweetEntry=entry
                    break
            tweet=tweetEntry["content"]["itemContent"]["tweet_results"]["result"]
            if '__typename' in tweet and tweet['__typename'] == 'TweetWithVisibilityResults':
                tweet=tweet['tweet']
        except Exception as e:
            continue
        return tweet
    raise twExtractError.TwExtractError(400, "Extract error")

def extractStatusV2Legacy(url):
    tweet = extractStatusV2(url)
    if 'errors' in tweet or 'legacy' not in tweet:
        raise twExtractError.TwExtractError(400, "Extract error")
    tweet['legacy']['user'] = tweet["core"]["user_results"]["result"]["legacy"]
    tweet['legacy']['user']['profile_image_url'] = tweet['legacy']['user']['profile_image_url_https']
    if 'card' in tweet:
        tweet['legacy']['card'] = tweet['card']['legacy']
    if 'extended_entities' in tweet['legacy']:
        tweet['legacy']['extended_entities'] = {'media':tweet['legacy']['extended_entities']['media']}
        for media in tweet['legacy']['extended_entities']['media']:
            media['media_url'] = media['media_url_https']
    return tweet['legacy']

def extractStatus(url):
    methods=[extractStatus_guestToken,extractStatus_syndication,extractStatus_token,extractStatusV2Legacy]
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