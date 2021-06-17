import hashlib
import time

from peewee import DoesNotExist

import errors
from database import User, Auth


class Authorization:
    '''
    Klasa służąca do logowania
    '''
    def __init__(self):
        # from config import GLOBAL_CONFIG
        pass

    def login(self, data):
        print('Authorization endpoint')
        if 'username' not in data or 'password' not in data:
            return errors.ERROR_LOGIN_FAILED, {}
        username = data['username']
        password = data['password']
        try:
            user = User.get(User.name == username)
            print(user.id)
        except User.DoesNotExist:
            return errors.ERROR_LOGIN_FAILED, {}
        auth = Auth.get(Auth.user_id == user.id)
        try:
            h = hashlib.sha512(password.encode('utf-8')).hexdigest()
        except:
            return errors.ERROR_LOGIN_FAILED, {}
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
        print('Logout reguest')
        username = data.get('username', None)
        user_token = data.get('token', None)

        if username and user_token:
            try:
                user = User.get(User.name == username)
                user_auth = Auth.get(Auth.user_id == user,
                                     Auth.login_token == user_token)
                user_auth.login_token = ''
                user_auth.save()
                print(user_auth.login_token)
            except (User.DoesNotExist, Auth.DoesNotExist):
                return errors.ERROR_LOGOUT_FAILED, {}

        return None, {'succesfully': True}
