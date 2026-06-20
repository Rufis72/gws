from gws._generics import GenericWaylandWindowManager
from gws.window import BasicWindow
from gws._errors import InvalidWindowID
from typing import Any, TYPE_CHECKING
import subprocess
import json
import re

if TYPE_CHECKING:
    from gws._typing import WindowLikeType, WindowLike

class Hyprland(GenericWaylandWindowManager):
    def _get_all_window_data(self) -> list[dict[str, Any]]:
        '''Returns the data given by 'hyprctl -j clients' as a dict
        
        A.k.a. it returns all the "clients" (windows) and their properties'''
        # calling hyprctl
        # note: this is the string version of the json
        text_window_data: bytes = subprocess.run(['hyprctl', '-j', 'clients'], stdout=subprocess.PIPE).stdout

        # getting the dict version
        dict_window_data: list[dict[str, Any]] = json.loads(text_window_data)

        # returning the data
        return dict_window_data
    
    def _get_window_data(self, id: str) -> dict:
        '''Returns the properties of this window specifically
        
        This takes the data from self._get_all_window_data and sorts
        through it to find this window's data. If it can't find it, it raises InvalidWindowID
        
        :param str id: The ID to find the window by'''
        # getting all window data
        all_window_data = self._get_all_window_data()

        # going through and finding the specific window data
        this_window_data: dict
        for window_data in all_window_data:
            if window_data.get('address') == id:
                this_window_data = window_data
                break
        else:
            raise InvalidWindowID(f'{id} is not a valid ID (or address in hyprland terms). Was the window closed?')
        
        # returning the window data
        return this_window_data
    
    def get_window_from_name(self, name: str, ignore_capitalization: bool = False, window_type: WindowLikeType = BasicWindow) -> WindowLike | None:
        '''Checks the name of every window, if the given name exactly
        matches the window name, a HyprlandWindow object is return of it.
        Otherwise, None is returned

        :param str name: The name to look for exact matches to
        :param bool ignore_capitalization: If capitalization should be ignored when looking for matches
        :param WindowLikeType window_type: The type of window to initialize from the name. By default is the BasicWindow'''
        # getting all the window data
        window_data = self._get_all_window_data()

        # going through each window and checking if the name matches
        for specific_window_data in window_data:
            # if we're ignoring capitalization we do the first line
            # otherwise we do the second
            if (
                (ignore_capitalization and name.lower() == specific_window_data.get('title').lower()) or
                (name == specific_window_data.get('title'))
            ):
                # returning a hyprland window object since we found a match
                return window_type(
                    self, 
                    specific_window_data.get('address')
                )
            
    def get_window_from_regex(self, pattern: str, window_type: WindowLikeType = BasicWindow) -> WindowLike | None:
        '''Checks the name of every window for a match against the given pattern.
        If a match is found, a window object is returned of that window.
        
        :param str pattern: The regex pattern to check against
        :param WindowLikeType window_type: The type of window to initialize from the regex. By default is the BasicWindow
        '''
        # getting all the window data
        window_data = self._get_all_window_data()

        # going through each window and checking if the name matches
        for specific_window_data in window_data:
            # if we're ignoring capitalization we do the first line
            # otherwise we do the second
            if re.match(pattern, specific_window_data.get('title')):
                # returning a hyprland window object since we found a match
                return window_type(
                    self,
                    specific_window_data.get('address')
                )

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
        window_size: tuple[int, int] = window_data.get('size') 
        
        # returning the position
        return window_size
    
    def get_name_of_window(self, id) -> str:
        # getting the all window data
        window_data = self._get_window_data(id)

        # getting the size
        window_name: str = window_data.get('title') 
        
        # returning the position
        return window_name