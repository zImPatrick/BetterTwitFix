failedToScan="Failed to scan your link! This may be due to an incorrect link, private/suspended account, deleted tweet, or Twitter itself might be having issues (Check here: https://api.twitterstat.us/)"
failedToScanExtra = "\n\nTwitter gave me this error: "

def genLikesDisplay(vnf):
    return ("\n\n💖 " + str(vnf['likes']) + " 🔁 " + str(vnf['rts']) + "\n")

def genQrtDisplay(qrt):
    verifiedCheck = "☑️" if ('verified' in qrt and qrt['verified']) else ""
    return ("\n─────────────\n ➤ QRT of " + qrt['handle'] + " (@" + qrt['screen_name'] + ")"+ verifiedCheck+":\n─────────────\n'" + qrt['desc'] + "'")