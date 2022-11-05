from flask import Flask, flash, request, redirect, url_for, render_template
import os
import cv2
from werkzeug.utils import secure_filename
import pytesseract
from pytesseract import Output

app = Flask(__name__)
config = r"--psm 11 --oem 3"

UPLOAD_FOLDER = 'static/uploads/'
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def home():
    arr = os.listdir(UPLOAD_FOLDER)
    print(arr)
    for file in arr:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], file))
    return render_template('index.html')

@app.route('/', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename);
        file.save(save_path)
        img = cv2.imread(save_path)
        text = pytesseract.image_to_string(img,config=config);
        flash('Image successfully uploaded and text displayed below')
        data = pytesseract.image_to_data(img,config=config,output_type=Output.DICT);
        amount_boxes = len(data['text'])

        for i in range(amount_boxes):
            if float(data['conf'][i]) > 50:
                (x,y,width,height) = (data['left'][i],data['top'][i],data['width'][i],data['height'][i])
                img = cv2.rectangle(img,(x,y),(x+width,y+height),(0,255,0),2)
        cv2.imwrite(save_path,img);

        return render_template('index.html', filename=filename, text=text)
    else:
        flash('Allowed image types are - png, jpg, jpeg')
        return redirect(request.url)

@app.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
