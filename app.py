import flask
import app.data as data
import json
import os
import requests
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook

app = flask.Flask(__name__, static_url_path='/static')
app.secret_key = 'debug_key'
blueprint = make_facebook_blueprint(
    client_id=os.environ.get('FACEBOOK_CLIENTID'),
    client_secret=os.environ.get('FACEBOOK_SECRET'),
)
app.register_blueprint(blueprint, url_prefix='/login')
data.init_db()


def is_authenticated():
    return 'user_id' in flask.session


@app.route('/login')
def login():
    return flask.redirect(flask.url_for('facebook.login'))


def try_login_user():
    if facebook.token and 'user_id' not in flask.session:
        # ask FB for account ID
        res = requests.get('https://graph.facebook.com/me?access_token=' + facebook.token['access_token'])
        fb_json = res.json()
        # try and get the use from out local DB
        user = data.get_user(fb_json['id'])
        # if we havent seen this user before, register them
        if not user:
            data.register_user(fb_json['id'], fb_json['name'])
        # save the users ID to our session
        flask.session['user_id'] = fb_json['id']


@app.route('/')
def index():
    try_login_user()
    if not is_authenticated():
        return flask.redirect(flask.url_for('facebook.login'))
    else:
        user_name = data.get_user(flask.session['user_id'])[1]
        movies = data.get_all_movies()
        movies.sort(key=lambda x: -x['popularity'])
        return flask.render_template('index.html', context={
            'user': {
                'username': user_name
            },
            'movies': movies[:50]
        })


@app.route('/api/1/vote/<movie_id>')
def vote(movie_id):
    if not is_authenticated():
        return json.dumps({
            'success': False,
            'message': 'You are not logged in'
        })
    res, msg = data.add_vote(flask.session['user_id'], movie_id)
    return json.dumps({
        'success': res,
        'message': msg
    })


@app.route('/api/1/all/movies')
def get_all_movies():
    data.get_all_movies()


def main():
    app.run(host='127.0.0.1', port='443', debug=True, ssl_context='adhoc')


if __name__ == '__main__':
    main()
