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
                print(f'CURRENT: {current_time}. START: {start_time}')
                if current_time >= start_time:
                    AuctionHandler.current_auction_started = True

            if AuctionHandler.current_auction_started:
                if changed:
                    AuctionHandler.current_end_time -= 1

                AuctionHandler.current_price = 5000
                AuctionHandler.current_leader = 2
                
                if not AuctionHandler.current_end_time:
                    AuctionHandler.end_of_time()

    def run(self):
        while True:
            self.receive()
            self.handle_auction()
