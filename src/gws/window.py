from gws._typing import WindowManagerLike, WindowLike
from gws._errors import OutOfBoundsInputError

class BasicWindow:
    '''The basic window object. Represents a window for any WindowManager'''

    def __init__(self, window_manager: WindowManagerLike, id: str):
        '''
        :param WindowManagerLike window_manager: The WindowManager object for the host machine's window manager
        :param str id: The ID of the window this object will represent'''
        self.window_manager: WindowManagerLike = window_manager
        self.id: str = id

    def click(self, x: int, y: int, button: str, duration: float = 0.09, bypass_out_of_bounds_check: bool = False):
        '''Clicks at a position relative to the window.
        Raises an error if the click is out of bounds of the window.
        
        :param int x: The x coord to click at
        :param int y: The y coord to click at
        :param float duration: The length to click for
        :param str button: The button to click. Either 'left' 'middle' or 'right'.
        :param bool bypass_out_of_bounds_check: If we should bypass checking if the click is out of bounds. '''
        # first we get if the click is out of bounds (if enabled)
        if not bypass_out_of_bounds_check:
            window_size = self.window_manager.get_size_of_window(self.id)

            # now we check if either the x or y is out of bounds
            if x > window_size[0]:
                raise OutOfBoundsInputError(f'Click at ({x}, {y}) has a bigger x than the window\'s size ({window_size[0]}, {window_size[1]})')
            elif y > window_size[1]:
                raise OutOfBoundsInputError(f'Click at ({x}, {y}) has a bigger y than the window\'s size ({window_size[0]}, {window_size[1]})')
            
        # now we're onto actually clicking
        # first we get the offset (the window's position)
        window_position = self.window_manager.get_position_of_window(self.id)

        # then we click
        self.window_manager.click(x + window_position[0], y + window_position[1], duration, button)

    def key_down(self, key: str):
        '''Presses a key down

        :param str key: The key to press'''
        self.window_manager.key_down(key)

    def key_up(self, key: str):
        '''Releases a key
        
        :param str key: The key to release'''
        self.window_manager.key_up(key)

    def press(self, key: str, duration: float):
        '''Presses and holds a key for duration time.
        
        :param str key: The key to press
        :param float duration: How long to hold the key
        '''
        self.window_manager.press(key, duration)

    def get_name(self) -> str:
        '''Returns the current name of this window'''
        return self.window_manager.get_name_of_window(self.id)
    
    def get_position(self) -> tuple[int, int]:
        '''Returns the current global position of the window'''
        return self.window_manager.get_position_of_window(self.id)
    
    def get_size(self) -> tuple[int, int]:
        '''Returns the current size of the window'''
        return self.window_manager.get_size_of_window(self.id)
    
    def typewrite(self, text: str, hold_duration: float = 0.09, spacing_duration: float = 0):
        '''Types characters, holding each one for a given time, and with a given duration between each key press.
        
        :param str text: The text to typewrite
        :param float hold_duration: The duration to hold each key
        :param float interval: The duration to wait between each key press'''
        self.window_manager.typewrite(text, hold_duration, spacing_duration)
