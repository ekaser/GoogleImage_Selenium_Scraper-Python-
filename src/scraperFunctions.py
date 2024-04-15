
import os, shutil, csv, time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from src.ImageObject import ImageObject
from src.WebDriverManager import WebDriverManager
import resources.env as env
from resources.textColors import greenText, headerText, redText, blueText
from threading import Semaphore

# lock = Semaphore(5)





#Scrapes image data from Google Images
def scrape(wd, label, data) :

    def scroll_down(): #scroll down on page
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)

    try :
        jsonObjs = []
        for kwrd in env.KWRDS :
            if (env.VERBOSE) : print(blueText("Gathering Search URL..."))
            wd.get('http://www.google.com')
            search = wd.find_element(By.NAME, 'q')
            search.send_keys(kwrd)
            search.send_keys(Keys.SPACE)
            search.send_keys(label)
            search.send_keys(Keys.RETURN)
            time.sleep(2)
            imgButton = wd.find_element(By.LINK_TEXT, "Images")
            imgButton.click()
            time.sleep(1)
            search = wd.find_element(By.NAME, 'q')
            # url = wd.current_url
            if (env.DEBUG) : print(greenText(wd.current_url))

            
            imageUrls = []
            imagesDownloadedStats = {x : 0 for x in env.CLASSES} # Download Stats Dictionary
            skips = 0
            max_images = env.MAX_IMAGES
            if (env.VERBOSE) : print(blueText("Gathering Image Sources..."))
            while len(imageUrls) + skips < max_images: 
                scroll_down()

                thumbnails = wd.find_elements(By.CLASS_NAME, "H8Rx8c") #Find Thumbnail
                for img in thumbnails[len(imageUrls) + skips:max_images]:

                    try :
                        img.click() #Click it
                        time.sleep(0.5)


                        images = wd.find_elements(By.CLASS_NAME, "jlTjKd") #Find the higher resolution image div
                        subImgs = []
                        for tmpImg in images :
                            tagImgs = tmpImg.find_elements(By.TAG_NAME, "img") #find images inside above div
                            if (tagImgs) :
                                for i in tagImgs:
                                    if (i.get_attribute("class") == "sFlh5c pT0Scc iPVvYb") : #find that high resolution image
                                        subImgs.append(i)
                            # while(not lock.acquire()) : time.sleep(1)
                            for image in subImgs:
                                imageSrc = image.get_attribute('src')
                                if (imageSrc in imageUrls) or (imageSrc in map(lambda d: d['src'], data) and not env.NEW_DATA): #prevent duplicates
                                    max_images += 1
                                    skips += 1
                                    break

                                if imageSrc and 'http' in imageSrc: #validate src
                                    imageAlt = image.get_attribute('alt').lower()
                                    
                                    if label in imageAlt: #validate label
                                        imageLabel = label
                                    else :
                                        imageLabel = label #Setting as the same for now, will improve tagging
                                        if (env.DEBUG or env.VERBOSE) : print(redText("Warning: No label for image"))
                                    imageFilename = imageLabel + str(len(imageUrls)+1)
                                    imageObj = ImageObject(src=imageSrc, label=imageLabel, filename=imageFilename) #create and add Image Object to set
                                    imageObj.setFilename(label + str(len(jsonObjs) + len(data)))
                                    
                                    imageUrls.append(imageSrc)
                                    jsonObj, resVal = imageObj.downloadImage()
                                    del imageObj
                                    if (not resVal) :
                                        jsonObjs.append(jsonObj)
                                        if (jsonObj['label'] != "None") : imagesDownloadedStats[jsonObj['label']] += 1
                                    else :
                                        if (env.DEBUG) : print(redText("Skipped Image"))        
                                    
                                    if (env.DEBUG) : print(greenText("\tFound " + str(len(jsonObjs)) + " image(s)"))
                                else:
                                    if (env.DEBUG) : print(redText("\timage src not found"))

                            # lock.release()
                    except Exception as exception:
                        if (env.DEBUG) : print("Exception in clicking thumbnail:\n" + str(exception))
                        continue
                    # finally :
                        # lock.release()

    except Exception as e :
        print("Scraper Error! -" + str(e))
        raise e
    finally :
        if (env.DEBUG) : print(greenText("returning objects: " + str(len(jsonObjs))))
        return jsonObjs
   