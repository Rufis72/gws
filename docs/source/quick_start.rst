.. _quick-start:

Quick Start
============

In this page, we'll be building a basic macro that handles window scaling,
movement, and is (mostly) os independant

If you haven't yet, you should probably :ref:`install GWS <installation>`

Setting up a basic file 
#########################

When you make any macro with GWS, there's gonna be two things that are
always there, the gws import, and initializing your window manager. 
GWS's window manager classes basically just wrap your actual window manager.
They handle all the logic for your specific window manager. This also means,
you need to choose the right one for your system. On MacOS, it's just MacOS,
we don't support windows yet, and Linux, we currently only have a full implementation
for Hyprland, but an X11 one is coming. We'll use MacOS for this example, but
they all have the same API, so you just need to change out the name, and you're good.

.. code-block:: python

    import gws

    # initalizing the window manager
    wm = gws.window_managers.macos.MacOS()
    # on Hyprland, this'd be: gws.window_managers.hyprland.Hyprland()

Great! Now you've set up your basic file. You can just use this for your macro,
but you don't have any of the benefits of GWS yet, it's pretty much just more
limited pyautogui. But, it's useful to know what your window manager can do, so
here's a few examples:

* .click, this lets you, well, click. The keys are 'left', 'middle', and 'right' This'll be important later.
* .press, .key_down, .key_up This lets you press/release/hold a key for some time
* .screenshot, .screenshot_region, these let you screenshot your entire screen, or only a specific portion
* .list_window_names, this lists all open window's names
* .get_window_from_name, .get_window_from_regex, these return a (by default) BasicWindow object for a window

Using windows
################

For this section, you're really gonna wanna focus on the last two examples above,
.list_window_names, .get_window_from_name and .get_window_from_regex. You might've
noticed I said some of those return a BasicWindow, but I haven't explained that yet,
so, we're gonna do that now!

Windows are the most powerful part of GWS, they're objects that represent a window
on your system, and they've got all the fancy stuff. They can do the same stuff that
your window manager you just made can, but with a bit extra (the fancy stuff).

Before we do any more, let's have an example. We're gonna get a window by a
regular expression. I'm using VS Code to type these docs, so that's what I'll be using.
Feel free, however, to use some other program, like Chrome, Firefox, your settings app, etc.

.. code-block:: python

    import gws

    wm = gws.window_managers.macos.Macos()

    # now we're gonna get our window
    vs_code_window = wm.get_window_from_regex('.*Visual Studio Code.*')

Now, you've got a window for VS Code! Assumming it found it of course, it can also
return None if it couldn't find anything, so watch out for that!

So far, we've only used one of the three methods I mentioned before, that's because
apps like to change their name (or title) a ton. So your web browser might start out as
"Home Page - Chrome", but when you go to youtube, it could be "www.youtube.com @BillWurtz - Chrome".
That's why we use regex, it'll generally match it pretty well, and apps don't like to
remove their name from their title. You can also get a window by an exact match
(or exact match excluding capitalization) with wm.get_window_from_name, which can
be useful with the next method we're about to use. 

Before we continue, I'm gonna write an outline for what we're trying to do here.
We're gonna open VS Code, click the "Terminal" button, then click "New Terminal".
After that, we're gonna typing in the terminal, "echo 'hello, world!'"

When VS Code opens, we don't know it's name, and there could be multiple open, so
how do we figure out which one we just opened? Well, there's an answer. We can
list all window names before we open it, list them after, then compare, like so:

