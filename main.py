from flask import Flask, render_template, request, redirect, url_for, session
from bidict import bidict
import random
from random import choice
import numpy as np
from tensorflow import keras
import io
import base64
import matplotlib.pyplot as plt


ENCODER = bidict({
    'alpha': 1, 'beta': 2, 'gamma': 3, 'delta': 4,'epsilon': 5, 'zeta': 6, 'eta': 7,'theta': 8, 'iota': 9, 'kappa': 10, 'lambda': 11, 'mu': 12, 'nu': 13, 'xi': 14, 'omnicron': 15, 'pi': 16, 'rho': 17, 
    'sigma': 18, 'tau': 19, 'upsilon': 20, 'phi': 21, 'chi': 22, 'psi': 23, 'omega': 24
})

app = Flask(__name__)
app.secret_key = "quiz"

@app.route('/')
def index():
    session.clear()
    return render_template("index.html")

@app.route("/add-data", methods=['GET'])
def add_data_get():
    message = session.get("message", "")
    letter = choice(list(ENCODER.keys()))
    labels = np.load("data/labels.npy")
    count = {k : 0 for k in ENCODER.keys()}
    for label in labels:
        count[label] += 1
    count = sorted(count.items(), key=lambda x: x[1])
    letter = count[0][0]
    return render_template("addData.html", letter=letter, message = message)

@app.route("/add-data", methods=['POST'])
def add_data_post():
    label = request.form["letter"]
    labels = np.load("data/labels.npy")
    labels = np.append(labels, label)
    np.save("data/labels.npy", labels)

    pixels = request.form["pixels"]
    pixels = pixels.split(",")
    img = np.array(pixels).astype(float).reshape(1, 50, 50)
    imgs = np.load("data/images.npy")
    imgs = np.vstack([imgs, img])
    np.save("data/images.npy", imgs)
    session["message"] = label + " added to dataset"
    return redirect(url_for("add_data_get"))


@app.route("/practice", methods=['GET'])
def practice_get():
    letter = choice(list(ENCODER.keys()))
    return render_template("practice.html", letter=letter, correct="")
    

@app.route("/practice", methods=['POST'])
def practice_post():
    letter = request.form["letter"]
    pixels = request.form["pixels"]
    pixels = pixels.split(",")
    img = np.array(pixels).astype(float).reshape(1, 50, 50, 1)
    model = keras.models.load_model("scripts/greek_letter.model")
    pred_letter =np.argmax(model.predict(img), axis=1)
    pred_letter = ENCODER.inverse[pred_letter[0]]
    correct = "yes" if pred_letter == letter else "no"
    letter = choice(list(ENCODER.keys()))
    return render_template("practice.html", letter=letter, correct=correct)


@app.route("/practice_guessing", methods=['GET'])
def practice_guessing_get():
    imgs = np.load("data/images.npy")
    random_num = random.randrange(0, len(ENCODER) - 1)
    imgs.astype("float32") / 255
    plt.figure()
    plt.imshow(imgs[random_num])
    plt.axis('off') 
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png')
    plt.close()
    img_buf.seek(0)
    img_str = base64.b64encode(img_buf.read()).decode("utf-8")
    return render_template("practice_guessing.html", image=img_str, num=random_num, correct="")
    

@app.route("/practice_guessing", methods=['POST'])
def practice_guessing_post():
    guess = request.form["u"]
    num = request.form["num"]
    if guess == list(ENCODER.keys())[num]:
        correct = "yes"
    else:
        correct = "no"

    return render_template("practice_guessing.html", num=num, correct=correct)
    

if __name__ == "__main__":
    app.run(debug=True)



    