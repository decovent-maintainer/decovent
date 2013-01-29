# setup.py
#
# Copyright (C) 2010 Adrian Cristea adrian dot cristea at gmail dotcom
#
# This module is part of Decovent and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php 
#
# http://groups.google.com.au/group/decovent

from setuptools import setup, find_packages

version = '1.1.1'

setup(name='Decovent',
      version=version,
      description="Python events rising and handling using decorators",
      long_description="""\
*Decovent* is a small Python library that allows an easy 
and elegant events rising and handling, using decorators. 

  New in this version: 
    * Private methods have been made public to facilitate inheritance

Basic example:

  | ``from decovent import *         #required import`` 
  | 
  | ``class Mouse(object):           #no special inheritance required``
  |   ``def __init__(self):``
  |       ``self.on_click()          #register handler (no arguments)``
  | 
  |   ``@raise_event()               #raises event *click*``
  |   ``def click(self, x, y):``
  |       ``return (x, y)``
  | 
  |   ``@raise_event()               #raises event *move*``
  |   ``def move(self, x, y): pass   #the event can be an empty method``
  | 
  |   ``@set_handler('click')        #handles event *click*``
  |   ``def on_click(self, x, y):    #arguments will be sent by the event``
  |       ``return (x, y)``
  | 
  | ``>> mouse = Mouse()             #the handler is registered`` 
  | ``>> e, h = mouse.click(10, 20)  #*click* event is raised and results`` 
  | ``>>                             #are returned as tuple in e and h``
  | ``>> mouse.move(30, 40)          #*move* event is raised, but unhandled`` 

Features:
 * Decovent has been tested with Python's both productive versions, 
   Python 2.6.4 and Python 3.1.1
 * events and handlers are tied to the local-thread
 * event name is case sensitive, Unicode safe and not required if it 
   equals the decorated method name
 * for an event can be registered as many handlers as necessary
 * handlers are registered for (class, event) pair, to differentiate between 
   events with similar names, but raised by different classes
 * a handler can be registered many times, but will be executed only once 
   for (class, event) pair
 * handlers execution order is the same as the registration order
 * handlers are always executed in parallel threads, synchronous or 
   asynchronous
 * parameters received by the handlers are being sent by the event
 * no arguments are required for a handler at registration time
 * a handler can be flagged to run only once for an event and then unregister 
   itself
 * @classmethods can be raised as events or registered as handlers
 * events and handlers can be memoized at local or global level
 * events and handlers can be synchronized on the same lock
 * the time allocated for the execution of an event or handler is controllable
 * the number of methods that can be executed in parallel is controllable 

Restrictions:
 * events and handlers must be methods that belong to new-style classes
 * @staticmethods can't be raised as events or registered as handlers
 * one handler can be registered for only one event 
 
It's important to understand that events and handlers are not classes but 
decorated methods that may belong to any new style class. There are no 
restrictions on the class itself regarding inheritance or the interfaces 
that are implemented.

Please see the documentation for the full list of features:
http://packages.python.org/Decovent
        """,
      classifiers=[
      'Development Status :: 5 - Production/Stable',
      'Environment :: MacOS X',
      'Environment :: Other Environment',
      'Environment :: Plugins',
      'Environment :: Web Environment',
      'Environment :: Win32 (MS Windows)',
      'Intended Audience :: Developers',
      'Intended Audience :: Education',
      'Intended Audience :: Information Technology',
      'Intended Audience :: Other Audience',
      'License :: OSI Approved :: MIT License',      
      'Operating System :: MacOS',
      'Operating System :: Microsoft :: Windows',
      'Operating System :: OS/2',
      'Operating System :: OS Independent',
      'Operating System :: POSIX :: Linux',
      'Operating System :: Unix',
      'Programming Language :: Python',
      'Programming Language :: Python :: 2.6',
      'Programming Language :: Python :: 3',      
      'Programming Language :: Python :: 3.0',      
      'Programming Language :: Python :: 3.1',
      'Topic :: Education',
      'Topic :: Internet :: WWW/HTTP',
      'Topic :: Software Development',
      'Topic :: Software Development :: Libraries',   
      'Topic :: Software Development :: Libraries :: Python Modules',      
      'Topic :: Utilities',            
      ],
      keywords='event raise handle decorator',
      author='Adrian Cristea',
      author_email='adrian.cristea@gmail.com ',
      url='http://groups.google.com.au/group/decovent',
      license='MIT',
      packages=find_packages('.', exclude=['examples*', 'test*']),
      zip_safe=False,
) 