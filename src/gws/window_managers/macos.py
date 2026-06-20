from gws._generics import GenericNonWaylandWindowManager
from gws.window import BasicWindow
from gws._errors import InvalidWindowID
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gws._typing import WindowLikeType, WindowLike

class Quartz(GenericNonWaylandWindowManager):
    pass