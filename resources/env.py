# Environment
_MULTITHREADING = True #Every class executse as an asynch function. Use with caution
PATH = ".\\"
DATA_DIR = PATH + "data\\" #Best not to change
DATA_NAME = "data.csv"
NEW_DATA = False #Do you want to delete the data folder on execution? Replaced by new data
IMAGE_DIR = DATA_DIR + "images\\" #Best not to change
MAX_IMAGES = 60
CLASSES = ["seahorse", "crab", "otter", "fish", "shark"] #, "squid", "turtle", "eel", "jellyfish", "dolphin"]
KWRDS = ['wild', 'real', ' '] #Don't leave blank. If you want to search only the class, leave a space
BROWSER_LOCATION = "C:\\Program Files\\Mozilla Firefox\\firefox.exe"
DRIVER = "resources\\driver.exe"
IMAGE_EXTENSION = ".jpg"
# Output
DEBUG = True #Do you want debug messages?
VERBOSE = True #Do you want messages about the program?

ZIP = False #Do you want to compress the data and images?