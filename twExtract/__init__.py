import yt_dlp
from yt_dlp.extractor import twitter
import json
import requests
import re
from . import twExtractError
bearer="Bearer AAAAAAAAAAAAAAAAAAAAAPYXBAAAAAAACLXUNDekMxqa8h%2F40K4moUkGsoc%3DTYfbDKbT3jJPCEVnMYqilB28NHfOPqkca3qaAxGfsyKCs0wRbw"
guestToken=None
pathregex = r"\w{1,15}\/(status|statuses)\/(\d{2,20})"
userregex = r"^https?:\/\/(?:www\.)?twitter\.com\/(?:#!\/)?@?([^/?#]*)(?:[?#/].*)?$"
userIDregex = r"\/i\/user\/(\d+)"
def getGuestToken():
    global guestToken
    if guestToken is None:
        r = requests.post("https://api.twitter.com/1.1/guest/activate.json", headers={"Authorization":bearer})
        guestToken = json.loads(r.text)["guest_token"]
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
        tweet = requests.get("https://api.twitter.com/1.1/statuses/show/" + twid + ".json?tweet_mode=extended&cards_platform=Web-12&include_cards=1&include_reply_count=1&include_user_entities=0", headers={"Authorization":bearer, "x-guest-token":guestToken})
        output = tweet.json()
        if "errors" in output:
            # pick the first error and create a twExtractError
            error = output["errors"][0]
            raise twExtractError.TwExtractError(error["code"], error["message"])
        return output
    except Exception as e:
        return extractStatus_fallback(url)

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
    # get guest token
    guestToken = getGuestToken()
    # get user
    if not useId:
        user = requests.get(f"https://api.twitter.com/1.1/users/show.json?screen_name={screen_name}",headers={"Authorization":bearer, "x-guest-token":guestToken})
    else:
        user = requests.get(f"https://api.twitter.com/1.1/users/show.json?user_id={screen_name}",headers={"Authorization":bearer, "x-guest-token":guestToken})
    output = user.json()
    if "errors" in output:
        # pick the first error and create a twExtractError
        error = output["errors"][0]
        raise twExtractError.TwExtractError(error["code"], error["message"])
    return output

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