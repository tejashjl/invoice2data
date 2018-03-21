"""
Keep helper functions not related to specific module.
"""
import os
import tempfile

import yaml
from collections import OrderedDict


# borrowed from http://stackoverflow.com/a/21912744
def ordered_load(
        stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict
):
    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)

    return yaml.load(stream, OrderedLoader)


def temporary_file_name(prefix="invoice_"):
    """ returns a temporary file-name """
    temporary_file = tempfile.NamedTemporaryFile(prefix=prefix)
    return temporary_file.name


def cleanup(filename):
    """ tries to remove the given filename. Ignores non-existent files """
    try:
        os.remove(filename)
    except OSError:
        pass
