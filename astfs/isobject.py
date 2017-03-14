""" Check any requested object in system to object type """
# -*- coding: utf-8 -*-
import inspect


def isobject(obj):
    """
    If requested object is a class/object - True returned, else False returned
    """
    if not obj:
        return
    if not hasattr(obj, '__dict__'):
        return False
    if inspect.isroutine(obj):
        return False
    if inspect.isclass(obj):
        return False  # if type(object) == types.TypeType:
    return True
