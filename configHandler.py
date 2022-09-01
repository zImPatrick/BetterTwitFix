import json
import os

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