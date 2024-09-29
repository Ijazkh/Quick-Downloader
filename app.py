from flask import Flask, request, jsonify, send_from_directory, render_template_string
import os
import yt_dlp as youtube_dl

app = Flask(__name__)

# HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QuickDownloader</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
            color: #333;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }
        header {
            background-color: #4caf50;
            color: white;
            padding: 1rem;
            text-align: center;
        }
        .container {
            max-width: 600px;
            margin: 2rem auto;
            padding: 2rem;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        input, select, button {
            width: 100%;
            padding: 1rem;
            margin-bottom: 1rem;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 1rem;
        }
        button {
            background-color: #4caf50;
            color: white;
            cursor: pointer;
            border: none;
        }
        button:hover {
            background-color: #45a049;
        }
        #progressContainer {
            margin-top: 2rem;
        }
        .hidden {
            display: none;
        }
        footer {
            background-color: #333;
            color: white;
            text-align: center;
            padding: 1rem;
            margin-top: auto;
        }
        .platforms {
            margin-top: 2rem;
            padding: 1rem;
            background-color: #e7f3fe;
            border: 1px solid #b3d4fc;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <header>
        <h1>QuickDownloader</h1>
        <p>Your go-to tool for downloading videos and audio from popular platforms</p>
    </header>
    <main>
        <div class="container">
            <input type="text" id="urlInput" placeholder="Enter video/audio URL">
            <select id="typeSelect">
                <option value="video">Video</option>
                <option value="audio">Audio</option>
            </select>
            <select id="qualitySelect">
                <option value="best">Best Quality</option>
                <option value="high">High Quality</option>
                <option value="medium">Medium Quality</option>
                <option value="low">Low Quality</option>
            </select>
            <button id="downloadButton">Download</button>
        </div>
        <div id="progressContainer" class="hidden">
            <p id="progressText">Preparing download...</p>
            <progress id="downloadProgress" value="0" max="100"></progress>
        </div>
        <div id="resultContainer" class="hidden">
            <p id="resultText">Download complete! <a id="downloadLink" href="#" download>Click here</a> to download your file.</p>
        </div>
        <div class="platforms">
            <h3>Supported Platforms:</h3>
            <ul>
                <li>YouTube: Download videos, playlists, and live streams.</li>
                <li>Vimeo: Download videos from public Vimeo pages.</li>
                <li>Facebook: Download videos from public Facebook posts.</li>
                <li>Twitter: Download videos from Twitter.</li>
                <li>SoundCloud: Download audio tracks.</li>
                <li>Dailymotion: Download videos from Dailymotion.</li>
                <li>Twitch: Download Twitch streams and highlights.</li>
                <li>Instagram: Download videos and images from Instagram posts.</li>
                <li>TikTok: Download TikTok videos.</li>
                <li>Mixer: Download videos from Mixer streams.</li>
            </ul>
        </div>
    </main>
    <footer>
        <p>© 2024 QuickDownloader. All rights reserved.</p>
    </footer>
    <script>
        document.getElementById('downloadButton').addEventListener('click', function() {
            const url = document.getElementById('urlInput').value;
            const downloadType = document.getElementById('typeSelect').value;
            const quality = document.getElementById('qualitySelect').value;

            if (url.trim() === '') {
                alert('Please enter a valid URL');
                return;
            }

            document.getElementById('progressContainer').classList.remove('hidden');
            document.getElementById('resultContainer').classList.add('hidden');

            fetch('/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url, downloadType, quality }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert('Error: ' + data.error);
                    document.getElementById('progressContainer').classList.add('hidden');
                } else {
                    document.getElementById('progressText').innerText = 'Download complete!';
                    document.getElementById('downloadProgress').value = 100;
                    document.getElementById('downloadLink').href = data.filePath;
                    document.getElementById('resultContainer').classList.remove('hidden');
                }
            })
            .catch(error => {
                alert('Error downloading file');
                console.error('Error:', error);
                document.getElementById('progressContainer').classList.add('hidden');
            });
        });
    </script>
</body>
</html>
"""


# Download media function using yt-dlp
def download_media(url, download_type, quality):
    download_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    ydl_opts = {
        'format': 'best' if download_type == 'video' else 'bestaudio',
        'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'postprocessors': [],
        'nocheckcertificate': True,  # To bypass SSL issues
        'geo_bypass': True,  # To bypass geographical restrictions
        'verbose': True,  # For detailed logs
    }

    # Quality adjustments
    if quality == 'high':
        ydl_opts['format'] = 'best[height<=1080]' if download_type == 'video' else 'bestaudio/best'
    elif quality == 'medium':
        ydl_opts['format'] = 'best[height<=720]' if download_type == 'video' else 'bestaudio/best'
    elif quality == 'low':
        ydl_opts['format'] = 'best[height<=480]' if download_type == 'video' else 'bestaudio/best'

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info_dict)
            return filename
    except Exception as e:
        print(f"Error downloading media: {e}")
        raise e

# Flask routes
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url')
    download_type = data.get('downloadType')
    quality = data.get('quality')

    try:
        # Download the media file
        file_path = download_media(url, download_type, quality)
        print(f"Downloaded file path: {file_path}")
        return jsonify({'filePath': f'/downloads/{os.path.basename(file_path)}'})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)})

@app.route('/downloads/<filename>', methods=['GET'])
def download_file(filename):
    try:
        return send_from_directory('downloads', filename, as_attachment=True)
    except Exception as e:
        return jsonify({'error': 'File not found'})

if __name__ == '__main__':
    app.run(debug=True)
