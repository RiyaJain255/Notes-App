import os
import sqlite3
from datetime import datetime

from flask import Flask, abort, g, redirect, render_template, request, url_for

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def create_app(test_config=None):
    app = Flask(__name__)
    app.config["DATABASE"] = os.environ.get(
        "DATABASE_PATH", os.path.join(BASE_DIR, "notes.db")
    )
    if test_config:
        app.config.update(test_config)

    # Make sure the folder for the database exists (needed in Docker: /data)
    db_dir = os.path.dirname(app.config["DATABASE"])
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    def get_db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(exception=None):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    def init_db():
        db = sqlite3.connect(app.config["DATABASE"])
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        db.commit()
        db.close()

    init_db()

    def get_note_or_404(note_id):
        note = get_db().execute(
            "SELECT * FROM notes WHERE id = ?", (note_id,)
        ).fetchone()
        if note is None:
            abort(404)
        return note

    def all_notes():
        return get_db().execute(
            "SELECT * FROM notes ORDER BY id DESC"
        ).fetchall()

    @app.route("/")
    def index():
        return render_template("index.html", notes=all_notes(), error=None)

    @app.route("/add", methods=["POST"])
    def add_note():
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        if not title or not content:
            return (
                render_template(
                    "index.html",
                    notes=all_notes(),
                    error="Title and content cannot be empty.",
                    title=title,
                    content=content,
                ),
                400,
            )
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db = get_db()
        db.execute(
            "INSERT INTO notes (title, content, created_at) VALUES (?, ?, ?)",
            (title, content, created_at),
        )
        db.commit()
        return redirect(url_for("index"))

    @app.route("/edit/<int:note_id>", methods=["GET", "POST"])
    def edit_note(note_id):
        note = get_note_or_404(note_id)
        if request.method == "POST":
            title = request.form.get("title", "").strip()
            content = request.form.get("content", "").strip()
            if not title or not content:
                note = dict(note)
                note["title"], note["content"] = title, content
                return (
                    render_template(
                        "edit.html",
                        note=note,
                        error="Title and content cannot be empty.",
                    ),
                    400,
                )
            db = get_db()
            db.execute(
                "UPDATE notes SET title = ?, content = ? WHERE id = ?",
                (title, content, note_id),
            )
            db.commit()
            return redirect(url_for("index"))
        return render_template("edit.html", note=note, error=None)

    @app.route("/delete/<int:note_id>", methods=["POST"])
    def delete_note(note_id):
        get_note_or_404(note_id)
        db = get_db()
        db.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        db.commit()
        return redirect(url_for("index"))

    @app.errorhandler(404)
    def not_found(error):
        return render_template("404.html"), 404

    return app


if __name__ == "__main__":
    app = create_app()
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 5000))
    app.run(host=host, port=port)
