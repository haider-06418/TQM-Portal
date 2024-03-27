# app.py
from flask import Flask, render_template, redirect, url_for, request, send_file
import os
import pandas as pd

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

# Route for processing the uploaded file
@app.route('/process_file', methods=['POST'])
def process_file():
    option = request.form['preprocessing-option']
    file = request.files['file-upload']

    # Check if a valid option is selected
    if option == 'choose-option':
        return "Select a valid option."

    # Check if the file type is CSV
    if not file.filename.endswith('.csv'):
        return "File type must be CSV."

    # Process the file based on the selected option
    processed_file = process_data(option, file)

    # Return the processed file
    return send_file(processed_file, as_attachment=True)

def process_data(option, file):
    # Implement your processing logic here
    # You can create separate Python programs for each option
    # For now, just save the file with a different name
    filename, file_extension = os.path.splitext(file.filename)
    processed_filename = f"{filename}_processed{file_extension}"

    # Save the processed file to the static folder
    processed_file_path = os.path.join('static', processed_filename)
    file.save(processed_file_path)

    return processed_file_path

if __name__ == '__main__':
    app.run(debug=True)
