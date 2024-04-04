from selenium import webdriver
import shutil
import os
from scraperFunctions import scrapeImageObjects, scrapeSearchUrls
from ImageObject import outputJSON
import time
import resources.env as env
from resources.textColors import greenText, blueText, redText, headerText
from multiprocessing.pool import ThreadPool


def webDriverOptions() :
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless=new")
    options.binary_location = env.BROWSER_LOCATION
    return options


class WebDriverManager() :
    def __init__(self) :
        self.webservice = webdriver.FirefoxService(executable_path=env.PATH+env.DRIVER)
        self.webservice.start()
        self.webdriver = webdriver.Firefox(options=webDriverOptions(), service=self.webservice)
        if (env.DEBUG) : print(greenText("Started WebDriverManager"))
    def stop(self) :
        if (env.DEBUG) : print(greenText("Stopping WebDriverManager"))
        self.webdriver.quit()
        self.webservice.stop()
    # def __del__(self) :
    #     if (env.DEBUG) : print(greenText("Stopping WebDriverManager"))
    #     self.webdriver.quit()
    #     self.webservice.stop()

def printVariables() :
    print(greenText("Variables: \n\tClasses(" + str(len(env.CLASSES)) + "): " + str(env.CLASSES) 
                   + "\n\tPATH: " + env.PATH + "\n\tMAX_IMAGES: " + str(env.MAX_IMAGES) 
                   + "\n\tDRIVER: " + env.DRIVER + "\n\tBROWSER_LOCATION: " + env.BROWSER_LOCATION))
def main() :
    print(headerText("Image Scraper 0.0.2"))

    if (env.DEBUG) : printVariables()

    os.makedirs(env.PATH + env.IMAGE_DIR, exist_ok=True)
    os.makedirs(env.PATH + env.DATA_DIR, exist_ok=True)
    jsonObjs = []
    # Scrape Google Image Search Urls
    urlManager = WebDriverManager()
    urls = scrapeSearchUrls(urlManager.webdriver, env.CLASSES)
    urlManager.stop()


    threadList = []
    pool = ThreadPool(processes=len(env.CLASSES))
    for imgClass in env.CLASSES :
        if (env.VERBOSE) : print(blueText("Scraping Class: " + imgClass))
        os.makedirs(env.PATH + env.IMAGE_DIR + str(imgClass), exist_ok=True)
        classManager = WebDriverManager()
        classThread = pool.apply_async(scrapeImageObjects, (classManager.webdriver, 1, env.MAX_IMAGES, urls[imgClass], imgClass))
        threadList.append([classManager, classThread])
 


        
    for manager, thread in threadList:
        imgObjects = thread.get()
        manager.stop()
        for i, imgObj in enumerate(imgObjects) : #Returns a list of valid image objects
            imgObj.setFilename(imgObj.label + str(i))
            imgObj.downloadImage(env.PATH + env.IMAGE_DIR + str(imgObj.label) + "\\")
            jsonObjs.append(imgObj.imageJSON())
        manager.stop()


    outputJSON(env.PATH + env.DATA_DIR, "data", jsonObjs)
    if (env.ZIP) :
        if (env.VERBOSE) : print(blueText("Zipping Files..."))
        shutil.make_archive(env.PATH + "data", 'zip', env.PATH + env.DATA_DIR)
        shutil.rmtree(env.PATH + env.DATA_DIR)
        shutil.make_archive(env.PATH + "images", 'zip', env.PATH + env.IMAGE_DIR)
        shutil.rmtree(env.PATH + env.IMAGE_DIR)
    if (env.VERBOSE) : print(blueText("Done!"))
main()