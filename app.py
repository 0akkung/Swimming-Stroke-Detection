from flask import Flask, render_template, redirect, url_for, request, flash, Response, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from swimming_detector import SwimmingDetector
from datetime import datetime
from io import BytesIO

from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user

app = Flask(__name__, template_folder='./templates')
app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
db = SQLAlchemy(app)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    """Create columns to store our data"""
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(1000), nullable=False)
    height = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    date_of_birth = db.Column(db.DateTime, nullable=False)
    swimming_records = db.relationship('SwimmingRecord', backref='user', lazy=True)

    def calculate_age(self):
        today = datetime.now()
        age = today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return age

    def __repr__(self):
        return '<User %r>' % self.username


class SwimmingRecord(db.Model):
    __tablename__ = 'swimming_records'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    stroke = db.Column(db.Integer, nullable=False)
    style = db.Column(db.String(20), nullable=False)
    strokes_per_minute = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)


with app.app_context():
    db.create_all()

counter = SwimmingDetector()

login_manager = LoginManager()  # Login manage for flask-login
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        # login code goes here
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(email=email).first()

        # check if the user actually exists
        # take the user-supplied password, hash it, and compare it to the hashed password in the database
        if not user or not check_password_hash(user.password, password):
            print("Invalid password")
            flash('Please check your login details and try again.')
            return redirect(url_for('login'))  # if the user doesn't exist or password is wrong, reload the page

        # if the above check passes, then we know the user has the right credentials
        login_user(user, remember=remember)
        return redirect(url_for('profile'))

    return render_template('login.html')


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # code to validate and add user to database goes here
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        height = request.form.get('height')
        weight = request.form.get('weight')
        dob = request.form.get('dob')
        dob = datetime.strptime(dob, '%Y-%m-%d').date()

        user = User.query.filter_by(
            email=email).first()  # if this returns a user, then the email already exists in database

        if user:  # if a user is found, we want to redirect back to signup page so user can try again
            flash('Email address already exists')
            return redirect(url_for('register'))

        # create a new user with the form data. Hash the password so the plaintext version isn't saved.
        new_user = User(email=email, name=name, password=generate_password_hash(password, method='pbkdf2:sha256'),
                        height=height, weight=weight, date_of_birth=dob)

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/profile')
@login_required
def profile():
    print(current_user.swimming_records)
    return render_template('profile.html')


@app.route('/swim')
@login_required
def swim():
    global counter
    counter.reset()
    return render_template('swim.html', counter=counter)


@app.route('/video_feed')
def video_feed():
    global counter
    return Response(counter.count_strokes(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/swim', methods=['POST'])
@login_required
def save_swim_result():
    global counter
    time = str(int(counter.get_elapsed_time())) + 's'
    stroke = counter.get_strokes()
    style = counter.get_style()
    spm = counter.get_strokes_per_minute()
    date = datetime.now()
    new_swimming_record = SwimmingRecord(user_id=current_user.id, time=time, stroke=stroke, style=style,
                                         strokes_per_minute=spm, date=date)

    # Add the new record to the database
    db.session.add(new_swimming_record)
    db.session.commit()

    return redirect(url_for('swim_result'))


@app.route('/swim/result')
@login_required
def swim_result():
    global counter
    strokes = counter.get_strokes()
    spm = counter.get_strokes_per_minute()
    # counter.reset()
    return render_template('swim-result.html', strokes=strokes, spm=spm)


@app.route('/plot_angle')
def plot_angle():
    # Create matplotlib graph
    plt = counter.plot_angles()

    # Save the graph to a BytesIO object
    img_bytes = BytesIO()
    plt.savefig(img_bytes, format='png')
    img_bytes.seek(0)

    # Clear the matplotlib plot to avoid memory leaks
    plt.clf()

    # Return the BytesIO object containing the graph image
    return send_file(img_bytes, mimetype='image/png')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
