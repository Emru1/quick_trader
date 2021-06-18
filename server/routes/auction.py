from datetime import datetime
from database import Auction, Auth
import time
from .authorization import check_auth
from peewee import DoesNotExist
import errors


class AuctionHandler:
    """
    Klasa służąca do obsłygi aukcji po stronie serwera
    current_auction - zmienna w klasie, taka sama dla każdej instancji. Możliwość odwołania bez instancji
    """

    current_auction = None
    current_auction_started = False
    current_leader = None  # id
    current_price = None
    current_end_time = 60
    previous_time = 0

    def load_auction(self):
        self.current_auction = Auction.select().\
            where(not Auction.ended).\
            order_by(Auction.start_time.asc())
        if not self.current_auction:
            return errors.ERROR_NO_AUCTION, {}
        self.actual_price = self.current_auction.start_price
        self.seller = self.current_auction.seller
        self.end_time = self.current_auction.end_time
        self.item_name = self.current_auction.name
        return None, {"Actual_price": self.actual_price,
                      "Seller": self.seller,
                      "End_time": self.end_time,
                      "Item_name": self.item_name}

    @classmethod
    def get_newest_auction(cls):
        '''
        Pobiera najnowszy (pojedynczy) rekord z bazy albo None (kiedy już wszystko obsluzone) i aktualizuje zmienną klasową,
        :return: Auction or None
        '''
        if not AuctionHandler.current_auction:
            try:
                AuctionHandler.current_auction = Auction.select().\
                    where(Auction.ended == 0).\
                    order_by(Auction.start_time.asc()).dicts().get()
            except DoesNotExist as e:
                AuctionHandler.current_auction = None

        return AuctionHandler.current_auction

    @classmethod
    def update_newest_auction(cls, name):
        AuctionHandler.current_auction['name'] = name

    @classmethod
    def get_auction_status(cls, data):
        '''
        Sprawdza status trwającej aukcji i zwraca strukturę wiadomości
        '''
        print('Info endpoint')
        # 1. sprawdz czy user zalogowany(token)
        # 2. sprawdz, jak tam licytacja (AuctionHandler.current_auction). Czas, a może już trwa?
        # 3. zwroc co trzeba

        if 'token' not in data or not check_auth(data['token']):
            print('niezalogowany uzyszkodnik')

        else:
            if AuctionHandler.current_auction and AuctionHandler.current_auction_started:
                info = {}
                info['name'] = AuctionHandler.current_auction['name']
                info['current_price'] = float(AuctionHandler.current_price)
                info['leader'] = AuctionHandler.current_leader
                info['end_time'] = AuctionHandler.current_end_time
                return None, info
            else:
                return errors.ERROR_LOGIN_FAILED, {}

    def bet(self, data):

        if not data["token"]:
            return errors.ERROR_AUTH_FAILED, {}
        bet_price = data["price"]
        username = Auth.get(Auth.login_token == data["token"]).name
        if bet_price < self.actual_price:
            return None
        self.actual_price = bet_price
        self.buyer = username
        self.end_time += 10
        return None, {"Actual_price": self.actual_price,
                      "Buyer": self.buyer,
                      "End_time": self.end_time}

    @classmethod
    def end_of_time(cls):
        if not AuctionHandler.current_auction:
            return

        print(f'OBSLUGIWANA: {AuctionHandler.current_auction}')
        query = Auction.update({Auction.ended: 1, Auction.buyer: AuctionHandler.current_leader,
                                Auction.start_price: AuctionHandler.current_price}).\
            where(Auction.id == AuctionHandler.current_auction['id'])
        query.execute()

        AuctionHandler.current_auction = None
        AuctionHandler.current_auction_started = False
        AuctionHandler.current_leader = None  # id
        AuctionHandler.current_price = None
        AuctionHandler.current_end_time = 60
        AuctionHandler.previous_time = 0

        # return None, {"Actual_price": self.actual_price,
        #               "Buyer": self.buyer}

    @classmethod
    def countdown_to_auction(cls, start_time):
        '''
        LICZY DO ROZPOCZECIA AUKCJI (THREAD)
        '''

        if AuctionHandler.current_auction:
            pass
            # while datetime.now() < start_time:
            #     time.sleep(1)
            #     print(f'czeka {datetime.now()} do {start_time}')
            # AuctionHandler.current_auction_started = True
