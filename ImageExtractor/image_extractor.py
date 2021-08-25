from selenium import webdriver
from ObjectRepos.object_repos import Object
import time
import os
import requests
from PIL import Image
import io
from log import App_Logger
import concurrent.futures


class ImageExtractor:
    MAX_THREADS = 30
    def __init__(self, executable_path, options):
        """
        This function initializes the chrome web browser
        :param executable_path: path to executable
        :param chrome_options: takes an instance of ChromeOptions
        """
        self.logger = App_Logger("extractor_logs.txt")
        self.MAX_THREADS = 30
        self.identifier = Object()

        try:
            self.driver = webdriver.Chrome(executable_path=executable_path, options=options)
            self.logger.log('info', 'Driver is Initialized.')
        except Exception as e:
            self.logger.log('error', f"(__init__): Something went wrong on initializing the webdriver object.\n" + str(e))

    def openURL(self, url):
        """
        Opens the passed url
        """
        try:
            self.driver.get(url)
            self.logger.log('info', 'Google Search Url is Hitted.')

        except Exception as e:
            self.logger.log('error', f"(openURL) - Something went wrong on opening the url {url}.\n" + str(e))

    # def getIdentifiersObject(self):
    #     """
    #     This function initializes the identifier object and returns identifier object
    #     """
    #     try:
    #         identifiers = Object()
    #     except Exception as e:
    #         self.logger.log(f"(getIdentifiersObject) - Could not find identifiers\n" + str(e))
    #
    #     return identifiers

    def searchImage(self, searchTerm):
        """
        This function helps to search using search term provided by user
        """

        try:
            # identifier = self.getIdentifiersObject()
            search_box = self.driver.find_element_by_name(name=self.identifier.getGoogleSearchBox())
            search_box.send_keys(searchTerm)

            search_button = self.driver.find_element_by_xpath(xpath=self.identifier.getGoogleSeachButton())
            search_button.click()
            self.logger.log('info', f'Images are searched for {searchTerm}.')
        except Exception as e:
            self.logger.log('error', f"(searchImage) - Something went wrong on searching.\n" + str(e))

    def getSearchUrl(self):
        """
        This function returns the search url for a particular search
        """
        try:
            # self.searchImage(searchTerm=search_string)
            search_url = self.driver.current_url
            self.logger.log('info', f'Url: {search_url}')
        except Exception as e:
            self.logger.log('error', f"(getSearchUrl) - Something went wrong on getting the url for search result.\n" + str(e))
        return search_url

    def scroll_to_end(self):
        """
        This function scrolls the web page at the end
        """
        try:
            # identifier = self.getIdentifiersObject()
            self.driver.execute_script(script=self.identifier.getScriptScrollToEnd())
            time.sleep(5)

        except Exception as e:
            self.logger.log('error', f"(scroll_to_end) - Something went wrong on scrolling the webpage to the end\n" + str(e))

    def show_more_button(self):
        """
        This function clicks on show more results button and shows more results
        """
        try:
            # identifier = self.getIdentifiersObject()
            self.driver.find_element_by_css_selector(css_selector=self.identifier.getShowMoreButton())
            self.driver.execute_script(script=self.identifier.getScriptShowMoreButton())
        except Exception as e:
            self.logger.log('error', f"(show_more_button) - Something went wrong on showing the more results \n" + str(e))

    def get_thumbnail_results(self):
        """
        This function returns all the thumbnails
        """
        try:
            # identifier = self.getIdentifiersObject()
            thumbnails = self.driver.find_elements_by_xpath(xpath=self.identifier.getThumbnailResults())
        except Exception as e:
            self.logger.log('error', f"(get_thumbnail_results) - Something went wrong on getting the thumbnails \n" + str(e))
        return thumbnails

    def get_actual_images(self):
        """
        This function returns all the actual images
        """
        try:
            # identifier = self.getIdentifiersObject()
            actual_images = self.driver.find_elements_by_css_selector(css_selector=self.identifier.getActualImages())
        except Exception as e:
            self.logger.log('error', f"(get_actual_images) - Something went wrong on getting the actual images \n" + str(e))
        return actual_images

    def getImageUrls(self, total_imgs):
        """
        This function returns all the urls of images
        """
        # print('In getImageUrls')
        # self.driver.get(searched_url)

        img_urls = set()
        img_count = 0
        results_start = 0

        while img_count < total_imgs:

            try:
                self.scroll_to_end()

                thumbnail_results = self.get_thumbnail_results()
                total_results = len(thumbnail_results)
                self.logger.log('info', f"Found: {total_results} search results. Extracting links from {results_start}:{total_results}")

                for img in thumbnail_results[results_start:total_results]:
                    self.driver.execute_script("arguments[0].click();", img)
                    time.sleep(0.25)

                    actual_images = self.get_actual_images()

                    for actual_image in actual_images:
                        if actual_image.get_attribute('src') and 'https' in actual_image.get_attribute('src'):
                            img_urls.add(actual_image.get_attribute('src'))

                    img_count = len(img_urls)
                    if img_count >= total_imgs:
                        self.logger.log('info', f"Found: {img_count} image links")
                        break
                    else:
                        self.logger.log('info', f"Found: {img_count}, looking for more image links ...")
                        self.show_more_button()
                        results_start = len(thumbnail_results)

            except Exception as e:
                 self.logger.log('error', f"(getImageUrls) - Something went wrong on getting image urls.\n" + str(e))

        return img_urls

    def downloadImages(self, folder_path, file_name, url):
        """
        This function downloads each image
        """
        # print('in downloadImages')
        try:
            image_content = requests.get(url).content

        except Exception as e:
            self.logger.log('error', f"COULD NOT DOWNLOAD {url} - {e}")

        try:
            image_file = io.BytesIO(image_content)
            image = Image.open(image_file).convert('RGB')

            file_path = os.path.join(folder_path, file_name).strip()

            with open(file_path, 'wb') as f:
                image.save(f, "JPEG", quality=85)
            self.logger.log('info', f"SAVED - {url} - AT: {file_path}")
        except Exception as e:
            self.logger.log('error', f"COULD NOT SAVE {url} - {e}")

    def saveInDestFolder(self, destDir: str, name: str, totalImgs: int):
        """
        This function saves each image in destination directory
        """
        # print('In saveInDestFolder')
        try:
            path = os.path.join(destDir, '_'.join(name.lower().split(' ')))
            if not os.path.isdir(path):
                os.mkdir(path)
            self.logger.log('info', f'Current Path: {path}')
            totalLinks = self.getImageUrls(totalImgs)
            self.logger.log('info', f'totalLinks: {totalLinks}')

            if totalLinks is None:
                self.logger.log('info', f'images not found for : {name}')
                # continue
            else:
                # for i, link in enumerate(totalLinks):
                #     file_name = f"{i}.jpg"
                #     # print(file_name)
                #     self.downloadImages(path, file_name, link)
                threads = min(self.MAX_THREADS, len(totalLinks))

                with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
                    args = ((path, f"{i}.jpg", link) for i, link in enumerate(totalLinks))
                    executor.map(lambda p: self.downloadImages(*p), args)
        except Exception as e:
            self.logger.log('error', f"(saveInDestFolder) - Something went wrong on saving the images \n" + str(e))

        return path

    # def getImageFiles(self, dir):
    #     try:
    #         files = os.listdir(dir)
    #         # self.logger.log('info', f"(getImageFiles) - Something went wrong on getting the files of all images \n" + str(e))
    #
    #     except Exception as e:
    #         self.logger.log('error', f"(getImageFiles) - Something went wrong on getting the files of all images \n" + str(e))
    #
    #     return files


    def closeDriver(self):
        """
        This function closes the connection
        """
        try:
            self.driver.close()
            self.logger.log('info', 'Driver is Closed.')
        except Exception as e:
            self.logger.log('error', f"(closeDriver) - Something went wrong on closing the driver.\n" + str(e))
