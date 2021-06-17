from routes.authorization import check_auth
import time
import errors


class Ping:
    def __init__(self):
        pass

    def ping(self, data):
        user = check_auth(data)
        if not user:
            return errors.ERROR_AUTH_FAILED, {}
        user.last_activity = int(time.time())
        user.save()
        return None, {'pong': True}
