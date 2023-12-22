# app.py
from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

# Route for the login page
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login')
def login():
    return render_template('login.html')

# Route for the home page
@app.route('/home')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)
