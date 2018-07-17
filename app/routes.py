from app import app
from flask import redirect, render_template, url_for

@app.route('/')
def index():
  context = {
    'title': 'Site Name'
  }
  return render_template('index.html', **context)