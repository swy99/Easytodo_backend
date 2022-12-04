from flask import Flask, request, jsonify, redirect, url_for, make_response
import json
import ssl
from oauthlib.oauth2 import WebApplicationClient
import requests
from api_server_initialization import *
from session_manager import *
from db_mananger import DBManager



DEBUG = True

GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_DISCOVERY_URL = init_google_oauth()

app = Flask('name')
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)
oauth_client_google = WebApplicationClient(GOOGLE_CLIENT_ID)

session_manager = SessionManager()
db_manager = DBManager()

def main():
    #ssl settings
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    if DEBUG: ssl_context.load_cert_chain(certfile='ssl/cert.pem', keyfile='ssl/key.pem', password='secret')# OAuth2 client setup
    else: ssl_context.load_cert_chain(certfile='/etc/letsencrypt/live/easytodo.p-e.kr/fullchain.pem', keyfile='/etc/letsencrypt/live/easytodo.p-e.kr/privkey.pem', password='secret')
    if DEBUG: app.run(host="localhost", port=443, ssl_context=ssl_context)
    else: app.run(host="0.0.0.0", port=443, ssl_context=ssl_context)

def response_login_success_json(session: Session, userinfo_dict: dict) -> str:  # make a json object with token and userinfo
    token_dict = {'sid': session.sid, 'expired_at': datetime2JSON(session.timeout), 'Cookie': 'sid=' + session.sid}
    res_dict = {'token': token_dict, 'userinfo': userinfo_dict}
    del res_dict['userinfo']['sub'], res_dict['userinfo']['uid']
    return json.dumps(res_dict, ensure_ascii=False)

def response_unauthorized(msg: str = ""):
    return msg, 401

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

# END OF auxiliary functions

@app.route('/')  # test api
def hello_world():
    return 'Hello, World!'

@app.route('/echo/<param>')  # get echo api
def get_echo_call(param):
    return jsonify({"param": param})

@app.route('/echo', methods=['POST'])  # post echo api
def post_echo_call():
    param = request.get_json()
    return jsonify(param)

@app.route('/login2', methods=['POST', 'GET'])
def login2():
    if not DEBUG: return
    # Find out what URL to hit for Google login
    authorization_endpoint = get_google_provider_cfg()["authorization_endpoint"]

    # Use library to construct the request for login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = oauth_client_google.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return request_uri

@app.route("/login2/callback")
def login_callback():
    if not DEBUG: return
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    token_endpoint = get_google_provider_cfg()["token_endpoint"]

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

    print(token_response.json())
    return token_response.json()

    # Parse the tokens!
    oauth_client_google.parse_request_body_response(json.dumps(token_response.json(), ensure_ascii=False))

    # Now that we have tokens (yay) let's find and hit URL
    # from Google that gives you user's profile information,
    # including their Google Profile Image and Email
    userinfo_endpoint = get_google_provider_cfg()["userinfo_endpoint"]
    uri, headers, body = oauth_client_google.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    userinfo_dict = userinfo_response.json()
    uid = userinfo_dict['sub']
    userinfo_dict['uid'] = uid

    if db_manager.is_member(uid) or db_manager.sign_up(userinfo_dict):
        userinfo_dict = db_manager.get_userinfo(uid)
        session = session_manager.login(userinfo_dict['uid'])
        resp_str = response_login_success_json(session, userinfo_dict)
        resp = make_response(resp_str)
        resp.set_cookie("sid", session.sid)
    else:
        resp = "error"

    return resp

@app.route("/login", methods=['POST'])
def login():
    tokens = request.get_json()

    # Parse the tokens!
    try:
        oauth_client_google.parse_request_body_response(json.dumps(tokens, ensure_ascii=False))
    except Exception as e:
        print(f'login {e}')
        return

    # Now that we have tokens (yay) let's find and hit URL
    # from Google that gives you user's profile information,
    # including their Google Profile Image and Email
    userinfo_endpoint = get_google_provider_cfg()["userinfo_endpoint"]
    uri, headers, body = oauth_client_google.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    try:
        userinfo_dict = userinfo_response.json()
    except Exception as e:
        print(f'login {e}')
        return
    uid = userinfo_dict['sub']
    userinfo_dict['uid'] = uid

    if db_manager.is_member(uid) or db_manager.sign_up(userinfo_dict):
        userinfo_dict = db_manager.get_userinfo(uid)
        session = session_manager.login(userinfo_dict['uid'])
        resp_str = response_login_success_json(session, userinfo_dict)
        resp = make_response(resp_str)
        resp.set_cookie("sid", session.sid)
    else:
        resp = "error"

    return resp

@app.route('/logout', methods=['POST'])
def logout():
    sid = request.cookies.get('sid')
    if session_manager.logout(sid):
        return make_response("LOGOUT successful")
    return response_unauthorized("session not found")

@app.route('/account', methods=['DELETE'])
def delete_account():
    res = response_unauthorized("account not found")
    sid = request.cookies.get('sid')
    uid = session_manager.sid_to_uid(sid)
    if uid is not None:
        if db_manager.delete_account(uid):
            session_manager.remove_session_by_uid(uid)
            res = make_response("account DELETED successfully")
        else:
            res = ("DB Error", 500)
    return res

@app.route('/todoitem', methods=['POST'])
def post_todoitem():
    ret = response_unauthorized("account not found")
    sid = request.cookies.get('sid')
    uid = session_manager.sid_to_uid(sid)
    if uid is not None:
        todoitems = request.get_json()
        res = False
        if type(todoitems) is list:
            res = db_manager.insert_listof_todoitems(uid, todoitems)
        elif type(todoitems) is dict:
            res = db_manager.insert_one_todoitem(uid, todoitems)
        ret = "Success" if res else "Fail"
    return ret

@app.route('/todoitem', methods=['GET'])
def get_todoitem():
    res = response_unauthorized("account not found")
    sid = request.cookies.get('sid')
    uid = session_manager.sid_to_uid(sid)
    if uid is not None:
        list_todoitem = db_manager.get_todoitems(uid)
        res = json.dumps(list_todoitem, ensure_ascii=False)
    return res

@app.route('/todoitem', methods=['PUT'])
def put_todoitem():
    ret = response_unauthorized("account not found")
    sid = request.cookies.get('sid')
    uid = session_manager.sid_to_uid(sid)
    if uid is not None:
        todoitems = request.get_json()
        res = False
        if type(todoitems) is list:
            res = False  # not Supported! /// db_manager.insert_listof_todoitems(uid, todoitems)
        elif type(todoitems) is dict:
            res = db_manager.update_one_todoitem(uid, todoitems)
        ret = "Success" if res else "Fail"
    return ret

@app.route('/todoitem', methods=['DELETE'])
def delete_todoitem():
    ret = response_unauthorized("account not found")
    sid = request.cookies.get('sid')
    uid = session_manager.sid_to_uid(sid)
    if uid is not None:
        id = request.args.get('id', type=int)
        if type(id) is not int:
            res = False
        else:
            res = db_manager.delete_one_todoitem(uid, id)
        ret = "Success" if res else "Fail"
    return ret

@app.route('/recommendation', methods=['GET'])
def get_recommendation():
    ret = response_unauthorized("account not found")
    sid = request.cookies.get('sid')
    uid = session_manager.sid_to_uid(sid)
    if uid is not None:
        ret = json.dumps(["Do Homework", "Exercise", "Take pills"])
    return ret

if __name__ == '__main__':
    main()
