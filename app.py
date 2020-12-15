from flask import Flask, render_template, request, send_from_directory, flash, redirect, send_file
from werkzeug.utils import secure_filename
import os
import csv
from OrderedPooledTesting import ORGeneratePools

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
MAXPOOLSIZE = 16
MAXTESTS = 6


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# at localhost:5000/upload pull upload.html
@app.route("/")
def upload_file():
    return render_template('upload.html')


# save uploaded file when submitted at localhost:5000/upload
@app.route("/uploader", methods = ['GET', 'POST'])
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
            # f.read to create a string of the uploaded file
            fstring = f.read()
            # create list of dictionaries keyed by header row
            # csv_dicts = [{k: v for k, v in row.items()} for row in
              # csv.DictReader(fstring.splitlines(), skipinitialspace=True)]
            pools = createData(f.filename)
            writeCSV(pools)
            # modify file before returning
            # returns the uploaded file as a download
            try:
                return send_file('pools.csv', as_attachment=True)
            except FileNotFoundError:
                abort(404)
            # return send_from_directory(filename='pools.csv', as_attachment=True, directory=UPLOAD_FOLDER) #and os.remove(UPLOAD_FOLDER + '/' + f.filename)


# check if the uploaded file is of the allowed extensions
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def writeCSV(pool):
    with open('pools.csv', 'w', newline='') as f:
        pool_keys = set().union(*(d.keys() for d in pool))
        writer = csv.DictWriter(f, fieldnames=pool_keys)
        writer.writeheader()
        # for data in sample:
        # genPools = ORGeneratePools(data, 16, 6)
        for data in pool:
            writer.writerow(data)


# Create a dict from the csv passed then send the data to ORGeneratePools and return that data
def createData(filename):
    pools = []
    with open(filename, mode='r') as f:
        reader = csv.DictReader(f)
        for data in reader:
            pools.append(data)

    for dicts in pools:
        dicts['CurrentProb'] = float(dicts['CurrentProb'])
        dicts['InitialProb'] = float(dicts['InitialProb'])

    print("Data from csv: ", pools)
    #print("Data generated: ", ORGeneratePools(pools, 16, 6))
    return ORGeneratePools(pools, MAXPOOLSIZE, MAXTESTS)


if __name__=="__main__":
    app.run(debug=True)
