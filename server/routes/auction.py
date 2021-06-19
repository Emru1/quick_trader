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
    info_sended = False

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
                AuctionHandler.current_price = float(
                    AuctionHandler.current_auction['start_price'])
            except DoesNotExist as e:
                AuctionHandler.current_auction = None

        return AuctionHandler.current_auction

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
            if not cls.current_auction and not cls.current_auction_started:
                # BRAK LICYTACJI W BAZIE
                return errors.ERROR_NO_AUCTION, {}

            elif cls.current_auction and not cls.current_auction_started:
                # wyslij info, kiedy odbiedzie sie najblizsza licytacja
                info = {}
                info['type'] = 'info'
                info['name'] = cls.current_auction['name']
                info['current_price'] = cls.current_price
                info['start_time'] = str(
                    cls.current_auction['start_time'])
                info['started'] = cls.current_auction_started
                return None, info

            else:
                # LICYTACJA TRWA -> WYŚLIJ JEJ STATUS
                return cls.get_current_auction_info()

    @classmethod
    def get_current_auction_info(cls):
        '''
        PRZYGOTOWUJE WIADOMOSC O AKTUALNEJ LICYTACJI
        '''
        info = {}
        info['type'] = 'info'
        info['name'] = AuctionHandler.current_auction['name']
        info['current_price'] = AuctionHandler.current_price
        info['leader'] = AuctionHandler.current_leader
        info['start_time'] = str(
            AuctionHandler.current_auction['start_time'])
        info['end_time'] = AuctionHandler.current_end_time
        info['started'] = AuctionHandler.current_auction_started
        return None, info

    @classmethod
    def end_of_time(cls):
        if not AuctionHandler.current_auction:
            return

        print(f'OBSLUGIWANA: {AuctionHandler.current_auction}')
        query = Auction.update({Auction.ended: 1, Auction.buyer: AuctionHandler.current_leader,
                                Auction.start_price: AuctionHandler.current_price}).\
            where(Auction.id == AuctionHandler.current_auction['id'])
        query.execute()

        cls.current_auction = None
        cls.current_auction_started = False
        cls.current_leader = None  # id
        cls.current_price = None
        cls.current_end_time = 60
        cls.previous_time = 0

    @classmethod
    def bet(cls, data):
        '''
        Obsługa betowania. Zwraca True/False - czy się udało
        :param: username - nazwa użytkownika
        :param: new_price - cena zaproponowana przez użytkownika
        '''
        logged = check_auth(data['token'])
        auction_conditions = (
            cls.current_auction and cls.current_auction_started and cls.current_end_time)
        user_conditions = (logged and cls.current_leader != data['username'])

        if auction_conditions and user_conditions:
            if data['price'] > cls.current_price:

                cls.current_price = data['price']
                cls.current_leader = data['username']
                cls.current_end_time += 10

                info = {}
                info['name'] = cls.current_auction['name']
                info['type'] = 'bet'
                info['current_price'] = cls.current_price
                info['leader'] = cls.current_leader
                info['end_time'] = AuctionHandler.current_end_time
                info['started'] = AuctionHandler.current_auction_started
                return None, info

        return errors.ERROR_LOGIN_FAILED, {}
