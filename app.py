from flask import Flask, render_template, request, jsonify
from playwright.async_api import async_playwright
import asyncio
import re

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/metar', methods=['POST'])
def get_metar():
    cities = request.form.getlist('cities[]')
    metar_list = []
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def fetch_metar(cities):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto("https://global.amo.go.kr/obsMetar/ObsMetar.do")
            await asyncio.sleep(5)
            page_content = await page.content()

            for city in cities:
                # 정규 표현식으로 도시이름이 포함된 줄 찾기
                pattern = rf'<td>{city}<\/td>.*?<td.*?>(.*?)<\/td>'
                result = re.search(pattern, page_content, re.DOTALL)

                if result:
                    metar_data = result.group(1)
                    metar_list.append((city, metar_data))
                else:
                    metar_list.append((city, '해당 결과를 찾을 수 없습니다.'))

            # 리소스 정리
            await context.close()
            await browser.close()

    loop.run_until_complete(fetch_metar(cities))

    return jsonify(metar_list)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
