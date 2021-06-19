import json
import errors
import time
from routes.auction import AuctionHandler


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
                if resp['type'] == 'bet':
                    self.send(None, resp)
                    return
                self.send(fd, resp)

    def route(self, data):
        if 'type' not in data:
            return errors.ERROR_JSON_NO_TYPE, {}

        error, ret = self.routes.route(data)
        if error:
            return error, {}
        return None, ret

    def handle_auction(self):
        '''
        Obsługa licytacji. Jeszcze nie wiem dlaczego tak
        '''

        newest_auction = AuctionHandler.get_newest_auction()
        current_time = int(time.time())

        if current_time > AuctionHandler.previous_time:
            changed = True
            AuctionHandler.previous_time = current_time
        else:
            changed = False

        if newest_auction:
            start_time = newest_auction['start_time']

            # AuctionHandler.countdown_to_auction(start_time)
            if changed:
                start_time = int(start_time.timestamp())
                if current_time >= start_time:
                    AuctionHandler.current_auction_started = True

            if AuctionHandler.current_auction_started:
                if not AuctionHandler.info_sended:
                    _, msg = AuctionHandler.get_current_auction_info()
                    self.send(None, msg)
                    AuctionHandler.info_sended = True
                if changed:
                    AuctionHandler.current_end_time -= 1

                # AuctionHandler.current_price = 5000
                # AuctionHandler.current_leader = 2

                if not AuctionHandler.current_end_time:
                    _, msg = AuctionHandler.get_current_auction_info()
                    self.send(None, msg)
                    AuctionHandler.end_of_time()

    def run(self):
        xtime = 1
        prevtime = 0
        while True:
            self.receive()
            self.handle_auction()

            xtime = int(time.time())
            if xtime > prevtime:
                prevtime = xtime
                if not xtime % 4:
                    self.send(None, {'type': 'ping'})
