from flask import Flask, request, jsonify, make_response
from langdetect import detect, detect_langs, LangDetectException
from firebase_admin import credentials, firestore, initialize_app
from datetime import datetime

app = Flask(__name__)


# Inline HTML/CSS for index page
INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Language Detection Application</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }
        .container {
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        textarea {
            width: 100%;
            padding: 10px;
            margin-bottom: 10px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        button {
            padding: 10px 20px;
            background-color: #007BFF;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background-color: #0056b3;
        }
        @media (max-width: 600px) {
            .container {
                margin: 20px;
                padding: 15px;
            }
        }
    </style>
    <script>
        function validateForm() {
            const text = document.querySelector('textarea').value;
            if (text.trim().length < 1) {
                alert('Please enter some text.');
                return false;
            }
            return true;
        }
    </script>
</head>
<body>
    <div class="container">
        <h1>Language Detection Application</h1>
        <form action="/detect" method="POST" onsubmit="return validateForm()">
            <textarea name="text" rows="5" placeholder="Enter text here..." required></textarea>
            <button type="submit">Detect Language</button>
        </form>
    </div>
</body>
</html>
"""

# Inline HTML/CSS for result page
RESULT_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Detection Result</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }
        .container {
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        a {
            display: inline-block;
            margin-top: 20px;
            color: #007BFF;
            text-decoration: none;
        }
        @media (max-width: 600px) {
            .container {
                margin: 20px;
                padding: 15px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Detection Result</h1>
        <p><strong>Input Text:</strong> {{ text }}</p>
        <p><strong>Detected Language:</strong> {{ language }}</p>
        <p><strong>Confidence:</strong> {{ confidence }}%</p>
        <a href="/">Detect Another Text</a>
    </div>
</body>
</html>
"""

# Home route
@app.route('/')
def index():
    return make_response(INDEX_HTML)

# Language detection route
@app.route('/detect', methods=['POST'])
def detect_language():
    try:
        text = request.form['text']
        if not text:
            return jsonify({'error': 'No text provided'}), 400

        # Predict language using langdetect
        detected_langs = detect_langs(text)
        detected_lang = detected_langs[0].lang
        confidence = detected_langs[0].prob * 100


        # Render result page with template string
        result_page = RESULT_HTML.replace('{{ text }}', text) \
                                .replace('{{ language }}', detected_lang) \
                                .replace('{{ confidence }}', f'{confidence:.2f}')
        return make_response(result_page)
    except LangDetectException as e:
        return jsonify({'error': 'Could not detect language. Please provide more text.'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API for external NLP integration
@app.route('/api/detect', methods=['POST'])
def api_detect():
    try:
        text = request.json.get('text')
        if not text:
            return jsonify({'error': 'No text provided'}), 400

        detected_langs = detect_langs(text)
        detected_lang = detected_langs[0].lang
        confidence = detected_langs[0].prob

        return jsonify({'language': detected_lang, 'confidence': float(confidence)})
    except LangDetectException as e:
        return jsonify({'error': 'Could not detect language. Please provide more text.'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
