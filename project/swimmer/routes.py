from flask import render_template, redirect, url_for, request, Response, send_file, flash, current_app
from datetime import datetime
from io import BytesIO
from project.forms import SwimmingForm, UserForm
from project.models import SwimmingRecord, Location, User
from flask_login import login_required, current_user
from project.swimmer import swimmer
from project.extensions import db
from project.swimming_detector import SwimmingDetector
from werkzeug.utils import secure_filename
import uuid as uuid
import os

detector = SwimmingDetector()


@swimmer.route('/profile')
@login_required
def profile():
    profile_pic = url_for('static', filename='')
    today = datetime.today().date()
    # Filter records for a specific user within the date range
    swimming_records_today = SwimmingRecord.query.filter(
        SwimmingRecord.profile_id == current_user.profile.id).all()
    print(swimming_records_today)

    # Calculate average strokes per minute
    total_strokes = sum(record.strokes_per_minute for record in swimming_records_today)
    average_strokes_per_minute = total_strokes / len(swimming_records_today) if swimming_records_today else 0

    return render_template('profile/index.html', swimming_records=swimming_records_today,
                           average_strokes_per_minute=average_strokes_per_minute)


@swimmer.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    id = current_user.id
    user = User.query.get_or_404(id)
    form = UserForm(request.form, obj=user)
    if request.method == "POST" and form.validate():
        form.populate_obj(user)

        print('validated')

        # code to validate and add user to database goes here
        profile_form = form.profile
        if not profile_form.profile_pic.data:
            print('no profile_pic')
        user.profile.height = profile_form.height.data
        user.profile.weight = profile_form.weight.data
        user.profile.gender = profile_form.gender.data

        # Grab image name
        # pic_filename = secure_filename(profile_form.profile_pic.filename)
        #
        # # Set UUID
        # pic_name = str(uuid.uuid1()) + "_" + pic_filename
        #
        # # Save the image
        # user.profile.profile_pic.save(os.path.join(current_app.config['UPLOAD_FOLDER'], pic_name))
        #
        # user.profile.profile_pic = pic_name

        db.session.commit()

        flash('Your profile has been successfully updated.', 'success')
        return redirect(url_for('swimmer.profile'))

    return render_template('profile/edit.html', form=form)


@swimmer.route('/swim', methods=['GET', 'POST'])
@login_required
def swim():
    global detector
    if request.method == 'GET':
        detector.reset()
    form = SwimmingForm(request.form)
    form.location.choices = [(c.id, c.name) for c in Location.query.all()]

    if request.method == 'POST' and form.validate():
        time = str(int(detector.get_elapsed_time())) + 's'
        stroke = detector.get_strokes()
        style = detector.get_style()
        length = form.length.data
        location = Location.query.filter_by(id=form.location.data).first().name
        spm = detector.get_strokes_per_minute()
        date = datetime.now()
        new_swimming_record = SwimmingRecord(profile_id=current_user.profile.id, time=time, stroke=stroke, style=style,
                                             pool_length=length, location=location,
                                             strokes_per_minute=spm, date=date)

        # Add the new record to the database
        db.session.add(new_swimming_record)
        db.session.commit()

        return redirect(url_for('swimmer.swim_result'))

    return render_template('swim.html', detector=detector, form=form)


@swimmer.route('/video_feed')
def video_feed():
    return Response(detector.count_strokes(), mimetype='multipart/x-mixed-replace; boundary=frame')


@swimmer.route('/swim', methods=['POST'])
@login_required
def save_swim_result():
    global detector


@swimmer.route('/swim/result')
@login_required
def swim_result():
    global detector
    strokes = detector.get_strokes()
    spm = detector.get_strokes_per_minute()
    # counter.reset()
    return render_template('swim-result.html', strokes=strokes, spm=spm)


@swimmer.route('/plot_angle')
def plot_angle():
    # Create matplotlib graph
    plt = detector.plot_angles()

    # Save the graph to a BytesIO object
    img_bytes = BytesIO()
    plt.savefig(img_bytes, format='png')
    img_bytes.seek(0)

    # Clear the matplotlib plot to avoid memory leaks
    plt.clf()

    # Return the BytesIO object containing the graph image
    return send_file(img_bytes, mimetype='image/png')
