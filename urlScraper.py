from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from imageHandler import ImageObject
from resources.env import DEBUG, VERBOSE
from resources.textColors import redText, greenText, blueText


def scrapeImageObjects(wd, delay, max_images, url, label):
    def scroll_down(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(delay)
    def findImageElements(wd, imageObjs, max_images) :
        imageUrls = set()
        skips = 0
        if (VERBOSE) : print(blueText("Gathering Image Sources..."))
        while len(imageObjs) + skips < max_images:
            scroll_down(wd)

            thumbnails = wd.find_elements(By.CLASS_NAME, "H8Rx8c")
            for img in thumbnails[len(imageObjs) + skips:max_images]:
                try:
                    img.click()
                    time.sleep(delay)
                except Exception as exception:
                    print("Exception in clicking thumbnail:\n" + str(exception))
                    continue

                images = wd.find_elements(By.CLASS_NAME, "jlTjKd")
                subImgs = []
                for tmpImg in images :
                    tagImgs = tmpImg.find_elements(By.TAG_NAME, "img")
                    if (tagImgs) :
                        for i in tagImgs:
                            if (i.get_attribute("class") == "sFlh5c pT0Scc iPVvYb") :
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
                            imageFilename = imageLabel + str(len(imageObjs)+1) + ".jpg"
                            imageObj = ImageObject(src=imageSrc, label=imageLabel, filename=imageFilename) #create and add Image Object to set
                            imageObjs.add(imageObj)
                            imageUrls.add(imageSrc)
                            
                            if (DEBUG) : print(greenText("\tFound " + str(len(imageObjs)) + " image(s)"))
                        else:
                            if (DEBUG) : print(redText("\timage src not found"))

        return imageObjs
    
    wd.get(url)
    imageObjs = set()
    findImageElements(wd, imageObjs, max_images)
    if (DEBUG) : print(greenText("returning objects: " + str(len(imageObjs))))
    return imageObjs


  

        
        

            

def getSearchUrls(wd, classes) :
    if (VERBOSE) : print(blueText("Gathering Search URLs..."))
    urls = {}
    for imgClass in classes :
        wd.get('http://www.google.com')
        search = wd.find_element(By.NAME, 'q')
        search.send_keys(imgClass)
        search.send_keys(Keys.RETURN) # hit return after you enter search text
        time.sleep(5) # sleep for 5 seconds so you can see the results
        imgButton = wd.find_element(By.LINK_TEXT, "Images")
        imgButton.click()
        time.sleep(3)
        search = wd.find_element(By.NAME, 'q')
        url = wd.current_url
        urls[imgClass] = url
    if (DEBUG) : print(greenText("Valid URLs: " + str(len(urls))))
    return urls