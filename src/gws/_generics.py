from abc import abstractmethod
import struct
import time
import subprocess
from gws._errors import DependencyNotFound

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

    def press(self, key: str, duration: float):
        '''Presses and holds a key for duration time.
  

    def get_position_of_window(self, id) -> tuple[int, int]:
        # getting the data of all windows
        window_data = self._get_window_data(id)

        # getting the position
        window_position: tuple[int, int] = window_data.get('at') 
        
        # returning the position
        return window_position
    
    def get_size_of_window(self, id) -> tuple[int, int]:
        # getting the all window data
        window_data = self._get_window_data(id)

        # getting the size
        window_size: tupl      
        If you want to use modifiers, you can type them, so left control is 'lctrl',
        or right shift as 'rshift'. If you want to add more modifiers while pressing
        a key, then you should use key down and up, as we currently don't support that. Sorry!
        
        :param str key: The key to press
        :param float duration: How long to hold the key'''
        self.key_down(key)
        time.sleep(duration)
        self.key_up(key)

    def typewrite(self, text: str, hold_duration: float, interval: float):
        '''Types characters, holding each one for a given time, and with a given duration between each key press.
        
        :param str text: The text to typewrite
        :param float hold_duration: The duration to hold each key
        :param float interval: The duration to wait between each key press'''
        for i, char in enumerate(text):
            # pressing the key
            self.press(char, hold_duration)

            # waiting the interval between each key press unless this
            # is the last character
            if not i == len(text) + 1:
                time.sleep(interval)
        


