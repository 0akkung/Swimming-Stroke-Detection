from flask import Flask, render_template, Response
from SwimmingDetector import SwimmingDetector

app = Flask(__name__, template_folder='./templates')
counter = None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/swim')
def swim():
    return render_template('swim.html')

@app.route('/video_feed')
def video_feed():
    return Response(counter.count_strokes(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    counter = SwimmingDetector()
    app.run(debug=True)
