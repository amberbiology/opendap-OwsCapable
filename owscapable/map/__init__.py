
from __future__ import (absolute_import, division, print_function)

def get_first_valid_href_attrib(element, keys=('{http://www.w3.org/1999/xlink}href', 'xlink_href')):
    """
    Tries to get the first valid attribute from the element for the given keys.
    
    :param element: The XML element.
    :param keys: Tuple of attribute keys to try, defaulting to commonly used xlink keys.
    :return: The value of the first found attribute, or None if none are found.
    """
    for key in keys:
        value = element.attrib.get(key)
        if value is not None:
            return value
    return None
