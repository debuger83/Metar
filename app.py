import asyncio
from playwright.async_api import async_playwright
import re
from flask import Flask, render_template, request

app = Flask(__name__)

async def get_metar(cities):
    url = "https://global.amo.go.kr/obsMetar/ObsMetar.do"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(url)
        await asyncio.sleep(5)

        # 전체 페이지 내용 가져오기
        page_content = await page.content()

        result_list = []
        for city in cities:
            # 정규 표현식으로 도시이름이 포함된 줄 찾기
            pattern = rf'<td>{city}<\/td>.*?<td.*?>(.*?)<\/td>'
            result = re.search(pattern, page_content, re.DOTALL)

            if result:
                metar_data = result.group(1)
                result_list.append((city, metar_data))
            else:
                result_list.append((city, f"{city} 결과를 찾을 수 없습니다."))

        # 리소스 정리
        await context.close()
        await browser.close()

        return result_list


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/get_metar', methods=['POST'])
def get_metar_route():
    cities = request.form.getlist('city')
    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(get_metar(cities))
    loop.close()

    return render_template('result.html', result=result)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
