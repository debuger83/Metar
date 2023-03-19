import asyncio
from playwright.async_api import async_playwright
import re

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

        for city in cities:
            # 정규 표현식으로 도시이름이 포함된 줄 찾기
            pattern = rf'<td>{city}<\/td>.*?<td.*?>(.*?)<\/td>'
            result = re.search(pattern, page_content, re.DOTALL)

            if result:
                metar_data = result.group(1)
                print(f"{city} :", metar_data)
            else:
                print(f"{city} 결과를 찾을 수 없습니다.")

        # 리소스 정리
        await context.close()
        await browser.close()

# 함수를 호출하고, 원하는 도시 이름을 리스트로 전달하세요.
cities = ["포항경주공항", "예천공항", "중원", "서울", "김포공항"]
await get_metar(cities)
