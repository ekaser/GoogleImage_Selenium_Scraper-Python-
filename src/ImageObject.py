import requests, io
from PIL import Image
from resources.env import DEBUG, IMAGE_EXTENSION, IMAGE_DIR
from resources.textColors import redText, greenText

# ImageObject Class. Used for storing scraped web element data. 
class ImageObject :
    def __init__(self, src="", label="", filename="") :
        self.src = src
        self.label=label
        self.filename=filename
        if (src == "" or label == "") :
            raise Exception("Invalid Image Object Initializers")
    def getSrc(self) :
        if (self.src) :
            return self.src
        else :
            if (DEBUG) : print("No image Src")
    def getLabel(self) :
        if (self.label) :
            return self.label
        else :
            if (DEBUG) : print("No image label")
    def getFilename(self) :
        if (self.filename) :
            return self.filename
        else :
            if (DEBUG) : print("No image filename")
    def setFilename(self, filename) :
        self.filename = filename
    def imageJSON(self) : #export data as json
        data = {
            "label" : str(self.label),
            "src" : str(self.src),
            "filename" : str(self.filename)
        }
        return data
    def downloadImage(self) : #dowload image from src to filename
        try :
            image_content = requests.get(self.src).content
            if (DEBUG) : print(greenText("Successful Request: " + self.src))
            image_file = io.BytesIO(image_content)
            image = Image.open(image_file)
            file_path = IMAGE_DIR + self.label + "\\" + self.filename + IMAGE_EXTENSION

            with open(file_path, "wb") as f:
                image.save(f, "JPEG")
            if (DEBUG) : print(greenText("Saved image: " + file_path))
            return self.imageJSON(), 0
        except Exception as e:
            if (DEBUG) : print(redText('FAILED -' + str(e)))
            return {}, 1


def downloadImages(imageObjects) :
    returnObjects = []
    for i, imgObj in enumerate(imageObjects) : # Returns a list of valid image objects
        imgObj.setFilename(imgObj.label + str(i))
        jsonObj, resVal = imgObj.downloadImage()
        if (not resVal) :
            returnObjects.append(jsonObj)
        else :
           if (DEBUG) : print(redText("Skipped Image"))
    
    return returnObjects
        

def callbackDownloadImage(imgObj) : #dowload image from src to filename
    try :
        image_content = requests.get(imgObj.src).content
        if (DEBUG) : print(greenText("Successful Request: " + imgObj.src))
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file)
        file_path = IMAGE_DIR + imgObj.label + "\\" + imgObj.filename + IMAGE_EXTENSION

        with open(file_path, "wb") as f:
            image.save(f, "JPEG")
        if (DEBUG) : print(greenText("Saved image: " + file_path))
        return imgObj.imageJSON(), 0
    except Exception as e:
        if (DEBUG) : print(redText('FAILED -' + str(e)))
        return {}, 1