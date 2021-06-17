from server.database import Auction, Auth
import errors


class AuctionHandler:
    """
    Klasa służąca do obsłygi aukcji po stronie serwera
    """
    def __init__(self):
        # from config import GLOBAL_CONFIG
        self.current_auction = None
        self.actual_price = None
        self.seller = None
        self.end_time = None
        self.item_name = None
        self.buyer = None
        pass

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

    def end_of_time(self):
        Auction.update({Auction.ended: True, Auction.buyer: self.buyer,
                        Auction.start_price: self.actual_price})
        return None, {"Actual_price": self.actual_price,
                      "Buyer": self.buyer}
