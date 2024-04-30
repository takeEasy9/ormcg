# -*- coding: utf-8 -*-

"""
@author: takeEasy9
@description: common methods for file operations
@version: 1.0.0
@since: 2024/4/30 19:30
"""
import os
import sys


def write_file(file_name: str, file_content: str, work_dir: str):
    """write file"""
    file_path = os.path.join(work_dir, file_name)
    if not os.path.exists(work_dir):
        os.makedirs(work_dir)
    with open(file_path, 'w', encoding='UTF-8', newline='') as file:
        file.write(file_content)


def get_current_work_dir():
    """get current working directory"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.getcwd()
