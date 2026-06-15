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

