import os
import random
import requests
import dumper

from flask import Flask, render_template

web_app = Flask(__name__, template_folder='.')

# At the root endpoint, serve a random frontend unless one was specified
@web_app.route('/')
def index():
    options = {
        "glass": glass,
        "pop": pop
    }

   # Retrieve the value of the environment variable INTERFACE
    interface = os.getenv('INTERFACE')
    
    # If INTERFACE is set and found in the dictionary, return the corresponding function result
    if interface in options:
        return options[interface]()
    
    # If INTERFACE is not set or doesn't match, randomly select one from the options
    return random.choice(list(options.values()))()
    
@web_app.route('/glass')
@web_app.route('/glass/')
def glass():
    return render_template('glass.html',
                           tagline=os.getenv("BRAND_TAGLINE", "A trivia Masterpiece!"),
                           title=os.getenv("BRAND_TITLE", "Trivia"),
                           logo=os.getenv("BRAND_LOGO", "DreeBotLogo.png"),
                           )

@web_app.route('/pop')
@web_app.route('/pop/')
def pop():
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

    otdb={}
    try:
        otdb_response = requests.get("https://opentdb.com/api_category.php", timeout=10).json()
        categories = list(otdb_response['trivia_categories'])
        dumper.dump(categories)
        categories.sort(key=lambda category: category["name"])
        for category in categories:
            otdb[category['id']] = category['name']
    except requests.exceptions.RequestException as e:
        None
    dumper.dump(otdb)
    return render_template('control.html', sets=sets, otdb=otdb)

@web_app.route('/common.js')
def common():
    return render_template('common.js', url=os.environ["BACKEND_URL"])


if __name__ == '__main__':
    # Run the Flask web server
    web_app.run(debug=True, host='0.0.0.0', port=int(os.getenv("PORT", "5000")))