.. code-block:: python

    import subprocess
    import gws
    import time

    wm = gws.window_managers.macos.MacOS()

    # now we're gonna list our open windows before
    windows_open_before = wm.list_window_names()

    # opening vs code
    # we're gonna assume it's on path as "code"
    # if it's not, you can replace "code" with
    # a path to it
    subprocess.run(['code'])

    # waiting a bit for vs code to open
    time.sleep(3)

    # now we get the windows open afterward
    windows_open_after = wm.list_window_names()

    # now we compare
    unique_names = []
    for window_name in windows_open_after:
        if not windows_open_before.__contains__(window_name):
            unique_names.append(window_name)

        # if it wasn't unique, we remove that one from
        # the list of ones that were open before
        # this is because if there's a new window opened
        # named "code", but there was also one before,
        # we wouldn't catch that, so here we at least try to
        else:
            windows_open_before.pop(windows_open_before.index(window_name))

    # we're gonna assume that in that time
    # only one window opened, the vs code one.
    # of course, if that's not the case, you'll
    # wanna add some second level of verification
    # to make sure it's the one you want
    vs_code_window_name = unique_names[0]

    # now, we get our vs code window from that!
    vs_code_window = wm.get_window_from_name(vs_code_window_name)

Using scaling
##################

Great! Now we've got a way to open VS Code, and get a window
object for it! But, what do we do from here? Well, now we wanna
click the "Terminal" button, right? Great! So let's find it!

We first wanna get the position of it on the window, then we'll
set our macro resolution to the size of our window. So, that way,
even if the macro is 2x bigger, the place we're clicking will be too!
Meaning, it'll still work. For me, my window is 2516x1396, and "Terminal"
was at 362, 36. Subtract the position of the window, and we get 340, 14.

So, let's use that to click the terminal button!

Note: If you're window is a different aspect ration than  mine, then it may
not perfectly work, and becuase my window is a weird aspect ratio, you may
have to find these values yourself.

.. code-block:: python

    import subprocess
    import gws
    import time

    wm = gws.window_managers.macos.MacOS()

    # now we're gonna list our open windows before
    windows_open_before = wm.list_window_names()

    # opening vs code
    subprocess.run(['code'])

    # waiting a bit for vs code to open
    time.sleep(3)

    # now we get the windows open afterward
    windows_open_after = wm.list_window_names()

    # now we compare
    unique_names = []
    for window_name in windows_open_after:
        if not windows_open_before.__contains__(window_name):
            unique_names.append(window_name)

        # if it wasn't unique, we remove that one from
        # the list of ones that were open before
        # this is because if there's a new window opened
        # named "code", but there was also one before,
        # we wouldn't catch that, so here we at least try to
        else:
            windows_open_before.pop(windows_open_before.index(window_name))
    
    vs_code_window_name = unique_names[0]

    vs_code_window = wm.get_window_from_name(vs_code_window_name)

    # next, we're gonna set our macro's resolution, so scaliing
    vs_code_window.set_macro_resolution(2516, 1396)

    # then, we're gonna click!
    vs_code_window.click(340, 14, 'left')

Hopefuly, that should've just clicked the "Terminal" button for you! If it
didn't, you're gonna wanna change where you're clicking, and maybe
the macro resolution if you so choose. The macro resolution is just so
you can say what size window you got the inputs on, and if you're getting
them on a different sized window then me, you'll probably wanna change that.

Finding (and clicking) images
###############################

Now, we're onto the final stretch! We've just gotta click the "New Terminal"
button, and type hello world! We could just click the way we just did, but
for the sake of learning GWS features, we're gonna do it a different way.
Instead, we're gonna take a screenshot of the "New Terminal" button, then find
it on the screen and click it!

we're gonna use a pretty simple image, this is the one I'm using:

.. image:: new_terminal_button.png
    :alt: The new terminal button

If you're using a different VS Code theme, then you'll probably wanna use a different image.
It's also not that high quality, since turns out VS Code hides the popup when I try to take a screenshot,
so I had to use OBS to take a video, then take it from that.

We're gonna use a method here, locate_center_on_window, but the entire locate\_... family is important.
When I say the locate\_... family, I mean like locate, locate_all, locate_on_window, locate_center_on_window, etc.
These all search some image (the haystack image) for another image (the needle image). For locate_on_window,
it searches a screenshot of the screen, then returns a tuple of the starting x, y, width, and height of the image. For
locate_center_on_window, it just returns the center of where it was found, which is what you'll probably mostly use.
If you wanna find stuff with the window manager, instead of the ones for the specific window, like window objects have,
it's got ones for the entire screen. So instead of locate_on_window, it's got locate_on_screen. Do be warned that these
can be quite slow.

