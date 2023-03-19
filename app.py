import os
from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_metar", methods=["POST"])
def get_metar():
    icao_code = request.form.get("icao_code")
    metar_url = f"https://tgftp.nws.noaa.gov/data/observations/metar/stations/{icao_code}.TXT"
    
    response = requests.get(metar_url)
    
    if response.status_code == 200:
        metar_text = response.text.strip()
        return jsonify({"status": "success", "metar": metar_text})
    else:
        return jsonify({"status": "error", "message": "Unable to fetch METAR data"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
