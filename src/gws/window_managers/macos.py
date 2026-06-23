from gws._generics import GenericNonWaylandWindowManager
from gws.window import BasicWindow
from gws._errors import InvalidWindowID
from typing import Any, TYPE_CHECKING
import re

# NOTE: This file is almost entirely AI generated
# I say almost, becasue I think I hand typed some of the imports above

from ApplicationServices import NSWorkspace
from Quartz import (
    CGWindowListCopyWindowInfo,
    kCGWindowListExcludeDesktopElements,
    kCGNullWindowID,
    kCGWindowNumber,
    kCGWindowName,
    kCGWindowOwnerName,
    kCGWindowOwnerPID,
    kCGWindowBounds,
    kCGWindowLayer,
)

if TYPE_CHECKING:
    from gws._typing import WindowLikeType, WindowLike

# Regular GUI apps, not background agents or menu-bar utilities.
NSApplicationActivationPolicyRegular = 0

class MacOS(GenericNonWaylandWindowManager):
    def _get_regular_application_pids(self) -> set[int]:
        workspace = NSWorkspace.sharedWorkspace()
        return {
            app.processIdentifier()
            for app in workspace.runningApplications()
            if app.activationPolicy() == NSApplicationActivationPolicyRegular
        }

    def _is_application_window(self, window_data: dict[str, Any], regular_application_pids: set[int]) -> bool:
        owner_pid = window_data.get(kCGWindowOwnerPID)
        if owner_pid not in regular_application_pids:
            return False

        if window_data.get(kCGWindowLayer) != 0:
            return False

        bounds = window_data.get(kCGWindowBounds) or {}
        width = int(bounds.get('Width', 0))
        height = int(bounds.get('Height', 0))
        if width <= 0 or height <= 0:
            return False

        # Skip title-bar strips and tiny utility windows.
        if height <= 33 and width >= 500:
            return False
        if width <= 64 and height <= 64:
            return False

        return True

    def _get_all_window_data(self) -> list[dict[str, Any]]:
        '''Returns window data for active application windows that are on-screen or minimized'''
        regular_application_pids = self._get_regular_application_pids()
        all_window_data = CGWindowListCopyWindowInfo(kCGWindowListExcludeDesktopElements, kCGNullWindowID)

        return [
            window_data
            for window_data in all_window_data
            if self._is_application_window(window_data, regular_application_pids)
        ]

    def _get_window_title(self, window_data: dict[str, Any]) -> str:
        title = window_data.get(kCGWindowName)
        if title:
            return title
        return window_data.get(kCGWindowOwnerName) or ''

    def _get_application_name(self, window_data: dict[str, Any]) -> str:
        return window_data.get(kCGWindowOwnerName) or ''

    def _get_window_data(self, id: str) -> dict[str, Any]:
        '''Returns the properties of this window specifically

        This takes the data from self._get_all_window_data and sorts
        through it to find this window's data. If it can't find it, it raises InvalidWindowID

        :param str id: The ID to find the window by'''
        all_window_data = self._get_all_window_data()

        for window_data in all_window_data:
            if str(window_data.get(kCGWindowNumber)) == id:
                return window_data

        raise InvalidWindowID(f'{id} is not a valid ID (or window number in macOS terms). Was the window closed?')

    def get_window_from_name(self, name: str, ignore_capitalization: bool = False, window_type: WindowLikeType = BasicWindow) -> WindowLike | None:
        window_data = self._get_all_window_data()

        for specific_window_data in window_data:
            title = self._get_window_title(specific_window_data)
            if (
                (ignore_capitalization and name.lower() == title.lower()) or
                (name == title)
            ):
                return window_type(
                    self,
                    str(specific_window_data.get(kCGWindowNumber))
                )

    def get_window_from_regex(self, pattern: str, window_type: WindowLikeType = BasicWindow) -> WindowLike | None:
        window_data = self._get_all_window_data()

        for specific_window_data in window_data:
            if re.match(pattern, self._get_window_title(specific_window_data)):
                return window_type(
                    self,
                    str(specific_window_data.get(kCGWindowNumber))
                )

    def get_position_of_window(self, id) -> tuple[int, int]:
        window_data = self._get_window_data(id)
        bounds = window_data.get(kCGWindowBounds)
        return (int(bounds['X']), int(bounds['Y']))

    def get_size_of_window(self, id) -> tuple[int, int]:
        window_data = self._get_window_data(id)
        bounds = window_data.get(kCGWindowBounds)
        return (int(bounds['Width']), int(bounds['Height']))

    def get_name_of_window(self, id) -> str:
        window_data = self._get_window_data(id)
        return self._get_window_title(window_data)

    def get_all_window_names(self) -> list[str]:
        '''Returns the names of every application that currently has an on-screen or minimized window'''
        application_names: list[str] = []
        seen_application_names: set[str] = set()

        for window_data in self._get_all_window_data():
            application_name = self._get_application_name(window_data)
            if application_name and application_name not in seen_application_names:
                seen_application_names.add(application_name)
                application_names.append(application_name)

        return application_names
