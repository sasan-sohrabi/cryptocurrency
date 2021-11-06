# Import relevant library for cryptocurrency project
import json

from flask import Flask, jsonify, Response, redirect, request, abort, flash, render_template
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
import config
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects

app = Flask(__name__)

limiter = Limiter(
    app,
    key_func=get_remote_address,
)

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

app.config.update(
    SECRET_KEY=config.SECRET_KEY
)


# silly user model
class User(UserMixin):

    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return "%d" % self.id


# create some users with ids 1 to 20
user = User(0)


# some protected url
@app.route('/', methods=['GET'])
@login_required
def home():
    with open('Data/Categories.json') as categories_file:
        data = json.load(categories_file)
        number_categories = len(data["data"])
        categories = data["data"]

    return render_template('index.html', data={'categories': categories, 'number_cryptocurrency': 7030,
                                               'number_categories': number_categories})


# return category from data of tables
@app.route('/category/<category_id>', methods=['GET'])
@login_required
def category(category_id):
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/category'
    parameters = {
        'id': category_id,
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': '3d228362-20d9-48b0-8c0c-ed94648159a2',
    }

    session = Session()
    session.headers.update(headers)

    with open('Data/Categories.json') as categories_file:
        data = json.load(categories_file)
        number_categories = len(data["data"])
        categories = data["data"]

    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        crypto = [{"name": element["name"], "symbol": element["symbol"], "slug": element["slug"]} for element in
                  data["data"]['coins']]
        return render_template('tables.html', data={'categories': crypto})

    except (ConnectionError, Timeout, TooManyRedirects) as e:
        return e


# somewhere to login
@app.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def login():
    if current_user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if password == config.PASSWORD and username == config.USERNAME:
            login_user(user)
            return redirect('/')
        else:
            return abort(401)
    else:
        return render_template('login.html')


# somewhere to logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('Logged out', 'success')
    return redirect('/login')


# handle login failed
@app.errorhandler(401)
def unauthorized(error):
    flash('Login Problem', 'danger')
    return redirect('/login')


# callback to reload the user object
@login_manager.user_loader
def load_user(userid):
    return User(userid)


# For checking that system is working or not.
@app.route('/v1/ok')
def health_check():
    check = {'message': 'ok'}
    return jsonify(check), 200


# If there is not valid url return 404 page (not found page)
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=80)
