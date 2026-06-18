from abc import abstractmethod
import struct
import time

class GenericWindowManager:
    '''
    The base class for every WindowManager class.

    A WindowManager class is something that provides
    an API to interact with windows in the window manager
    that class is being implemented for.

    Or, as an example, a Quartz (the MacOS window manager) WindowManager
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
    def move_mouse(self, x: int, y: int):
        '''Moves the mouse to an absolute position on the screen
        
        :param int x: The absolute x position to move the mouse to
        :param int y: The absolute y position to move the mouse to'''
        ...

    def _move_mouse_non_wayland(self, x: int, y: int):
        import pyautogui
        pyautogui.moveTo(x, y)

    def click(self, x: int, y: int, duration: float, button: str):
        '''Either left, middle, or right clicks at a given position for duration time.
        
        :param int x: The x position of where to click
        :param int y: the y position of where to click
        :param float duration: How long to click for
        :param str button: The type of click. Either 'left', 'middle', or 'right'.'''
        self.mouse_down(button, x, y)
        time.sleep(duration)
        self.mouse_up(button)

    def _click_non_wayland(self, x: int, y: int, duration: float, button: str):
        '''Either left, middle, or right clicks at a given position for duration time.

        This is the non-wayland speciifc version, and will crash if run on a system running wayland
        
        :param int x: The x position of where to click
        :param int y: the y position of where to click
        :param float duration: How long to click for
        :param str button: The type of click. Either 'left', 'middle', or 'right'.'''
        import pyautogui
        pyautogui.click(x, y, duration=duration, button=button)

    @abstractmethod
    def mouse_down(self, button: str, x: int | None = None, y: int | None = None):
        '''Presses a mouse button down.

        Takes x and y, but can be left blank if you just wanna
        use the current mouse position
        
        :param str button: The mouse button to press down. Either 'middle', 'left', or 'right'.
        :param int x: The x that the input is at. If not specified is wherever the mouse currently is
        :param int y: The y that the input is at. If not specified is wherever the mouse currently is'''
        ...

    @abstractmethod
    def mouse_up(self, button: str):
        '''Presses a mouse button down.
        Takes x and y, but can be left blank if you just wanna
        use the current mouse position
        
        :param str button: The mouse button to press down. Either 'middle', 'left', or 'right'.
        :param int x: The x that the input is at. If not specified is wherever the mouse currently is
        :param int y: The y that the input is at. If not specified is wherever the mouse currently is'''
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


class GenericWaylandWindowManager(GenericWindowManager):
    '''The base class for most Wayland compositors. It provides input and image capture support
    through wayland automation, but wayland automation may not support all compositors out of the box'''

    def __init__(self):
        # setting up wayland_automation
        import wayland_automation
        self.wayland_mouse = wayland_automation.Mouse()
        self.wayland_keyboard = wayland_automation.Keyboard()

    def _get_wayland_mouse_key_code(self, button: str):
        if button.lower() == 'left':
            return 0x110
        elif button.lower() == 'right':
            return 0x111
        elif button.lower() == 'middle':
            return 0x112
        else:
            return None

    def mouse_up(self, button: str, x: int | None = None, y: int | None = None):
        # first we get the key code
        button_code = self._get_wayland_mouse_key_code(button)

        # then we move the mouse if x and y is specificed
        if x is not None and y is not None:
            self.move_mouse(x, y)

        # then we send a press message
        self.wayland_mouse.send_message(
            self.wayland_mouse.current_virtual_pointer_id, 
            2, 
            struct.pack(f"{self.wayland_mouse.endianness}III", 0, button_code, 0)
        )

        # one frame after, we tell wayland the message is done
        self.wayland_mouse.send_message(self.wayland_mouse.current_virtual_pointer_id, 4, b'') 

    def mouse_down(self, button: str, x: int | None = None, y: int | None = None):
        # first we get the key code
        button_code = self._get_wayland_mouse_key_code(button)

        # then we move the mouse if x and y is specificed
        if x is not None and y is not None:
            self.move_mouse(x, y)

        # then we send a press message
        self.wayland_mouse.send_message(
            self.wayland_mouse.current_virtual_pointer_id, 
            2, 
            struct.pack(f"{self.wayland_mouse.endianness}III", 0, button_code, 1)
        )

        # one frame after, we tell wayland the message is done
        self.wayland_mouse.send_message(self.wayland_mouse.current_virtual_pointer_id, 4, b'') 

    def move_mouse(self, x: int, y: int):
        from wayland_automation.utils.screen_resolution import get_resolution

        # getting the resolution
        # not sure what it means, but wayland-automations does it
        # it internally in mouse_controller.py
        height, width = get_resolution()
        self.wayland_mouse.send_motion_absolute(x, y, int(height), int(width))
