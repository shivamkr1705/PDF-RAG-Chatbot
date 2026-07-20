import os

from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

from utils import process_pdf, ask_question

UPLOAD_FOLDER = "uploads"

app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs("vectorstore", exist_ok=True)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_pdf():
    

    try:

        if "pdf" not in request.files:
            return jsonify({
                "success": False,
                "message": "No PDF selected."
            })

        file = request.files["pdf"]

        if file.filename == "":
            return jsonify({
                "success": False,
                "message": "Please choose a PDF."
            })

        filename = secure_filename(file.filename)

        filepath = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        file.save(filepath)

        process_pdf(filepath)

        return jsonify({
            "success": True,
            "message": "PDF uploaded successfully!"
        })

    except Exception as e:

        print(e)

        return jsonify({
            "success": False,
            "message": str(e)
        })


@app.route("/chat", methods=["POST"])
def chat():

    try:

        data = request.get_json()

        question = data.get("question", "")

        if question == "":
            return jsonify({
                "answer": "Please enter a question."
            })

        answer = ask_question(question)

        return jsonify({
            "answer": answer
        })

    except Exception as e:

        print(e)

        return jsonify({
            "answer": str(e)
        })


if __name__ == "__main__":

    app.run(debug=True)