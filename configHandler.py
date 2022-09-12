import json
import os

if ('RUNNING_SERVERLESS' in os.environ and os.environ['RUNNING_SERVERLESS'] == '1'):
    config = {
            "config":{
                "link_cache":os.environ["VXTWITTER_LINK_CACHE"],
                "database":os.environ["VXTWITTER_DATABASE"],
                "table":os.environ["VXTWITTER_DATABASE_TABLE"],
                "method":os.environ["VXTWITTER_METHOD"], 
                "color":os.environ["VXTWITTER_COLOR"], 
                "appname": os.environ["VXTWITTER_APP_NAME"], 
                "repo": os.environ["VXTWITTER_REPO"], 
                "url": os.environ["VXTWITTER_URL"],
                "combination_method": os.environ["VXTWITTER_COMBINATION_METHOD"] # can either be 'local' or a URL to a server handling requests in the same format
                },
            "api":{"api_key":os.environ["VXTWITTER_TWITTER_API_KEY"],
            "api_secret":os.environ["VXTWITTER_TWITTER_API_SECRET"],
            "access_token":os.environ["VXTWITTER_TWITTER_ACCESS_TOKEN"],
            "access_secret":os.environ["VXTWITTER_TWITTER_ACCESS_SECRET"],
            "apiMirrors":[]
            }
        }
else:
    # Read config from config.json. If it does not exist, create new.
    if not os.path.exists("config.json"):
        with open("config.json", "w") as outfile:
            default_config = {
                "config":{
                    "link_cache":"json",
                    "database":"[url to mongo database goes here]",
                    "table":"TwiFix",
                    "method":"youtube-dl", 
                    "color":"#43B581", 
                    "appname": "vxTwitter", 
                    "repo": "https://github.com/dylanpdx/BetterTwitFix", 
                    "url": "https://vxtwitter.com",
                    "combination_method": "local" # can either be 'local' or a URL to a server handling requests in the same format
                    },
                "api":{"api_key":"[api_key goes here]",
                "api_secret":"[api_secret goes here]",
                "access_token":"[access_token goes here]",
                "access_secret":"[access_secret goes here]",
                "apiMirrors":[]
                }
            }

            json.dump(default_config, outfile, indent=4, sort_keys=True)

        config = default_config
    else:
        f = open("config.json")
        config = json.load(f)
        f.close()
