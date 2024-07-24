from flask import Flask, render_template, request, send_file, jsonify
import os
import cv2
import numpy as np

app = Flask(__name__)
upload_file_path = 'uploaded_file'

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        if 'file' not in request.files:
            return "No file part"
        file = request.files['file']
        if file.filename == '':
            return "No selected file"
        if file:
            file_extension = os.path.splitext(file.filename)[1]
            file_path_with_extension = upload_file_path + file_extension
            file.save(file_path_with_extension)
            with open('file_info.txt', 'w') as f:
                f.write(file_path_with_extension)
            return "File successfully uploaded"
    return render_template("upload.html")

@app.route("/editselection", methods=["POST"])
def editselection():
    selection = request.form.get("item")
    
    def gray():
        if os.path.exists('file_info.txt'):
            with open('file_info.txt', 'r') as f:
                file_path_with_extension = f.read()
            if os.path.exists(file_path_with_extension):
                img = cv2.imread(file_path_with_extension)
                if img is None:
                    return "Error reading the image file"
                gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                file_extension = os.path.splitext(file_path_with_extension)[1]
                gray_file_path = os.path.join('static', f'gray_uploaded_file{file_extension}')
                cv2.imwrite(gray_file_path, gray_image)
                return gray_file_path
            else:
                return "No file uploaded"
        else:
            return "No file information available"

    def saturation():
        if os.path.exists('file_info.txt'):
            with open('file_info.txt', 'r') as f:
                file_path_with_extension = f.read()
            if os.path.exists(file_path_with_extension):
                img = cv2.imread(file_path_with_extension)
                if img is None:
                    return "Error reading the image file"
                hsv_image = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
                hsv_image[:, :, 1] *= value
                hsv_image[:, :, 1] = np.clip(hsv_image[:, :, 1], 0, 255)
                hsv_image = hsv_image.astype(np.uint8)
                saturated_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)
                file_extension = os.path.splitext(file_path_with_extension)[1]
                sat_file_path = os.path.join('static', f'saturated_uploaded_file{file_extension}')
                cv2.imwrite(sat_file_path, saturated_image)
                return sat_file_path

    def bright():
        if os.path.exists('file_info.txt'):
            with open('file_info.txt', 'r') as f:
                file_path_with_extension = f.read()
            if os.path.exists(file_path_with_extension):
                img = cv2.imread(file_path_with_extension).astype(np.float32)
                if img is None:
                    return "Error reading the image file"
                img += value
                img = np.clip(img, 0, 255).astype(np.uint8)
                file_extension = os.path.splitext(file_path_with_extension)[1]
                bright_file_path = os.path.join('static', f'bright_uploaded_file{file_extension}')
                cv2.imwrite(bright_file_path, img)
                return bright_file_path

    def rotate():
        if os.path.exists('file_info.txt'):
            with open('file_info.txt', 'r') as f:
                file_path_with_extension = f.read()
            if os.path.exists(file_path_with_extension):
                img = cv2.imread(file_path_with_extension)
                if img is None:
                    return "Error reading the image file"
                M = cv2.getRotationMatrix2D((img.shape[1] // 2, img.shape[0] // 2), value, 1)
                cos = np.abs(M[0, 0])
                sin = np.abs(M[0, 1])
                new_w = int((img.shape[0] * sin) + (img.shape[1] * cos))
                new_h = int((img.shape[0] * cos) + (img.shape[1] * sin))
                M[0, 2] += (new_w / 2) - (img.shape[1] / 2)
                M[1, 2] += (new_h / 2) - (img.shape[0] / 2)
                rotated = cv2.warpAffine(img, M, (new_w, new_h))
                file_extension = os.path.splitext(file_path_with_extension)[1]
                rotate_file_path = os.path.join('static', f'rotated_uploaded_file{file_extension}')
                cv2.imwrite(rotate_file_path, rotated)
                return rotate_file_path

    if selection=="gray":
        preview_path = gray()
    elif selection=="sat":
        value=request.form.get("value_sat",type=float)
        preview_path=saturation()
    elif selection == "bright":
        value=request.form.get("value_bright",type=int)
        preview_path = bright()
    elif selection == "rotate":
        value=request.form.get("value_rotate",type=int)
        preview_path = rotate()
        
    else:
        return "Invalid selection"

    if preview_path:
        return jsonify({'preview_path': preview_path})
    else:
        return jsonify({'error': 'Invalid selection'})

if __name__ == "__main__":
    app.run(debug=True, port=5001)
