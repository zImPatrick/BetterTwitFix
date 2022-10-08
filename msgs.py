failedToScan="Failed to scan your link! This may be due to an incorrect link, private/suspended account, deleted tweet, or Twitter itself might be having issues (Check here: https://api.twitterstat.us/)"
failedToScanExtra = "\n\nTwitter gave me this error: "
tweetNotFound="Tweet not found."
tweetSuspended="This Tweet is from a suspended account." 

def genLikesDisplay(vnf):
    return ("\n\n💖 " + str(vnf['likes']) + " 🔁 " + str(vnf['rts']))

def genQrtDisplay(qrt):
    verifiedCheck = "☑️" if ('verified' in qrt and qrt['verified']) else ""
    return ("\n─────────────\n ➤ QRT of " + qrt['uploader'] + " (@" + qrt['screen_name'] + ")"+ verifiedCheck+":\n─────────────\n'" + qrt['description'] + "'")

def genPollDisplay(poll):
    pctSplit=10
    output="\n\n"
    for choice in poll["choices"]:
        output+=choice["text"]+"\n"+("█"*int(choice["percent"]/pctSplit)) +" "+str(choice["percent"])+"%\n"
    return output

def formatEmbedDesc(type,body,qrt,pollDisplay,likesDisplay):
    # Trim the embed description to 248 characters, prioritizing poll and likes
    output = ""
    if pollDisplay==None:
        pollDisplay=""

    if qrt!={} and not (type=="" or type=="Video"):

        qrtDisplay=genQrtDisplay(qrt)
        if 'id' in qrt and ('https://twitter.com/'+qrt['screen_name']+'/status/'+qrt['id']) in body:
            body = body.replace(('https://twitter.com/'+qrt['screen_name']+'/status/'+qrt['id']),"")
            body = body.strip()
        body+=qrtDisplay
        qrt={}

    if type=="" or type=="Video":
        output = body+pollDisplay
    elif qrt=={}:
        output= body+pollDisplay+likesDisplay
    else:
        output= body + likesDisplay
    if len(output)>248:
        # find out how many characters we need to remove
        diff = len(output)-248
        # remove the characters from body, add ellipsis
        body = body[:-(diff+1)]+"…"
        return formatEmbedDesc(type,body,qrt,pollDisplay,likesDisplay)
    else:
        return output