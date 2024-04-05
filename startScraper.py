import os,json, shutil, csv
from src.WebDriverManager import WebDriverManager
from src.scraperFunctions import scrapeImageObjects, scrapeSearchUrl
from src.ImageObject import downloadImages
from multiprocessing.pool import ThreadPool
import resources.env as env
from resources.textColors import greenText, headerText, redText, blueText

## Helpers
# Prints env Variables
def printVariables() :
    print(greenText("Variables: \n\tClasses(" + str(len(env.CLASSES)) + "): " + str(env.CLASSES) 
                   + "\n\tPATH: " + env.PATH + "\n\tMAX_IMAGES: " + str(env.MAX_IMAGES) 
                   + "\n\tDRIVER: " + env.DRIVER + "\n\tBROWSER_LOCATION: " + env.BROWSER_LOCATION + "\n\tIMAGE_EXTENSION: " + env.IMAGE_EXTENSION))
    
# JSON Output Function
def outputJSONToCSV(jsonData) :
    # filePath = env.DATA_DIR + env.DATA_NAME
    filePath = env.DATA_DIR + env.DATA_NAME
    with open(filePath, "w") as outFile :
        writer = csv.DictWriter(outFile, fieldnames=['filename', 'src', 'label'])
        writer.writeheader()
        writer.writerows(jsonData)
        if (env.DEBUG) : print(greenText("Output to CSV success"))


# Main scraping function  
def main() :    
    print(headerText("Image Scraper 0.1.3"))
    if (env.DEBUG) : printVariables()
    os.makedirs(env.IMAGE_DIR, exist_ok=True) # Nested Folders.
    jsonObjs, urlThreads, imageObjectThreads, downloadThreads = [], [], [], []
    urlsReceived = 0
    imagesDownloadedStats = {x : 0 for x in env.CLASSES} # Download Stats Dictionary
    pool = ThreadPool(processes=len(env.CLASSES)*10) #Max Threads is 3*number of classes
    try :
        # Threading URL scraping / Opening webdrivers
        for imgClass in env.CLASSES :
            if (env.VERBOSE) : print(blueText("Scraping Class: " + imgClass))
            os.makedirs(env.IMAGE_DIR + str(imgClass), exist_ok=True)
            classManager = WebDriverManager()
            urlThread = pool.apply_async(scrapeSearchUrl, args=(classManager.webdriver, imgClass))
            urlThreads.append([classManager, urlThread, imgClass])

        # Get Urls and start scraping
        for manager, thread, classLabel in urlThreads :
            url = thread.get() # Await URL thread join
            urlsReceived += 1
            classThread = pool.apply_async(scrapeImageObjects, args=(manager.webdriver, env.MAX_IMAGES, url, classLabel))
            imageObjectThreads.append([manager, classThread])

        # Get the scraped image objects and download their images
        for manager, thread in imageObjectThreads:
  
            imgObjects = thread.get() # Await Image Object Thread join
            manager.stop()
            # for i, imgObj in enumerate(imgObjects) : # Returns a list of valid image objects
            #     imgObj.setFilename(imgObj.label + str(i))
            try :
                if (env.VERBOSE) : print(blueText("Downloading Images..."))
                downloadThread = pool.apply_async(downloadImages, args=([imgObjects]))
                downloadThreads.append(downloadThread)
            except Exception as e :
                if (env.DEBUG) : print(redText(redText("Skipping all Image downloads! - " + str(e))))
                break

        for thread in downloadThreads : #Finish downloads and JSON
            returnedObjs = thread.get()
            for jsonObj in returnedObjs:
                jsonObjs.append(jsonObj)
                if (jsonObj['label'] != "None") : imagesDownloadedStats[jsonObj['label']] += 1


        outputJSONToCSV(jsonObjs)
        if (env.ZIP) : # Compresses files and deletes uncompressed files
            if (env.VERBOSE) : print(blueText("Zipping Files..."))
            shutil.make_archive(env.PATH + "data", 'zip', env.DATA_DIR)
            shutil.rmtree(env.DATA_DIR)
        if (env.VERBOSE or env.DEBUG) : 
            print(blueText("Done!"))
            print(blueText("URLs found: " + str(urlsReceived) + "\nImages Downloaded per class: "))
            for imgClass in imagesDownloadedStats.keys():
                print(blueText("\t -" + imgClass + ": \t" + str(imagesDownloadedStats[imgClass])))
    except Exception as e :
        print(redText("Scraping Error! - " + str(e)))
        if (env.KILLALL) :
            for manager, thread, _ in urlThreads :
                manager.stop()
                thread.kill()
            for _, thread in imageObjectThreads :
                thread.kill()
    pool.close()
    pool.join()
    return 0
main()