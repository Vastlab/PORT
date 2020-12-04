from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename


app = Flask(__name__)


# at localhost:5000/upload pull upload.html
@app.route("/")
def upload_file():
    return render_template('upload.html')


# save uploaded file when submitted at localhost:5000/upload
@app.route("/uploader", methods = ['GET', 'POST'])
def uploader_file():
    if request.method == 'POST':
        f = request.files['file']
        #modify file before returning

        #returns the uploaded file as a download
        return send_file(f.filename, as_attachment=True)


if __name__=="__main__":
    app.run(debug=True)
