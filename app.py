import os
import asyncio
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from playwright.async_api import async_playwright

app = Flask(__name__)
CORS(app)

async def get_metar(cities):
    url = "https://global.amo.go.kr/obsMetar/ObsMetar.do"
    results = {}
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(url)
        await asyncio.sleep(5)

        page_content = await page.content()

        for city in cities:
            pattern = rf'<td>{city}<\/td>.*?<td.*?>(.*?)<\/td>'
            result = re.search(pattern, page_content, re.DOTALL)

            if result:
                metar_data = result.group(1)
                results[city] = metar_data
            else:
                results[city] = "결과를 찾을 수 없습니다."

        await context.close()
        await browser.close()

    return results

@app.route('/api/metar', methods=['POST'])
def metar_api():
    data = request.get_json()
    cities = data.get('cities', [])
    loop = asyncio.get_event_loop()
    metar_results = loop.run_until_complete(get_metar(cities))
    return jsonify(metar_results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
