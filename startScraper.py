import os,json, shutil
from src.WebDriverManager import WebDriverManager
from src.scraperFunctions import scrapeImageObjects, scrapeSearchUrl
from multiprocessing.pool import ThreadPool
import resources.env as env
from resources.textColors import greenText, headerText, redText, blueText

##Helpers
#Prints env Variables
def printVariables() :
    print(greenText("Variables: \n\tClasses(" + str(len(env.CLASSES)) + "): " + str(env.CLASSES) 
                   + "\n\tPATH: " + env.PATH + "\n\tMAX_IMAGES: " + str(env.MAX_IMAGES) 
                   + "\n\tDRIVER: " + env.DRIVER + "\n\tBROWSER_LOCATION: " + env.BROWSER_LOCATION + "\n\tIMAGE_EXTENSION: " + env.IMAGE_EXTENSION))
    
# JSON Output Function
def outputJSON(outPath, jsonFilename, jsonData) :
    jsonObject = json.dumps(jsonData, indent=3)
    filePath = outPath + jsonFilename + ".json"
    with open(filePath, "w") as outfile :
        json.dump(jsonObject, outfile, indent=3)
        if (env.DEBUG) : print(greenText("Output to JSON success"))


#Main scraping function  
def main() :    
    print(headerText("Image Scraper 0.1.0"))
    if (env.DEBUG) : printVariables()
    os.makedirs(env.PATH + env.IMAGE_DIR, exist_ok=True)
    os.makedirs(env.PATH + env.DATA_DIR, exist_ok=True)
    jsonObjs, urlThreadList, imageObjectThreadList = [], [], []
    urlsReceived = 0
    imagesDownloadedStats = {x : 0 for x in env.CLASSES} #Download Stats Dictionary
    pool = ThreadPool(processes=len(env.CLASSES)*2)
    try :
        # Threading URL scraping
        for imgClass in env.CLASSES :
            if (env.VERBOSE) : print(blueText("Scraping Class: " + imgClass))
            os.makedirs(env.PATH + env.IMAGE_DIR + str(imgClass), exist_ok=True)
            classManager = WebDriverManager()
            urlThread = pool.apply_async(scrapeSearchUrl, (classManager.webdriver, imgClass))
            urlThreadList.append([classManager, urlThread, imgClass])

        #Get Urls and start scraping
        for manager, thread, classLabel in urlThreadList :
            url = thread.get() #Await URL thread join
            urlsReceived += 1
            classThread = pool.apply_async(scrapeImageObjects, (manager.webdriver, 1, env.MAX_IMAGES, url, classLabel))
            imageObjectThreadList.append([manager, classThread])

        # Get the scraped image objects and download their images
    
        for manager, thread in imageObjectThreadList:
            if (env.VERBOSE) : print(blueText("Downloading Images..."))
            imgObjects = thread.get() #Await Image Object Thread join
            for i, imgObj in enumerate(imgObjects) : #Returns a list of valid image objects
                imgObj.setFilename(imgObj.label + str(i))
                imgObj.downloadImage(env.PATH + env.IMAGE_DIR + str(imgObj.label) + "\\")
                if (imgObj.label != "None") : imagesDownloadedStats[imgObj.label] += 1
                jsonObjs.append(imgObj.imageJSON())
            manager.stop()


        outputJSON(env.PATH + env.DATA_DIR, "data", jsonObjs)
        if (env.ZIP) : #Compresses Filse and deletes uncompressed files
            if (env.VERBOSE) : print(blueText("Zipping Files..."))
            shutil.make_archive(env.PATH + "data", 'zip', env.PATH + env.DATA_DIR)
            shutil.rmtree(env.PATH + env.DATA_DIR)
            shutil.make_archive(env.PATH + "images", 'zip', env.PATH + env.IMAGE_DIR)
            shutil.rmtree(env.PATH + env.IMAGE_DIR)
        if (env.VERBOSE or env.DEBUG) : 
            print(blueText("Done!"))
            print(blueText("URLs found: " + str(urlsReceived) + "\nImages Downloaded per class: "))
            for imgClass in imagesDownloadedStats.keys():
                print(blueText("\t -" + imgClass + ": \t" + str(imagesDownloadedStats[imgClass])))

    except Exception as e :
        print(redText("Scraping Error! - " + str(e)))
        if (env.KILLALL) :
            for manager, thread, _ in urlThreadList :
                manager.stop()
                thread.kill()
            for _, thread in imageObjectThreadList :
                thread.kill()
main()