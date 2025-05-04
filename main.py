from flask import Flask, render_template, request, redirect, flash, send_from_directory, url_for
import os
import shutil
import yt_dlp

app = Flask(__name__)
app.secret_key = 'supersecretkey'

DOWNLOAD_FOLDER = os.path.join(os.getcwd(), 'downloads')
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

ffmpeg_exec = shutil.which("ffmpeg")
if not ffmpeg_exec:
    raise EnvironmentError("FFmpeg not found on the system!")

FFMPEG_PATH = os.path.dirname(ffmpeg_exec)


@app.route('/', methods=['GET', 'POST'])
def index():
    downloaded_file = None
    processing_done = False
    video_title = None
    thumbnail_url = None
    duration = None
    filesize_mb = None

    if request.method == 'POST':
        url = request.form.get('url')
        download_type = request.form.get('download_type')

        if not url:
            flash("Please provide a valid URL.", "error")
            return redirect('/')

        ydl_opts = {
            'ffmpeg_location': FFMPEG_PATH,
            'format': 'bestaudio/best' if download_type == 'mp3' else 'bestvideo+bestaudio/best',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        }

        if download_type == 'mp3':
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

                video_title = info.get('title', '')
                thumbnail_url = info.get('thumbnail', '')
                duration = info.get('duration')
                filesize_bytes = info.get('filesize') or info.get('filesize_approx')
                if filesize_bytes:
                    filesize_mb = round(filesize_bytes / (1024 * 1024), 2)

                if download_type == 'mp3':
                    filename = os.path.splitext(filename)[0] + '.mp3'

                downloaded_file = os.path.basename(filename)
                processing_done = True

        except Exception as e:
            flash(f"An error occurred: {e}", "error")
            return redirect('/')

        return render_template(
            'index.html',
            filename=downloaded_file,
            processing_done=processing_done,
            video_title=video_title,
            thumbnail_url=thumbnail_url,
            duration=duration,
            filesize_mb=filesize_mb
        )

    return render_template('index.html')


@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)






