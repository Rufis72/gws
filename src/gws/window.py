from gws._typing import WindowManagerLike
from gws._errors import OutOfBoundsInputError

class BasicWindow:
    '''The basic window object. Represents a window for any WindowManager'''

    def __init__(self, window_manager: WindowManagerLike, id: str):
        '''
        :param WindowManagerLike window_manager: The WindowManager object for the host machine's window manager
        :param str id: The ID of the window this object will represent'''
        self.window_manager: WindowManagerLike = window_manager
        self.id: str = id

    def click_at(self, x: int, y: int, button: str, duration: float = 0.09, bypass_out_of_bounds_check: bool = False):
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
