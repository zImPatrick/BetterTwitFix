# vxTwitter
(A fork of TwitFix)
Basic flask server that serves fixed twitter video embeds to desktop discord by using either the Twitter API or Youtube-DL to grab tweet video information. This also automatically embeds the first link in the text of non video tweets (API Only)

## Differences from fxtwitter
fxtwitter exposed all recently processed tweets publicly via a "latest" and "top" page.

Even though Tweets are public, it was a personal concern for me that a tweet with potentially sensitive information in it could suddenly be shown to however many people were browsing the latest tweets page, and could be used as a tool for harassment. This was removed in [The following commit](https://github.com/dylanpdx/BetterTwitFix/commit/87ba86ba502e73ddb370bd4e5b964548d3272400#diff-a11c36d9b2d53672d6b3d781dca5bef9129159947de66bc3ffaec5fab389d80cL115)

Additionally, vxTwitter has a 'none' cache option, which is intended to be used behind a service like CloudFlare. vxtwitter.com currently runs with this option enabled to protect user privacy. 
## How to use the hosted version

Just replace twitter.com with vxtwitter.com on the link to the tweet! `https://twitter.com/jack/status/20` -> `https://vxtwitter.com/jack/status/20`

## API
If you're a nerd like me and want to use information about a tweet in your code, you can make a request to `api.vxtwitter.com` to get basic information about a tweet:
`https://api.vxtwitter.com/Twitter/status/1263145271946551300`
```json
{
    "date": "Wed May 20 16:31:15 +0000 2020",
    "date_epoch": 1589992275,
    "hashtags": [],
    "likes": 60038,
    "mediaURLs": [
        "https://video.twimg.com/amplify_video/1263145212760805376/vid/1280x720/9jous8HM0_duxL0w.mp4?tag=13"
    ],
    "replies": 11720,
    "retweets": 16729,
    "text": "Testing, testing...\n\nA new way to have a convo with exactly who you want. We’re starting with a small % globally, so keep your 👀 out to see it in action. https://t.co/pV53mvjAVT",
    "tweetID": "1263145271946551300",
    "tweetURL": "https://twitter.com/Twitter/status/1263145271946551300",
    "user_name": "Twitter",
    "user_screen_name": "Twitter"
}
```
#

**Note**: If you enjoy this service, please considering donating via [Ko-Fi](https://ko-fi.com/dylanpdx) to help cover server costs

I do not monitor any tweets processed by this server. Additionally, if you plan on hosting the code yourself and are concerned about this, be sure to check how to disable logging on the web server you are using (i.e Nginx)

## How to host
### Ubuntu Linux Server
The following instructions were tested with Ubuntu 22.10, and assumes a stock OS

Edit config.json to fit your setup

First, get everything updated by running `sudo apt-get update`

Verify Python is installed by running `python3 --version` or `python --version`. Versions 3.8, 3.9, and 3.10 are supported (This includes versions like 3.10.7)

Run the following command: `git clone https://github.com/dylanpdx/BetterTwitFix`
This will download all the code for vxTwitter. Once that is done, you can run `cd BetterTwitFix` to enter the newly downloaded folder. 

Install pip and venv by running the following command: `apt install python3-pip python3-venv`

Create a virtual enviornment for all of BetterTwitFix's dependencies to live in by running `python3 -m venv venv` and then `source venv/bin/activate`

After that completes, install all the requirements for BetterTwitFix by running `pip3 install -r requirements.txt` and then `pip3 install uwsgi`

Test that everything is correct by running `python3 twitfix.py`. If all worked out well you should see a message that says it's running! You're not done yet though! Press CTRL+C to exit out of that for now.

Edit the twitfix.service file. You can use nano for this by running `nano twitfix.service`

Edit the variables under the [Service] secton. User and Group will need to be changed to the user you want to run this under, and WorkingDirectory, Environment, and ExecStart will all need to have `/home/dylan/BetterTwitFix` replaced with the directory you downloaded the code to. After that, you can save & exit the file (`CTRL+X then Y` on nano) and copy it to your system services by running `sudo cp twitfix.service /etc/systemd/system/`

Finally, get everything going by running `systemctl start twitfix` and `systemctl enable twitfix`

this script uses the youtube-dl python module, along with flask, twitter and pymongo, so install those with pip (you can use `pip install -r requirements.txt`) and start the server with `python twitfix.py`

After that, you need to set up an nginx proxy to point towards `/tmp/twitfix.sock`, which isn't covered here.

### Docker Setup
The following instructions were tested with Ubuntu 22.10, and assumes a stock OS

Edit config.json to fit your setup

First, install docker by following these instructions: [Install using the apt repository](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository) 

Run the following command: `git clone https://github.com/dylanpdx/BetterTwitFix`
This will download all the code for vxTwitter. Once that is done, you can run `cd BetterTwitFix` to enter the newly downloaded folder. 

Remove the following lines in twitfix.ini:
```ini
socket = /var/run/twitfix.sock
chmod-socket = 660
```
and replace with
```ini
socket = 0.0.0.0:9000
buffer-size = 8192
```

Finally, run this command to set up everything through Docker: `docker-compose up -d --build`

### Serverless Setup
This assumes your AWS credentials are set up

Run the following command: `git clone https://github.com/dylanpdx/BetterTwitFix`

Enter into that directory and install serverless framework into it by running `npm install -g serverless`

Then run `serverless deploy`

Finally, set up a new API gateway resource to point towards the main Lambda function (should start with vxTwitter) 

## Config

vxTwitter generates a config.json in its root directory the first time you run it, the options are:

**API** - This will be where you put the credentials for your twitter API if you use this method

**database** - This is where you put the URL to your mongoDB database if you are using one

**link_cache** - (Options: **db**, **json**)

- **db**: Caches all links to a mongoDB database. This should be used if you are using uWSGI and are not just running the script on its own as one worker
- **json**: This saves cached links to a local **links.json** file
- **dynamodb**: Saves cached links to a DynamoDB database - set `table` to the table name to cache links to.
- **none**: Does not cache requests. Not reccomended as you can easily use up your Twitter API credits with this. Intended for use with another cache system (i.e NGINX uwsgi_cache)

**color** - Accepts a hex formatted color code, can change the embed color

**appname** - Can change the app name easily wherever it's shown

**repo** - used to change the repo url that some links redirect to

**url** - used to tell the user where to look for the oembed endpoint, make sure to set this to your public facing url

**combination_method** - using c.vxtwitter as the url causes vxTwitter to combine all images in the post into one. This is CPU intensive, so you might not want it running on the same machine that's serving requests. When `combination_method` is set to `local`, it will use the local machine to combine the images. This requires pillow to be installed. If you want to use another server, replace `local` with the URL to the endpoint which combines images. Both methods use the code in the `combineImg` module. Inside, there's also a `Dockerfile` intended to be deployed as a combination endpoint on an [AWS Lambda function](https://docs.aws.amazon.com/lambda/latest/dg/images-create.html).

## Other stuff

We check for t.co links in non video tweets, and if one is found, we direct the discord useragent to embed that link directly, this means that twitter links containing youtube / vimeo links will automatically embed those as if you had just directly linked to that content

This project is licensed under the **Do What The Fuck You Want Public License**
