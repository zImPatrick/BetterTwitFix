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
    var preference = localStorage.getItem("openLinksPreference");
    if (preference === "true"){
        const os = detectOS();

        url = `twitter://status?id=${tweetId}`
        if(os === 'android'){
            window.location = url;
        }else if (os === 'ios'){
            window.location.replace(url);
        }
    
        setTimeout(() => {
            window.location = `https://x.com/i/status/${tweetId}`
        }, 1000)
    }
}