from routes.authorization import Authorization
import errors


class Router:
    """
    Klasa ta definiuje różne endpointy w aplikacji
    """
    def __init__(self):
        self.routes = {
            'auth': Authorization().login,
        }

    def route(self, data):
        if data['type'] not in self.routes:
            return errors.ERROR_TYPE_NON_EXIST, {}
        error, ret = self.routes[data['type']](data)
        if error:
            return error, {}
        return None, {'type': data['type']} | ret
