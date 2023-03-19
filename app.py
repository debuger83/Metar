from flask import Flask, render_template
import asyncio
from playwright.async_api import async_playwright
import re

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

        results = []
        for city in cities:
            # 정규 표현식으로 도시이름이 포함된 줄 찾기
            pattern = rf'<td>{city}<\/td>.*?<td.*?>(.*?)<\/td>'
            result = re.search(pattern, page_content, re.DOTALL)

            if result:
                metar_data = result.group(1)
                results.append((city, metar_data))
            else:
                results.append((city, f"{city} 결과를 찾을 수 없습니다."))

        # 리소스 정리
        await context.close()
        await browser.close()

        return results

@app.route('/')
def home():
    cities = ["포항경주공항", "예천공항", "중원", "서울", "김포공항"]
    results = asyncio.run(get_metar(cities))
    return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
