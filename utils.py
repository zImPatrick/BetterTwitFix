import re

pathregex = re.compile("\\w{1,15}\\/(status|statuses)\\/(\\d{2,20})")


def getTweetIdFromUrl(url):
    match = pathregex.search(url)
    if match is not None:
        return match.group(2)
    else:
        return None