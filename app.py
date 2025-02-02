from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# SQLite Veritabanını Başlat
def setup_database():
    conn = sqlite3.connect("licenses.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS license_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            license_key TEXT UNIQUE NOT NULL,
            is_used BOOLEAN DEFAULT FALSE
        )
    """)

    # Örnek lisans anahtarları ekleyelim
    sample_keys = ["ABC12345", "XYZ98765", "DEF67890"]
    for key in sample_keys:
        try:
            cursor.execute("INSERT INTO license_keys (license_key) VALUES (?)", (key,))
        except sqlite3.IntegrityError:
            pass  # Anahtar zaten varsa ekleme yapma

    conn.commit()
    conn.close()

setup_database()

@app.route("/verify", methods=["POST"])
def verify_license():
    """Lisans anahtarını doğrular ve kullanılmış olarak işaretler."""
    data = request.json
    key = data.get("key")

    if not key:
        return jsonify({"success": False, "message": "Lisans anahtarı gerekli!"})

    conn = sqlite3.connect("licenses.db")
    cursor = conn.cursor()

    cursor.execute("SELECT is_used FROM license_keys WHERE license_key = ?", (key,))
    result = cursor.fetchone()

    if result is None:
        return jsonify({"success": False, "message": "Geçersiz Lisans Anahtarı!"})
    elif result[0]:  # Anahtar daha önce kullanılmış mı?
        return jsonify({"success": False, "message": "Bu lisans anahtarı zaten kullanılmış!"})
    else:
        cursor.execute("UPDATE license_keys SET is_used = 1 WHERE license_key = ?", (key,))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Lisans anahtarı doğrulandı ve artık kullanıldı!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
