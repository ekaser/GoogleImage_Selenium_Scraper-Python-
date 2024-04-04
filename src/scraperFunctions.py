from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from src.ImageObject import ImageObject
from resources.env import DEBUG, VERBOSE, IMAGE_EXTENSION
from resources.textColors import redText, greenText, blueText

#Scrapes Images from a Google Image Search URL. The meat and potatoes
def scrapeImageObjects(wd, delay, max_images, url, label):
    def scroll_down(wd): #scrpll down on page
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(delay)

    # wd.get(url)
    imageObjs = set()
    imageUrls = set()
    skips = 0
    if (VERBOSE) : print(blueText("Gathering Image Sources..."))
    while len(imageObjs) + skips < max_images: #While we have unique images less than our max images...
        scroll_down(wd)

        thumbnails = wd.find_elements(By.CLASS_NAME, "H8Rx8c") #Find Thumbnail
        for img in thumbnails[len(imageObjs) + skips:max_images]:
            try:
                img.click() #Click it
                time.sleep(delay)
            except Exception as exception:
                print("Exception in clicking thumbnail:\n" + str(exception))
                continue

            images = wd.find_elements(By.CLASS_NAME, "jlTjKd") #Find the higher resolution image div
            subImgs = []
            for tmpImg in images :
                tagImgs = tmpImg.find_elements(By.TAG_NAME, "img") #find images inside above div
                if (tagImgs) :
                    for i in tagImgs:
                        if (i.get_attribute("class") == "sFlh5c pT0Scc iPVvYb") : #find that high resolution image
                            subImgs.append(i)

                for image in subImgs:
                    if image.get_attribute('src') in imageUrls: #prevent duplicates
                        max_images += 1
                        skips += 1
                        break

                    if image.get_attribute('src') and 'http' in image.get_attribute('src'): #validate src
                        imageSrc = image.get_attribute('src')
                        imageAlt = image.get_attribute('alt').lower()
                        
                        if label in imageAlt: #validate label
                            imageLabel = label
                        else :
                            imageLabel = "None"
                            if (DEBUG or VERBOSE) : print(redText("Warning: No label for image"))
                        imageFilename = imageLabel + str(len(imageObjs)+1) + IMAGE_EXTENSION
                        imageObj = ImageObject(src=imageSrc, label=imageLabel, filename=imageFilename) #create and add Image Object to set
                        imageObjs.add(imageObj)
                        imageUrls.add(imageSrc)
                        
                        if (DEBUG) : print(greenText("\tFound " + str(len(imageObjs)) + " image(s)"))
                    else:
                        if (DEBUG) : print(redText("\timage src not found"))
    if (DEBUG) : print(greenText("returning objects: " + str(len(imageObjs))))
    return imageObjs
  
#Scrapes Google Image Search URLs for provided classes. Not threaded currently
def scrapeSearchUrl(wd, imgClass) :
    if (VERBOSE) : print(blueText("Gathering Search URL..."))
    wd.get('http://www.google.com')
    search = wd.find_element(By.NAME, 'q')
    search.send_keys(imgClass)
    search.send_keys(Keys.RETURN)
    time.sleep(5)
    imgButton = wd.find_element(By.LINK_TEXT, "Images")
    imgButton.click()
    time.sleep(2)
    search = wd.find_element(By.NAME, 'q')
    url = wd.current_url
    if (DEBUG) : print(greenText(url))
    return url

   