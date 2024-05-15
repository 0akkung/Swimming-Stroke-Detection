from flask import render_template, session
from project.models import User, SwimmingRecord
from flask_login import login_required, login_user, logout_user
from project.coach import coach


@coach.route('/dashboard')
@login_required
def dashboard():
    swimmers = User.query.filter_by(role='swimmer').all()
    return render_template('coach/dashboard.html', swimmers=swimmers)


@coach.route('/swimmer/<swimmer_name>')
def swimmer_profile(swimmer_name):
    swimmer = User.query.filter_by(name=swimmer_name).first()
    # Filter records for a specific user within the date range
    swimming_records_today = SwimmingRecord.query.filter(
        SwimmingRecord.profile_id == swimmer.profile.id).all()
    print(swimming_records_today)

    # Calculate average strokes per minute
    total_strokes = sum(record.strokes_per_minute for record in swimming_records_today)
    average_strokes_per_minute = total_strokes / len(swimming_records_today) if swimming_records_today else 0

    return render_template('coach/swimmer_profile.html', swimmer=swimmer,
                           swimming_records=swimming_records_today,
                           average_strokes_per_minute=average_strokes_per_minute)
