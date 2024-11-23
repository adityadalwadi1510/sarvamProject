from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# API configuration
TRANSLATE_API_URL = "https://api.sarvam.ai/translate"
TEXT_TO_SPEECH_API_URL = "https://api.sarvam.ai/text-to-speech"
API_KEY = "ccb6b820-d6c6-44bc-8402-1eab2f230e5a"  # Replace with your actual API key

# Supported languages for translation and text-to-speech
LANGUAGES = {
    'hi-IN': 'Hindi',
    'gu-IN': 'Gujarati',
    'bn-IN': 'Bengali',
    # Add other supported language codes and names as needed
}

class Translate:
    def __init__(self, api_key):
        self.api_key = api_key

    def translate(self, text, src_lang, target_lang):
        headers = {
            'Content-Type': 'application/json',
            'api-subscription-key': self.api_key,
        }
        payload = {
            "input": text,
            "source_language_code": "en-IN",
            "target_language_code": "hi-IN",
            # "source_language_code": src_lang,
            # "target_language_code": target_lang,
            "speaker_gender": "Male",
            "mode": "formal",
            "model": "mayura:v1",
            "enable_preprocessing": True
        }
        response = requests.post(TRANSLATE_API_URL, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get('translated_text', '')
        else:
            error_message = response.json().get('message', 'Translation failed.')
            raise Exception(f"API Error: {error_message}")

class TextToSpeech:
    def __init__(self, api_key):
        self.api_key = api_key

    def synthesize(self, text, language):
        headers = {
            'Content-Type': 'application/json',
            'api-subscription-key': self.api_key,
        }
        payload = {
             "inputs": [text],
            # "target_language_code": text,
            "target_language_code": "hi-IN",
            "speaker": "meera",
            "pitch": 0,
            "pace": 1.65,
            "loudness": 1.5,
            "speech_sample_rate": 8000,
            "enable_preprocessing": True,
            "model": "bulbul:v1"
        }
        response = requests.post(TEXT_TO_SPEECH_API_URL, json=payload, headers=headers)
        if response.status_code == 200:
            audio_data = response.content
            content_type = response.headers.get('Content-Type', 'audio/mpeg')
            return audio_data, content_type
        else:
            error_message = response.json().get('message', 'Text-to-speech synthesis failed.')
            raise Exception(f"API Error: {error_message}")

translator = Translate(API_KEY)
tts = TextToSpeech(API_KEY)

@app.route('/languages', methods=['GET'])
def get_languages():
    # Return the list of supported languages
    languages = [{'code': code, 'name': name} for code, name in LANGUAGES.items()]
    return jsonify(languages)

@app.route('/translate', methods=['POST'])
def translate_text():
    data = request.json
    target_lang = data.get('target_language')
    text = data.get('text')

    source_lang = 'en'  # Assuming the source language is English

    if not all([source_lang, target_lang, text]):
        return jsonify({'error': 'Missing parameters'}), 400

    try:
        translated_text = translator.translate(text, source_lang, target_lang)
        return jsonify({'translated_text': translated_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    data = request.json
    text = data.get('text')
    language = data.get('language')

    if not all([text, language]):
        return jsonify({'error': 'Missing parameters'}), 400

    try:
        audio_data, content_type = tts.synthesize(text, language)
        return Response(audio_data, mimetype=content_type)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
