# -*- coding: utf-8 -*-
"""
@shirafujilab
Create on Thu Apr 18

Contents:
    - json parameter import (JPImport)

"""

import json
import os



def json_import(hist):

    """
    Process:
        1. get current directory path
        2. up to root directory
        3. go to config directory
        4. get target params

    """

    """ Directory """
    # get current dir
    cur_dir = os.path.dirname(os.path.abspath(__file__))

    # up to root dir
    upper_dir = os.path.join(cur_dir, "..", "..")

    # add path
    params_path = os.path.join(upper_dir, "data", "params.json")

    with open(params_path, "r") as j:
        params = json.load(j)

    """ Merge dict for history """

    return_dict = {}

    # unpacking and merge dicts
    for key in hist:
        return_dict = return_dict|params[key]

    return return_dict

