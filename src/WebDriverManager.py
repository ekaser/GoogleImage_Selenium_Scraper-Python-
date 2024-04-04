from selenium import webdriver
from resources.env import BROWSER_LOCATION, PATH, DRIVER, DEBUG
from resources.textColors import greenText

def webDriverOptions() :
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless=new")
    options.binary_location = BROWSER_LOCATION
    return options


class WebDriverManager() :
    def __init__(self) :
        self.webservice = webdriver.FirefoxService(executable_path=PATH+DRIVER)
        self.webservice.start()
        self.webdriver = webdriver.Firefox(options=webDriverOptions(), service=self.webservice)
        if (DEBUG) : print(greenText("Started WebDriverManager"))
    def stop(self) :
        if (DEBUG) : print(greenText("Stopping WebDriverManager"))

        self.webdriver.quit()
        self.webservice.stop()
    def __end__(self) :
        if (DEBUG) : print(greenText("Stopping WebDriverManager"))
        
        self.webdriver.quit()
        self.webservice.stop()




