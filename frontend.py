import os
import requests
import dumper

from flask import Flask, render_template

web_app = Flask(__name__, template_folder='.')

# Serve index.html at the root endpoint
@web_app.route('/')
def index():
    return render_template('glass.html',
                           tagline=os.getenv("BRAND_TAGLINE", "A trivia Masterpiece!"),
                           title=os.getenv("BRAND_TITLE", "Trivia"),
                           logo=os.getenv("BRAND_LOGO", "DreeBotLogo.png"),
                           )

@web_app.route('/pop')
@web_app.route('/pop/')
def index():
    return render_template('pop.html',
                           tagline=os.getenv("BRAND_TAGLINE", ""),
                           title=os.getenv("BRAND_TITLE", "Trivia-Pop!"),
                           logo=os.getenv("BRAND_LOGO", "DreeBotLogo.png")
                           )

@web_app.route('/control')
@web_app.route('/control/')
def control():
    sets = []
    datapath = os.getenv("DATA_PATH", "")
    if not datapath == "":
        files = os.listdir(datapath)
        sets = [file.split(datapath)[0] for file in files if file.lower().endswith(".csv")]

    otdb_response = requests.get("https://opentdb.com/api_category.php").json()
    otdb={}
    categories = list(otdb_response['trivia_categories'])
    dumper.dump(categories)
    categories.sort(key=lambda category: category["name"])
    for category in categories:
        otdb[category['id']] = category['name']
    dumper.dump(otdb)
    return render_template('control.html', sets=sets, otdb=otdb)

@web_app.route('/common.js')
def common():
    return render_template('common.js', url=os.environ["BACKEND_URL"])


if __name__ == '__main__':
    # Run the Flask web server
    web_app.run(debug=True, host='0.0.0.0', port=int(os.getenv("PORT", "5000")))

