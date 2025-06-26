from flask import Flask, render_template, redirect, request, send_file, session
from app import song_fetcher
import os
import uuid
from app import utils
from dotenv import load_dotenv

output = os.getenv("OUTPUT_DIR", "/tmp/spotify_downloader")

app = Flask(
    __name__,
    template_folder=os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "templates")
    )
)

load_dotenv()
app.secret_key = os.getenv("SECRET_KEY")

@app.route("/download/<filename>")
def download(filename):
    if 'user_id' not in session:
        return "Session expired.", 403
    
    user_folder = os.path.join(output, session['user_id'])
    file_path = os.path.join(user_folder, filename)
    
    if not os.path.exists(file_path):
        return "File not found. It may have been deleted or never downloaded.", 404

    return send_file(file_path, as_attachment=True)

@app.route("/", methods=['GET', 'POST'])
def home():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    
    user_folder = os.path.join(output, session['user_id'])

    if request.method == 'POST':
        link = request.form['link']
        file_path = song_fetcher.song_download(link, user_folder)
        
        if file_path[0] is None:
            return render_template("index.html", error="Failed to download the file. Please check the link or try again.")
        
        filename = os.path.basename(file_path[0])
        
        utils.schedule_deletion(user_folder, delay=600)

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return render_template("partials/result.html", filename=filename, cover_url=file_path[1])
        
        return render_template("index.html", filename=filename, cover_url=file_path[1])

    return render_template("index.html")
