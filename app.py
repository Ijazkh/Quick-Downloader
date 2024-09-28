from flask import Flask, request, jsonify, send_from_directory, render_template
import os
import yt_dlp as youtube_dl

app = Flask(__name__)

def download_media(url, download_type, quality):
    download_folder = os.path.join(os.getcwd(), 'downloads')
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    ydl_opts = {
        'format': 'best' if download_type == 'video' else 'bestaudio',
        'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'postprocessors': [],  # Avoid using ffmpeg
        'ratelimit': 1000000,  # Set rate limit to 1MB/s to avoid throttling
        'retries': 3,          # Retry the download up to 3 times
    }

    # Adjust quality settings
    if quality == 'high':
        ydl_opts['format'] = 'best[height<=1080]' if download_type == 'video' else 'bestaudio/best'
    elif quality == 'medium':
        ydl_opts['format'] = 'best[height<=720]' if download_type == 'video' else 'bestaudio/best'
    elif quality == 'low':
        ydl_opts['format'] = 'best[height<=480]' if download_type == 'video' else 'bestaudio/best'

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info_dict)
            return filename
        except Exception as e:
            raise e

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url')
    download_type = data.get('downloadType')
    quality = data.get('quality')

    try:
        file_path = download_media(url, download_type, quality)
        return jsonify({'filePath': f'/downloads/{os.path.basename(file_path)}'})
    except ConnectionResetError:
        return jsonify({'error': 'Connection reset by server. Please try again.'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/downloads/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory('downloads', filename)

if __name__ == '__main__':
    app.run(debug=True)
