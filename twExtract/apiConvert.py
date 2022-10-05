# frankenstein a twitter 1.1 API response from the v2 API response
# why? Because atm I don't want to rewrite the entire processing for a tweet
# temporary™️ solution

# these can be copied directly
legacyTweetFields = ["created_at","display_text_range","entities","extended_entities","favorite_count","retweet_count","reply_count","is_quote_status","full_text","possibly_sensitive"]
legacyUserFields = ["name","screen_name","verified"]

def convertUser(userv2):
    v1User={}
    for field in legacyUserFields:
        if field in userv2["legacy"]:
            v1User[field] = userv2["legacy"][field]
    v1User["profile_image_url"] = userv2["legacy"]["profile_image_url_https"]
    return v1User

def convertTweet(tweetv2,qrts=True):
    v1Status={}
    for field in legacyTweetFields:
        if field in tweetv2["legacy"]:
            v1Status[field] = tweetv2["legacy"][field]
    v1Status["id"] = int(tweetv2["legacy"]["conversation_id_str"])
    v1Status["id_str"] = tweetv2["legacy"]["conversation_id_str"]
    v1Status["user"] = convertUser(tweetv2["core"]["user_results"]["result"])
    if qrts and v1Status["is_quote_status"]:
        v1Status["quoted_status"] = convertTweet(tweetv2["quoted_status_result"]["result"])
    if 'card' in tweetv2:
        v1Status["card"] = {"binding_values":{},"name":tweetv2["card"]["legacy"]["name"]}
        for lvalue in tweetv2["card"]["legacy"]["binding_values"]:
            key = lvalue["key"]
            value = lvalue["value"]
            v1Status["card"]["binding_values"][key] = value

    return v1Status