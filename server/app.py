import json
import errors


def string_to_json(data):
    try:
        ret = json.loads(data)
    except json.JSONDecodeError:
        return None
    return ret


class App:
    """
    Klasa będąca reprezentacją całej aplikacji, czy raczej jej funkcjonalności
    """
    def __init__(self, inqueue, outqueue, routes):
        # from config import GLOBAL_CONFIG
        self.inqueue = inqueue
        self.outqueue = outqueue

        self.routes = routes

    def send(self, fd, data):
        json_str = json.dumps(data)
        self.outqueue.put({'fd': fd, 'data': json_str})

    def receive(self):
        while not self.inqueue.empty():
            data = self.inqueue.get()
            fd = data['fd']
            data_dict = string_to_json(data['data'])
            if not data_dict:
                self.send(fd, {
                    'type': 'error',
                    'error': errors.ERROR_JSON_PARSE,
                })
                continue

            error, resp = self.route(data_dict)
            if error:
                self.send(fd, {'type': 'error', 'error': error})
            else:
                self.send(fd, resp)

    def route(self, data):
        if 'type' not in data:
            return errors.ERROR_JSON_NO_TYPE, {}

        error, ret = self.routes.route(data)
        if error:
            return error, {}
        return None, ret

    def run(self):
        while True:
            self.receive()
