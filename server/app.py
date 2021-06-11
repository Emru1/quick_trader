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
        pass

    def receive(self):
        while not self.inqueue.empty():
            data = self.inqueue.get()
            data_dict = string_to_json(data['data'])
            if not data_dict:
                self.outqueue.put({
                    'fd': data['fd'],
                    'data': {
                        'type': 'error',
                        'error': errors.ERROR_JSON_PARSE,
                    }
                })
                continue
            self.route(data_dict)

    def route(self, data):
        xdata = data['data']
        if 'type' not in xdata:
            self.outqueue.put({
                'fd': data['fd'],
                'data': {
                    'type': 'error',
                    'error': errors.ERROR_JSON_NO_TYPE,
                }
            })
            return
