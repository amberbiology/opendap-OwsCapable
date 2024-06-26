# =============================================================================
# OWSLib. Copyright (C) 2005 Sean C. Gillies
#
# Contact email: sgillies@frii.com
# =============================================================================

from __future__ import (absolute_import, division, print_function)


def patch_well_known_namespaces(etree_module):

    import warnings
    from owscapable.namespaces import Namespaces
    ns = Namespaces()

    """Monkey patches the etree module to add some well-known namespaces."""

    try:
        register_namespace = etree_module.register_namespace
    except AttributeError:
        try:
            etree_module._namespace_map

            def register_namespace(prefix, uri):
                etree_module._namespace_map[uri] = prefix
        except AttributeError:
            def register_namespace(prefix, uri):
                pass
            warnings.warn("Only 'lxml.etree' >= 2.3 and 'xml.etree.ElementTree' >= 1.3 are fully supported!")

    for k, v in list(ns.get_namespaces().items()):
        register_namespace(k, v)

# try to find lxml or elementtree
try:
    from lxml import etree
except ImportError:
    try:
        # Python 2.5 with ElementTree included
        import xml.etree.ElementTree as etree
    except ImportError:
        try:
            # Python < 2.5 with ElementTree installed
            import elementtree.ElementTree as etree
        except ImportError:
            raise RuntimeError('You need either lxml or ElementTree to use OWSLib!')

patch_well_known_namespaces(etree)
