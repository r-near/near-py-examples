# Import the necessary components from the NEAR SDK
from near_sdk_py import view, call, init, Storage

# Define contract class
class HelloNear:
    def __init__(self):
        # Initialize state with default greeting
        self.greeting = "Hello"
    
    @view
    def get_greeting(self):
        """Returns the current greeting"""
        return self.greeting
    
    @call
    def set_greeting(self, message):
        """Sets a new greeting"""
        self.greeting = message
        return self.greeting
