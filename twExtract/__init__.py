import yt_dlp
from yt_dlp.extractor import twitter
import json
import requests
import re
from . import twExtractError, apiConvert
import urllib

guestToken=None
graphql_api=None
pathregex = r"\w{1,15}\/(status|statuses)\/(\d{2,20})"
authToken = "Bearer AAAAAAAAAAAAAAAAAAAAAPYXBAAAAAAACLXUNDekMxqa8h%2F40K4moUkGsoc%3DTYfbDKbT3jJPCEVnMYqilB28NHfOPqkca3qaAxGfsyKCs0wRbw"
# Below token seems to block NSFW? Might be doing something wrong.. But it's the only token which returns full extended_entities objects.
# authToken = "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"

def getGuestToken(graphql_required=False):
    global guestToken
    global graphql_api
    if guestToken is None:
        r = requests.post("https://api.twitter.com/1.1/guest/activate.json", headers={"Authorization":authToken})
        guestToken = json.loads(r.text)["guest_token"]
    if graphql_required and graphql_api is None:
        r = requests.get("https://twitter.com/jack/status/20")
        response = r.text
        script_url = re.search(r"https:\/\/abs.twimg.com\/responsive-web\/client-web-legacy\/main.[a-f0-9]+.js", response)[0]
        script = requests.get(script_url).text
        graphql_api = re.search(r"{queryId:\"([a-zA-Z0-9\-_]+)\",operationName:\"TweetDetail\",operationType:\"query\"", script, re.M)[1]
    return guestToken

def extractStatus_fallback(url):
    twIE = twitter.TwitterIE()
    twIE.set_downloader(yt_dlp.YoutubeDL())
    twid = twIE._match_id(url)
    status = twIE._call_api(
    'statuses/show/%s.json' % twid, twid, {
        'cards_platform': 'Web-12',
        'include_cards': 1,
        'include_reply_count': 1,
        'include_user_entities': 0,
        'tweet_mode': 'extended',
    })
    return status

def extractStatusv2(url, nsfw=False):
    # get tweet ID
    m = re.search(pathregex, url)
    if m is None:
        raise twExtractError.TwExtractError(400, "Invalid URL")
    twid = m.group(2)
    # get guest token
    guestToken = getGuestToken(True)
    # get tweet
    variables = {
        "focalTweetId": twid,
        "with_rux_injections": False,
        "includePromotedContent": False,
        "withCommunity": False,
        "withQuickPromoteEligibilityTweetFields": False,
        "withBirdwatchNotes": False,
        "withSuperFollowsUserFields": False,
        "withDownvotePerspective": False,
        "withReactionsMetadata": False,
        "withReactionsPerspective": False,
        "withSuperFollowsTweetFields": False,
        "withVoice": False,
        "withV2Timeline": True
    }
    features = {"verified_phone_label_enabled":False,"responsive_web_graphql_timeline_navigation_enabled":False,"unified_cards_ad_metadata_container_dynamic_card_content_query_enabled":False,"tweetypie_unmention_optimization_enabled":False,"responsive_web_uc_gql_enabled":False,"vibe_api_enabled":False,"responsive_web_edit_tweet_api_enabled":True,"graphql_is_translatable_rweb_tweet_is_translatable_enabled":False,"standardized_nudges_misinfo":False,"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":False,"interactive_text_enabled":False,"responsive_web_text_conversations_enabled":False,"responsive_web_enhance_cards_enabled":False}
    r = requests.get(f"https://twitter.com/i/api/graphql/{graphql_api}/TweetDetail?variables={urllib.parse.quote(json.dumps(variables))}&features={urllib.parse.quote(json.dumps(features))}", headers={"Authorization":authToken, "x-guest-token":guestToken})
    output = r.json()
    if "errors" in output:
        # pick the first error and create a twExtractError
        error = output["errors"][0]
        if "No status found with that ID" in error["message"] or 'suspended' in error["message"]:
            raise twExtractError.TwExtractError(error["code"], error["message"])
    for tweet in output["data"]["threaded_conversation_with_injections_v2"]["instructions"][0]["entries"]:
        if tweet["entryId"] == f"tweet-{twid}":
            if 'tombstone' in tweet["content"]["itemContent"]["tweet_results"]["result"] and 'Age-restricted' in tweet["content"]["itemContent"]["tweet_results"]["result"]['tombstone']['text']['text']:
                return extractStatus_fallback(url)
            return apiConvert.convertTweet(tweet["content"]["itemContent"]["tweet_results"]["result"])

    return None

def extractStatus(url):
    try:
        # get tweet ID
        m = re.search(pathregex, url)
        if m is None:
            return extractStatus_fallback(url)
        twid = m.group(2)
        # get guest token
        guestToken = getGuestToken()
        # get tweet
        tweet = requests.get("https://api.twitter.com/1.1/statuses/show/" + twid + ".json?tweet_mode=extended&cards_platform=Web-12&include_cards=1&include_reply_count=1&include_user_entities=0", headers={"Authorization":authToken, "x-guest-token":guestToken})
        output = tweet.json()
        if "errors" in output:
            # pick the first error and create a twExtractError
            error = output["errors"][0]
            raise twExtractError.TwExtractError(error["code"], error["message"])
        return output
    except Exception as e:
        return extractStatus_fallback(url)

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