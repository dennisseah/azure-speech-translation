from flask import Flask, request, send_file, send_from_directory
import os
import tempfile
from azureservices.speech import to_text, to_speech
from azureservices.translate import translate

languages = {
    "ja": "ja-JP-KeitaNeural",
    "de": "de-DE-AmalaNeural",
    "ms": "ms-MY-OsmanNeural",
    "es": "es-ES-AlvaroNeural",
    "zh": "zh-CN-XiaochenNeural",
}

app = Flask(__name__)
static = os.path.join(os.path.dirname(__file__), "static")


@app.route("/")
def record():
    return send_from_directory(static, "index.html")


@app.route("/translate", methods=["POST"])
def upload_file():
    lang = request.args.get("lang")
    input_file = request.files["file"]
    temp_file = f"{tempfile.NamedTemporaryFile().name}.wav"
    input_file.save(temp_file)

    translated = translate(to_text(temp_file), "en", lang)
    to_speech(translated, temp_file, languages[lang])

    return send_file(
        temp_file,
        mimetype="audio/wav",
        as_attachment=True,
        download_name="translate.wav",
    )


@app.route("/<path:path>")
def _static(path):
    return send_from_directory(static, path)


if __name__ == "__main__":
    app.run()
