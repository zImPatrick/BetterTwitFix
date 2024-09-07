function detectOS() {
    const userAgent = navigator.userAgent || navigator.platform

    if (/android/i.test(userAgent)) {
        return 'android';
    }

    if (/iPad|iPhone|iPod/.test(userAgent) || (/Macintosh/.test(userAgent) && 'ontouchend' in document)) {
        return 'ios';
    }

    return 'unknown';
}

function openTweet(tweetId){
    if (localStorage.getItem("openLinksPreference") === "true") {
        const os = detectOS();
        url = `twitter://status?id=${tweetId}`
        if(os === 'android'){
            window.location = url;
        }else if (os === 'ios'){
            window.location.replace(url);
        }
    } else if (localStorage.getItem("frontendToggle") === "true" && localStorage.getItem("frontendUrl") !== null) {
        window.location = `${frontendUrl}/i/status/${tweetId}`
    } else {
        window.location = `https://x.com/i/status/${tweetId}`
    }

    setTimeout(() => {
        window.location = `https://x.com/i/status/${tweetId}`
    }, 1000)
}
