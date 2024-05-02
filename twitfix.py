from weakref import finalize
from flask import Flask, render_template, request, redirect, abort, Response, send_from_directory, url_for, send_file, make_response, jsonify
from flask_cors import CORS
import re
import os
import combineImg
from io import BytesIO, StringIO
import msgs
import twExtract as twExtract
from configHandler import config
from cache import addVnfToLinkCache,getVnfFromLinkCache
from yt_dlp.utils import ExtractorError
import vxlogging as log
from utils import getTweetIdFromUrl, pathregex
from vxApi import getApiResponse
from urllib.parse import urlparse 
app = Flask(__name__)
CORS(app)
user_agent=""

generate_embed_user_agents = [
    "facebookexternalhit/1.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36",
    "Mozilla/5.0 (Windows; U; Windows NT 10.0; en-US; Valve Steam Client/default/1596241936; ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36",
    "Mozilla/5.0 (Windows; U; Windows NT 10.0; en-US; Valve Steam Client/default/0; ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36", 
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/601.2.4 (KHTML, like Gecko) Version/9.0.1 Safari/601.2.4 facebookexternalhit/1.1 Facebot Twitterbot/1.0", 
    "facebookexternalhit/1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; Valve Steam FriendsUI Tenfoot/0; ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36", 
    "Slackbot-LinkExpanding 1.0 (+https://api.slack.com/robots)", 
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:38.0) Gecko/20100101 Firefox/38.0", 
    "Mozilla/5.0 (compatible; Discordbot/2.0; +https://discordapp.com)", 
    "TelegramBot (like TwitterBot)", 
    "Mozilla/5.0 (compatible; January/1.0; +https://gitlab.insrt.uk/revolt/january)", 
    "Synapse (bot; +https://github.com/matrix-org/synapse)",
    "Iframely/1.3.1 (+https://iframely.com/docs/about)",
    "test"]

def isValidUserAgent(user_agent):
    return True
    if user_agent in generate_embed_user_agents:
        return True
    elif "WhatsApp/" in user_agent:
        return True
    return False

def message(text):
    return render_template(
        'default.html', 
        message = text, 
        color   = config['config']['color'], 
        appname = config['config']['appname'], 
        repo    = config['config']['repo'], 
        url     = config['config']['url'] )

def renderImageTweetEmbed(tweetData,image,appnameSuffix=""):
    qrt = tweetData['qrt']
    pollData = None
    embedDesc = msgs.formatEmbedDesc("Image",tweetData['text'],qrt,pollData,msgs.genLikesDisplay(tweetData))
    return render_template("image.html",
                    tweet=tweetData,
                    pic=[image],
                    host=config['config']['url'],
                    desc=embedDesc,
                    tweetLink=f'https://twitter.com/{tweetData["user_screen_name"]}/status/{tweetData["tweetID"]}',
                    appname=config['config']['appname']+appnameSuffix,
                    )

def renderVideoTweetEmbed(tweetData,mediaInfo,appnameSuffix=""):
    qrt = tweetData['qrt']
    pollData = None
    embedDesc = msgs.formatEmbedDesc("Video",tweetData['text'],qrt,pollData,msgs.genLikesDisplay(tweetData))
    return render_template("video.html",
                    tweet=tweetData,
                    media=mediaInfo,
                    host=config['config']['url'],
                    desc=embedDesc,
                    tweetLink=f'https://twitter.com/{tweetData["user_screen_name"]}/status/{tweetData["tweetID"]}',
                    appname=config['config']['appname']+appnameSuffix,
                    )

def renderTextTweetEmbed(tweetData,appnameSuffix=""):
    qrt = tweetData['qrt']
    pollData = None
    embedDesc = msgs.formatEmbedDesc("Text",tweetData['text'],qrt,pollData,msgs.genLikesDisplay(tweetData))
    return render_template("text.html",
                    tweet=tweetData,
                    host=config['config']['url'],
                    desc=embedDesc,
                    tweetLink=f'https://twitter.com/{tweetData["user_screen_name"]}/status/{tweetData["tweetID"]}',
                    appname=config['config']['appname']+appnameSuffix,
                    )

@app.route('/robots.txt')
def robots():
    return "User-agent: *\nDisallow: /"

@app.route('/') # If the useragent is discord, return the embed, if not, redirect to configured repo directly
def default():
    return redirect(config['config']['repo'], 301)

@app.route('/oembed.json') #oEmbed endpoint
def oembedend():
    desc  = request.args.get("desc", None)
    user  = request.args.get("user", None)
    link  = request.args.get("link", None)
    ttype = request.args.get("ttype", None)
    provName = request.args.get("provider",None)
    return  oEmbedGen(desc, user, link, ttype,providerName=provName)

def getTweetData(twitter_url):
    cachedVNF = getVnfFromLinkCache(twitter_url)
    if cachedVNF is not None:
        return cachedVNF
    
    try:
        rawTweetData = twExtract.extractStatusV2Anon(twitter_url)
    except:
        rawTweetData = None
    if rawTweetData is None:
        rawTweetData = twExtract.extractStatusV2(twitter_url,workaroundTokens=config['config']['workaroundTokens'].split(','))
    if 'error' in rawTweetData:
        return None

    if rawTweetData is None:
        return None
    tweetData = getApiResponse(rawTweetData)
    if tweetData is None:
        return None
    addVnfToLinkCache(twitter_url,tweetData)
    return tweetData

