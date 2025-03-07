from near_sdk_py import view, call, init, Context, Storage, Log
import time

class Auction:
    # Storage keys
    AUCTION_END_KEY = "auction_end"
    HIGHEST_BID_KEY = "highest_bid"
    
    @init
    def initialize(self, duration_minutes):
        """
        Initializes the auction with a duration in minutes.
        
        This function must be called first.
        """
        current_time_ms = time.time() * 1000
        auction_end = current_time_ms + (duration_minutes * 60 * 1000)
        
        # Store auction end time in persistent storage
        Storage.set(self.AUCTION_END_KEY, str(auction_end))
        
        # Initialize highest bid
        initial_bid = {
            "account_id": "",
            "amount": 0
        }
        Storage.set_json(self.HIGHEST_BID_KEY, initial_bid)
        
        return {"auction_end": auction_end}
    
    @call
    def place_bid(self):
        """
        Places a bid in the auction.
        
        The bid amount is taken from the attached deposit.
        """
        deposit = Context.attached_deposit()
        predecessor = Context.predecessor_account_id()
        
        # Get current auction end time from storage
        auction_end = float(Storage.get_string(self.AUCTION_END_KEY) or 0)
        
        current_time_ms = time.time() * 1000
        if current_time_ms > auction_end:
            raise Exception("Auction has ended")
        
        # Get current highest bid from storage
        highest_bid = Storage.get_json(self.HIGHEST_BID_KEY) or {"account_id": "", "amount": 0}
        
        if deposit <= highest_bid["amount"]:
            raise Exception("Bid is not higher than current highest bid")
            
        # Update highest bid in storage
        new_highest_bid = {
            "account_id": predecessor,
            "amount": deposit
        }
        Storage.set_json(self.HIGHEST_BID_KEY, new_highest_bid)
        
        Log.info(f"New highest bid: {deposit} from {predecessor}")
        return new_highest_bid
    
    @view
    def get_highest_bid(self):
        """Returns the current highest bid information"""
        return Storage.get_json(self.HIGHEST_BID_KEY) or {"account_id": "", "amount": 0}
    
    @view
    def get_auction_status(self):
        """Returns the current auction status"""
        current_time_ms = time.time() * 1000
        
        # Get auction end time from storage
        auction_end = float(Storage.get_string(self.AUCTION_END_KEY) or 0)
        
        # Get highest bid from storage
        highest_bid = Storage.get_json(self.HIGHEST_BID_KEY) or {"account_id": "", "amount": 0}
        
        return {
            "ended": current_time_ms > auction_end,
            "end_time": auction_end,
            "current_time": current_time_ms,
            "highest_bid": highest_bid
        }


# Export the contract methods
auction = Auction()

# These exports make functions available to the NEAR runtime
initialize = auction.initialize
place_bid = auction.place_bid
get_highest_bid = auction.get_highest_bid
get_auction_status = auction.get_auction_status
