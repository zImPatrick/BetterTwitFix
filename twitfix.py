from random import Random, random
from weakref import finalize
from flask import Flask, render_template, request, redirect, abort, Response, send_from_directory, url_for, send_file, make_response, jsonify
from flask_cors import CORS
import textwrap
import requests
import re
import os
import urllib.parse
import urllib.request
import combineImg
from datetime import date,datetime, timedelta
from io import BytesIO
import msgs
import twExtract as twExtract
from configHandler import config
from cache import addVnfToLinkCache,getVnfFromLinkCache
import random
app = Flask(__name__)
CORS(app)

pathregex = re.compile("\\w{1,15}\\/(status|statuses)\\/\\d{2,20}")
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
    "test"]

@app.route('/') # If the useragent is discord, return the embed, if not, redirect to configured repo directly
def default():
    user_agent = request.headers.get('user-agent')
    if user_agent in generate_embed_user_agents:
        return message("TwitFix is an attempt to fix twitter video embeds in discord! created by Robin Universe :)\n\n💖\n\nClick me to be redirected to the repo!")
    else:
        return redirect(config['config']['repo'], 301)

@app.route('/oembed.json') #oEmbed endpoint
def oembedend():
    desc  = request.args.get("desc", None)
    user  = request.args.get("user", None)
    link  = request.args.get("link", None)
    ttype = request.args.get("ttype", None)
    return  oEmbedGen(desc, user, link, ttype)

@app.route('/<path:sub_path>') # Default endpoint used by everything
def twitfix(sub_path):
    user_agent = request.headers.get('user-agent')
    match = pathregex.search(sub_path)
    print(request.url)

    if request.url.startswith("https://d.vx"): # Matches d.fx? Try to give the user a direct link
        if match.start() == 0:
            twitter_url = "https://twitter.com/" + sub_path
        if user_agent in generate_embed_user_agents:
            print( " ➤ [ D ] d.vx link shown to discord user-agent!")
            if request.url.endswith(".mp4") and "?" not in request.url:
                # TODO: Cache this, but not for too long as disk space can fill up
                if "?" not in request.url:
                    clean = twitter_url[:-4]
                else:
                    clean = twitter_url
                vid = requests.get(direct_video_link(clean))
                return Response(vid.content,mimetype="video/mp4")
            else:
                return message("To use a direct MP4 link in discord, remove anything past '?' and put '.mp4' at the end")
        else:
            print(" ➤ [ R ] Redirect to MP4 using d.fxtwitter.com")
            return dir(sub_path)
    elif request.url.startswith("https://c.vx"):
        twitter_url = sub_path

        if match.start() == 0:
            twitter_url = "https://twitter.com/" + sub_path
        
        if user_agent in generate_embed_user_agents:
            return embedCombined(twitter_url)
        else:
            print(" ➤ [ R ] Redirect to " + twitter_url)
            return redirect(twitter_url, 301)
    elif request.url.endswith(".mp4") or request.url.endswith("%2Emp4"):
        twitter_url = "https://twitter.com/" + sub_path
        
        if "?" not in request.url:
            clean = twitter_url[:-4]
        else:
            clean = twitter_url
        # TODO: Cache this, but not for too long as disk space can fill up
        vid = requests.get(direct_video_link(clean))
        return Response(vid.content,mimetype="video/mp4")

    elif request.url.endswith("/1") or request.url.endswith("/2") or request.url.endswith("/3") or request.url.endswith("/4") or request.url.endswith("%2F1") or request.url.endswith("%2F2") or request.url.endswith("%2F3") or request.url.endswith("%2F4"):
        twitter_url = "https://twitter.com/" + sub_path
        
        if "?" not in request.url:
            clean = twitter_url[:-2]
        else:
            clean = twitter_url

        image = ( int(request.url[-1]) - 1 )
        return embed_video(clean, image)

    if match is not None:
        twitter_url = sub_path

        if match.start() == 0:
            twitter_url = "https://twitter.com/" + sub_path

        if user_agent in generate_embed_user_agents:
            res = embed_video(twitter_url)
            return res

        else:
            print(" ➤ [ R ] Redirect to " + twitter_url)
            return redirect(twitter_url, 301)
    else:
        return message("This doesn't appear to be a twitter URL")

        
