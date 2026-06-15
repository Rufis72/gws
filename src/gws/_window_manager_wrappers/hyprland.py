from gws._generics import GenericWindow
from gws._typing import WindowLike, GetWindowFn
from gws._errors import InvalidWindowID
from typing import Any
import subprocess
import json
import re

def _get_all_window_data() -> list[dict[str, Any]]:
        '''Returns the data given by 'hyprctl -j clients' as a dict
        
        A.k.a. it returns all the "clients" (windows) and their properties'''
        # calling hyprctl
        # note: this is the string version of the json
        text_window_data: str = subprocess.run(['hyprctl', '-j', 'clients'], stdout=subprocess.PIPE).stdout

        # getting the dict version
        dict_window_data: list[dict[str, Any]] = json.loads(text_window_data)

        # returning the data
        return dict_window_data

def get_window_from_name(name: str, ignore_capitalization: bool = False) -> HyprlandWindow | None:
    '''Checks the name of every window, if the given name exactly
    matches the window name, a HyprlandWindow object is return of it.
    Otherwise, None is returned
    
    :param str name: The name to look for exact matches to
    :param bool ignore_capitalization: If capitalization should be ignored when looking for matches'''
    # getting all the window data
    window_data = _get_all_window_data()

    # going through each window and checking if the name matches
    for specific_window_data in window_data:
        # if we're ignoring capitalization we do the first line
        # otherwise we do the second
        if (
            (ignore_capitalization and name.lower() == specific_window_data.get('title').lower()) or
            (name == specific_window_data.get('title'))
        ):
            # returning a hyprland window object since we found a match
            return HyprlandWindow(
                specific_window_data.get('address')
            )
        
def get_window_from_regex(pattern: str) -> HyprlandWindow | None:
    '''Checks the name of every window for a match against the given pattern.
    If a match is found, a HyprlandWindow object is returned of that window.
    
    :param str pattern: The regex pattern to check against
    '''
    # getting all the window data
    window_data = _get_all_window_data()

    # going through each window and checking if the name matches
    for specific_window_data in window_data:
        # if we're ignoring capitalization we do the first line
        # otherwise we do the second
        if re.match(pattern, specific_window_data.get('title')):
            # returning a hyprland window object since we found a match
            return HyprlandWindow(
                specific_window_data.get('address')
            )

class HyprlandWindow(GenericWindow):
    def _get_window_data(self) -> dict:
        '''Returns the properties of this window specifically
        
        This takes the data from self._get_all_window_data and sorts
        through it to find this window's data. If it can't find it, it raises InvalidWindowID'''
        # getting all window data
        all_window_data = _get_all_window_data()

        # going through and finding the specific window data
        this_window_data: dict
        for window_data in all_window_data:
            if window_data.get('address') == self.id:
                this_window_data = window_data
                break
        else:
            raise InvalidWindowID(f'{self.id} is not a valid ID (address on hyprland). Was the window closed?')
        
        # returning the window data
        return this_window_data

    def get_position(self) -> tuple[int, int]:
        # getting the all window data
        window_data = self._get_window_data()

        # getting the position
        window_position: list[int] = window_data.get('at') 
        
        # returning the position
        return tuple(window_position)
    
    def get_size(self) -> tuple[int, int]:
        # getting the all window data
        window_data = self._get_window_data()

        # getting the size
        window_size: list[int] = window_data.get('size') 
        
        # returning the position
        return tuple(window_size)
    
    def get_name(self) -> tuple[int, int]:
        # getting the all window data
        window_data = self._get_window_data()

        # getting the size
        window_name: str = window_data.get('title') 
        
        # returning the position
        return window_name