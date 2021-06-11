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
    def __init__(self, inqueue, outqueue):
        # from config import GLOBAL_CONFIG
        self.inqueue = inqueue
        self.outqueue = outqueue

        self.routes = [
            'auth',
        ]

        pass

    def send(self, fd, data):
        self.outqueue.put({'fd': fd, 'data': data})

    def receive(self):
        while not self.inqueue.empty():
            data = self.inqueue.get()
            data_dict = string_to_json(data['data'])
            if not data_dict:
                self.send(data['fd'], {
                    'type': 'error',
                    'error': errors.ERROR_JSON_PARSE,
                })
                continue
            self.route(data_dict)

    def route(self, data):
        xdata = data['data']
        if 'type' not in xdata:
            self.send(data['fd'], {
                'type': 'error',
                'error': errors.ERROR_JSON_NO_TYPE
            })
            return

        route = data['type']
        if route not in self.routes:
            self.send(data['fd'], {
                'type': 'error',
                'error': errors.ERROR_TYPE_NON_EXIST
            })
            return
