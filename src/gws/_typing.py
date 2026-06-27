from typing import Protocol
from typing_extensions import TypeAlias, Type
from gws.window import BasicWindow
from PIL import Image
from typing import Any
from pyscreeze import Box, Point
from typing import Generator

class WindowLike(Protocol):
    def __init__(self, window_manager: WindowManagerLike, id: str) -> None: ...
    def get_name(self) -> str: ...
    def get_position(self) -> tuple[int, int]: ...
    def get_size(self) -> tuple[int, int]: ...
    def click(self, x: int, y: int, button: str, duration: float = 0.09, bypass_out_of_bounds_check: bool = False): ...
    def key_down(self, key: str): ...
    def key_up(self, key: str): ...
    def press(self, key: str, duration: float): ...
    def typewrite(self, text: str, hold_duration: float = 0.09, spacing_duration: float = 0): ...
    def screenshot(self) -> Image.Image: ...
    def screenshot_region(self, x: int, y: int, width: int, height: int) -> Image.Image: ...
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
    ) -> Box | None: ...

    def locate_all_on_window(
        self,
        image: str | Image.Image | Any,
        *,
        grayscale: bool | None = None,
        limit: int = 10000,
        region: tuple[int, int, int, int] | None = None,
        step: int = 1,
        confidence: float = 0.999,
    ) -> Generator[Box, None, None]: ...

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
    ) -> Point | None: ...

class GetWindowFn(Protocol):
    def __call__(self, name: str) -> WindowLike: ...

class WindowManagerLike(Protocol):
    def get_window_from_name(self, name: str, ignore_capitalization: bool = False, window_type: WindowLikeType = BasicWindow) -> WindowLike | None: ...
    def get_window_from_regex(self, pattern: str, window_type: WindowLikeType = BasicWindow) -> WindowLike | None: ...
    def get_name_of_window(self, id: str) -> str: ...
    def get_position_of_window(self, id: str) -> tuple[int, int]: ...
    def get_size_of_window(self, id: str) -> tuple[int, int]: ...
    def click(self, x: int, y: int, duration: float | int, button: str): ...
    def mouse_down(self, button: str): ...
    def mouse_up(self, button: str): ...
    def key_down(self, key: str): ...
    def key_up(self, key: str): ...
    def press(self, key: str, duration: float): ...
    def typewrite(self, text: str, hold_duration: float = 0.09, spacing_duration: float = 0): ...
    def screenshot(self) -> Image.Image: ...
    def screenshot_region(self, x: int, y: int, w: int, h: int) -> Image.Image: ...
    # apparently the types should be automatically assigned for the ones that are
    # basically just wrappers for pyscreeze
    # so locate, locateAll, locateOnScreen, etc
    # pretty much all the ones with locate below this
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
    ) -> Box | None: ...

    def locate_all(
        self,
        needleImage: str | Image.Image | Any,
        haystackImage: str | Image.Image | Any,
        grayscale: bool | None = None,
        limit: int = 10000,
        region: tuple[int, int, int, int] | None = None,
        step: int = 1,
        confidence: float = 0.999,
    ) -> Generator[Box, None, None]: ...

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
    ) -> Box | None: ...

    def locate_all_on_screen(
        self,
        image: str | Image.Image | Any,
        *,
        grayscale: bool | None = None,
        limit: int = 10000,
        region: tuple[int, int, int, int] | None = None,
        step: int = 1,
        confidence: float = 0.999,
    ) -> Generator[Box, None, None]: ...

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
    ) -> Point | None: ...

WindowLikeType: TypeAlias = Type[WindowLike]
'''WindowLike but for un-instantiated references and such'''