@app.route('/dir/<path:sub_path>') # Try to return a direct link to the MP4 on twitters servers
def dir(sub_path):
    user_agent = request.headers.get('user-agent')
    url   = sub_path
    match = pathregex.search(url)
    if match is not None:
        twitter_url = url

        if match.start() == 0:
            twitter_url = "https://twitter.com/" + url

        if user_agent in generate_embed_user_agents:
            res = embed_video(twitter_url)
            return res

        else:
            print(" ➤ [ R ] Redirect to direct MP4 URL")
            return direct_video(twitter_url)
    else:
        return redirect(url, 301)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico',mimetype='image/vnd.microsoft.icon')

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
        if not img.startswith("https://pbs.twimg.com"):
            abort(400)
    finalImg= combineImg.genImageFromURL(imgs)
    imgIo = BytesIO()
    finalImg = finalImg.convert("RGB")
    finalImg.save(imgIo, 'JPEG',quality=70)
    imgIo.seek(0)
    return send_file(imgIo, mimetype='image/jpeg')

def upgradeVNF(vnf):
    # Makes sure any VNF object passed through this has proper fields if they're added in later versions
    if 'verified' not in vnf:
        vnf['verified']=False
    return vnf

def getDefaultTTL(): # TTL for deleting items from the database
    return datetime.today().replace(microsecond=0) + timedelta(days=1)

def direct_video(video_link): # Just get a redirect to a MP4 link from any tweet link
    cached_vnf = getVnfFromLinkCache(video_link)
    if cached_vnf == None:
        try:
            vnf = link_to_vnf(video_link)
            addVnfToLinkCache(video_link, vnf)
            return redirect(vnf['url'], 301)
            print(" ➤ [ D ] Redirecting to direct URL: " + vnf['url'])
        except Exception as e:
            print(e)
            return message(msgs.failedToScan)
    else:
        return redirect(cached_vnf['url'], 301)
        print(" ➤ [ D ] Redirecting to direct URL: " + vnf['url'])

def direct_video_link(video_link): # Just get a redirect to a MP4 link from any tweet link
    cached_vnf = getVnfFromLinkCache(video_link)
    if cached_vnf == None:
        try:
            vnf = link_to_vnf(video_link)
            addVnfToLinkCache(video_link, vnf)
            return vnf['url']
            print(" ➤ [ D ] Redirecting to direct URL: " + vnf['url'])
        except Exception as e:
            print(e)
            return message(msgs.failedToScan)
    else:
        return cached_vnf['url']
        print(" ➤ [ D ] Redirecting to direct URL: " + vnf['url'])

def embed_video(video_link, image=0): # Return Embed from any tweet link
    cached_vnf = getVnfFromLinkCache(video_link)

    if cached_vnf == None:
        try:
            vnf = link_to_vnf(video_link)
            addVnfToLinkCache(video_link, vnf)
            return embed(video_link, vnf, image)

        except Exception as e:
            print(e)
            return message(msgs.failedToScan)
    else:
        vnf = upgradeVNF(vnf)
        return embed(video_link, cached_vnf, image)

def tweetInfo(url, tweet="", desc="", thumb="", uploader="", screen_name="", pfp="", tweetType="", images="", hits=0, likes=0, rts=0, time="", qrt={}, nsfw=False,ttl=None,verified=False): # Return a dict of video info with default values
    if (ttl==None):
        ttl = getDefaultTTL()
    vnf = {
        "tweet"         : tweet,
        "url"           : url,
        "description"   : desc,
        "thumbnail"     : thumb,
        "uploader"      : uploader,
        "screen_name"   : screen_name,
        "pfp"           : pfp,
        "type"          : tweetType,
        "images"        : images,
        "hits"          : hits,
        "likes"         : likes,
        "rts"           : rts,
        "time"          : time,
        "qrt"           : qrt,
        "nsfw"          : nsfw,
        "ttl"           : ttl,
        "verified"      : verified
    }
    return vnf

def get_tweet_data_from_api(video_link):
    print(" ➤ [ + ] Attempting to download tweet info from Twitter API")
    twid = int(re.sub(r'\?.*$','',video_link.rsplit("/", 1)[-1])) # gets the tweet ID as a int from the passed url
    tweet = twitter_api.statuses.show(_id=twid, tweet_mode="extended")
    #print(tweet) # For when I need to poke around and see what a tweet looks like
    return tweet

