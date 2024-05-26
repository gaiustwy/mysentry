from flask import Flask, render_template
import os
import subprocess

app = Flask(__name__)

# def get_video_metadata(video_path):
#     try:
#         result = subprocess.run(
#             ["ffprobe", "-v", "error", "-of", "compact", video_path, "-show_entries", "format_tags=comment"],
#             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
#         )
#         # metadata = result.stdout.strip()
#         print(result.stdout.strip())
#         if metadata.startswith("format_tags_comment="):
#             return metadata[len("format_tags_comment="):].strip('"')
#         return "No comment"
#     except Exception as e:
#         print(f"Error getting metadata for {video_path}: {e}")
#         return "Error retrieving comment"


# print(get_video_metadata("static/test.vid.mp4"))

@app.route('/')
def index():
	static_folder = os.path.join(app.root_path, 'static')
	clips = [f for f in os.listdir(static_folder) if f.endswith('.mp4')]
	return render_template('index.html', clips = clips)

if __name__ == '__main__':
    app.run(debug=True)