class GenericWaylandWindowManager(GenericWindowManager):
    '''The base class for most Wayland compositors. It provides input and image capture support
    through wayland automation, but wayland automation may not support all compositors out of the box'''

    def __init__(self):
        # setting up wayland_automation
        import wayland_automation
        self.mouse = wayland_automation.Mouse()
        self.keyboard = wayland_automation.Keyboard()

    def get_monitor_data(self) -> list[dict[str, str | int | float]]:
        '''Returns the data from wayland-info -i wl_output, and parses it to
        be more usable'''
        # first we call wayland-info and get the data for the displays
        try:
            wayland_info_output = subprocess.run(['wayland-info', '-i', 'wl_output'], check=True, text=True, capture_output=True).stdout
        except subprocess.CalledProcessError as e:
            # if it's wayland-info not found, we say that the dependency couldn't be found.
            # otherwise we just pass the error along to the user
            if str(e.stderr).__contains__('wayland-info: command not found'):
                raise DependencyNotFound(f'An error was encountered when trying to run wayland-info, which appears to be related to it not being on PATH/not being installed. Do you have wayland-info installed? This is the given error message: \n{e}')
            else:
                raise Exception(f'Got an error when running "wayland-info -i wl_output": {e}')
            
        # parsing the screen data
        # first we get the interface data for each monitor
        monitor_interfaces_data: list[str] = wayland_info_output.split('interface: \'wl_output\'')

        # next we go through each monitor's data and turn it into a dict
        monitor_data: list[dict[str, int | str | float]] = []
        for monitor_text in monitor_interfaces_data:
            # making a dict for this monitor
            monitor_data_dict = {}

            # we exclude the first line because it's just the remaining bit of the header
            # so it's just version:  [version], name: [name]
            for line in monitor_text.split('\n')[1:]:
                # stripping any space before it, and any new lines after, and just general fluff
                line = line.lstrip().rstrip('\n').rstrip()

                # if it's the name
                if line.__contains__('name'):
                    monitor_data_dict['name'] = line.split(': ')[1]

                # if it's the description
                if line.__contains__('description'):
                    monitor_data_dict['description'] = line.split(': ')[1]

                # if it's the position data
                if line.__contains__('x: '):
                    # this one's a little different, since there's
                    # multiple values on one line
                    # I couldn't think of a better name for the variable,
                    # but this is just the values split up
                    value_text = line.rstrip(',').split(', ')

                    # the first in the values text is the x, second is y, third is scale
                    monitor_data_dict['x'] = int(value_text[0].lstrip('x: '))
                    monitor_data_dict['y'] = int(value_text[1].lstrip('y: '))
                    monitor_data_dict['scale'] = float(value_text[2].lstrip('scale: '))

                # if it's the physical dimensions
                if line.__contains__('physical_width: '):
                    value_text = line.rstrip(',').split(', ')

                    # the first in the values text is the physical width, then physical height
                    monitor_data_dict['physical_width'] = value_text[0].lstrip('physical_width: ')
                    monitor_data_dict['physical_height'] = value_text[1].lstrip('physical_height: ')

                # if it's the subpixel orientation and output_transform
                if line.__contains__('subpixel_orientation'):
                    value_text = line.rstrip(',').split(', ')

                    # the first in the values text is the subpixel orientation, then output_transform
                    monitor_data_dict['subpixel_orientation'] = value_text[0].lstrip('subpixel_orientation: ')
                    monitor_data_dict['output_transform'] = value_text[1].lstrip('output_transform: ')

                # if it's the width and such
                if line.__contains__('width: ') and not line.__contains__('physical'):
                    value_text = line.rstrip(',').split(', ')

                    # the first in the values text is the width, height, then refresh rate
                    monitor_data_dict['width'] = int(value_text[0].lstrip('width: ').rstrip(' px'))
                    monitor_data_dict['height'] = int(value_text[1].lstrip('height: ').rstrip(' px'))
                    monitor_data_dict['refresh_rate'] = float(value_text[2].lstrip('refresh: ').rstrip(' Hz'))

            # adding the finished monitor dict to the list
            monitor_data.append(monitor_data_dict)

        # returning the final data
        return monitor_data

    def get_screen_space_rectangle(self) -> tuple[int, int]:
        '''This takes however the user has arranged their screens
        and their sizes and turns it into one big rect for the total screen size.
        
        As an example, if the user has two 1920x1080 monitors, one at (0, 0)
        and one positioned at (1920, 0), then the total screen size would be
        3840x1080. We get this by taking the offset for each monitor, and adding it's size.
        So, the first is (1920, 1080) + (0, 0) = (1920, 1080).
        The second is (1920, 1080) + (1920, 0) = (3840, 1080). We take the biggest x and y
        we find, and that's the output.'''
        # getting the monitor info
        monitor_info = self.get_monitor_data()

        # going through and adding the offset the size for each montiro
        # also factoring in scale
        # then adding it to a list to get the max of
        x_data: list[int] = []
        y_data: list[int] = []
        for monitor in monitor_info:
            x_data.append((monitor.get('width') * monitor.get('scale')) + monitor.get('x'))
            y_data.append((monitor.get('height') * monitor.get('scale')) + monitor.get('y'))

        # returning the biggest of both groups
        return (max(x_data), max(y_data))



    def _get_mouse_key_code(self, button: str):
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
        button_code = self._get_mouse_key_code(button)

        # then we move the mouse if x and y is specificed
        if x is not None and y is not None:
            self.move_mouse(x, y)

        # then we send a press message
        self.mouse.send_message(
            self.mouse.current_virtual_pointer_id, 
            2, 
            struct.pack(f"{self.mouse.endianness}III", 0, button_code, 0)
        )

        # one frame after, we tell wayland the message is done
        self.mouse.send_message(self.mouse.current_virtual_pointer_id, 4, b'') 

    def mouse_down(self, button: str, x: int | None = None, y: int | None = None):
        # first we get the key code
        button_code = self._get_mouse_key_code(button)

        # then we move the mouse if x and y is specificed
        if x is not None and y is not None:
            self.move_mouse(x, y)

        # then we send a press message
        self.mouse.send_message(
            self.mouse.current_virtual_pointer_id, 
            2, 
            struct.pack(f"{self.mouse.endianness}III", 0, button_code, 1)
        )

        # one frame after, we tell wayland the message is done
        self.mouse.send_message(self.mouse.current_virtual_pointer_id, 4, b'') 

    def move_mouse(self, x: int, y: int):
        # getting the resolution
        # not sure what it means, but wayland-automations does it
        # it internally in mouse_controller.py
        height, width = self.get_screen_space_rectangle()
        self.mouse.send_motion_absolute(x, y, 2560 + 1920, 1440)

    def key_down(self, key: str):
        self.keyboard.keyDown(key)

    def key_up(self, key: str):
        self.keyboard.keyUp(key)
