from flask import Flask, render_template, request
from requests_html import HTMLSession

app = Flask(__name__)

def get_gimpo_metar():
    session = HTMLSession()
    url = 'https://global.amo.go.kr/obsMetar/ObsMetar.do'

    response = session.get(url)
    response.html.render(sleep=2)

    metar_list = response.html.find('#obsList > tr')

    for metar in metar_list:
        if '김포공항' in metar.text:
            return metar.text

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        gimpo_metar = get_gimpo_metar()
        return render_template('index.html', gimpo_metar=gimpo_metar)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
