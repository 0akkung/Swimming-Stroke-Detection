from flask import Flask, render_template, Response
from SwimmingDetector import SwimmingDetector

app = Flask(__name__, template_folder='./templates')
counter = None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(counter.count_strokes(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    counter = SwimmingDetector()
    app.run(debug=True)
