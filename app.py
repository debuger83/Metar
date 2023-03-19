import os
import asyncio
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from playwright.async_api import async_playwright
import re

app = Flask(__name__)
CORS(app)

async def get_metar(cities):
    url = "https://global.amo.go.kr/obsMetar/ObsMetar.do"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(url)
        await asyncio.sleep(5)

        page_content = await page.content()

        metar_data = {}
        for city in cities:
            pattern = rf'<td>{city}<\/td>.*?<td.*?>(.*?)<\/td>'
            result = re.search(pattern, page_content, re.DOTALL)

            if result:
                metar_data[city] = result.group(1)
            else:
                metar_data[city] = "결과를 찾을 수 없습니다."

        await context.close()
        await browser.close()
    
    return metar_data

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/metar", methods=["GET"])
async def metar_api():
    cities = request.args.get("cities", "").split(",")
    metar_data = await get_metar(cities)
    return jsonify(metar_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
