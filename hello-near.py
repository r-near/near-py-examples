# Import the necessary components from the NEAR SDK
from near_sdk_py import view, call, Contract

# Define contract class
class HelloNear:
    @init
    def new(self):
        # Initialize state with default greeting
        self.storage["greeting"] = "Hello"
    
    @view
    def get_greeting(self) -> str:
        """Returns the current greeting"""
        return self.storage["greeting"]
    
    @call
    def set_greeting(self, message: str) -> str:
        """Sets a new greeting"""
        self.storage["greeting"] = message
        return message
