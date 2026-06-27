from typing import TYPE_CHECKING
from gws._errors import OutOfBoundsInputError
from PIL import Image

if TYPE_CHECKING:
    from gws._typing import WindowManagerLike

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

    def screenshot(self) -> Image.Image:
        '''Takes a screenshot of the entire window, returns it as a Pillow Image.'''
        # getting data about the window and saving it to a variable, so we don't have
        # to redo requests
        window_size = self.get_size()
        window_position = self.get_position()

        # taking a screenshot and returning it
        return self.window_manager.screenshot_region(*window_position, window_position[0] + window_size[0], window_position[1] + window_size[1])
    
    def screenshot_region(self, x: int, y: int, width: int, height: int) -> Image.Image:
        '''Takes a screenshot of a region of the window, and returns it as a Pillow Image object. 
        If the region would be outside of the window, a OutOfBoundsInputError is raised.
        
        If you want to take a screenshot that spans more than window, use your window manager's screenshot 
        or screenshot_region methods instead.
        :param int x: The starting x for the screenshot region
        :param int y: The starting y for the screenshot region
        :param int width the width of the screenshot region
        :param int height the height of the screenshot region:'''
        # getting data about the window and saving it to a variable, so we don't have
        # to redo requests
        window_size = self.get_size()
        window_position = self.get_position()

        # making sure that the screenshot region isn't outside of the size of the window
        if x + width > window_size[0] or y + height > window_size[1]:
            raise OutOfBoundsInputError(f'The final end position of the region ({x + width}, {y + height})to take the screenshot of is outside the size of the window. {window_position} If you want to take a screenshot of more than one window, use your window manager\'s screenshot or screenshot_region methods.')

        # taking a screenshot and returning it
        return self.window_manager.screenshot_region(window_position[0] + x, window_position[1] + x, window_position[0] + width, window_position[1] + height)
