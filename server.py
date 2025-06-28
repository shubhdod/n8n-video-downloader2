from flask import Flask, request, jsonify
import subprocess
import uuid

app = Flask(__name__)

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')
    quality = data.get('quality', 'best')
    media_type = data.get('type', 'video')

    if not url:
        return jsonify({'error': 'Missing URL'}), 400

    filename = f"{uuid.uuid4()}.%(ext)s"
    ytdlp_command = [
        "yt-dlp",
        "-f", quality,
        "--no-playlist",
        "-o", filename,
        "--get-url"
    ]

    if media_type == 'audio':
        ytdlp_command += ["-x", "--audio-format", "mp3"]

    ytdlp_command.append(url)

    try:
        result = subprocess.run(ytdlp_command, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            return jsonify({"error": result.stderr, "output": result.stdout}), 500
        return jsonify({"url": result.stdout.strip()})
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Download timed out"}), 504

@app.route('/', methods=['GET'])
def home():
    return "yt-dlp API is running", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)