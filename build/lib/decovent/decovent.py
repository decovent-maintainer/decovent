# decovent.py
#
# Copyright (C) 2010 Adrian Cristea adrian dot cristea at gmail dotcom
#
# This module is part of Decovent and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
#
# http://groups.google.com.au/group/decovent

"""
Decovent is a small Python library, that allows an easy
and elegant events rising and handling using decorators.

Source:
    http://pypi.python.org/pypi/Decovent
Documentation:
    http://packages.python.org/Decovent
"""
import sys
import threading
import logging
import Queue
import types

log = logging.getLogger('decovent')


class event_context(object):
    """
    light session container

    . asynchronous
        controls handlers execution mode
    . debug
        activates logging based debugging
    . encoding
        encoding used to encode event/handler's name
    . errors
        encoding errors
    . exc_info
        controls sys.exc_info() return for faulty executions
    . memoize
        activates memoization at global level
    . threads
        maximum threads started for handlers execution
    . traceback
        controls traceback return for faulty executions

    """

    def __init__(self, asynchronous=False, debug=False, encoding='UTF-8',
                 errors='strict', exc_info=False, memoize=False,
                 threads=3, traceback=False):

        self.asynchronous = asynchronous
        self.debug = debug
        self.encoding = encoding
        self.errors = errors
        self.exc_info = exc_info
        self.memoize = memoize
        self.threads = threads
        self.traceback = traceback

        self.active = threading.BoundedSemaphore(value=3)
        self.local = threading.local()
        self.local.events = {}
        self.memos = {}

default_context = event_context()


