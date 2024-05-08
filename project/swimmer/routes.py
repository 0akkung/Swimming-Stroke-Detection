from flask import render_template, redirect, url_for, request, Response, send_file
from project.swimming_detector import SwimmingDetector
from datetime import datetime
from io import BytesIO
from project.models import db, SwimmingRecord
from flask_login import login_required, current_user
from project.swimmer import swimmer

detector = SwimmingDetector()


@swimmer.route('/profile')
@login_required
def profile():
    today = datetime.today().date()
    # Filter records for a specific user within the date range
    swimming_records_today = SwimmingRecord.query.filter(
        SwimmingRecord.user_id == current_user.id).all()
    print(swimming_records_today)

    # Calculate average strokes per minute
    total_strokes = sum(record.strokes_per_minute for record in swimming_records_today)
    average_strokes_per_minute = total_strokes / len(swimming_records_today) if swimming_records_today else 0

    return render_template('profile.html', swimming_records=swimming_records_today,
                           average_strokes_per_minute=average_strokes_per_minute)


@swimmer.route('/swim')
@login_required
def swim():
    global detector
    detector.reset()
    return render_template('swim.html', detector=detector)


@swimmer.route('/video_feed')
def video_feed():
    global detector
    return Response(detector.count_strokes(), mimetype='multipart/x-mixed-replace; boundary=frame')


@swimmer.route('/swim', methods=['POST'])
@login_required
def save_swim_result():
    global detector
    time = str(int(detector.get_elapsed_time())) + 's'
    stroke = detector.get_strokes()
    style = detector.get_style()
    length = request.form['length']
    spm = detector.get_strokes_per_minute()
    date = datetime.now()
    new_swimming_record = SwimmingRecord(user_id=current_user.id, time=time, stroke=stroke, style=style,
                                         pool_length=length,
                                         strokes_per_minute=spm, date=date)

    # Add the new record to the database
    db.session.add(new_swimming_record)
    db.session.commit()

    return redirect(url_for('swimmer.swim_result'))


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
