from flask import Flask, request, jsonify
import requests
import base64
import logging
from flask_cors import CORS  # Doğru import
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
CORS(app)  # CORS ayarını burada yapabilirsiniz, örn: CORS(app, resources={r"/*": {"origins": "*"}})
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

WOOCOMMERCE_URL = "https://epsonpedreset.com"
WOOCOMMERCE_CONSUMER_KEY = "ck_3bc3155f21ad13877a116c8e3e5f26c5da5d2241"
WOOCOMMERCE_CONSUMER_SECRET = "cs_f8ef467a7324dadfff97098ea010e9582868ddb0"

def get_woocommerce_auth_header():
    auth_str = f"{WOOCOMMERCE_CONSUMER_KEY}:{WOOCOMMERCE_CONSUMER_SECRET}"
    encoded_auth = base64.b64encode(auth_str.encode()).decode()
    return {"Authorization": f"Basic {encoded_auth}"}

@app.route("/verify", methods=["POST"])
def verify_license():
    data = request.json
    key = data.get("key")
    if not key:
        logger.warning("Lisans anahtarı gerekli!")
        return jsonify({"success": False, "message": "Lisans anahtarı gerekli!"}), 400
    try:
        api_url = f"{WOOCOMMERCE_URL}/wp-json/wc/v3/orders"
        headers = get_woocommerce_auth_header()
        params = {"search": key}
        response = requests.get(api_url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        orders = response.json()

        if orders:
            for order in orders:
                 if key == order.get("customer_note"):
                     return jsonify({"success": True, "message": "Lisans anahtarı doğrulandı!"})
            return jsonify({"success": False, "message": "Geçersiz Lisans Anahtarı"}), 401
        else:
            return jsonify({"success": False, "message": "Geçersiz Lisans Anahtarı"}), 401
    except requests.exceptions.RequestException as e:
       logger.error(f"API İstek hatası: {e}")
       return jsonify({"success": False, "message": f"API İsteği hatası: {e}"}), 500
    except Exception as e:
       logger.error(f"Beklenmeyen bir hata: {e}")
       return jsonify({"success": False, "message": f"Beklenmeyen bir hata: {e}"}), 500

@app.errorhandler(HTTPException)
def handle_exception(e):
    """HTTP Exceptionları yakalar ve JSON formatında cevap döndürür."""
    return jsonify({"success": False, "message": str(e)}), e.code

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)