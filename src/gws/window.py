from typing import TYPE_CHECKING, Generator, Any
from gws._errors import OutOfBoundsInputError
from PIL import Image
from pyscreeze import Box, Point
from math import ceil, lcm
from PIL.Image import Resampling

if TYPE_CHECKING:
    from gws._typing import WindowManagerLike

class BasicWindow:
    '''The basic window object. Represents a window for any WindowManager'''

    # not sure where to put this, so I'm putting it here
    # NOTE: When a method takes input that could be scaled, it's scaling logic
    # should be input / scale, otherwise if it outputs scaled data, it
    # should be input * scale

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
        click_pos = (0, 0)

        # first, we set click_pos to it's x and y relative
        # to the window
        # if we're supposed to scale that, we do
        # otherwise, we don't
        # scaling it
        if scale:
            # getting the scale
            # we get window_size seperately because we might use it later
            window_size = self.get_size()
            scale_x, scale_y = self.calculate_scale(window_size)

            # scaling the click position
            # we divide here because multiplication is for
            # real_position -> scaled_internal_handling_position, and we wanna go
            # scaled_internal_handling_positiion -> real_position
            click_pos = self.scale_point((x, y), (scale_x, scale_y))

        # not scaling it
        else:
            click_pos = (x, y)

        # then we add the window's offset (it's position)
        click_pos = (click_pos[0] + window_position[0], click_pos[1] + window_position[1])

        # making sure the click isn't out of bounds (if enabled)
        if not bypass_out_of_bounds_check:
            # if we didn't get the window_size earlier from scaling
            if not scale:
                window_size = self.get_size()
            if click_pos[0] > window_size[0] + window_position[0]:
                raise OutOfBoundsInputError(f'Click at ({click_pos[0]}, {click_pos[1]}) has a bigger x than the window\'s size ({window_size[0]}, {window_size[1]})')
            elif click_pos[1] > window_size[1] + window_position[1]:
                raise OutOfBoundsInputError(f'Click at ({click_pos[0]}, {click_pos[1]}) has a bigger y than the window\'s size ({window_size[0]}, {window_size[1]})')

        # clicking
        self.window_manager.click(*click_pos, duration, button)

    def set_macro_resolution(self, width: int, height: int):
        '''Sets the macro resolution. You can think of this as the
        size "canvas" the macro is designed to "paint". 
        This automatically sets the scale for the macro, so
        you could design for a, for example, 1000x1000 window,
        and click at the bottom left most spot ((0, 1000) in this
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
            return (window_size[0] / self.macro_resolution[0], window_size[1] / self.macro_resolution[1])

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
        If the point is a float, it's ceiled.
        
        That means if your point is (1000, 0) and your window is a 500x500 window,
        but the macro was intended for a 1000x1000 window, it'll figure out the scale
        is (0.5, 0.5), then multiply your point by it'''
        return (
            ceil(point[0] * scale[0]),
            ceil(point[1] * scale[1])
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
            x = ceil(x * scale_x)
            y = ceil(y * scale_y)
            width = ceil(width * scale_x)
            height = ceil(height * scale_y)

        # making sure that the screenshot region isn't outside of the size of the window
        if x + width > window_size[0] or y + height > window_size[1]:
            raise OutOfBoundsInputError(f'The final end position of the region ({x + width}, {y + height}) to take the screenshot of is outside the size of the window. {window_size} If you want to take a screenshot of more than one window, use your window manager\'s screenshot or screenshot_region methods.')

        # taking a screenshot and returning it
        return self.window_manager.screenshot_region(window_position[0] + x, window_position[1] + y, width, height)
    
    def get_pixel(self, x: int, y: int, scale: bool = True) -> tuple[int, int, int, int]:
        '''Returns a RGBA tuple of a pixel on the window.
        
        This method literally takes a screenshot of the
        entire window, the extracts one pixel, so if
        you may need the screenshot we're getting here,
        it's far more optimal to just take the screenshot,
        then use .pixel on the image. You would of course,
        then also need to handle scaling if you did this,
        but you can just use your_window_variable.scale_point((your, point), your_window_variable.get_scale())

        If the pixel you're trying to access
        
        :param int x: The x position of the pixel to get
        :param int y: The y position of the pixel to get
        :param bool scale: If the x and y should be scaled
        to the actual size of the window'''
        # scaling if we should
        if scale:
            x, y = self.scale_point((x, y), self.get_scale())

        # getting a screenshot of the window
        window_screenshot = self.screenshot()

        # making sure the pixel isn't outside
        # of the image
        if x > window_screenshot.size[0] or y > window_screenshot.size[1]:
            raise OutOfBoundsInputError(f'The pixel you\'re trying to access ({x}, {y}) is outside of the window. (The window is {window_screenshot.size[0]}, {window_screenshot.size[1]})')
        
        # returning the pixel
        return window_screenshot.getpixel((x, y))
    
    def _scale_window_screenshot_with_lcm(self, screenshot: Image.Image) -> Image.Image:
        '''The way that we scale screenshots is somewhat complicated. Basically,
        imagine we've got a window of 100x100, but a macro designed for 200x200,
        and we're looking for an image that was taken on that 200x200 window.
        Easy, we just scale the screenshot by 2, great! What happens if the
        window the macro was designed for was 110x110. Well now we've got a 
        scale of (1.1, 1.1), and that'll be all blurry and bad for finding stuff.
        So, we get the lowest common multiple of the two, that way it stays whole numbers
        
        :param PIL.Image.Image screenshot: The screenshot to scale'''
        # if there's no scaling to be done, we don't
        if self.macro_resolution is None:
            return screenshot
    
        else:
            # first we calculate the size we'll
            # scale the screenshot to
            # to do that, we need to get the window size
            # luckily, the screenshot of the window is the
            # size of the window!
            window_size = screenshot.size
            scaled_screenshot_size = (
                lcm(self.macro_resolution[0], window_size[0]), 
                lcm(self.macro_resolution[1], window_size[1])
            )

            # if we still won't be scaling it, returning the screenshot
            if scaled_screenshot_size == window_size:
                return screenshot

            # scaling and returning the window
            return screenshot.resize(scaled_screenshot_size)
        
    def _scale_needle_image_from_scaled_screenshot(self, image: Image.Image, scaled_screenshot_size: tuple[int, int], window_size: None | tuple[int, int] = None) -> Image.Image:
        '''Scales the needle image by the same scale factor the window screenshot seems like it was
        relative to the macro resolution. 
        
        This means that if the macro resolution is 1920x1080, and the screenshot is 1920x1080, then
        the scale (1, 1), so we scale the image by (1, 1). If we the macro resolution was still 1920x1080,
        but the screenshot was instead 3840x2160, then the scale'd be (2, 2), so the image would be 
        scaled by that
        
        :param PIL.Image.Image image: The needle image to scale
        :param scaled_screenshot_size
        :param None | tuple[int, int] window_size: The current size of the window, if not passed we can get it on our own'''
        # if there's no macro resolution, we don't scale anything
        if self.macro_resolution is None:
            return image

        # if window size is None, we get it ourselves
        if window_size is None:
            window_size = self.get_size()

        # first we calculate the scale factor we would/are scale the haystack image by
        scale_x = scaled_screenshot_size[0] / window_size[0]
        scale_y = scaled_screenshot_size[1] / window_size[1]

        # if we'd just be scaling it by (1, 1), we return the image
        if scale_x == 1 and scale_y == 1:
            return image

        scaled_image = image.resize((
            int(image.size[0] * scale_x),
            int(image.size[1] * scale_y))
        )

        # returning the scaled image
        return scaled_image
    
    def locate_on_window(
        self,
        image: str | Image.Image,
        *,
        grayscale: bool | None = None,
        limit: int = 1,
        region: tuple[int, int, int, int] | None = None,
        step: int = 1,
        confidence: float = 0.999,
        scale_with_lcm: bool = False,
        scale_haystack_image: bool = True,
        scale_needle_image: bool = True,
        haystack_scaling_resampling: int = Resampling.BICUBIC,
    ) -> Box | None:
        '''This is pretty much a wrapper for pyscreeze.locate, but we also implement some scaling logic,
        and also taking screenshots. So, for more help regarding the how stuff is found, check out there first!
        This also means, that we only have docs here for our custom in house logic, as I'm also not 100% sure
        what some of these things means, and I wouldn't want to spread misinformation. Sorry about that!

        Also, pyautogui pretty much just also wraps pyscreeze, so if you're trying to find a Stack Overflow
        thread or something like that for an issue, you can also try searching for that, but pyautogui.

        This function locates and returns the first match of
        the given image it finds in a screenshot of the window.
        How well it has to match can be changed by changing 
        confidence (0 is anything matches 1 is exact pixel 
        to pixel match)

        There's two different kinds of scaling for images, the faster one that won't crash the
        program, and only scales up to macro resolution, and one that scales past the macro resolution
        to improve quality to the point where it's almost indistinguishable from from not scaling at all.
        The second option works amazingly when you know the aspect ratio will stay the same. (Like fullscreen
        on a 16:9 monitor.) However, if you cannot garuntee that, unless you've got A LOT of ram and CPU,
        you probably don't want to enable it.
        
        :param bool scale_with_lcm: This toggles if we should scale up to a resolution past (or equal to) to macro resolution, so we can make sure the 
        scale up and down will all be whole numbers. This improves accuracy to the point where you can't tell there's scaling happening most of the time, 
        but also takes far more ram. In some cases, it can take over 100gb of ram, so only use this when you need the accuracy, and can garuntee the aspect
        ratio will be similar. (Like fullscreen on a 16:9 monitor)
        :param bool scale_needle_image: If the given image should be scaled to a happy medium with the haystack image (their lowest common multiple)
        :param bool scale_haysatack_image: If the screenshot should be scaled to a happy medium with the needle image (their lowest common multiple)
        :param int haystack_scaling_resampling: If we scale the haystack image (the screenshot of the window here), what resampling we should use. This is only used for non-lcm scaling'''
        # capturing the window
        window_screenshot = self.screenshot()

        # getting the size of the window from the screenshot we just took
        window_size = window_screenshot.size

        # if we were given the path to an image, opening it
        if type(image) == str:
            image = Image.open(image)

        # only scaling if we would scale anything in the first place
        if self.macro_resolution is not None and self.macro_resolution != window_size:
            if scale_haystack_image:
                if scale_with_lcm:
                    window_screenshot = self._scale_window_screenshot_with_lcm(window_screenshot)
                else:
                    window_screenshot = window_screenshot.resize(self.macro_resolution, resample=haystack_scaling_resampling)

            if scale_needle_image:
                # the logic is always the same for scaling the needle image,
                # scale it by however much the window screenshot was scaled by
                image = self._scale_needle_image_from_scaled_screenshot(image, window_screenshot.size, window_size)

        # finding a match for the image
        match = self.window_manager.locate(image, window_screenshot, grayscale=grayscale, limit=limit, region=region, step=step, confidence=confidence)

        # if we got None, returning that
        if match is None:
            return None

        # if we scaled things up with LCM, meaning
        # we scaled beyond the macro resolution,
        # we scale back down to the macro resolution
        if self.macro_resolution is not None and scale_haystack_image and scale_with_lcm:
            # calculating scale
            scale_x = lcm(window_size[0], self.macro_resolution[0]) / self.macro_resolution[0]
            scale_y = lcm(window_size[1], self.macro_resolution[1]) / self.macro_resolution[1]

            return Box(int(match.left / scale_x), int(match.top / scale_y), int(match.width / scale_x), int(match.height / scale_y))

        # returning the matches
        return match

    def locate_all_on_window(
        self,
        image: str | Image.Image,
        *,
        grayscale: bool | None = None,
        limit: int = 10000,
        region: tuple[int, int, int, int] | None = None,
        step: int = 1,
        confidence: float = 0.999,
        scale_with_lcm: bool = False,
        scale_haystack_image: bool = True,
        scale_needle_image: bool = True,
        haystack_scaling_resampling: int = Resampling.BICUBIC,
    ) -> list[Box]:
        '''This is pretty much a wrapper for pyscreeze.locate_all, but we also implement some scaling logic,
        and also taking screenshots. So, for more help regarding the how stuff is found, check out there first!
        This also means, that we only have docs here for our custom in house logic, as I'm also not 100% sure
        what some of these things means, and I wouldn't want to spread misinformation. Sorry about that!

        Also, pyautogui pretty much just also wraps pyscreeze, so if you're trying to find a Stack Overflow
        thread or something like that for an issue, you can also try searching for that, but pyautogui.

        This function finds, and returns the locations of everywhere it finds some image inside another image.
        How well the image has to match part of the other image is set by confidence. Also, there's scaling,
        meaning if you designed the macro/whatever you're doing for one resolution, but the window is another,
        it can automatically scale it for you. 

        There's two different kinds of scaling for images, the faster one that won't crash the
        program, and only scales up to macro resolution, and one that scales past the macro resolution
        to improve quality to the point where it's almost indistinguishable from from not scaling at all.
        The second option works amazingly when you know the aspect ratio will stay the same. (Like fullscreen
        on a 16:9 monitor.) However, if you cannot garuntee that, unless you've got A LOT of ram and CPU,
        you probably don't want to enable it.
        
        :param bool scale_with_lcm: This toggles if we should scale up to a resolution past (or equal to) to macro resolution, so we can make sure the 
        scale up and down will all be whole numbers. This improves accuracy to the point where you can't tell there's scaling happening most of the time, 
        but also takes far more ram. In some cases, it can take over 100gb of ram, so only use this when you need the accuracy, and can garuntee the aspect
        ratio will be similar. (Like fullscreen on a 16:9 monitor)
        :param bool scale_needle_image: If the given image should be scaled to a happy medium with the haystack image (their lowest common multiple)
        :param bool scale_haysatack_image: If the screenshot should be scaled to a happy medium with the needle image (their lowest common multiple)
        :param int haystack_scaling_resampling: If we scale the haystack image (the screenshot of the window here), what resampling we should use. This is only used for non-lcm scaling'''

        # capturing the window
        window_screenshot = self.screenshot()

        # getting the size of the window from the screenshot we just took
        window_size = window_screenshot.size

        # if we were given the path to an image, opening it
        if type(image) == str:
            image = Image.open(image)

        # only scaling if we would scale anything in the first place
        if self.macro_resolution is not None and self.macro_resolution != window_size:
            if scale_haystack_image:
                if scale_with_lcm:
                    window_screenshot = self._scale_window_screenshot_with_lcm(window_screenshot)
                else:
                    window_screenshot = window_screenshot.resize(self.macro_resolution, resample=haystack_scaling_resampling)

            if scale_needle_image:
                # the logic is always the same for scaling the needle image,
                # scale it by however much the window screenshot was scaled by
                image = self._scale_needle_image_from_scaled_screenshot(image, window_screenshot.size, window_size)

        # finding all matches for the image
        matches = self.window_manager.locate_all(image, window_screenshot, grayscale=grayscale, limit=limit, region=region, step=step, confidence=confidence)

        # turning the matches from a generator into a list
        matches_list = [match for match in matches]

        # if we scaled things up with LCM, meaning
        # we scaled beyond the macro resolution,
        # we scale back down to the macro resolution
        if self.macro_resolution is not None and scale_haystack_image and scale_with_lcm:
            # calculating scale
            scale_x = lcm(window_size[0], self.macro_resolution[0]) / self.macro_resolution[0]
            scale_y = lcm(window_size[1], self.macro_resolution[1]) / self.macro_resolution[1]

            for i, match in enumerate(matches_list):
                # scaling everything
                matches_list[i] = Box(int(match.left / scale_x), int(match.top / scale_y), int(match.width / scale_x), int(match.height / scale_y))

        # returning the matches
        return matches_list

    def locate_center_on_window(
        self,
        image: str | Image.Image,
        *,
        grayscale: bool | None = None,
        limit: int = 1,
        region: tuple[int, int, int, int] | None = None,
        step: int = 1,
        confidence: float = 0.999,
        scale_with_lcm: bool = False,
        scale_haystack_image: bool = True,
        scale_needle_image: bool = True,
        haystack_scaling_resampling: int = Resampling.BICUBIC
    ) -> Point | None:
        '''This is pretty much a wrapper for pyscreeze.locate_all, but we also implement some scaling logic,
        and also taking screenshots. So, for more help regarding the how stuff is found, check out there first!
        This also means, that we only have docs here for our custom in house logic, as I'm also not 100% sure
        what some of these things means, and I wouldn't want to spread misinformation. Sorry about that!

        Also, pyautogui pretty much just also wraps pyscreeze, so if you're trying to find a Stack Overflow
        thread or something like that for an issue, you can also try searching for that, but pyautogui.

        This function is pretty much the same as locate_on_window, where it searches a screenshot of the
        window, then returns the first thing that matches (well enough, how well is decided by confidence)
        the needle image. The only difference, is that instead of returning a rectangle for where it found
        the match, it just returns the center of it.

        There's two different kinds of scaling for images, the faster one that won't crash the
        program, and only scales up to macro resolution, and one that scales past the macro resolution
        to improve quality to the point where it's almost indistinguishable from from not scaling at all, then
        scales back down to macro resolution.
        The second option works amazingly when you know the aspect ratio will stay the same. (Like fullscreen
        on a 16:9 monitor.) However, if you cannot garuntee that, unless you've got A LOT of ram and CPU,
        you probably don't want to enable it.

        :param bool scale_with_lcm: This toggles if we should scale up to a resolution past (or equal to) to macro resolution, so we can make sure the 
        scale up and down will all be whole numbers. This improves accuracy to the point where you can't tell there's scaling happening most of the time, 
        but also takes far more ram. In some cases, it can take over 100gb of ram, so only use this when you need the accuracy, and can garuntee the aspect
        ratio will be similar. (Like fullscreen on a 16:9 monitor)
        :param bool scale_needle_image: If the given image should be scaled to a happy medium with the haystack image (their lowest common multiple)
        :param bool scale_haysatack_image: If the screenshot should be scaled to a happy medium with the needle image (their lowest common multiple)
        :param int haystack_scaling_resampling: If we scale the haystack image (the screenshot of the window here), what resampling we should use. This is only used for non-lcm scaling'''
        # capturing the window
        window_screenshot = self.screenshot()

        # getting the size of the window from the screenshot we just took
        window_size = window_screenshot.size

        # if we were given the path to an image, opening it
        if type(image) == str:
            image = Image.open(image)

        # only scaling if we would scale anything in the first place
        if self.macro_resolution is not None and self.macro_resolution != window_size:
            if scale_haystack_image:
                if scale_with_lcm:
                    window_screenshot = self._scale_window_screenshot_with_lcm(window_screenshot)
                else:
                    window_screenshot = window_screenshot.resize(self.macro_resolution, resample=haystack_scaling_resampling)

            if scale_needle_image:
                # the logic is always the same for scaling the needle image,
                # scale it by however much the window screenshot was scaled by
                image = self._scale_needle_image_from_scaled_screenshot(image, window_screenshot.size, window_size)

        # finding a match for the image
        match = self.window_manager.locate_center(image, window_screenshot, grayscale=grayscale, limit=limit, region=region, step=step, confidence=confidence)

        # if we got None, returning that
        if match is None:
            return None

        # if we scaled things up with LCM, meaning
        # we scaled beyond the macro resolution,
        # we scale back down to the macro resolution
        if self.macro_resolution is not None and scale_haystack_image and scale_with_lcm:
            # calculating scale
            scale_x = lcm(window_size[0], self.macro_resolution[0]) / self.macro_resolution[0]
            scale_y = lcm(window_size[1], self.macro_resolution[1]) / self.macro_resolution[1]

            return(Point(int(match.x / scale_x), int(match.y / scale_y)))

        # returning the matches
        return match
