import re

pathregex = re.compile("\\w{1,15}\\/(status|statuses)\\/(\\d{2,20})")
endTCOregex = re.compile("(^.*?) +https:\/\/t.co\/.*?$")

def getTweetIdFromUrl(url):
    match = pathregex.search(url)
    if match is not None:
        return match.group(2)
    else:
        return None
    
def stripEndTCO(text):
    # remove t.co links at the end of a string
    match = endTCOregex.search(text)
    if match is not None:
        return match.group(1)
    else:
        return text