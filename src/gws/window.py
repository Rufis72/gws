from typing import TYPE_CHECKING, Generator, Any
from gws._errors import OutOfBoundsInputError
from PIL import Image
from pyscreeze import Box, Point
from math import floor, ceil

if TYPE_CHECKING:
    from gws._typing import WindowManagerLike

class BasicWindow:
    '''The basic window object. Represents a window for any WindowManager'''

    # not sure where to put this, so I'm putting it here
    # NOTE: When a method takes input that could be scaled, it's scaling logic
    # should be ceil(input / scale), otherwise if it outputs scaled data, it
    # should be floor(input * scale)

    def __init__(self, window_manager: WindowManagerLike, id: str):
        '''
        :param WindowManagerLike window_manager: The WindowManager object for the host machine's window manager
        :param str id: The ID of the window this object will represent'''
        self.window_manager: WindowManagerLike = window_manager
        self.id: str = id
        self.macro_resolution: tuple[int, int] | None = None

    def click(self, x: int, y: int, button: str, duration: float = 0.09, bypass_out_of_bounds_check: bool = False, scale: bool = True):
        '''Clicks at a position relative to the window.
        Raises an error if the click is out of bounds of the window.
        
        :param int x: The x coord to click at
        :param int y: The y coord to click at
        :param float duration: The length to click for
        :param str button: The button to click. Either 'left' 'middle' or 'right'.
        :param bool bypass_out_of_bounds_check: If we should bypass checking if the click is out of bounds.
        :param bool scale: If the click should be scaled from the macro resolution to the actual window resolution, if macro resolution is set. '''
        # first we get the offset (the window's position)
        window_position = self.window_manager.get_position_of_window(self.id)

        # then we calculate where to click
        click_pos: tuple[int, int] = (x + window_position[0], y + window_position[1])

        # scaling it if we're supposed to
        if scale:
            # getting the scale
            # we get window_size seperately because we might use it later
            window_size = self.get_size()
            scale_x, scale_y = self.calculate_scale(window_size)

            # scaling the click position
            # we divide here because multiplication is for
            # real_position -> scaled_internal_handling_position, and we wanna go
            # scaled_internal_handling_positiion -> real_position
            click_pos = (ceil(click_pos[0] * scale_x), ceil(click_pos[1] * scale_y))

        # making sure the click isn't out of bounds (if enabled)
        if not bypass_out_of_bounds_check:
            # if we didn't get the window_size earlier from scaling
            if not scale:
                window_size = self.get_size()
            if click_pos[0] > window_size[0]:
                raise OutOfBoundsInputError(f'Click at ({click_pos[0]}, {click_pos[1]}) has a bigger x than the window\'s size ({window_size[0]}, {window_size[1]})')
            elif click_pos[1] > window_size[1]:
                raise OutOfBoundsInputError(f'Click at ({click_pos[0]}, {click_pos[1]}) has a bigger y than the window\'s size ({window_size[0]}, {window_size[1]})')

        # clicking
        self.window_manager.click(*click_pos, duration, button)

    def set_macro_resolution(self, width: int, height: int):
        '''Sets the macro resolution. You can think of this as the
        size "canvas" the macro is designed to "paint". 
        This automatically sets the scale for the macro, so
        you could design for a, for example, 1000x1000 window,
        and click at the bottom left most spot ((1000, 1000) in this
        case), and even if the window isn't 1000x1000, it'll scale it
        so that you're still clicking in the bottom left corner.
        Or if you wanted to click at (200, 0), it'll scale that
        too.'''
        self.macro_resolution = (width, height)

    def calculate_scale(self, window_size: tuple[int, int]):
        '''Returns the scale to multiply by so that points
        are relatively in the same position as the window size
        the macro was designed for.
        
        This means if the macro was designed for a 1000x1000
        window, but the window is currently 500x500, the scale
        would be (0.5, 0.5).
        
        If there is no macro resolution set, it defaults to (1, 1)
        
        This is different then get_scale, as calculate_scale doens't
        get the window size for you, which is useful if you've already
        got that, and you don't want to re-get it. (So optimization
        pretty much)'''
        # if there's no macro resolution
        if self.macro_resolution is None:
            return (1, 1)
        else:
            return (window_size[0] / self.macro_resolution[0], window_size[0] / self.macro_resolution[1])

    def get_scale(self) -> tuple[float, float]:
        '''Returns the scale to multiply by so that points
        are relatively in the same position as the window size
        the macro was designed for.
        
        This means if the macro was designed for a 1000x1000
        window, but the window is currently 500x500, the scale
        would be (0.5, 0.5).
        
        If there is no macro resolution set, it defaults to (1, 1)
        
        This is different then calculate_scale, as get_scale gets all
        values for you, whereas calculate_scale requires you
        to pass the window_size, which can be useful when you already
        have that data. (So optimzation pretty much)'''
        # if there's no macro resolution
        if self.macro_resolution is None:
            return (1, 1)
        else:
            window_size = self.get_size()
            return self.calculate_scale(window_size)

    def scale_point(self, point: tuple[int, int], scale: tuple[float, float]) -> tuple[int, int]:
        '''Scales a point using the macro resolution. If there is no
        macro resolution, it just returns the point, otherwise
        it multiplies the point's x by the scale gotten from the macro resolution.
        If the point is a float, it's floored.
        
        That means if your point is (1000, 0) and your window is a 500x500 window,
        but the macro was intended for a 1000x1000 window, it'll figure out the scale
        is (0.5, 0.5), then multiply your point by it'''
        return (
            floor(point[0] * scale[0]),
            floor(point[1] * scale[1])
        )

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
    
    def screenshot_region(self, x: int, y: int, width: int, height: int, scale: bool = True) -> Image.Image:
        '''Takes a screenshot of a region of the window, and returns it as a Pillow Image object. 
        If the region would be outside of the window, a OutOfBoundsInputError is raised.
        
        If you want to take a screenshot that spans more than window, use your window manager's screenshot 
        or screenshot_region methods instead.
        :param int x: The starting x for the screenshot region
        :param int y: The starting y for the screenshot region
        :param int width: the width of the screenshot region
        :param int height: the height of the screenshot region
        :param bool scale: If the given coordinates should be scaled based off macro resolution if given'''
        # getting data about the window and saving it to a variable, so we don't have
        # to redo requests
        window_size = self.get_size()
        window_position = self.get_position()

        # scaling stuff if we're supposed to
        if scale:
            # getting the scale
            scale_x, scale_y = self.calculate_scale(window_size)

            # adjusting the x, y, width, and height based of the scale
            # NOTE: The reason we're turning scale from an (int, int) into 
            # two different variables and back again is because I named
            # the scale parameter, and I'm too lazy to change it
            x = floor(x * scale_x)
            y = floor(y * scale_y)
            width = floor(width * scale_x)
            height = floor(height * scale_y)

        # making sure that the screenshot region isn't outside of the size of the window
        if x + width > window_size[0] or y + height > window_size[1]:
            raise OutOfBoundsInputError(f'The final end position of the region ({x + width}, {y + height})to take the screenshot of is outside the size of the window. {window_position} If you want to take a screenshot of more than one window, use your window manager\'s screenshot or screenshot_region methods.')

        # taking a screenshot and returning it
        return self.window_manager.screenshot_region(window_position[0] + x, window_position[1] + y, width, height)
    
    def locate_on_window(
        self,
        image: str | Image.Image | Any,
        minSearchTime: float = 0,
        *,
        grayscale: bool | None = None,
        limit: int = 1,
        region: tuple[int, int, int, int] | None = None,
        step: int = 1,
        confidence: float = 0.999,
        scale: bool = True,
    ) -> Box | None:
        '''The logic here is incredibly similar to it's underlying
        library pyscreeze, so check there for docs. Pyautogui also
        uses pyscreeze under the hood, and pretty much just wraps it
        so you can check their docs over there too.
        
        This function locates and returns the first match of
        the given image it finds in a screenshot of the window.
        How well it has to match can be changed by changing 
        confidence (0 is anything matches 1 is exact pixel 
        to pixel match)
        
        :param bool scale: If the given output should be scaled according to the macro resolution (if set)'''
        # capturing the window
        window_screenshot = self.screenshot()

        # finding a match for the image
        match = self.window_manager.locate(image, window_screenshot, grayscale=grayscale, limit=limit, region=region, step=step, confidence=confidence)

        # if we couldn't find a match, returning None
        if match is None:
            return None

        # if we're supposed to scale it, scaling it
        if scale:
            # getting the scale
            scale_x, scale_y = self.get_scale()

            # calculating and returning the scaled box
            # we divide by the scale here, because multiplication is for turning
            # coords for the macro resolution to the actual resolution
            # so division is doing the opposite
            # which is what we're doin ghere
            return Box(
                ceil(match.left / scale_x),
                ceil(match.top / scale_y),
                ceil(match.width / scale_x),
                ceil(match.height / scale_y)
            )
        
        # otherwise we just return the box we just got
        return match

    def locate_all_on_window(
        self,
        image: str | Image.Image | Any,
        *,
        grayscale: bool | None = None,
        limit: int = 10000,
        region: tuple[int, int, int, int] | None = None,
        step: int = 1,
        confidence: float = 0.999,
        scale: bool = True
    ) -> Generator[Box, None, None]:
        ''':param bool scale: If the given output should be scaled according to the macro resolution (if set)'''
        # capturing the window
        window_screenshot = self.screenshot()

        # finding all matches for the image
        matches = self.window_manager.locate_all(image, window_screenshot, grayscale=grayscale, limit=limit, region=region, step=step, confidence=confidence)

        # if we're supposed to scale it, scaling it
        if scale:
            # getting the scale
            scale_x, scale_y = self.get_scale()

            # going through each match and scaling it
            scaled_matches: list[Box] = []

            for match in matches:

                # calculating and returning the scaled box
                # we divide by the scale here, because multiplication is for turning
                # coords for the macro resolution to the actual resolution
                # so division is doing the opposite
                # which is what we're doin ghere
                scaled_matches.append(Box(
                    ceil(match.left / scale_x),
                    ceil(match.top / scale_y),
                    ceil(match.width / scale_x),
                    ceil(match.height / scale_y)
                ))

            return (y for y in scaled_matches)
        # otherwise we just return the matches
        else:
            # why is there the for y in matches bit?
            # it's because the original API for pyscreeze does it, and
            # we're trying to have pretty close parity
            return matches

    def locate_center_on_window(
        self,
        image: str | Image.Image | Any,
        *,
        minSearchTime: float = 0,
        grayscale: bool | None = None,
        limit=None,
        region: tuple[int, int, int, int] | None = None,
        step: int = 1,
        confidence: float = 0.999,
        scale: bool = True
    ) -> Point | None:
        ''':param bool scale: If the given output should be scaled according to the macro resolution (if set)'''
        # capturing the window
        window_screenshot = self.screenshot()

        # finding a match for the image
        match = self.window_manager.locate_center(image, window_screenshot, grayscale=grayscale, limit=limit, region=region, step=step, confidence=confidence)

        # if we couldn't find a match, returning None
        if match is None:
            return None

        # if we should scale the output, doing that
        if scale:
            # getting the scale
            scale_x, scale_y = self.get_scale()

            # returning the scaled point
            # we divide by the scale here, because multiplication is for turning
            # coords for the macro resolution to the actual resolution
            # so division is doing the opposite
            # which is what we're doin ghere
            return Point(floor(match.x / scale_x), floor(match.y / scale_y))
        else:
            return match
