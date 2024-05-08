from flask import Blueprint, render_template
from project.main import main


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/about')
def about():
    return render_template('about.html')
