from typing import Protocol
from typing_extensions import TypeAlias, Type
from gws.window import BasicWindow
from PIL import Image
from pyscreeze import Box, Point

class WindowLike(Protocol):
    id: str

    def __init__(self, window_manager: WindowManagerLike, id: str) -> None: ...
    def set_macro_resolution(self, width: int, height: int): ...
    def calculate_scale(self, window_size: tuple[int, int]) -> tuple[float, float]: ...
    def get_scale(self) -> tuple[float, float]: ...
    def scale_point(self, point: tuple[int, int], scale: tuple[float, float]) -> tuple[int, int]: ...
    def get_name(self) -> str: ...
    def get_position(self) -> tuple[int, int]: ...
    def get_size(self) -> tuple[int, int]: ...
    def click(self, x: int, y: int, button: str, duration: float = 0.09, bypass_out_of_bounds_check: bool = False, scale: bool = True): ...
    def key_down(self, key: str): ...
    def key_up(self, key: str): ...
    def press(self, key: str, duration: float): ...
    def typewrite(self, text: str, hold_duration: float = 0.09, spacing_duration: float = 0): ...
    def screenshot(self) -> Image.Image: ...
    def screenshot_region(self, x: int, y: int, width: int, height: int, scale: bool = True) -> Image.Image: ...
    def get_pixel(self, x: int, y: int, scale: bool = True) -> tuple[int, int, int, int]: ...
    def locate_on_window(
        self,
        image: str | Image.Image,
        *,
        grayscale: bool | None = None,
        limit: int = 1,
        region: tuple[int, int, int, int] | None = None,
        step: int = 1,
        confidence: float = 0.999,
        scale_haystack_image: bool = True,
        scale_needle_image: bool = True,
    ) -> Box | None: ...

    def locate_all_on_window(
        self,
        image: str | Image.Image,
        *,
        grayscale: bool | None = None,
        limit: int = 10000,
        region: tuple[int, int, int, int] | None = None,
        step: int = 1,
        confidence: float = 0.999,
        scale_haystack_image: bool = True,
        scale_needle_image: bool = True,
    ) -> list[Box]: ...

    def locate_center_on_window(
        self,
        image: str | Image.Image,
        *,
        grayscale: bool | None = None,
        limit: int = 1,
        region: tuple[int, int, int, int] | None = None,
        step: int = 1,
        confidence: float = 0.999,
        scale_haystack_image: bool = True,
        scale_needle_image: bool = True,
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
    def typewrite(self, text: str, hold_duration: float = 0.09, interval: float = 0): ...
    def screenshot(self) -> Image.Image: ...
    def screenshot_region(self, x: int, y: int, width: int, height: int) -> Image.Image: ...
    def get_pixel(self, x: int, y: int) -> tuple[int, int, int, int]: ...
    def list_window_names(self) -> list[str]: ...
    def locate(
        self,
        needle_image: str | Image.Image,
        haystack_image: str | Image.Image,
        *,
        grayscale: bool | None = None,
        limit: int = 1,
        region: tuple[int, int, int, int] | None = None,
        step: int = 1,
        confidence: float = 0.999,
    ) -> Box | None: ...

    def locate_all(
        self,
        needle_image: str | Image.Image,
        haystack_image: str | Image.Image,
        grayscale: bool | None = None,
        limit: int = 10000,
        region: tuple[int, int, int, int] | None = None,
        step: int = 1,
        confidence: float = 0.999,
    ) -> list[Box]: ...

    def locate_on_screen(
        self,
        image: str | Image.Image,
        *,
        grayscale: bool | None = None,
        limit: int = 1,
        region: tuple[int, int, int, int] | None = None,
        step: int = 1,
        confidence: float = 0.999,
    ) -> Box | None: ...

    def locate_all_on_screen(
        self,
        image: str | Image.Image,
        *,
        grayscale: bool | None = None,
        limit: int = 10000,
        region: tuple[int, int, int, int] | None = None,
        step: int = 1,
        confidence: float = 0.999,
    ) -> list[Box]: ...

    def locate_center(
        self,
        needle_image: str | Image.Image,
        haystack_image: str | Image.Image,
        *,
        grayscale: bool | None = None,
        limit: int = 1,
        region: tuple[int, int, int, int] | None = None,
        step: int = 1,
        confidence: float = 0.999,
    ) -> Point | None: ...

    def locate_center_on_screen(
        self,
        image: str | Image.Image,
        *,
        grayscale: bool | None = None,
        limit: int = 1,
        region: tuple[int, int, int, int] | None = None,
        step: int = 1,
        confidence: float = 0.999,
    ) -> Point | None: ...

WindowLikeType: TypeAlias = Type[WindowLike]
'''WindowLike but for un-instantiated references and such'''