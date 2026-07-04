Best practices
================

This page outlines best practices for doing different
things with GWS

.. _scaling-best-practices:

Scaling best practices
-----------------------

How to choose your macro's resolution
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In general, if you plan for your macro to be run somewhere
with a different resolution, be it the window is a different
size, or the monitor, or amounts of monitors, etc, you want to
design your macro at a higher resolution then the biggest place
you think it'll be run.

In general, you shouldn't just choose say 2561x1441 because
it's 1 pixel higher than a normal 1440p monitor. That can actually
be quite detramental. This is because, if you're dealing with images,
and trying to find some image on the screen, we scale that stuff too, 
and if you're scaling an image by 1.001, that's gonna get really blurry.
So, in stead, you generall want to use the lowest common multiple (LCM)
of the two.

As an example, let's say you're designing a macro for a 4k monitor (
3840x2160) and a 1440p monitor (2560x1440). You'll first want to find the
LCM of 3840, and 2560. That's gonna be 7680. Next, you'll find the LCM of
1440 and 2160. That's 4320. Great! Now you've got your macro's resolution,
7680x4320!