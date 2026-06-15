from abc import abstractmethod
from gws._typing import WindowLike, GetWindowFn

class GenericWindow:
    def __init__(self, id):
        '''
        Initialises a window from it's id, and a function to get
        the window for the window manager the system is using

        :param int id: The ID used to identify the window
        '''
        self.id: str = id

    @abstractmethod 
    def get_name(self) -> str:
        '''Returns the current name of the window'''
        ...

    @abstractmethod
    def get_position(self) -> tuple[int, int]:
        '''Returns the absolute position of the window
        
        Note: for people implementing this for wayland compositors, good luck!'''
        ...
    
    @abstractmethod
    def get_size(self) -> tuple[int, int]:
        '''Returns the size of the window'''
        ...

    @abstractmethod
    def click(self, x: int, y: int, duration: float | int, type: str):
        '''Either left, middle, or right clicks at a given position for duration time.
        
        :param int x: The x position of where to click
        :param int y: the y position of where to click
        :param float | int duration: How long to click for
        :param str type: The type of click. Either 'left', 'middle', or 'right'.'''
        ...

    @abstractmethod
    def mouse_down(self, type: str):
        '''Presses a mouse button down.
        
        :param str type: The mouse button to press down. Either 'middle', 'left', or 'right'.'''
        ...

    @abstractmethod
    def mouse_up(self, type: str):
        '''Unpresses a mouse button.
        
        :param str type: The mouse button to release. Either 'middle', 'left', or 'right'.'''
        ...

    @abstractmethod
    def key_down(self, key: str):
        '''Presses a keyboard button
        
        :param str key: The key to press. Can be a typical character on the keyboard like 'a' or 'V', or a special character like 'enter'.'''
        ...
    
    @abstractmethod
    def key_up(self, key: str):
        '''Releases a keyboard button
        
        :param str key: The key to release. Can be a typical character on the keyboard like 'a' or 'V', or a special character like 'enter'.'''
        ...

    @abstractmethod
    def typewrite(self, text: str, hold_duration: float, spacing_duration: float):
        '''Types characters, holding each one for a given time, and with a given duration between each key press.
        
        :param str text: The text to typewrite
        :param float hold_duration: The duration to hold each key
        :param float spacing_duration: The duration to wait between each key press'''
        ...