An inportant note, all these functions have similar parameters, but the confidence parameter is the most useful here.
It's basically, how well does this need to match to be considered a match.

Anyways, that's enough yapping, onto an example:

.. code-block:: python

    import subprocess
    import gws
    import time

    wm = gws.window_managers.macos.MacOS()

    # now we're gonna list our open windows before
    windows_open_before = wm.list_window_names()

    # opening vs code
    subprocess.run(['code'])

    # waiting a bit for vs code to open
    time.sleep(3)

    # now we get the windows open afterward
    windows_open_after = wm.list_window_names()

    # now we compare
    unique_names = []
    for window_name in windows_open_after:
        if not windows_open_before.__contains__(window_name):
            unique_names.append(window_name)

        # if it wasn't unique, we remove that one from
        # the list of ones that were open before
        # this is because if there's a new window opened
        # named "code", but there was also one before,
        # we wouldn't catch that, so here we at least try to
        else:
            windows_open_before.pop(windows_open_before.index(window_name))
    
    vs_code_window_name = unique_names[0]

    vs_code_window = wm.get_window_from_name(vs_code_window_name)

    # next, we're gonna set our macro's resolution, so scaliing
    vs_code_window.set_macro_resolution(2516, 1396)

    # then, we're gonna click!
    vs_code_window.click(340, 14, 'left')

    # finding the image
    # new_terminal_button.png is the image from earlier
    terminal_button_center = vs_code_window.locate_center_on_window('./new_terminal_button.png', confidence = 0.8)

    # now we're gonna click it
    vs_code_window.click(*terminal_button_center, 'left')

Typing things
################

Finally, we're onto our final step, typing. In GWS, this is quite simple.
There's a few methods, typewrite, key_down, key_up, and press

typewrite just writes text you give it. It can have pauses between characters, and you
can tell it how long to hold it for

key_down presses a key down

key_up releases a key

press presses a key down, waits some amount of time, then releases it.

For this, we're gonna click in the general area of where the terminal normally appears,
then typewrite what we need to.

.. code-block:: python

    import subprocess
    import gws
    import time

    wm = gws.window_managers.macos.MacOS()

    # now we're gonna list our open windows before
    windows_open_before = wm.list_window_names()

    # opening vs code
    subprocess.run(['code'])

    # waiting a bit for vs code to open
    time.sleep(3)

    # now we get the windows open afterward
    windows_open_after = wm.list_window_names()

    # now we compare
    unique_names = []
    for window_name in windows_open_after:
        if not windows_open_before.__contains__(window_name):
            unique_names.append(window_name)

        # if it wasn't unique, we remove that one from
        # the list of ones that were open before
        # this is because if there's a new window opened
        # named "code", but there was also one before,
        # we wouldn't catch that, so here we at least try to
        else:
            windows_open_before.pop(windows_open_before.index(window_name))
    
    vs_code_window_name = unique_names[0]

    vs_code_window = wm.get_window_from_name(vs_code_window_name)

    # next, we're gonna set our macro's resolution, so scaliing
    vs_code_window.set_macro_resolution(2516, 1396)

    # then, we're gonna click!
    vs_code_window.click(340, 14, 'left')

    # finding the image
    terminal_button_center = vs_code_window.locate_center_on_window('./new_terminal_button.png', confidence = 0.8)

    # now we're gonna click it
    vs_code_window.click(*terminal_button_center, 'left')

    # clicking and typing in the terminal
    vs_code_window.click(1336, 1217, 'left')
    vs_code_window.typewrite('echo "hello, world"')

    # entering the text
    vs_code_window.press('enter', 0.5)

Closing remarks, and other
#############################

Now, you've just made a basic macro! Thanks for sticking with the quick start, and I
hope the rest of the docs can answer any questions you may run into!

A few things that are good to know:
* If you ever want to disable scaling, any method that scales stuff also has a scale parameter, which you can just set to False. 
Be careful that you don't pass scaled stuff into a function, then tell it now to scale it back down! I've done this a few times,
and it can be quite annoying to debug
* The doc strings for the actual methods will be more up to date and detailed then what's online here