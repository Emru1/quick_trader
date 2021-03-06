import hashlib
import time

from peewee import DoesNotExist

import errors
from database import User, Auth


def check_auth(token: str):
    '''
    Ja bym sprawdzał jeszcze czy username się zgadza.
    user: MArcin tokensadads
    user: Łukasz tokensadasa
    '''
    if type(token) is dict:
        try:
            xtoken = token['auth']
        except KeyError:
            return None
    else:
        xtoken = token

    if type(xtoken) is not str:
        return None
    try:
        auth = Auth.get(Auth.login_token == xtoken)
        user = User.get(User.id == auth.user_id)
    except DoesNotExist:
        return None
    return user


class Authorization:
    '''
    Klasa służąca do logowania
    '''
    def __init__(self):
        # from config import GLOBAL_CONFIG
        pass

    def login(self, data):
        if 'username' not in data or 'password' not in data:
            return errors.ERROR_LOGIN_FAILED, {}
        username = data['username']
        password = data['password']
        try:
            user = User.get(User.name == username)
        except User.DoesNotExist:
            return errors.ERROR_LOGIN_FAILED, {}
        auth = Auth.get(Auth.user_id == user.id)
        h = hashlib.sha512(password.encode('utf-8')).hexdigest()
        if auth.password_sha512 == h:
            now = int(time.time())
            xtime = str(now).encode('utf-8')
            xpass = str(password).encode('utf-8')
            xname = str(username).encode('utf-8')
            ret = hashlib.sha512(xtime + b'\0' + xpass + b'\0' +
                                 xname).hexdigest()

            auth.login_token = ret
            auth.login_date = now
            auth.save()

            return None, {'token': ret}
        else:
            return errors.ERROR_LOGIN_FAILED, {}

    def logout(self, data):
        username = data.get('username', None)
        user_token = data.get('token', None)

        if username and user_token:
            try:
                user = User.get(User.name == username)
                user_auth = Auth.get(Auth.user_id == user,
                                     Auth.login_token == user_token)
                user_auth.login_token = ''
                user_auth.save()
            except (User.DoesNotExist, Auth.DoesNotExist):
                return errors.ERROR_LOGOUT_FAILED, {}

        return None, {'succesfully': True}
