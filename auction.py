from near_sdk_py import view, call, init, Context, Log
import time

class Auction:
    def __init__(self):
        # Initialize state variables
        self.auction_end = 0  # Time when auction ends
        self.highest_bid = {
            "account_id": "",
            "amount": 0
        }
    
    @init
    def initialize(self, duration_minutes):
        """
        Initializes the auction with a duration in minutes.
        
        This function must be called first.
        """
        current_time_ms = time.time() * 1000
        self.auction_end = current_time_ms + (duration_minutes * 60 * 1000)
        return {"auction_end": self.auction_end}
    
    @call
    def place_bid(self):
        """
        Places a bid in the auction.
        
        The bid amount is taken from the attached deposit.
        """
        deposit = Context.attached_deposit()
        predecessor = Context.predecessor_account_id()
        
        current_time_ms = time.time() * 1000
        if current_time_ms > self.auction_end:
            raise Exception("Auction has ended")
            
        if deposit {'<='} self.highest_bid["amount"]:
            raise Exception("Bid is not higher than current highest bid")
            
        # Update highest bid
        self.highest_bid = \{
            "account_id": predecessor,
            "amount": deposit
        }
        
        Log.info(f"New highest bid: {deposit} from {predecessor}")
        return self.highest_bid
    
    @view
    def get_highest_bid(self):
        """Returns the current highest bid information"""
        return self.highest_bid
    
    @view
    def get_auction_status(self):
        """Returns the current auction status"""
        current_time_ms = time.time() * 1000
        return \{
            "ended": current_time_ms > self.auction_end,
            "end_time": self.auction_end,
            "current_time": current_time_ms,
            "highest_bid": self.highest_bid
        }
