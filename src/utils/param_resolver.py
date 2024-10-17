# -*- coding: utf-8 -*-
"""
@shirafujilab
Create on: 2024-10-17

Contents:
    - str is converted  to equation

"""

import json
import os



def param_resolver(params):

    for key, value in params.items():

        if isinstance(value, str):
            
            if key not in ["b1_equ", "WI12_equ"]:

                params[key] = eval(value)

    return params