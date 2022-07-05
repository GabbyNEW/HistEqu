# heroku logs -a just-a-temp-flask --tail
from enum import auto
from flask import Flask, render_template, request, redirect, url_for, session
import matplotlib
from PIL import Image
from histogram_equalization import he
from dynamic_histogram_equalization import dhe
import io
from werkzeug.utils import secure_filename
import os

# Define the static and uploads directories
UPLOAD_FOLDER = 'uploads/'
STATIC_FOLDER = 'static/'
app = Flask(__name__, static_folder=STATIC_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.secret_key = 'super secret key'

# NOTE: Using autoreload on Heroku causes the flask app to crash and not start
app.config['TEMPLATES_AUTO_RELOAD'] = True
print("Running with auto reload " + "enabled" if str(app.config['TEMPLATES_AUTO_RELOAD']) else "disabled")

# Routing
@app.route("/", methods = ['POST', 'GET', 'PUT'])
def index():
    return render_template('index.html')

@app.route("/upload", methods = ['GET'])
def goto_upload():
    return redirect(url_for('index') + '#upload')

@app.route("/select", methods = ['GET'])
def goto_select():
    return redirect(url_for('index') + '#select')

@app.route("/result", methods = ['GET'])
def goto_result():
    if 'input_image' in session :
        input_image = session['input_image']
        output_image = session['output_image']
    else :
        input_image = None
        output_image = None
    session.clear()
    return render_template('index.html', input_image=input_image, output_image=output_image, anchor="#result")

@app.route("/image_upload", methods= ['POST'])
def dhe_upload():
    size = 480, 480
    # TODO Change the key name
    method = request.form['key']

    image = request.files["file"]
    im = Image.open(image)
    im.filename = "input.jpg"
    im.thumbnail(size, Image.ANTIALIAS)
    width, height = im.size
    print("Image resized to " + str(width) + "x" + str(height))
    im.save(os.path.join(app.config["UPLOAD_FOLDER"], im.filename))
    session['input_image'] = im.filename
    # 1 for DHE, 2 for HE
    if method == 1:
        perform_dhe(input_image=im.filename)
        session['output_image'] = "output_dhe.jpeg"
    else:
        perform_he(input_image=image.filename)
        session['output_image'] = "output_he.jpeg"

    # return redirect(url_for('.dhe_web'))
    return "Success"

@app.route('/uploads/<filename>')
def send_image_file(filename=''):
    from flask import send_from_directory
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route('/downloads/<filename>')
def download_image_file(filename=''):
    from flask import send_from_directory
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

def perform_he(input_image):
    # stores the np.array of the output image
    result = he("uploads/"+input_image)
    # convert np.array to .PNG image and save it
    im = Image.fromarray(result)
    im.save('uploads/output_he.jpeg')

def perform_dhe(input_image):
    # stores the np.array of the output image
    result = dhe("uploads/"+input_image)
    # convert np.array to .PNG image and save it
    im = Image.fromarray(result)
    im.save('uploads/output_dhe.jpeg')