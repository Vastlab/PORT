from flask import Flask, render_template, request, send_from_directory, flash, redirect, send_file, after_this_request
from werkzeug.utils import secure_filename
import os
import csv
from OrderedPooledTesting import ORGeneratePools

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'xls'}
MAX_POOL_SIZE = 16
MAX_TESTS = 6


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
"""
 To do:
    Make the site pretty, include examples and instructions for uploading the data
    Secure coding principles, html headers avoid xss vulnerabilities
    Consistent programming check quotes 
    Assign manual entry to variables in a pool dict
        if the given form does not have certain aspects filled out such as provider ID, current probability,
        positive, and test number filled out then those should be automatically given some value such as 0
"""


# at localhost:5000/upload pull upload.html
@app.route('/')
def upload_file():
    return render_template('upload.html')


# save uploaded file when submitted at localhost:5000/upload
@app.route('/uploader', methods=['GET', 'POST'])
def uploader_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        f = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if f.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if f and allowed_file(f.filename):
            f.filename = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))
            # Creates a list of dictionaries for use with
            pools = createData(f.filename)
            writeCSV(pools)
            f.close()
            os.remove('uploads/' + f.filename)
            # os.remove('uploads/pools.csv')
            # returns the uploaded file as a download
            try:
                # Delete the uploaded file after the request as well as pools.csv
                @after_this_request
                def remove_file(response):
                    try:
                        f.close()
                        os.remove(f.filename)
                        os.remove('pools.csv')
                    except Exception as error:
                        app.logger.error("Error removing downloaded file ", error)
                    return response
                return send_file('pools.csv', as_attachment=True)
            except FileNotFoundError:
                abort(404)
            # return send_from_directory(filename='pools.csv', as_attachment=True, directory=UPLOAD_FOLDER)

@app.route('/example')
def example():
    return render_template('example.html')


# Form for manual entry returns here
@app.route('/manual-entry', methods=['GET', 'POST'])
def manual_upload():
    # Create list of samples as in generateSamples
    # Needs to obtain number of samples from input data to create each sample
    # Also needs to make infection rate be collected per sample instead of constant/sample

    samples = [{
        'SampleID': uuid.uuid4().hex,
        'ProviderID': ProviderID,
        'UserKey': uuid.uuid4().hex,
        'InitialProb': infectionRate,
        'CurrentProb': infectionRate,
        'numTest': 1,
        'Positive': "Unknown"} for index in range(countSamples)]


# check if the uploaded file is of the allowed extensions
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Write data to a csv file for download
def writeCSV(pool):
    with open('pools.csv', 'w', newline='') as f:
        # pool_keys = set().union(*(d.keys() for d in pool))
        writer = csv.writer(f)
        # writer.writeheader()
        # for data in sample:
        # genPools = ORGeneratePools(data, 16, 6)
        for data in pool[0]['colPools']:
            writer.writerow(data)


# Create a dict from the csv passed then send the data to ORGeneratePools and return that data
def createData(filename):
    filename = 'uploads/' + filename
    pools = []
    with open(filename, mode='r') as f:
        reader = csv.DictReader(f)
        for data in reader:
            pools.append(data)
    # Cast string to floats for operation
    for dicts in pools:
        dicts['CurrentProb'] = float(dicts['CurrentProb'])
        dicts['InitialProb'] = float(dicts['InitialProb'])

    print("Data from csv: ", pools)
    # print("Data generated: ", ORGeneratePools(pools, 16, 6))
    return ORGeneratePools(pools, MAX_POOL_SIZE, MAX_TESTS)


if __name__ == "__main__":
    app.run(debug=True)
