'''For future reference, this file is intended to be
used to make sure every external dependency needed
can be checked for to make sure it's installed'''
import shutil
from functools import wraps

# checking every dependency we need to see if it's installed
wtype_installed: bool = shutil.which('wtype') is not None
wayland_utils_installed: bool = shutil.which('wayland-info') is not None
grim_installed = shutil.which('grim') is not None


# making a bunch of decorators for each dependency
def requires_wtype(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # if wtype isn't installed, raising an error
        if not wtype_installed:
            raise RuntimeError(f'wtype isn\'t installed, and is required to do typing input on Wayland. Are you sure you\'ve installed/it\'s on path as "wtype"?')
        
        # running the function we're decorating
        return func(*args, **kwargs)
    return wrapper

def requires_wayland_utils(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # if wayland_utils isn't installed, raising an error
        if not wayland_utils_installed:
            raise RuntimeError(f'wayland_utils isn\'t installed, and is required to get monitor info on Wayland. Are you sure you\'ve installed/it\'s on path as "wayland-info"? \n\n(Note: the package being wayland-utils, but it\'s on path as wayland-info isn\'t a mistake, it\'s what the package chose.)')
        
        # running the function we're decorating
        return func(*args, **kwargs)
    return wrapper

def requires_grim(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # if grim isn't installed, raising an error
        if not grim_installed:
            raise RuntimeError(f'grim isn\'t installed, and is required to take screenshots on Wayland. Are you sure you\'ve installed/it\'s on path as "grim"?')
        
        # running the function we're decorating
        return func(*args, **kwargs)
    return wrapper