def determineEmbedTweet(tweetData):
    # Determine which tweet, i.e main or QRT, to embed the media from.
    # if there is no QRT, return the main tweet => default behavior
    # if both don't have media, return the main tweet => embedding qrt text will be handled in the embed description
    # if both have media, return the main tweet => priority is given to the main tweet's media
    # if only the QRT has media, return the QRT => show the QRT's media, not the main tweet's
    # if only the main tweet has media, return the main tweet => show the main tweet's media, embedding QRT text will be handled in the embed description
    if tweetData['qrt'] is None:
        return tweetData
    if tweetData['qrt']['hasMedia'] and not tweetData['hasMedia']:
        return tweetData['qrt']
    return tweetData

@app.route('/<path:sub_path>') # Default endpoint used by everything
def twitfix(sub_path):
    match = pathregex.search(sub_path)
    if match is None:
        abort(404)
    twitter_url = f'https://twitter.com/i/status/{getTweetIdFromUrl(sub_path)}'

    tweetData = getTweetData(twitter_url)
    if tweetData is None:
        return message(msgs.failedToScan)
    qrt = None
    if 'qrtURL' in tweetData and tweetData['qrtURL'] is not None:
        qrt = getTweetData(tweetData['qrtURL'])
    tweetData['qrt'] = qrt
    ###return tweetData

    embedIndex = -1
    # if url ends with /1, /2, /3, or /4, we'll use that as the index
    if sub_path[-2:] in ["/1","/2","/3","/4"]:
        embedIndex = int(sub_path[-1])-1
        sub_path = sub_path[:-2]
    if request.url.startswith("https://api.vx"): # Directly return the API response if the request is from the API
        return tweetData
    elif request.url.startswith("https://d.vx"): # direct embed
        # direct embeds should always prioritize the main tweet, so don't check for qrt
        # determine what type of media we're dealing with
        if not tweetData['hasMedia'] and qrt is None:
            return renderTextTweetEmbed(tweetData)
        elif tweetData['allSameType'] and tweetData['media_extended'][0]['type'] == "image" and embedIndex == -1 and tweetData['combinedMediaUrl'] != None:
            return redirect(tweetData['combinedMediaUrl'], 302)
        else:
            # this means we have mixed media or video, and we're only going to embed one
            if embedIndex == -1: # if the user didn't specify an index, we'll just use the first one
                embedIndex = 0
            media = tweetData['media_extended'][embedIndex]
            if media['type'] == "image":
                return redirect(media['url'], 302)
            elif media['type'] == "video" or media['type'] == "animated_gif":
                return redirect(media['url'], 302) # TODO: might not work
    else: # full embed
        embedTweetData = determineEmbedTweet(tweetData)
        if not embedTweetData['hasMedia']:
            return renderTextTweetEmbed(tweetData)
        elif embedTweetData['allSameType'] and embedTweetData['media_extended'][0]['type'] == "image" and embedIndex == -1 and embedTweetData['combinedMediaUrl'] != None:
            return renderImageTweetEmbed(tweetData,embedTweetData['combinedMediaUrl'],appnameSuffix=" - See original tweet for full quality")
        else:
            # this means we have mixed media or video, and we're only going to embed one
            if embedIndex == -1: # if the user didn't specify an index, we'll just use the first one
                embedIndex = 0
            media = embedTweetData['media_extended'][embedIndex]
            if media['type'] == "image":
                return renderImageTweetEmbed(tweetData,media['url'] , appnameSuffix=f' - Media {embedIndex+1}/{len(embedTweetData["media_extended"])}')
            elif media['type'] == "video" or media['type'] == "animated_gif":
                return renderVideoTweetEmbed(tweetData,media)

    return tweetData

@app.route('/favicon.ico')
def favicon(): # pragma: no cover
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico',mimetype='image/vnd.microsoft.icon')

@app.route('/apple-touch-icon.png')
def apple_touch_icon(): # pragma: no cover
    return send_from_directory(os.path.join(app.root_path, 'static'), 'apple-touch-icon.png',mimetype='image/png')

@app.route("/rendercombined.jpg")
def rendercombined():
    # get "imgs" from request arguments
    imgs = request.args.get("imgs", "")

    if 'combination_method' in config['config'] and config['config']['combination_method'] != "local":
        url = config['config']['combination_method'] + "/rendercombined.jpg?imgs=" + imgs
        return redirect(url, 302)
    # Redirecting here instead of setting the embed URL directly to this because if the config combination_method changes in the future, old URLs will still work

    imgs = imgs.split(",")
    if (len(imgs) == 0 or len(imgs)>4):
        abort(400)
    #check that each image starts with "https://pbs.twimg.com"
    for img in imgs:
        result = urlparse(img)
        if result.hostname != "pbs.twimg.com" or result.scheme != "https":
            abort(400)
    finalImg= combineImg.genImageFromURL(imgs)
    imgIo = BytesIO()
    finalImg = finalImg.convert("RGB")
    finalImg.save(imgIo, 'JPEG',quality=70)
    imgIo.seek(0)
    return send_file(imgIo, mimetype='image/jpeg',max_age=86400)

def oEmbedGen(description, user, video_link, ttype,providerName=None):
    if providerName == None:
        providerName = config['config']['appname']
    out = {
            "type"          : ttype,
            "version"       : "1.0",
            "provider_name" : providerName,
            "provider_url"  : config['config']['repo'],
            "title"         : description,
            "author_name"   : user,
            "author_url"    : video_link
            }

    return out

if __name__ == "__main__":
    app.config['SERVER_NAME']='localhost:80'
    app.run(host='0.0.0.0')
