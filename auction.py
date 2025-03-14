from near_sdk_py import Contract, view, call, init, ONE_YOCTO, CrossContract

class AuctionContract(Contract):
    @init
    def initialize(self, end_time, auctioneer):
        """Initialize the auction contract with an end time and auctioneer account"""
        # Save auction end time
        self.storage["auction_end_time"] = end_time
        
        # Initialize highest bid with current account and 1 yocto
        initial_bid = {
            "bidder": self.current_account_id,
            "bid": ONE_YOCTO
        }
        self.storage["highest_bid"] = initial_bid
        
        # Set auctioneer
        self.storage["auctioneer"] = auctioneer
        
        # Initialize claimed status
        self.storage["claimed"] = False
        
        return {"success": True}
    
    @call
    def bid(self):
        """Place a bid in the auction"""
        # Get auction end time
        auction_end_time = self.storage["auction_end_time"]
        
        # Assert the auction is still ongoing
        current_time = self.block_timestamp
        if current_time >= auction_end_time:
            raise InvalidInput("Auction has ended")
        
        # Current bid
        bid_amount = self.attached_deposit
        bidder = self.predecessor_account_id
        
        # Get last bid
        highest_bid = self.storage["highest_bid"]
        last_bidder = highest_bid["bidder"]
        last_bid = highest_bid["bid"]
        
        # Check if the deposit is higher than the current bid
        if bid_amount <= last_bid:
            raise InvalidInput("You must place a higher bid")
        
        # Update the highest bid
        new_highest_bid = {
            "bidder": bidder,
            "bid": bid_amount
        }
        self.storage["highest_bid"] = new_highest_bid
        
        # Log the new bid
        self.log_event("new_bid", {
            "bidder": bidder,
            "amount": bid_amount
        })
        
        # Transfer tokens back to the last bidder
        return CrossContract(last_bidder).transfer(last_bid).value()
    
    @call
    def claim(self):
        """Claim the auction proceeds after it has ended"""
        # Get auction end time and claimed status
        auction_end_time = self.storage["auction_end_time"]
        claimed = self.storage.get("claimed", False)
        
        # Assert the auction has ended
        current_time = self.block_timestamp
        if current_time <= auction_end_time:
            raise InvalidInput("Auction has not ended yet")
        
        # Assert the auction has not been claimed
        if claimed:
            raise InvalidInput("Auction has already been claimed")
        
        # Mark as claimed
        self.storage["claimed"] = True
        
        # Get highest bid and auctioneer
        highest_bid = self.storage["highest_bid"]
        auctioneer = self.storage["auctioneer"]
        
        # Log the claim
        self.log_event("auction_claimed", {
            "winner": highest_bid["bidder"],
            "amount": highest_bid["bid"]
        })
        
        # Transfer tokens to the auctioneer
        return CrossContract(auctioneer).transfer(highest_bid["bid"]).value()
    
    @view
    def get_highest_bid(self):
        """Returns the current highest bid information"""
        return self.storage.get("highest_bid")
    
    @view
    def get_auction_end_time(self):
        """Returns the auction end time"""
        return self.storage.get("auction_end_time")
    
    @view
    def get_auction_status(self):
        """Returns the overall status of the auction"""
        current_time = self.block_timestamp
        auction_end_time = self.storage["auction_end_time"]
        highest_bid = self.storage["highest_bid"]
        claimed = self.storage.get("claimed", False)
        
        return {
            "is_active": current_time < auction_end_time,
            "time_remaining": max(0, auction_end_time - current_time),
            "highest_bidder": highest_bid["bidder"],
            "highest_bid": highest_bid["bid"],
            "claimed": claimed,
            "auctioneer": self.storage["auctioneer"]
        }
