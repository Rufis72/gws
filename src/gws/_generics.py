from abc import abstractmethod
from gws._typing import WindowLike, GetWindowFn
from typing import ClassVar, Final
import wayland_automation
import pyautogui

class GenericWindowManager:
    WAYLAND: ClassVar[bool]

    def __init__(self, id):
        '''
        The base class for every WindowManager class.

        A WindowManager class is something that provides
        an API to interact with windows in the window manager
        that class is being implemented for.

        Or, without fancy wording, a Quartz (the MacOS window manager) WindowManager
        class should interact with Quartz
        '''

    @abstractmethod 
    def get_name_of_window(self, id: str) -> str:
        '''Returns the current name of a window from it's ID
        
        :param str id: The ID to find the window by'''
        ...

    @abstractmethod
    def get_position_of_window(self, id: str) -> tuple[int, int]:
        '''Returns the absolute position of a window from it's ID
        
        Note: for people implementing this for wayland compositors, good luck!
        :param str id: The ID to find the window by'''
        ...
    
    @abstractmethod
    def get_size_of_window(self, id: str) -> tuple[int, int]:
        '''Returns the size of the window from it's ID
        
        :param str id: The ID to find the window by'''
        ...

    @abstractmethod
    def click(self, x: int, y: int, duration: float | int, button: str):
        '''Either left, middle, or right clicks at a given position for duration time.
        
        :param int x: The x position of where to click
        :param int y: the y position of where to click
        :param float | int duration: How long to click for
        :param str button: The type of click. Either 'left', 'middle', or 'right'.'''

    @abstractmethod
    def mouse_down(self, button: str):
        '''Presses a mouse button down.
        
        :param str button: The mouse button to press down. Either 'middle', 'left', or 'right'.'''

    @abstractmethod
    def mouse_up(self, button: str):
        '''Unpresses a mouse button.
        
        :param str button: The mouse button to release. Either 'middle', 'left', or 'right'.'''

    @abstractmethod
    def key_down(self, key: str):
        '''Presses a keyboard button
        
        :param str key: The key to press. Can be a typical character on the keyboard like 'a' or 'V', or a special character like 'enter'.'''
    
    @abstractmethod
    def key_up(self, key: str):
        '''Releases a keyboard button
        
        :param str key: The key to release. Can be a typical character on the keyboard like 'a' or 'V', or a special character like 'enter'.'''

    @abstractmethod
    def typewrite(self, text: str, hold_duration: float, spacing_duration: float):
        '''Types characters, holding each one for a given time, and with a given duration between each key press.
        
        :param str text: The text to typewrite
        :param float hold_duration: The duration to hold each key
        :param float spacing_duration: The duration to wait between each key press'''
