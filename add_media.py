from pathlib import Path

p = Path("app.py")
s = p.read_text()

if "from werkzeug.utils import secure_filename" not in s:
    s = s.replace(
        "import os",
        "import os\nimport uuid\nfrom werkzeug.utils import secure_filename",
        1
    )

start = s.find('@app.route("/media")')
end = s.find('\nif __name__ == "__main__":', start)

if start < 0 or end < 0:
    print("ERROR: Media route location not found")
    raise SystemExit

route = '''
@app.route("/media", methods=["GET", "POST"])
def media():
    if "user" not in session:
        return redirect("/")

    categories = {
        "photos": {"label": "Photos", "extensions": {"jpg", "jpeg", "png", "webp"}},
        "videos": {"label": "Videos", "extensions": {"mp4", "mov"}},
        "brochures": {"label": "Brochures", "extensions": {"pdf"}},
        "price_lists": {"label": "Price Lists", "extensions": {"pdf"}}
    }

    with connect() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS media_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                filename TEXT NOT NULL,
                filepath TEXT NOT NULL,
                uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

    if request.method == "POST":
        category = request.form.get("category", "")
        title = request.form.get("title", "").strip()
        uploaded = request.files.get("file")

        if category not in categories or not uploaded or not uploaded.filename:
            flash("Select a category and file")
            return redirect("/media")

        original = secure_filename(uploaded.filename)
        ext = original.rsplit(".", 1)[-1].lower() if "." in original else ""

        if ext not in categories[category]["extensions"]:
            flash("File type not allowed")
            return redirect("/media")

        folder = Path("static/media") / category
        folder.mkdir(parents=True, exist_ok=True)
        filename = uuid.uuid4().hex + "." + ext
        filepath = folder / filename
        uploaded.save(str(filepath))

        with connect() as con:
            con.execute(
                "INSERT INTO media_files(title,category,filename,filepath) VALUES(?,?,?,?)",
                (title or original, category, original, str(filepath))
            )

        flash("File uploaded successfully")
        return redirect("/media")

    with connect() as con:
        files = con.execute(
            "SELECT * FROM media_files ORDER BY id DESC"
        ).fetchall()

    return render_template("media.html", files=files, categories=categories)
'''

s = s[:start] + route + s[end:]
p.write_text(s)

Path("templates").mkdir(exist_ok=True)
Path("templates/media.html").write_text("""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Vision Honda Media Centre</title>
<style>
body{font-family:Arial;background:#f2f4f8;margin:0;padding:18px;color:#222}
header{background:#b5122b;color:white;padding:22px;border-radius:14px}
.card{background:white;padding:20px;border-radius:14px;margin-top:18px}
input,select,button{width:100%;padding:14px;margin:9px 0;box-sizing:border-box;font-size:16px}
button{background:#b5122b;color:white;border:0;border-radius:8px}
.file{padding:14px;border-bottom:1px solid #ddd}
</style>
</head>
<body>
<header><h1>VISION HONDA</h1><h3>Media & Documents Centre</h3>
<a href="/dashboard" style="color:white">Back to Dashboard</a></header>
{% with messages = get_flashed_messages() %}
{% for message in messages %}<p>{{ message }}</p>{% endfor %}
{% endwith %}
<div class="card">
<h2>Upload New File</h2>
<form method="POST" enctype="multipart/form-data">
<select name="category" required>
<option value="">Select category</option>
<option value="photos">Photos</option>
<option value="videos">Videos</option>
<option value="brochures">Brochures</option>
<option value="price_lists">Price Lists</option>
</select>
<input name="title" placeholder="File title / Honda model">
<input type="file" name="file" required>
<button type="submit">UPLOAD FILE</button>
</form></div>
<div class="card"><h2>Uploaded Files</h2>
{% for item in files %}
<div class="file"><b>{{ item.title }}</b><br>
{{ categories[item.category].label }} · {{ item.filename }}<br>
<a href="/{{ item.filepath }}" target="_blank">Open / View File</a></div>
{% else %}<p>No files uploaded yet.</p>{% endfor %}
</div></body></html>""")

print("MEDIA UPLOAD SYSTEM INSTALLED")