import requests, io
from PIL import Image
from resources.env import DEBUG, IMAGE_EXTENSION
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
    def downloadImage(self, downloadPath) : #dowload image from src to filename
        try :
            image_content = requests.get(self.src).content
            if (DEBUG) : print(greenText("Successful Request: " + self.src))
            image_file = io.BytesIO(image_content)
            image = Image.open(image_file)
            file_path = downloadPath + self.filename

            with open(file_path, "wb") as f:
                image.save(f, "JPEG")
            if (DEBUG) : print(greenText("Saved image: " + file_path))
        except Exception as e:
            if (DEBUG) : print(redText('FAILED -' + str(e)))

