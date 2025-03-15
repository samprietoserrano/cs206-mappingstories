import sys
sys.path.append('/Users/samxp/Documents/Coding and Software/EJ-BayCurious/')
from analyzer_process import location_results

import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

# Set up Flask app
app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for flash messages

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/results/<path:file_id>')
def results(file_id):
    try:
        with open(file_id, 'r') as file:
            # transcript = file.read()

            lines = file.readlines()
            title = lines[0]
            transcript = ''.join(lines[1:]) if len(lines) > 1 else ''

        ranked_locations = location_results(title, transcript)

        return render_template('results.html', ranked_locations=ranked_locations)
    
    except Exception as e:
        flash(f"Error processing file: {str(e)}")
        return redirect(url_for('index'))
    

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        
        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:             
                return render_template('loading.html', file_id=filepath)
            except Exception as e:
                flash(f"Error processing file: {str(e)}")
                return redirect(request.url)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)