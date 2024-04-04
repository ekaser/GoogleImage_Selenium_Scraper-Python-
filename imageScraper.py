from selenium import webdriver
import shutil
import os
from urlScraper import scrapeImageObjects, getSearchUrls
from imageHandler import outputJSON
import resources.env as env
from resources.textColors import greenText, blueText, redText, headerText

def startWebDriver() :
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless=new")
    options.binary_location = env.BINARY_LOCATION
    wdService = webdriver.FirefoxService(executable_path=env.PATH+env.DRIVER)
    wdService.start()
    wd = webdriver.Firefox(options=options, service=wdService)
    if (env.DEBUG) : print(greenText("Started WebDriver"))
    return wd, wdService

def stopWebDriver(wd, wdService) :
    if (env.DEBUG) : print(greenText("Stopping WebDriver"))
    wd.quit()
    wdService.stop()

def printVariables() :
    print(greenText("Variables: \n\tClasses(" + str(len(env.CLASSES)) + "): " + str(env.CLASSES) 
                   + "\n\tPATH: " + env.PATH + "\n\tMAX_IMAGES: " + str(env.MAX_IMAGES) 
                   + "\n\tDRIVER: " + env.DRIVER + "\n\tBINARY_LOCATION: " + env.BINARY_LOCATION))
def main() :
    print(headerText("Image Scraper 0.0.1"))
    wd, wdService = startWebDriver()
    if (env.DEBUG) : printVariables()

    os.makedirs(env.PATH + env.IMAGE_DIR, exist_ok=True)
    os.makedirs(env.PATH + env.DATA_DIR, exist_ok=True)
    jsonObjs = []
    urls = getSearchUrls(wd, env.CLASSES)
    for imgClass in env.CLASSES :
        if (env.VERBOSE) : print(blueText("Scraping Class: " + imgClass))
        os.makedirs(env.PATH + env.IMAGE_DIR + str(imgClass), exist_ok=True)
        imgObjects = scrapeImageObjects(wd, 1, env.MAX_IMAGES, urls[imgClass], imgClass)
        if (env.VERBOSE) : print(blueText("Downloading images from source..."))
        for imgObj in imgObjects:
            imgObj.downloadImage(env.PATH + env.IMAGE_DIR + str(imgClass) + "\\")
            jsonObjs.append(imgObj.imageJSON())

    outputJSON(env.PATH + env.DATA_DIR, "data", jsonObjs)
    if (env.ZIP) :
        if (env.VERBOSE) : print(blueText("Zipping Files..."))
        shutil.make_archive(env.PATH + "data", 'zip', env.PATH + env.DATA_DIR)
        shutil.rmtree(env.PATH + env.DATA_DIR)
        shutil.make_archive(env.PATH + "images", 'zip', env.PATH + env.IMAGE_DIR)
        shutil.rmtree(env.PATH + env.IMAGE_DIR)
        stopWebDriver(wd, wdService)
    if (env.VERBOSE) : print(blueText("Done!"))
main()