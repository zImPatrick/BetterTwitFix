import yt_dlp
from yt_dlp.extractor import twitter
import uuid
import json
import requests
import re
import random
from . import twExtractError
from configHandler import config
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
    try:
        # get tweet ID
        m = re.search(pathregex, url)
        if m is None:
            raise twExtractError.TwExtractError(400, "Extract error")
        twid = m.group(2)
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
    except Exception as e:
        raise twExtractError.TwExtractError(400, "Extract error")


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