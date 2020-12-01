from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
app = Flask(__name__)

@app.route("/")
def upload_page():
    return "Proceed to localhost:5000/upload"


# at localhost:5000/upload pull upload.html
@app.route("/upload")
def upload_file():
    return render_template('upload.html')


# save uploaded file when submitted at localhost:5000/upload
@app.route("/uploader", methods = ['GET', 'POST'])
def uploader_file():
    if request.method == 'POST':
        f = request.files['file']
        f.save(secure_filename(f.filename))
        return 'file uploaded successfully'


if __name__=="__main__":
    app.run(debug=True)