def link_to_vnf_from_tweet_data(tweet,video_link):
    imgs = ["","","","", ""]
    print(" ➤ [ + ] Tweet Type: " + tweetType(tweet))
    # Check to see if tweet has a video, if not, make the url passed to the VNF the first t.co link in the tweet
    if tweetType(tweet) == "Video":
        if tweet['extended_entities']['media'][0]['video_info']['variants']:
            best_bitrate = -1
            thumb = tweet['extended_entities']['media'][0]['media_url']
            for video in tweet['extended_entities']['media'][0]['video_info']['variants']:
                if video['content_type'] == "video/mp4" and video['bitrate'] > best_bitrate:
                    url = video['url']
                    best_bitrate = video['bitrate']
    elif tweetType(tweet) == "Text":
        url   = ""
        thumb = ""
    else:
        imgs = ["","","","", ""]
        i = 0
        for media in tweet['extended_entities']['media']:
            imgs[i] = media['media_url_https']
            i = i + 1

        #print(imgs)
        imgs[4] = str(i)
        url   = ""
        images= imgs
        thumb = tweet['extended_entities']['media'][0]['media_url_https']

    qrt = {}

    if 'quoted_status' in tweet:
        qrt['desc']       = tweet['quoted_status']['full_text']
        qrt['handle']     = tweet['quoted_status']['user']['name']
        qrt['screen_name'] = tweet['quoted_status']['user']['screen_name']
        qrt['verified'] = tweet['quoted_status']['user']['verified']

    text = tweet['full_text']

    if 'possibly_sensitive' in tweet:
        nsfw = tweet['possibly_sensitive']
    else:
        nsfw = False

    if 'entities' in tweet and 'urls' in tweet['entities']:
        for eurl in tweet['entities']['urls']:
            text = text.replace(eurl["url"],eurl["expanded_url"])

    vnf = tweetInfo(
        url, 
        video_link, 
        text, thumb, 
        tweet['user']['name'], 
        tweet['user']['screen_name'], 
        tweet['user']['profile_image_url'], 
        tweetType(tweet), 
        likes=tweet['favorite_count'], 
        rts=tweet['retweet_count'], 
        time=tweet['created_at'], 
        qrt=qrt, 
        images=imgs,
        nsfw=nsfw,
        verified=tweet['user']['verified']
        )
        
    return vnf


def link_to_vnf_from_unofficial_api(video_link):
    print(" ➤ [ + ] Attempting to download tweet info from UNOFFICIAL Twitter API")
    try:
        tweet = twExtract.extractStatus(video_link)
    except Exception as e:
        print(' ➤ [ !!! ] Local UNOFFICIAL API Failed')
        if ('apiMirrors' in config['config'] and len(config['config']['apiMirrors']) > 0):
            mirror = random.choice(config['config']['apiMirrors'])
            print(" ➤ [ + ] Using API Mirror: "+mirror)
            tweet = requests.get(mirror+"?url="+video_link).json()
    print (" ➤ [ ✔ ] Unofficial API Success")
    return link_to_vnf_from_tweet_data(tweet,video_link)


def link_to_vnf_from_api(video_link):
    tweet = get_tweet_data_from_api(video_link)
    return link_to_vnf_from_tweet_data(tweet,video_link)

def link_to_vnf(video_link): # Return a VideoInfo object or die trying
    try:
        return link_to_vnf_from_unofficial_api(video_link)
    except Exception as e:
        print(" ➤ [ !!! ] Unofficial Twitter API Failed")
        print(e)

def message(text):
    return render_template(
        'default.html', 
        message = text, 
        color   = config['config']['color'], 
        appname = config['config']['appname'], 
        repo    = config['config']['repo'], 
        url     = config['config']['url'] )

def getTemplate(template,vnf,desc,image,video_link,color,urlDesc,urlUser,urlLink,appNameSuffix=""):
    return render_template(
        template, 
        likes      = vnf['likes'], 
        rts        = vnf['rts'], 
        time       = vnf['time'], 
        screenName = vnf['screen_name'], 
        vidlink    = vnf['url'], 
        pfp        = vnf['pfp'],  
        vidurl     = vnf['url'], 
        desc       = desc,
        pic        = image,
        user       = vnf['uploader'], 
        video_link = video_link, 
        color      = color, 
        appname    = config['config']['appname'] + appNameSuffix, 
        repo       = config['config']['repo'], 
        url        = config['config']['url'], 
        urlDesc    = urlDesc, 
        urlUser    = urlUser, 
        urlLink    = urlLink,
        tweetLink  = vnf['tweet'] )

