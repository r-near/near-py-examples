from near_sdk_py import view, call, init, Context, Storage, Log, ONE_YOCTO

class Auction:
    # Storage keys
    HIGHEST_BID_KEY = "highest_bid"
    AUCTION_END_TIME_KEY = "auction_end_time"
    AUCTIONEER_KEY = "auctioneer"
    CLAIMED_KEY = "claimed"
    
    @init
    def init(self, end_time, auctioneer):
        """Initialize the auction contract with an end time and auctioneer account"""
        # Save auction end time
        Storage.set_json(self.AUCTION_END_TIME_KEY, end_time)
        
        # Initialize highest bid with current account and 1 yocto
        initial_bid = {
            "bidder": Context.current_account_id(),
            "bid": ONE_YOCTO
        }
        Storage.set_json(self.HIGHEST_BID_KEY, initial_bid)
        
        # Set auctioneer
        Storage.set(self.AUCTIONEER_KEY, auctioneer)
        
        # Initialize claimed status
        Storage.set_json(self.CLAIMED_KEY, False)
        
        return True
    
    @call
    def bid(self):
        """Place a bid in the auction"""
        # Get auction end time
        auction_end_time = Storage.get_json(self.AUCTION_END_TIME_KEY)
        
        # Assert the auction is still ongoing
        current_time = Context.block_timestamp()
        assert current_time < auction_end_time, "Auction has ended"
        
        # Current bid
        bid_amount = Context.attached_deposit()
        bidder = Context.predecessor_account_id()
        
        # Get last bid
        highest_bid = Storage.get_json(self.HIGHEST_BID_KEY)
        last_bidder = highest_bid["bidder"]
        last_bid = highest_bid["bid"]
        
        # Check if the deposit is higher than the current bid
        assert bid_amount > last_bid, "You must place a higher bid"
        
        # Update the highest bid
        new_highest_bid = {
            "bidder": bidder,
            "bid": bid_amount
        }
        Storage.set_json(self.HIGHEST_BID_KEY, new_highest_bid)
        
        # Transfer tokens back to the last bidder
        from near_sdk_py import CrossContract
        return CrossContract.transfer(last_bidder, last_bid)
    
    @call
    def claim(self):
        """Claim the auction proceeds after it has ended"""
        # Get auction end time and claimed status
        auction_end_time = Storage.get_json(self.AUCTION_END_TIME_KEY)
        claimed = Storage.get_json(self.CLAIMED_KEY)
        
        # Assert the auction has ended
        current_time = Context.block_timestamp()
        assert current_time > auction_end_time, "Auction has not ended yet"
        
        # Assert the auction has not been claimed
        assert not claimed, "Auction has already been claimed"
        
        # Mark as claimed
        Storage.set_json(self.CLAIMED_KEY, True)
        
        # Get highest bid and auctioneer
        highest_bid = Storage.get_json(self.HIGHEST_BID_KEY)
        auctioneer = Storage.get_string(self.AUCTIONEER_KEY)
        
        # Transfer tokens to the auctioneer
        from near_sdk_py import Promise
        return Promise.create_batch(auctioneer).transfer(highest_bid["bid"])
    
    @view
    def get_highest_bid(self):
        """Returns the current highest bid information"""
        return Storage.get_json(self.HIGHEST_BID_KEY)
    
    @view
    def get_auction_end_time(self):
        """Returns the auction end time"""
        return Storage.get_json(self.AUCTION_END_TIME_KEY)


# Export the contract methods
auction = Auction()

# These exports make functions available to the NEAR runtime
init = auction.init
bid = auction.bid
claim = auction.claim
get_highest_bid = auction.get_highest_bid
get_auction_end_time = auction.get_auction_end_time
