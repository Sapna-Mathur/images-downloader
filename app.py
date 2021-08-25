from flask import Flask, request, render_template
from ImageExtractor.image_extractor import ImageExtractor
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from MailService.mail_service import MailService
import time

app = Flask(__name__)

chrome_opts = webdriver.ChromeOptions()
chrome_opts.headless = True

destDir = './Images/'


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def job():
    try:
        string = request.form['serchterm']
        totalImgs = int(request.form['number'])
        requestor = request.form['email']

        extractor_object = ImageExtractor(executable_path=ChromeDriverManager().install(), options=chrome_opts)
        extractor_object.openURL("https://www.google.co.in/imghp?hl=en&tab=ri&ogbl")
        extractor_object.searchImage(string)
        extractor_object.getSearchUrl()
        path = extractor_object.saveInDestFolder(destDir, string, totalImgs)
        MailService(direct=path, receiver=requestor)
        extractor_object.closeDriver()
        print('Job is Done!!!!')

    except:
        print('abc')

    msg = f'Images of {string} has been attached to your email.Kindly download them from there!!'
    return render_template('result.html', result=msg)

if __name__ == "__main__":
    app.run(debug=True)