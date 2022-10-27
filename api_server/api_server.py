from flask import Flask, request, jsonify, redirect, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
import json
import ssl
import os
from oauthlib.oauth2 import WebApplicationClient
import requests
from api_server_initialization import *

# Third party libraries
# Internal imports
# Configuration

GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_DISCOVERY_URL = init_google_oauth()

app = Flask('name')
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)
oauth_client_google = WebApplicationClient(GOOGLE_CLIENT_ID)


def login_callback(userinfo):
    print(userinfo)

def main():
    #ssl settings
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    ssl_context.load_cert_chain(certfile='ssl/cert.pem', keyfile='ssl/key.pem', password='secret')# OAuth2 client setup
    app.run(host="0.0.0.0", port=443, ssl_context=ssl_context)

@app.route('/') #test api
def hello_world():
    return 'Hello, World!'

@app.route('/echo/<param>') #get echo api
def get_echo_call(param):
    return jsonify({"param": param})

@app.route('/echo', methods=['POST']) #post echo api
def post_echo_call():
    param = request.get_json()
    return jsonify(param)

@app.route('/login', methods=['POST'])
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = oauth_client_google.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return request_uri

@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send request to get tokens! Yay tokens!
    token_url, headers, body = oauth_client_google.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    oauth_client_google.parse_request_body_response(json.dumps(token_response.json()))

    # Now that we have tokens (yay) let's find and hit URL
    # from Google that gives you user's profile information,
    # including their Google Profile Image and Email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = oauth_client_google.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    login_callback(userinfo_response.json())
    # Send user back to homepage
    return redirect(url_for("hello_world"))

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


if __name__ == '__main__':
    main()
