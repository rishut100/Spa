import sys
import os
import glob
import re
import cv2
import requests
from flask import Flask, redirect, url_for, request, render_template
from datetime import date
from .Eye_Tracking import eye_tracker


app = Flask(__name__)
uploads_dir = os.path.join(app.instance_path, 'uploads')
chunk_no = 0


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        print("DATA ==>")
        print(request.form['link'])
        if request.files:
            video = request.files['videofile']
            today = date.today()
            dateTime = today.strftime("%b-%d-%Y")
            dateTime = dateTime + str(chunk_no) + '.mp4'
            video.save(os.path.join(uploads_dir, dateTime))
            chunk_no += 1
            eye_tracker(os.path.join(uploads_dir, dateTime))
    else:
        print('hello')
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
