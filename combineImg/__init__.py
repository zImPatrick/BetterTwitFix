from PIL import Image, ImageOps, ImageFilter
from requests import get
from io import BytesIO
import base64
import concurrent.futures
from time import time as timer

# find the highest res image in an array of images
def findImageWithMostPixels(imageArray):
    maxPixels = 0
    maxImage = None
    for image in imageArray:
        pixels = image.size[0] * image.size[1]
        if pixels > maxPixels:
            maxPixels = pixels
            maxImage = image
    return maxImage

def getTotalImgSize(imageArray): # take the image with the most pixels, multiply it by the number of images, and return the width and height
    maxImage = findImageWithMostPixels(imageArray)
    if (len(imageArray) == 1):
        return (maxImage.size[0], maxImage.size[1])
    elif (len(imageArray) == 2):
        return (maxImage.size[0] * 2, maxImage.size[1])
    else:
        return (maxImage.size[0] * 2, maxImage.size[1]*2)

def scaleImageIterable(args):
    image = args[0]
    targetWidth = args[1]
    targetHeight = args[2]
    pad=args[3]
    image = image.convert('RGBA')
    image = ImageOps.expand(image,20)
    if pad:
        newImg = ImageOps.contain(image, (targetWidth, targetHeight))
    else:
        newImg = ImageOps.fit(image, (targetWidth, targetHeight)) # scale + crop
    return newImg

def scaleAllImagesToSameSize(imageArray,targetWidth,targetHeight,pad=True): # scale all images in the array to the same size, preserving aspect ratio
    newImageArray = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        newImageArray = [executor.submit(scaleImageIterable, (image, targetWidth, targetHeight,pad)) for image in imageArray]
        newImageArray = [future.result() for future in newImageArray]
    return newImageArray

def blurImage(image, radius):
    return image.filter(ImageFilter.GaussianBlur(radius=radius))

def combineImages(imageArray, totalWidth, totalHeight,pad=True):
    x = 0
    y = 0
    if (len(imageArray) == 1): # if there is only one image, just return it
        return imageArray[0]
    # image generation is needed
    topImg = findImageWithMostPixels(imageArray)
    newImage = Image.new("RGBA", (totalWidth, totalHeight),(0, 0, 0, 0))
    imageArray = scaleAllImagesToSameSize(imageArray,topImg.size[0],topImg.size[1],pad)
    if (len(imageArray) == 2): # if there are two images, combine them horizontally
        for image in imageArray:
            newImage.paste(image, (x, y))
            x += image.size[0]
    elif (len(imageArray) == 3): # the elusive 3 image upload
        # if there are three images, combine the first two horizontally, then combine the last one vertically
        imageArray[2] = scaleAllImagesToSameSize([imageArray[2]],totalWidth,topImg.size[1],pad)[0] # take the last image, treat it like an image array and scale it to the total width, but same height as all individual images
        for image in imageArray[0:2]:
            newImage.paste(image, (x, y))
            x += image.size[0]
        y += imageArray[0].size[1]
        x = 0
        # paste the final image so that it's centered
        newImage.paste(imageArray[2], (int((totalWidth - imageArray[2].size[0]) / 2), y))
    elif (len(imageArray) == 4): # if there are four images, combine the first two horizontally, then combine the last two vertically
        for image in imageArray[0:2]:
            newImage.paste(image, (x, y))
            x += image.size[0]
        y += imageArray[0].size[1]
        x = 0
        for image in imageArray[2:4]:
            newImage.paste(image, (x, y))
            x += image.size[0]
    else:
        for image in imageArray:
            newImage.paste(image, (x, y))
            x += image.size[0]
    return newImage

def saveImage(image, name):
    image.save(name)

# combine up to four images into a single image
def genImage(imageArray):
    totalSize=getTotalImgSize(imageArray)
    combined = combineImages(imageArray, *totalSize)

    finalImg = combined.convert('RGB')

    bbox = finalImg.getbbox()
    finalImg = finalImg.crop(bbox)

    return finalImg

def downloadImage(url):
    return Image.open(BytesIO(get(url).content))

def genImageFromURL(urlArray):
    # this method avoids storing the images in disk, instead they're stored in memory
    # no cache means that they'll have to be downloaded again if the image is requested again
    # TODO: cache?
    start = timer()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        imageArray = [executor.submit(downloadImage, url) for url in urlArray]
        imageArray = [future.result() for future in imageArray]
    print(f"Images downloaded in: {timer() - start}s")
    start = timer()
    finalImg = genImage(imageArray)
    print(f"Image generated in: {timer() - start}s")
    return finalImg
    
def lambda_handler(event, context):
    if ("queryStringParameters" not in event):
        return {
            "statusCode": 400,
            "body": "Invalid request."
        }
    images = event["queryStringParameters"].get("imgs","").split(",")
    for img in images:
        if not img.startswith("https://pbs.twimg.com"):
            return {'statusCode':400,'body':'Invalid image URL'}
    combined = genImageFromURL(images)
    buffered = BytesIO()
    combined.save(buffered,format="JPEG",quality=60)
    combined_str=base64.b64encode(buffered.getvalue()).decode('ascii')
    return {
        'statusCode': 200,
        "headers": 
        {
            "Content-Type": "image/jpeg"
        },
        'body': combined_str,
        'isBase64Encoded': True
    }