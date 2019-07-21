from flask import current_app, render_template
from . import main


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/use_method')
def use_method():

    content = ""
    with open('use_method.md', 'r') as f:
        content = f.read()

    return render_template('use_method.html', text=content)
