from flask import Flask, render_template, request, send_from_directory, flash, redirect, send_file, after_this_request
from werkzeug.utils import secure_filename
import os
import csv
from OrderedPooledTesting import ORGeneratePools

UPLOAD_FOLDER = ''
ALLOWED_EXTENSIONS = {'csv', 'xls'}
MAX_POOL_SIZE = 32
MAX_TESTS = 6


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


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
            os.remove(UPLOAD_FOLDER + f.filename)
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


@app.route('/example')
def example():
    return render_template('example.html')


# Form for individual testing returns here
@app.route('/intersection', methods=['GET', 'POST'])
def computeIntersect():
    # User enters positive rows and columns and submits the pools file
    # This function will return a file with the intersecting samples to the rows/columns that are positive for
    # individual testing.
    if request.method == 'POST':
        # Access the list of data
        rows = request.form["positiveR"]
        rows = rows.upper()
        cols = request.form["positiveC"]
        cols = cols.upper()
        # Use the same safeguards as initial submit to protect from malicious file uploads
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
            # Save the file first
            f.filename = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))

            # Read from file using openpyxl and create a list from rowsCols
            # Need to remove trailing whitespace
            listR = rows.strip().split(" ")
            listC = cols.strip().split(" ")
            samples2Test = []
            # Create lists from each row/col pair
            with open(f.filename, 'r') as file:
                reader = csv.reader(file)
                # create list of row content from listR
                data = [row for count, row in enumerate(reader) if str(count + 1) in listR]
            # Create content for columns
            for row in data:
                '''
                We know that individual test must be done at each intersection thus we only need the sample
                that is located at the column of the rows we already collect the data of.    
                '''
                for col in listC:
                    samples2Test.append(row[int(col) - 1])
            # Write samples2test to a csv or text file as the individual tests that must be completed
            with open("individualTests.txt", 'w') as file:
                file.write("The following samples should be given individual tests: \n")
                for sample in samples2Test:
                    file.write("%s\n" % sample)
            try:
                # Delete the uploaded file after the request as well as pools.csv
                @after_this_request
                def remove_file(response):
                    try:
                        os.remove(f.filename)
                        os.remove('individualTests.txt')
                    except Exception as error:
                        app.logger.error("Error removing downloaded file ", error)
                    return response
                return send_file("individualTests.txt", as_attachment=True)
            except FileNotFoundError:
                abort(404)


# check if the uploaded file is of the allowed extensions
def allowed_file(filename):
    """
    Determine if an uploaded file is of the allowed extensions
    :param filename: Uploaded filename
    :return: returns the file extension of upload
    """
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Write data to a csv file for download
def writeCSV(pool):
    """
    :param pool: pool object
    :return: No return
    """
    with open('pools.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        # Write all pools to one file with a label of the pool type
        for pool in pool:
            # Label the pool type
            poolType = []
            poolType.append(pool['type'])
            writer.writerow(poolType)
            # Write data if the pool is of PORT
            if (pool["type"] == "PORT"):
                # Check if col > rows then transpose
                if (len(pool['rowPools'][0]) >= len(pool['colPools'][0])):
                    for data in pool['colPools']:
                        writer.writerow(data)
                else:
                    for data in pool['rowPools']:
                        writer.writerow(data)
            elif (pool["type"] == "SINGLE"):
                # Write single testing
                singlePool = []
                for data in pool['rowPools']:
                    singlePool.append(data)
                    writer.writerow(singlePool)
                    singlePool = []
            elif (pool["type"] == "IND"):
                # Write individual tests to the file
                writer.writerow(pool['Pool'])


# Create a dict from the csv passed then send the data to ORGeneratePools and return that data
def createData(filename):
    filename = UPLOAD_FOLDER + filename
    pools = []
    with open(filename, mode='r') as f:
        reader = csv.DictReader(f)
        for data in reader:
            pools.append(data)
    # Cast string to floats for operation
    for dicts in pools:
        dicts['CurrentProb'] = float(dicts['CurrentProb'])
        dicts['InitialProb'] = float(dicts['InitialProb'])

    return ORGeneratePools(pools, MAX_POOL_SIZE, MAX_TESTS)


if __name__ == "__main__":
    app.run(debug=True)
