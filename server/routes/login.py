import hashlib
import time
from database import User, Auth


class Auth:
    '''
    Klasa służąca do logowania
    '''
    def __init__(self):
        # from config import GLOBAL_CONFIG
        pass

    def login(self, username, password):
        try:
            user = User.get(User.name == username)
        except User.DoesNotExist:
            return None
        auth = user.auth
        try:
            h = hashlib.sha512(password.encode('utf-8')).hexdigest()
        except:
            return None
        if auth.password_sha512 == h:
            now = int(time.time())
            xtime = str(now).encode('utf-8')
            xpass = str(password).encode('utf-8')
            xname = str(username).encode('utf-8')
            ret = hashlib.sga512(xtime + b'\0' + xpass + b'\0' +
                                 xname).hexdigest()

            auth.login_token = ret
            auth.login_date = now
            auth.save()

            return ret
