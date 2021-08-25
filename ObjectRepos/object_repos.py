class Object:

    def getGoogleSearchBox(self):
        element = "q"
        return element

    def getGoogleSeachButton(self):
        xpath = "//button[@aria-label='Google Search']"
        return xpath

    def getShowMoreButton(self):
        css_selector = ".mye4qd"
        return css_selector

    def getScriptScrollToEnd(self):
        script = "window.scrollTo(0, document.body.scrollHeight);"
        return script

    def getScriptShowMoreButton(self):
        script = "document.querySelector('.mye4qd').click();"
        return script

    def getThumbnailResults(self):
        xpath = "//img[contains(@class,'Q4LuWd')]"
        return xpath

    def getActualImages(self):
        css_selector = "img.n3VNCb"
        return css_selector

