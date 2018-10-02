from functools import wraps
import json
from os import environ as env
from werkzeug.exceptions import HTTPException

from dotenv import load_dotenv, find_dotenv
from flask import Flask, jsonify, redirect, render_template, session, url_for
from authlib.flask.client import OAuth
from six.moves.urllib.parse import urlencode

app = Flask(__name__)
app.config['SECRET_KEY'] = env['AUTH_SECRET']
oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id=env['AUTH_CLIENT'],
    client_secret=env['AUTH_SECRET'],
    api_base_url='https://gigdb.auth0.com',
    access_token_url='https://gigdb.auth0.com/oauth/token',
    authorize_url='https://gigdb.auth0.com/authorize',
    client_kwargs={
        'scope': 'openid profile',
    },
)


# /server.py

# Here we're using the /callback route.
@app.route('/callback')
def callback_handling():
    # Handles response from token endpoint
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()

    # Store the user information in flask session.
    session['jwt_payload'] = userinfo
    session['profile'] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }
    return redirect('/dashboard')

@app.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri='https://practicehelper.heroku.com/callback', audience='https://gigdb.auth0.com/userinfo')

def requires_auth(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    if 'profile' not in session:
      # Redirect to Login page here
      return redirect('/')
    return f(*args, **kwargs)

  return decorated

@app.route('/dashboard')
@requires_auth
def dashboard():
    return render_template('dashboard.html',
                           userinfo=session['profile'],
                           userinfo_pretty=json.dumps(session['jwt_payload'], indent=4))

@app.route('/logout')
def logout():
    # Clear session stored data
    session.clear()
    # Redirect user to logout endpoint
    params = {'returnTo': url_for('home', _external=True), 'client_id': 'LC14lzbQwLdWWmHvP3Rr99n4miC592E0'}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))

@app.route('/')
def home():
    return render_template('home.html')


if __name__ == "__main__":
    app.run(debug=True)