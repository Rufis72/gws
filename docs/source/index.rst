.. GWS documentation master file, created by
   sphinx-quickstart on Sat Jul  4 09:11:32 2026.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

GWS documentation
=================

Welcome to the GWS docs! These are pretty basic docks aimed to be able to get
you up and running with GWS, and also answer general questions. For most details
on how different methods work, check out the docs in the actual library. They should
be more up to date, and detailed too

What is GWS?
################

GWS is a cross platform macro library that aims to make it as easy to write reproducable 
macros that work on every system. In practice, this means we abstract os/system dependant
stuff. We also make it so you can just macro a window, and we can
handle scaling input and such if the window is a different size then what the macro was designed
for. When doing this, there are general best practices, which you can see :ref:`scaling-best-practices`.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   quick_start
   best_practices
   installation
