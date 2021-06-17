from routes.authorization import Authorization
from routes.ping import Ping
import errors


class Router:
    """
    Klasa ta definiuje różne endpointy w aplikacji
    """
    def __init__(self):
        self.routes = {
            'auth': Authorization().login,
            'logout': Authorization().logout,
            'ping': Ping().ping,
        }

    def route(self, data):
        print(data)
        if data['type'] not in self.routes:
            return errors.ERROR_TYPE_NON_EXIST, {}
        error, ret = self.routes[data['type']](data)
        if error:
            return error, {}
        return None, {'type': data['type']} | ret
