import os
import numpy as np
from flask import Flask, request, render_template, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from PIL import Image
import random

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed to enable session management
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max upload size 16 MB

# Create upload folder if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Check if the file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Random prediction function
def random_predict():
    diseases = ['N', 'D', 'G', 'C', 'A', 'H', 'M', 'O']
    return random.choice(diseases)

# Home route
@app.route('/')
def home():
    return render_template('home.html')

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Save registration info in a session for demo purposes
        session['user'] = {'username': username, 'email': email, 'password': password}
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Check if the login details match the session data
        user = session.get('user')
        if user and user['email'] == email and user['password'] == password:
            session['logged_in'] = True
            return redirect(url_for('predict'))
        else:
            flash('Invalid email or password. Please try again.')
    return render_template('login.html')

# Prediction route
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if not session.get('logged_in'):
        flash('You must be logged in to access this page.')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Extract patient info from form
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        gender = request.form['gender']
        symptoms = request.form['symptoms']
        health_details = request.form['health_details']
        
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part. Please upload an image.')
            return redirect(request.url)
        
        file = request.files['file']
        
        # If user does not select file, browser may submit an empty part without filename
        if file.filename == '':
            flash('No selected file. Please upload an image.')
            return redirect(request.url)
        
        # Check if the file is allowed
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Randomly predict a disease
            disease_name = random_predict()

            # Treatment and Precautions
            full_disease_names = {
                'N': 'Normal',
                'D': 'Diabetes',
                'G': 'Glaucoma',
                'C': 'Cataract',
                'A': 'Age related Macular Degeneration',
                'H': 'Hypertension',
                'M': 'Pathological Myopia',
                'O': 'Other diseases/abnormalities'
            }

            treatment_dict = {
                'N': 'Regular eye checkups and use of prescribed eye drops.',
                'D': 'Medication to manage diabetes and regular eye exams.',
                'G': 'Eye drops to reduce intraocular pressure or surgery.',
                'C': 'Surgery to remove cataract and restore vision.',
                'A': 'Lifestyle changes and medication to reduce cholesterol.',
                'H': 'Medications or surgery to manage hypertension.',
                'M': 'Photocoagulation therapy to treat pathological myopia.',
                'O': 'Medication and lifestyle changes for optimal eye health.'
            }
            precautions_dict = {
                'N': 'Avoid exposure to bright lights, wear sunglasses.',
                'D': 'Maintain blood sugar levels, avoid smoking.',
                'G': 'Regular eye exams, avoid strenuous activities.',
                'C': 'Wear protective eyewear, avoid bright light post-surgery.',
                'A': 'Healthy diet, avoid junk food.',
                'H': 'Regular exercise, manage stress levels.',
                'M': 'Avoid excessive screen time, use reading glasses.',
                'O': 'Maintain healthy diet, regular eye exams.'
            }

            treatment = treatment_dict[disease_name]
            precautions = precautions_dict[disease_name]
            disease_full_name = full_disease_names[disease_name]

            return render_template('result.html', disease_name=disease_full_name,
                                   treatment=treatment, precautions=precautions)
        else:
            flash('Invalid file format. Please upload a valid image file.')
            
    return render_template('predict.html')

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
