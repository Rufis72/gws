from abc import abstractmethod, ABCMeta
import struct
import time
import subprocess
from gws._errors import DependencyNotFound
from gws.window import BasicWindow
from typing import TYPE_CHECKING, Any, Generator
from PIL import Image
from io import BytesIO
import pyscreeze

if TYPE_CHECKING:
    from gws._typing import WindowLikeType, WindowLike

class GenericWindowManager(metaclass=ABCMeta):
    '''
    The base class for every WindowManager class.

    A WindowManager class is something that provides
    an API to interact with windows in the window manager
    that class is being implemented for.

    Or, as an example, a Quartz (the MacOS window manager) WindowManager
    class should interact with Quartz
    '''

    @abstractmethod
    def get_window_from_name(self, name: str, ignore_capitalization: bool = False, window_type: WindowLikeType = BasicWindow) -> WindowLike | None:
        '''Checks the name of every window, if the given name exactly
        matches the window name, a HyprlandWindow object is return of it.
        Otherwise, None is returned

        :param str name: The name to look for exact matches to
        :param bool ignore_capitalization: If capitalization should be ignored when looking for matches
        :param WindowLikeType window_type: The type of window to initialize from the name. By default is the BasicWindow'''
        ...

    @abstractmethod
    def get_window_from_regex(self, pattern: str, window_type: WindowLikeType = BasicWindow) -> WindowLike | None:
        '''Checks the name of every window for a match against the given pattern.
        If a match is found, a window object is returned of that window.
        
        :param str pattern: The regex pattern to check against
        :param WindowLikeType window_type: The type of window to initialize from the regex. By default is the BasicWindow
        '''
        ...

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

    def click(self, x: int, y: int, duration: float, button: str):
        '''Either left, middle, or right clicks at a given position for duration time.
        
        :param int x: The x position of where to click
        :param int y: the y position of where to click
        :param float duration: How long to click for
        :param str button: The type of click. Either 'left', 'middle', or 'right'.'''
        self.mouse_down(button, x, y)
        time.sleep(duration)
        self.mouse_up(button)

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

        :param str key: The key to press
        :param float duration: How long to hold the key
        '''
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

    @abstractmethod
    def screenshot(self) -> Image.Image:
        '''Takes a screenshot of all monitors. Returns it as a PIL Image object'''
        ...

    def screenshot_region(self, x: int, y: int, width: int, height: int) -> Image.Image:
        '''Takes a screenshot of a specific region on your computer. 
        The image is a rectangle from (x, y) to (x + width, y + height)

        It depends on the window manager, but typically (0, 0) is in the top left corner,
        and bigger x is more to the right, and bigger y is downward.
        This should be normalized across all window managers that it's top left is (0, 0),
        but if things are flipped, that's probably why. (either that or something is seriously
        broken)
        
        :param int x: The starting x for the rectangle
        :param int y: The starting y for the rectangle
        :param int width the width of the rectangle
        :param int height the height of the rectangle:'''
        ...

    def locate(
        self,
        needleImage: str | Image.Image | Any,
        haystackImage: str | Image.Image | Any,
        *,
        grayscale: bool | None = None,
        limit: int = 1,
        region: tuple[int, int, int, int] | None = None,
        step: int = 1,
        confidence: float = 0.999,
    ) -> pyscreeze.Box | None:
        '''This is a wrapper for pyscreeze.locateAll, so refer to there for documentation.
        Pyautogui also pretty much wraps pyscreeze, so they may have useful docs over there too.'''
        return pyscreeze.locate(needleImage, haystackImage, grayscale=grayscale, limit=limit, region=region, step=step, confidence=confidence)

    def locate_all(
        self,
        needleImage: str | Image.Image | Any,
        haystackImage: str | Image.Image | Any,
        grayscale: bool | None = None,
        limit: int = 10000,
        region: tuple[int, int, int, int] | None = None,
        step: int = 1,
        confidence: float = 0.999,
    ) -> Generator[pyscreeze.Box, None, None]:
        '''This is a wrapper for pyscreeze.locateAll, so refer to there for documentation.
        Pyautogui also pretty much wraps pyscreeze, so they may have useful docs over there too.'''
        return pyscreeze.locateAll(needleImage, haystackImage, grayscale=grayscale, limit=limit, region=region, step=step, confidence=confidence)

    def locate_on_screen(
        self,
        image: str | Image.Image | Any,
        minSearchTime: float = 0,
        *,
        grayscale: bool | None = None,
        limit: int = 1,
        region: tuple[int, int, int, int] | None = None,
        step: int = 1,
        confidence: float = 0.999,
    ) -> pyscreeze.Box | None:
        '''This is almost a wrapper for pyscreeze.locateAll, so refer to there for documentation.
        Pyautogui also pretty much wraps pyscreeze, so they may have useful docs over there too.
        The reason this is almost a wrapper, is because we use our own screenshot utility for wayland,
        but on non-wayland systems, we uses pyautogui's screenshot utility (pyscreeze).
        
        This function takes a screenshot of the screen, then finds and returns the first match it finds
        for a given image.'''
        # getting the screen
        desktop_screenshot = self.screenshot()

        # finding and returning any match we find
        return pyscreeze.locate(image, desktop_screenshot, grayscale=grayscale, limit=limit, region=region, step=step, confidence=confidence)

    def locate_all_on_screen(
        self,
        image: str | Image.Image | Any,
        *,
        grayscale: bool | None = None,
        limit: int = 10000,
        region: tuple[int, int, int, int] | None = None,
        step: int = 1,
        confidence: float = 0.999,
    ) -> Generator[pyscreeze.Box, None, None]:
        '''This is almost a wrapper for pyscreeze.locateAll, so refer to there for documentation.
        Pyautogui also pretty much wraps pyscreeze, so they may have useful docs over there too.
        The reason this is almost a wrapper, is because we use our own screenshot utility for wayland,
        but on non-wayland systems, we uses pyautogui's screenshot utility (pyscreeze).
        
        This function finds all of some image on the screen, and returns a list of the positions.
        How exact the match has to be is determined by confidence, which should be between 0 (anything
        matches) and 1 (only an exact pixel match matches).'''
        # getting the screen
        desktop_screenshot = self.screenshot()

        # returning what was found
        return self.locate_all(image, desktop_screenshot, grayscale, limit, region, step, confidence)

    def locate_center_on_screen(
        self,
        image: str | Image.Image | Any,
        *,
        minSearchTime: float = 0,
        grayscale: bool | None = None,
        limit=None,
        region: tuple[int, int, int, int] | None = None,
        step: int = 1,
        confidence: float = 0.999,
    ) -> pyscreeze.Point | None:
        '''This is almost a wrapper for pyscreeze.locateCenterOnScreen, so refer to there for documentation.
        Pyautogui also pretty much wraps pyscreeze, so they may have useful docs over there too.
        The reason this is almost a wrapper, is because we use our own screenshot utility for wayland,
        but on non-wayland systems, we uses pyautogui's screenshot utility (pyscreeze).
        
        This function is the same as locate_on_screen, but instead of returning the top left corner,
        it returns the center.'''
        # locating the image on the screen
        match_coords = self.locate_on_screen(image, minSearchTime, grayscale=grayscale, limit=limit, region=region, step=step, confidence=confidence)

        # if we couldn't find a match we return none
        if match_coords is None:
            return None
        # otherwise returning the center of the match
        else:
            return pyscreeze.center(match_coords)
        


class GenericWaylandWindowManager(GenericWindowManager):
    '''The base class for most Wayland compositors. It provides input and image capture support
    through wayland automation, but wayland automation may not support all compositors out of the box'''

    def __init__(self):
        # setting up wayland_automation
        import wayland_automation
        self.mouse = wayland_automation.Mouse()
        self.keyboard = wayland_automation.Keyboard()

    def get_monitor_data(self) -> list[dict[str, str | int | float]]:
        '''Returns the data from wayland-info -i zxdg_output_manager_v1, and parses it to
        be more usable'''
        # first we call wayland-info and get the data for the displays
        try:
            wayland_info_output = subprocess.run(['wayland-info', '-i', 'zxdg_output_manager_v1'], check=True, text=True, capture_output=True).stdout
        except subprocess.CalledProcessError as e:
            # if it's wayland-info not found, we say that the dependency couldn't be found.
            # otherwise we just pass the error along to the user
            if str(e.stderr).__contains__('wayland-info: command not found'):
                raise DependencyNotFound(f'An error was encountered when trying to run wayland-info, which appears to be related to it not being on PATH/not being installed. Do you have wayland-info installed? This is the given error message: \n{e}')
            else:
                raise Exception(f'Got an error when running "wayland-info -i zxdg_output_manager": {e}')
            
        # parsing the screen data
        # first we get the interface data for each monitor
        # we remove the first one because that's before the interface. So it's ['', '...', ...]
        # and we want ['...', ...]
        monitor_interfaces_data: list[str] = wayland_info_output.split('xdg_output_v1')[1:]

        # next we go through each monitor's data and turn it into a dict
        monitor_data: list[dict[str, int | str | float]] = []
        for monitor_text in monitor_interfaces_data:
            # cleaning up any empty lines above and below
            monitor_text = monitor_text.strip()

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
                elif line.__contains__('description'):
                    monitor_data_dict['description'] = line.split(': ')[1].strip('\'')

                # if it's the position data
                elif line.__contains__('logical_x: '):
                    # this one's a little different, since there's
                    # multiple values on one line
                    # I couldn't think of a better name for the variable,
                    # but this is just the values split up
                    value_text = line.rstrip(',').split(', ')

                    # the first in the values text is the x, second is y, third is scale
                    monitor_data_dict['x'] = int(value_text[0].lstrip('logical_x: '))
                    monitor_data_dict['y'] = int(value_text[1].lstrip('logical_y: '))
                
                # if it's the width and such
                elif line.__contains__('logical_width: ') and not line.__contains__('physical'):
                    value_text = line.rstrip(',').split(', ')

                    # the first in the values text is the width, height, then rate
                    monitor_data_dict['width'] = int(value_text[0].lstrip('logical_width: '))
                    monitor_data_dict['height'] = int(value_text[1].lstrip('logical_height: '))

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
            x_data.append(monitor.get('width') + monitor.get('x'))
            y_data.append(monitor.get('height') + monitor.get('y'))

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
        try:
            subprocess.run(['wtype', '-P', key], check=True)
        except subprocess.CalledProcessError as e:
            if str(e.stderr).__contains__('wtype: command not found'):
                raise DependencyNotFound(f'An error was encountered when trying to run wtype, which appears to be related to it not being on PATH/not being installed. Do you have wtype installed? This is the given error message: \n{e}')
            else:
                raise Exception(f'Got an error when running "wtype -P {key}": {e}')

    def key_up(self, key: str):
        try:
            subprocess.run(['wtype', '-p', key])
        except subprocess.CalledProcessError as e:
            if str(e.stderr).__contains__('wtype: command not found'):
                raise DependencyNotFound(f'An error was encountered when trying to run wtype, which appears to be related to it not being on PATH/not being installed. Do you have wtype installed? This is the given error message: \n{e}')
            else:
                raise Exception(f'Got an error when running "wtype -p {key}": {e}')
    
    def screenshot_region(self, x: int, y: int, width: int, height: int) -> Image.Image:
        try:
            grim_output = subprocess.run(['grim', '-g', f'{x},{y} {width}x{height}', '-'], stdout=subprocess.PIPE, check=True).stdout
        except FileNotFoundError as e:
            raise DependencyNotFound(f'Could not find grim, which is required for taking screenshots. Is it on PATH/installed?')
        except subprocess.CalledProcessError as e:
            raise Exception(f'Got this error when running \'grim -g "{x},{y} {width}x{height}" - \': {e}')
        
        # turning the png (or other file format) output into an image object
        return Image.open(BytesIO(grim_output)).convert('RGBA')

    
    def screenshot(self) -> Image.Image:
        try:
            grim_output = subprocess.run(['grim', '-'], stdout=subprocess.PIPE, check=True).stdout
        except FileNotFoundError as e:
            raise DependencyNotFound(f'Could not find grim, which is required for taking screenshots. Is it on PATH/installed?')
        except subprocess.CalledProcessError as e:
            raise Exception(f'Got this error when running \'grim -\': {e}')
        
        # turning the png (or other file format) output into an image object
        return Image.open(BytesIO(grim_output)).convert('RGBA')
            


       

class GenericNonWaylandWindowManager(GenericWindowManager):
    def key_down(self, key: str):
        import pyautogui
        pyautogui.keyDown(key)

    def key_up(self, key: str):
        import pyautogui
        pyautogui.keyUp(key)

    def mouse_down(self, button: str, x: int | None = None, y: int | None = None):
        import pyautogui
        pyautogui.mouseDown(x, y, button)

    def mouse_up(self, button: str):
        import pyautogui
        pyautogui.mouseUp(button=button)

    def move_mouse(self, x: int, y: int):
        import pyautogui
        pyautogui.moveTo(x, y)

    def screenshot(self) -> Image.Image:
        import pyautogui
        return pyautogui.screenshot()
    
    def screenshot_region(self, x: int, y: int, width: int, height: int) -> Image.Image:
        import pyautogui
        return pyautogui.screenshot(region=(x, y, width, height))
