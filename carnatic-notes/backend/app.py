from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import librosa
import numpy as np
from pydub import AudioSegment
import tempfile

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def mp3_to_wav(mp3_path):
    """Convert MP3 to WAV using pydub."""
    wav_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
    audio = AudioSegment.from_mp3(mp3_path)
    audio.export(wav_path, format="wav")
    return wav_path

def extract_notes(wav_path):
    """Extract Carnatic notes from audio."""
    y, sr = librosa.load(wav_path, sr=None)
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
    notes = []

    for i, pitch in enumerate(np.mean(pitches, axis=0)):
        if pitch > 0:  # Only process valid pitches
            freq = librosa.hz_to_midi(pitch)  # Convert frequency to MIDI
            notes.append((librosa.midi_to_hz(freq), i / sr))

    # Map frequencies to Carnatic swaras
    def map_to_swara(freq):
        swaras = ["Sa", "Ri", "Ga", "Ma", "Pa", "Da", "Ni"]
        base_freq = 240.0  # Base Sa frequency
        for i, swara in enumerate(swaras):
            if abs(freq - base_freq * (2 ** (i / 12.0))) < 5:
                return swara
        return None

    swara_notes = [{"swara": map_to_swara(freq), "time": time} for freq, time in notes if map_to_swara(freq)]
    return swara_notes

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        wav_path = mp3_to_wav(filepath)
        notes = extract_notes(wav_path)
        os.remove(filepath)
        os.remove(wav_path)
        return jsonify(notes)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
