import uuid
from datetime import datetime, timedelta
from functools import wraps

import jwt
from flask import Flask, request, make_response, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

import db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'THE SECRET KEY'


@app.route('/')
def HelloWorld():
    return "Hello World!"


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message': 'Token is missing !!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = db.findUserById(data['user_id'])[0]
        except:
            return jsonify({
                'message': 'Token is invalid !!'
            }), 401
        return f(current_user, *args, **kwargs)

    return decorated


@app.route('/user', methods=['GET'])
@token_required
def get_all_users(current_user):
    users = db.getAllUser()
    output = []
    for user in users:
        output.append({
            'user_id': user['user_id'],
            'name': user['name'],
            'phone': user['phone']
        })

    return jsonify({'users': output})


@app.route('/signup', methods=['POST'])
def signup():
    data = request.form

    name, phone = data.get('name'), data.get('phone')
    password = data.get('password')
    if db.hasAnUser(phone):
        return make_response(jsonify({'token': '',
                                      'user': {'user_id': '', 'name': '',
                                               'phone': ''}, 'error': 'User already Exists!, Login to Continue'}), 202)
    passwd_hash = generate_password_hash(password)
    user = {"user_id": str(uuid.uuid4()), "name": name, "phone": phone, "password": passwd_hash}
    db.user_collection.insert_one(user)

    token = jwt.encode({
        'user_id': user['user_id'],
        'exp': datetime.utcnow() + timedelta(minutes=30)
    }, app.config['SECRET_KEY'])
    return make_response(jsonify({'token': token.decode(encoding='utf-8', errors='strict'),
                                  'user': {'user_id': user['user_id'], 'name': user['name'],
                                           'phone': user['phone']}, 'error': ''}), 201)


@app.route('/login', methods=['POST'])
def login():
    auth = request.form

    if not auth or not auth.get('phone') or not auth.get('password'):
        return make_response({'token': '', 'user': {'user_id': '', 'name': '',
                                                    'phone': ''}, 'error': 'Authentication Failed'}, 401)

    if not db.hasAnUser(auth.get('phone')):
        return make_response({'token': '', 'user': {'user_id': '', 'name': '',
                                                    'phone': ''}, 'error': 'User Does not exist'}, 401)

    user = db.findUserByPhone(auth.get('phone'))[0]
    if check_password_hash(user['password'], auth.get('password')):
        token = jwt.encode({
            'user_id': user['user_id'],
            'exp': datetime.utcnow() + timedelta(minutes=30)
        }, app.config['SECRET_KEY'])

        return make_response(jsonify({'token': token.decode(encoding='utf-8', errors='strict'),
                                      'user': {'user_id': user['user_id'], 'name': user['name'],
                                               'phone': user['phone']}, 'error': ''}), 200)
    # returns 403 if password is wrong
    return make_response({'token': '', 'user': {'user_id': '', 'name': '',
                                                'phone': ''}, 'error': 'Password incorrect'}, 403)


if __name__ == '__main__':
    app.run()
