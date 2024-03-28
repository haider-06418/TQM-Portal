# app.py
from flask import Flask, render_template, redirect, url_for, request, send_file
import os
import subprocess

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
    # Define the path to the Python script for each option
    script_paths = {
        'address-normalization': 'scripts/address_normalization.py',
        'rfo-assignment': 'scripts/rfo_assignment.py',
        'repeated-customer': 'scripts/repeated_customer.py',
        'out-of-tat': 'scripts/out_of_tat.py'
    }

    # Get the path to the script for the selected option
    script_path = script_paths.get(option)
    if not script_path:
        return f"No program found for option: {option}"

    # Save the uploaded file
    filename = os.path.join('uploads', file.filename)
    file.save(filename)

    # Execute the script with the uploaded file as input
    output_file = os.path.join('static', f'{option}_processed.csv')
    subprocess.run(['python', script_path, filename, output_file])

    return output_file

if __name__ == '__main__':
    app.run(debug=True)
