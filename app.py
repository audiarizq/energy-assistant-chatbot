"""
Aplikasi Web Chatbot Tematik dengan Flask (versi final).

Jalankan:
    python app.py
lalu buka http://127.0.0.1:5000
"""
import os
import uuid
from pathlib import Path

from flask import Flask, abort, jsonify, redirect, render_template, request, session, url_for

from chatbot import ChatbotEngine, ChatHistory, load_themes

BASE_DIR = Path(__file__).resolve().parent


def create_app(config: dict | None = None) -> Flask:
    """Application factory: memudahkan konfigurasi berbeda untuk pengujian."""
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "energybot-dev-secret-change-me"),
        # Database produksi selalu berada di folder proyek EnergyBot.
        # Konfigurasi pengujian masih dapat menimpanya melalui create_app().
        DATABASE=str(BASE_DIR / "chat_history.db"),
        THEMES_DIR=str(BASE_DIR / "themes"),
        THRESHOLD=float(os.environ.get("THRESHOLD", "0.45")),
        MAX_LEN=500,
    )
    if config:
        app.config.update(config)

    # Muat semua tema dan buat satu engine per tema
    themes = load_themes(app.config["THEMES_DIR"])
    engines = {tid: ChatbotEngine(t, app.config["THRESHOLD"]) for tid, t in themes.items()}
    history = ChatHistory(app.config["DATABASE"])

    def get_session_id() -> str:
        """Setiap pengunjung mendapat ID sesi unik yang disimpan di cookie."""
        if "sid" not in session:
            session["sid"] = uuid.uuid4().hex
        return session["sid"]

    def get_theme_or_404(theme_id: str) -> dict:
        if theme_id not in themes:
            abort(404, description=f"Tema '{theme_id}' tidak ditemukan")
        return themes[theme_id]

    # ------------------------------------------------------------------ #
    # Halaman (mengembalikan HTML)
    # ------------------------------------------------------------------ #
    @app.route("/")
    def index():
        return redirect(url_for("chat_page", theme_id="energybot"))

    @app.route("/chat/<theme_id>")
    def chat_page(theme_id):
        theme = get_theme_or_404(theme_id)
        return render_template("chat.html", theme=theme)

    @app.route("/chat/<theme_id>/admin")
    def admin_page(theme_id):
        theme = get_theme_or_404(theme_id)
        return render_template(
            "admin.html", theme=theme,
            summary=history.summary(theme_id),
            stats=history.stats(theme_id),
            unknown=history.unknown_questions(theme_id),
            threshold=app.config["THRESHOLD"],
        )

    @app.route("/admin/<theme_id>")
    def legacy_admin_page(theme_id):
        return redirect(url_for("admin_page", theme_id=theme_id))

    # ------------------------------------------------------------------ #
    # REST API (mengembalikan JSON)
    # ------------------------------------------------------------------ #
    @app.get("/api/themes")
    def api_themes():
        return jsonify([
            {"id": t["id"], "name": t["name"], "description": t["description"]}
            for t in themes.values()
        ])

    @app.post("/api/chat")
    def api_chat():
        data = request.get_json(silent=True) or {}
        message = str(data.get("message", "")).strip()
        theme_id = data.get("theme", "")

        if theme_id not in engines:
            return jsonify({"error": "Tema tidak valid"}), 400
        if not message:
            return jsonify({"error": "Pesan tidak boleh kosong"}), 400
        if len(message) > app.config["MAX_LEN"]:
            return jsonify({"error": f"Pesan maksimal {app.config['MAX_LEN']} karakter"}), 400

        sid = get_session_id()
        result = engines[theme_id].reply(message)

        # Hanya pertanyaan pengguna yang disimpan. Respons bot tidak disimpan
        # karena dashboard memakai data pertanyaan untuk visualisasi intent.
        history.add(sid, theme_id, "user", message, result["intent"], result["score"])
        return jsonify(result)

    @app.post("/api/explain")
    def api_explain():
        """Tiga kandidat intent teratas: untuk belajar melihat cara bot 'berpikir'."""
        data = request.get_json(silent=True) or {}
        theme_id = data.get("theme", "")
        if theme_id not in engines:
            return jsonify({"error": "Tema tidak valid"}), 400
        message = str(data.get("message", ""))[: app.config["MAX_LEN"]]
        return jsonify({"threshold": app.config["THRESHOLD"],
                        "candidates": engines[theme_id].explain(message)})

    @app.get("/api/history/<theme_id>")
    def api_history(theme_id):
        get_theme_or_404(theme_id)
        return jsonify(history.get(get_session_id(), theme_id))

    @app.delete("/api/history/<theme_id>")
    def api_clear_history(theme_id):
        get_theme_or_404(theme_id)
        # Endpoint ini dipertahankan untuk kompatibilitas, tetapi tidak
        # menghapus SQLite. Penghapusan riwayat pengguna hanya dilakukan DOM.
        return jsonify({"status": "ok", "database_unchanged": True})

    @app.delete("/api/admin/history/<theme_id>")
    def api_admin_clear_history(theme_id):
        get_theme_or_404(theme_id)
        history.clear_theme(theme_id)
        return jsonify({"status": "ok", "database_unchanged": False})

    @app.get("/api/stats/<theme_id>")
    def api_stats(theme_id):
        get_theme_or_404(theme_id)
        return jsonify(history.stats(theme_id))

    @app.errorhandler(403)
    @app.errorhandler(404)
    def not_found(err):
        if request.path.startswith("/api/"):
            return jsonify({"error": err.description}), err.code
        return render_template("404.html", message=err.description, code=err.code), err.code

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