def embed(video_link, vnf, image):
    print(" ➤ [ E ] Embedding " + vnf['type'] + ": " + vnf['url'])
    
    desc    = re.sub(r' http.*t\.co\S+', '', vnf['description'])
    urlUser = urllib.parse.quote(vnf['uploader'])
    urlDesc = urllib.parse.quote(desc)
    urlLink = urllib.parse.quote(video_link)
    likeDisplay = msgs.genLikesDisplay(vnf)
    
    try:
        if vnf['type'] == "":
            desc = desc
        elif vnf['type'] == "Video":
            desc = desc
        elif vnf['qrt'] == {}: # Check if this is a QRT and modify the description
            desc = (desc + likeDisplay)
        else:
            qrtDisplay = msgs.genQrtDisplay(vnf["qrt"])
            desc = (desc + qrtDisplay +  likeDisplay)
    except:
        vnf['likes'] = 0; vnf['rts'] = 0; vnf['time'] = 0
        print(' ➤ [ X ] Failed QRT check - old VNF object')
    appNamePost = ""
    if vnf['type'] == "Text": # Change the template based on tweet type
        template = 'text.html'
    if vnf['type'] == "Image":
        if vnf['images'][4]!="1":
            appNamePost = " - Image " + str(image+1) + "/" + str(vnf['images'][4])
        image = vnf['images'][image]
        template = 'image.html'
    if vnf['type'] == "Video":
        urlDesc = urllib.parse.quote(textwrap.shorten(desc, width=220, placeholder="..."))
        template = 'video.html'
    if vnf['type'] == "":
        urlDesc  = urllib.parse.quote(textwrap.shorten(desc, width=220, placeholder="..."))
        template = 'video.html'
        
    color = "#7FFFD4" # Green

    if vnf['nsfw'] == True:
        color = "#800020" # Red
    
    return getTemplate(template,vnf,desc,image,video_link,color,urlDesc,urlUser,urlLink)


def embedCombined(video_link):
    cached_vnf = getVnfFromLinkCache(video_link)

    if cached_vnf == None:
        try:
            vnf = link_to_vnf(video_link)
            addVnfToLinkCache(video_link, vnf)
            return embedCombinedVnf(video_link, vnf)

        except Exception as e:
            print(e)
            return message(msgs.failedToScan)
    else:
        return embedCombinedVnf(video_link, cached_vnf)

def embedCombinedVnf(video_link,vnf):
    if vnf['type'] != "Image" or vnf['images'][4] == "1":
        return embed(video_link, vnf, 0)
    desc    = re.sub(r' http.*t\.co\S+', '', vnf['description'])
    urlUser = urllib.parse.quote(vnf['uploader'])
    urlDesc = urllib.parse.quote(desc)
    urlLink = urllib.parse.quote(video_link)
    likeDisplay = msgs.genLikesDisplay(vnf)

    if vnf['qrt'] == {}: # Check if this is a QRT and modify the description
            desc = (desc + likeDisplay)
    else:
        qrtDisplay=msgs.genQrtDisplay(vnf["qrt"])
        desc = (desc + qrtDisplay +  likeDisplay)

    image = "https://vxtwitter.com/rendercombined.jpg?imgs="
    for i in range(0,int(vnf['images'][4])):
        image = image + vnf['images'][i] + ","
    image = image[:-1] # Remove last comma

    color = "#7FFFD4" # Green

    if vnf['nsfw'] == True:
        color = "#800020" # Red
    return getTemplate('image.html',vnf,desc,image,video_link,color,urlDesc,urlUser,urlLink,appNameSuffix=" - View original tweet for full quality")


def tweetType(tweet): # Are we dealing with a Video, Image, or Text tweet?
    if 'extended_entities' in tweet:
        if 'video_info' in tweet['extended_entities']['media'][0]:
            out = "Video"
        else:
            out = "Image"
    else:
        out = "Text"

    return out


def oEmbedGen(description, user, video_link, ttype):
    out = {
            "type"          : ttype,
            "version"       : "1.0",
            "provider_name" : config['config']['appname'],
            "provider_url"  : config['config']['repo'],
            "title"         : description,
            "author_name"   : user,
            "author_url"    : video_link
            }

    return out

if __name__ == "__main__":
    app.config['SERVER_NAME']='localhost:80'
    app.run(host='0.0.0.0')
