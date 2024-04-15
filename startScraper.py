import os, shutil, csv, time
from multiprocessing.pool import ThreadPool
from operator import itemgetter
from src.scraperFunctions import scrape
from src.WebDriverManager import WebDriverManager
import resources.env as env
from resources.textColors import greenText, headerText, redText, blueText



## Helpers
# Prints env Variables
def printVariables() :
    print(greenText("Variables: \n\tClasses(" + str(len(env.CLASSES)) + "): " 
                    + str(env.CLASSES) + "\n\tKEYWORDS: " + str(env.KWRDS)
                   + "\n\tPATH: " + env.PATH + "\n\tMAX_IMAGES: " + str(env.MAX_IMAGES) 
                   + "\n\tDRIVER: " + env.DRIVER + "\n\tBROWSER_LOCATION: " + env.BROWSER_LOCATION + "\n\tIMAGE_EXTENSION: " + env.IMAGE_EXTENSION))
    
# JSON Output Function
def outputJSONToCSV(jsonData) :
    # filePath = env.DATA_DIR + env.DATA_NAME
    filePath = env.DATA_DIR + env.DATA_NAME
    fileMode = "a"
    if (env.DEBUG) : print(greenText("TRYING TO OPEN"))
    with open(filePath, fileMode) as outFile :
        if (env.DEBUG) : print(greenText("OPENED"))
        writer = csv.DictWriter(outFile, fieldnames=['filename', 'src', 'label'])
        writer.writeheader()
        writer.writerows(jsonData)
        if (env.DEBUG) : print(greenText("Output to CSV success"))
        outFile.close()


def importJSONFromCSV(filePath) :
    with open(filePath, "r") as inFile :
        reader = csv.DictReader(inFile, fieldnames=['filename', 'src', 'label'])
        jsonObjs = []
        for row in reader :
            jsonObjs.append(row)

        inFile.close()
        dictObjs = {}
        sortedObjs = sorted(jsonObjs, key=itemgetter('label'))
        print()

        for imgClass in env.CLASSES :
            classObjs = [obj for obj in sortedObjs if obj['label'] == imgClass]
            dictObjs[imgClass] = classObjs
        return dictObjs
    
# Main scraping function  
def main() :
    print(headerText("Image Scraper 0.1.3"))
    if (env.DEBUG) : printVariables()
    os.makedirs(env.IMAGE_DIR, exist_ok=True) # Nested Folders.
    if (env.NEW_DATA) : 
        try : 
            {shutil.rmtree(env.DATA_DIR)}
        finally : 
            os.makedirs(env.IMAGE_DIR, exist_ok=False) # Nested Folders.
            importJsonObjs = {cls : [] for cls in env.CLASSES}
    else :
        importJsonObjs = importJSONFromCSV(env.DATA_DIR + env.DATA_NAME)
        if (env.VERBOSE or env.DEBUG) : print(blueText("Imported Data"))
    scraperThreads = []
    urlsReceived = 0
    

    def killManagers() :
        for manager, _ in scraperThreads :
            manager.stop()


    try :
        # Threading URL scraping / Opening webdrivers
        pool = ThreadPool(processes=len(env.CLASSES))
        for imgClass in env.CLASSES : 
            if (env.VERBOSE) : print(blueText("Scraping Class: " + imgClass))
            os.makedirs(env.IMAGE_DIR + str(imgClass), exist_ok=True)
            webManager = WebDriverManager()
            if (env._MULTITHREADING) :
                scraperThread = pool.apply_async(scrape, args=(webManager.webdriver, imgClass, importJsonObjs[imgClass]), callback=outputJSONToCSV)
                scraperThreads.append((webManager, scraperThread))
                # scraperThread.start()
            else :
                resObjs = scrape(imgClass, importJsonObjs[imgClass])
                # exportJsonObjs.extend(resObjs)
                
        
        if (env._MULTITHREADING) :
            complete = 0
            while(complete < len(env.CLASSES)) :
                for manager, thread in scraperThreads :
                    if (thread.ready()) :
                        manager.stop()
                        if (env.VERBOSE) : print(blueText("complete"))
                        complete += 1
                        scraperThreads.remove((manager, thread))
                
        if (env.ZIP) : # Compresses files and deletes uncompressed files
            if (env.VERBOSE) : print(blueText("Zipping Files..."))
            shutil.make_archive(env.PATH + "data", 'zip', env.DATA_DIR)
            shutil.rmtree(env.DATA_DIR)
    except TimeoutError as te :
        print(redText("Timeout -" + str(te)))
        # print("Total Images: \t" + str(len(exportJsonObjs)))
    except KeyboardInterrupt as ke:
        print("Exiting on CTRL+C")
        killManagers()
        exit(0)

   
    except Exception as e :
        print(redText("scraper Error - " + str(e)))
        raise e
    finally : #Cleanup
        # pool.close()
        pool.terminate()
        pool.join()
        if (env.VERBOSE or env.DEBUG) : 
            print(blueText("Done!"))
        # exit(0)
            # for imgClass in env.CLASSES:
                # print(blueText("\t -" + imgClass + ": \t" + str(imagesDownloadedStats[imgClass])))


if __name__ == "__main__" : 
    main() 






