import hashlib
import time

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
        except User.DoesNotExist:
            return errors.ERROR_LOGIN_FAILED, {}
        auth = Auth.get(Auth.user == user)
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