class raise_event(object):
    """ Decorator class that executes handlers registered for an event
    Parameters:
    - event - the event that was raised. If None, the decorated
              method name will be used as the event to be raised
    - memoize_ - if True, the execution result will be cached. If False,
                decovent.memoize will be used
    - lock - if provided the event and handlers will be synchronized on
             this lock. The lock must be of type threading.RLock()
    - timeout - maximum time allocated for the event's execution
    """

    def __init__(self, event=None, memoize_=False, lock=None, timeout=None,
                 context=default_context):

        self.event = event
        self.memoize = memoize_ or context.memoize
        self.lock = lock
        self.timeout = timeout
        self.context = context

    def __call__(self, f):
        def wrapped_f(*args, **kwargs):
            self.queue = Queue.Queue()
            self.e_result = None
            self.h_result = []

            self._check(f, *args)
            self.event = self._encode(self.event or f.func_name)
            class_ = self._class(*args)
            hash_ = __builtins__['hash'](class_)

            if self.context.debug and log.isEnabledFor(logging.DEBUG):
                msg = 'Raising event %s.%s():%s'
                log.debug(msg % (str(class_), self.event,
                                 f.func_code.co_firstlineno))

            handlers = self._extract(self.event, hash_)
            self.e_result = self._exec_e(f, *args, **kwargs)

            if handlers:
                max_threads = self._threads(len(handlers))
                for i in range(max_threads):
                    t = threading.Thread(target=self._exec_h,
                                         args=args, kwargs=kwargs)
                    t.daemon = True
                    t.start()

                for handler in handlers:
                    self.queue.put(handler)

                    if self.context.asynchronous:
                        #event, class, handler, memoize, timeout
                        e, c, h, m, t = handler
                        self.h_result.append((None, None, c, h))

                if not self.context.asynchronous:
                    self.queue.join()

            return (self.e_result, tuple(self.h_result))
        return wrapped_f

    def _check(self, f, *args):
        """ Checks if event's class is a new style class and the event is
        not a static method
        """

        msg = 'Event "[%s:%s] %s()" must belong to a new style class '
        msg += 'and can\'t be a static method'
        msg = msg % (f.func_code.co_filename, str(f.func_code.co_firstlineno),
                     f.func_name)
        try:
            if isinstance(args[0], (types.FunctionType, types.LambdaType,
                                    types.ClassType, types.InstanceType)):
                raise TypeError(msg)
            if not hasattr(args[0], '__dict__'):
                if not hasattr(args[0], '__slots__'):
                    raise TypeError(msg)
        except IndexError:
            raise TypeError(msg)

    def _class(self, *args):
        """ This method tries to differentiate between a class and an instance
        to cater for @classmethod which returns a class not an instance """

        if hasattr(args[0], '__mro__'):
            #this is a class
            return args[0]
        else:
            #this is an instance
            return type(args[0])

    def _exec_e(self, f, *args, **kwargs):
        """ Executes the event """
        info = '%s.%s()' % (str(self._class(args[0])), f.func_name)

        if self.context.debug and log.isEnabledFor(logging.DEBUG):
            msg = '[%s] Processing event %s'
            log.debug(msg % (threading.current_thread().name, info))

        if isinstance(self.lock, threading._RLock):
            #synchronization
            self.lock.acquire()
        try:
            result = self._memoize(self.memoize, self.timeout,
                                   f, *args, **kwargs)
            result.extend((self._class(args[0]), f))
            return tuple(result)
        except Exception as err:
            if self.context.exc_info:
                if not self.context.traceback:
                    return (False, sys.exc_info()[:2], self._class(args[0]), f)
                return (False, sys.exc_info(), self._class(args[0]), f)
            else:
                return (False, err, self._class(args[0]), f)
        finally:
            if isinstance(self.lock, threading._RLock):
                self.lock.release()

            if self.context.debug and log.isEnabledFor(logging.DEBUG):
                msg = '[%s] Processing of event %s is completed'
                log.debug(msg % (threading.current_thread().name, info))

    def _exec_h(self, *args, **kwargs):
        """ Executes registered handlers """

        while True:
            try:
                event, class_, handler, memoize_, timeout = self.queue.get()

                if isinstance(self.lock, threading._RLock):
                    #synchronization
                    self.lock.acquire()

                try:
                    info = '%s.%s()' % (str(class_), handler.func_name)

                    if self.context.debug and log.isEnabledFor(logging.DEBUG):
                        msg = '[%s] Processing handler %s'
                        log.debug(msg % (threading.current_thread().name,
                                         info))

                    args = list(args[:])
                    #switch 'self' to handler's class
                    args[0] = class_
                    if not self.context.asynchronous:
                        result = self._memoize(memoize_, timeout,
                                               handler, *args, **kwargs)
                        result.extend((class_, handler))
                        self.h_result.append(tuple(result))
                    else:
                        self._memoize(memoize_, timeout,
                                      handler, *args, **kwargs)
                except Exception as err:
                    if not self.context.asynchronous:
                        if self.context.exc_info:
                            if not self.context.traceback:
                                self.h_result.append((False,
                                                      sys.exc_info()[:2],
                                                      class_, handler))
                            else:
                                self.h_result.append((False, sys.exc_info(),
                                                      class_, handler))
                        else:
                            self.h_result.append((False, err, class_, handler))
                finally:
                    if isinstance(self.lock, threading._RLock):
                        self.lock.release()

                    if not self.context.asynchronous:
                        self.queue.task_done()

                    if self.context.debug and log.isEnabledFor(logging.DEBUG):
                        msg = '[%s] Processing of handler %s is completed'
                        log.debug(msg % (threading.current_thread().name,
                                         info))
            except Queue.Empty:
                break

    def _extract(self, event, hash_):
        """ Extracts registered handlers """

        handlers = []
        if hash_ in self.context.local.events:
            for i in range(len(self.context.local.events[hash_]) - 1, -1, -1):
                event_, class_, handler, unregister, \
                    memoize_, timeout = self.context.local.events[hash_][i]
                if event_ == event:
                    handlers.append((event_, class_, handler,
                                     (memoize_ or self.context.memoize),
                                     timeout))
                    if unregister:
                        del self.context.local.events[hash_][i]
                        if len(self.context.local.events[hash_]) == 0:
                            del self.context.local.events[hash_]
            handlers.reverse()
            if ((handlers and self.context.debug and
                 log.isEnabledFor(logging.DEBUG))):

                for h in handlers:
                    event_, class_, handler, memoize_, timeout = h
                    msg = 'Event intercepted by %s.%s():%s'
                    log.debug(msg % (str(class_), handler.func_name,
                                     handler.func_code.co_firstlineno))
        return handlers

    def _memoize(self, memoize_, timeout, f, *args, **kwargs):
        """
            memoize = { hash: ((args, kwargs, result), ...),
                        hash: ((args, kwargs, result), ...),
                      ...}
            hash = class_hash + func_hash + func_name
        """
        if not memoize_:
            self.context.active.acquire()
            try:
                if not isinstance(timeout, (int, float)) or timeout <= 0:
                    return [True, f(*args, **kwargs)]

                result = self._timeout(timeout, f, *args, **kwargs)

                if isinstance(result, tuple) and len(result) == 3:
                    #error occurred
                    if isinstance(result[1], Exception):
                        if self.context.exc_info:
                            if not self.context.traceback:
                                return [False, result[:2]]
                            return [False, result]
                        return [False, result[1]]
                return [True, result]
            finally:
                self.context.active.release()
        else:
            args_ = list(args[:])
            args_[0] = self._class(args_[0])
            hash_ = str(hash(args_[0])) + str(hash(f)) + '_' + f.func_name

            if hash_ in self.context.memos:
                for m in self.context.memos[hash_]:
                    _args, _kwargs, result = m
                    if _args == args_ and _kwargs == kwargs:

                        if ((self.context.debug and
                             log.isEnabledFor(logging.DEBUG))):
                            msg = '[%s] Reading from cache: ' + \
                                  '%s.%s(args=%s, kwargs=%s)'
                            log.debug(msg % (threading.current_thread().name,
                                             str(args_[0]), f.func_name,
                                             str(args), str(kwargs)))
                        return [True, result]

            self.context.active.acquire()
            try:
                if not isinstance(timeout, (int, float)) or timeout <= 0:
                    result = f(*args, **kwargs)
                else:
                    result = self._timeout(timeout, f, *args, **kwargs)

                    if isinstance(result, tuple) and len(result) == 3:
                        #error occurred
                        if isinstance(result[1], Exception):
                            if self.context.exc_info:
                                if not self.context.traceback:
                                    return [False, result[:2]]
                                return [False, result]
                            return [False, result[1]]
            finally:
                self.context.active.release()

            lock = threading.RLock()
            lock.acquire()
            try:
                if self.context.debug and log.isEnabledFor(logging.DEBUG):
                    msg = '[%s] Storing in cache: %s.%s(args=%s, kwargs=%s)'
                    log.debug(msg % (threading.current_thread().name,
                                     str(args_[0]), f.func_name,
                                     str(args), str(kwargs)))

                if hash_ not in self.context.memos:
                    self.context.memos[hash_] = []

                self.context.memos[hash_].append(
                    (tuple(args_), kwargs, result))

                return [True, result]
            finally:
                lock.release()

    def _timeout(self, timeout, f, *args, **kwargs):
        """ Controls the time allocated for the execution of a method """

        t = spawn_thread(target=f, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()
        t.join(timeout)

        if not t.is_alive():
            if t.exc_info:
                return t.exc_info
            return t.result
        else:
            try:
                msg = '[%s] Execution was forcefully terminated'
                raise RuntimeError(msg % t.name)
            except:
                return sys.exc_info()

    def _threads(self, counter):
        """ Calculates maximum number of threads that will be started
        """

        t = self.context.threads
        if not isinstance(t, int):
            t = 3
        if t < counter:
            return t
        return counter

    def _encode(self, value):
        if isinstance(value, unicode):
            value = value.encode(self.context.encoding, self.context.errors)
        return value


class set_handler(object):
    """ Decorator class that registers event handlers

    events = {
        hash:((event, handler_class, handler, unregister, memoize, timeout),
              ...),
        hash:((event, handler_class, handler, unregister, memoize, timeout),
              ...),
        ...}
    Parameters:
    - event - the event that triggers handler call
    - class_ - the class the event belongs to.
               If None, the current class is assumed
    - unregister - if True, handler will be unregistered for
                   (class, event) after first call
    - memoize_ - if True, the execution result will be cached. If False,
                 decovent.memoize will be used
    - timeout - maximum time allocated for the handler's execution
    """

    def __init__(self, event, class_=None, unregister=False,
                 memoize_=False, timeout=None, context=default_context):
        self.class_ = class_
        self.event = self._encode(event)
        self.unregister = unregister
        self.memoize = memoize_
        self.timeout = timeout
        self.context = context

    def __call__(self, f):
        def wrapped_f(*args, **kwargs):
            self._check_h(f, *args)
            self.class_ = self._class(self.class_) or self._class(args[0])
            self.class_name = str(self.class_)
            self._check_e(self.class_, self.event)

            if self.context.debug and log.isEnabledFor(logging.DEBUG):
                msg = 'Registering handler for %s.%s'
                log.debug(msg % (str(self.class_name), self.event))

            hash_ = __builtins__['hash'](self.class_)

            h_class = self._class(args[0])
            h_class_hash = __builtins__['hash'](h_class)
            h_method_hash = __builtins__['hash'](f)

            if not hash_ in self.context.local.events:
                self.context.local.events[hash_] = []

            handlers = self.context.local.events[hash_]
            registered = False

            if handlers:
                for event, class_, handler, unregister, \
                        memoize_, timeout in handlers:

                    if event == self.event:
                        if h_class_hash == __builtins__['hash'](class_):
                            if h_method_hash == __builtins__['hash'](handler):
                                registered = True
                                if ((self.context.debug and
                                     log.isEnabledFor(logging.DEBUG))):
                                    log.debug('Handler is already registered')
                                break
            if not registered:
                self.context.local.events[hash_].append(
                    (self.event, h_class, f,
                     self.unregister,
                     self.memoize,
                     self.timeout))
                if self.context.debug and log.isEnabledFor(logging.DEBUG):
                    log.debug('Handler was registered successfully')
        return wrapped_f

    def _class(self, class_):
        """ This method tries to differentiate between a class and an instance
        to cater for @classmethod which returns a class not an instance """

        if class_:
            if hasattr(class_, '__mro__'):
                #this is a class
                return class_
            else:
                #this is an instance
                return type(class_)

    def _check(self, class_):
        """ Checks if class_ is a new style class """

        if isinstance(class_, (types.FunctionType, types.LambdaType,
                               types.ClassType, types.InstanceType)):
            return False
        if not hasattr(class_, '__dict__'):
            if not hasattr(class_, '__slots__'):
                return False
        return True

    def _check_e(self, class_, event):
        """ Checks if event's class is a new style class and the event is
        not a static method """

        if not self._check(class_):
            msg = 'Event "%s.%s()" must belong to a new style class '
            msg += 'and can\'t be a static method'
            raise TypeError(msg % (str(class_), str(event)))

    def _check_h(self, f, *args):
        """ Checks if handler's class is a new style class and the handler is
        not a static method """

        msg = 'Handler "[%s:%s] %s()" must belong to a new style class '
        msg += 'and can\'t be a static method'
        msg = msg % (f.func_code.co_filename, str(f.func_code.co_firstlineno),
                     f.func_name)
        try:
            if not self._check(args[0]):
                raise TypeError(msg)
        except IndexError:
            raise TypeError(msg)

    def _encode(self, value):
        if isinstance(value, unicode):
            value = value.encode(self.context.encoding, self.context.errors)
        return value


class spawn_thread(threading.Thread):
    """ Spawns a new thread and returns the execution result """

    def __init__(self, target, args=(), kwargs={}, default=None):
        threading.Thread.__init__(self)
        self._target = target
        self._args = args
        self._kwargs = kwargs
        self.result = default
        self.exc_info = None

    def run(self):
        try:
            self.result = self._target(*self._args, **self._kwargs)
        except:
            self.exc_info = sys.exc_info()
        finally:
            del self._target, self._args, self._kwargs


def active(value):
    """ Controls the maximum number of concurrent executions """
    self.context.active = threading.BoundedSemaphore(value=value)


def reset(class_=None, event=None, context=default_context):
    """ Convenience method to reset events at
    global or class or (class, event) level
    """

    if class_ is None and event is not None:
        msg = "Class must be provided to unregister handlers for an event"
        raise UnboundLocalError(msg)

    if class_ is None:
        context.local.events = {}
        return

    hash_ = hash(class_)
    if hash_ in context.local.events:
        if event is None:
            del context.local.events[hash_]
            return

        if isinstance(event, unicode):
            event = event.encode(context.encoding, context.errors)

        for i in range(len(context.local.events[hash_]) - 1, -1, -1):
            event_, class_, handler, unregister, memoize_, timeout = \
                context.local.events[hash_][i]
            if event_ == event:
                del context.local.events[hash_][i]
                if len(context.local.events[hash_]) == 0:
                    del context.local.events[hash_]
