#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
import sys
import os
import commands
import time
import json
import argparse


__version__ = 'v0.0.1'

MB = 1 << 20
DEFAULT_LARGER_THAN = 1024

HELP_TEXT = """调用 ncdu 来定位文件系统中占用了较大空间的文件、目录，使用前请先安装 ncdu，参考： https://dev.yorhel.nl/ncdu """


class FindLargeFiles(object):
    def __init__(self):
        self.parser = argparse.ArgumentParser(description=HELP_TEXT)
        self.parser.add_argument('path', type=str, nargs='?', default='.', help='要查找的路径')
        self.parser.add_argument('--version', '-V', action='version', version=__version__)
        self.parser.add_argument('--larger_than', '-L', type=float, default=DEFAULT_LARGER_THAN, help='查找大于多少MB的文件')
        self.args = self.parser.parse_args()
        self.ncdu_output_file_path = '/tmp/ncdu_%s.json' % int(time.time())

    def call_ncdu(self):
        path_to_find = self.args.path
        # 调用 ncdu，结果输出到文件
        ncdu_command = "ncdu -qxo %s %s" % (self.ncdu_output_file_path, path_to_find)
        status, _ = commands.getstatusoutput(ncdu_command)
        if status != 0:
            print "'%s' 执行出错" % ncdu_command
            sys.exit(1)

    def remove_ncdu_tmp_file(self):
        if os.path.isfile(self.ncdu_output_file_path):
            os.remove(self.ncdu_output_file_path)

    def recurse_ncdu_dir_obj(self, parent_dir_name, file_or_dir_list_obj):
        for file_or_dir_obj in file_or_dir_list_obj:
            if isinstance(file_or_dir_obj, dict):
                file_name = os.path.join(parent_dir_name, file_or_dir_obj.get('name', ''))
                file_size = file_or_dir_obj.get('asize')
                print file_size
                if file_size > self.args.larger_than * MB:
                    yield (file_name, round(file_size / MB, 2))
            else:  # list 的情况
                file_name = os.path.join(parent_dir_name, file_or_dir_obj[0].get('name', ''))
                self.recurse_ncdu_dir_obj(file_name, file_or_dir_obj)

    def parse_ncdu_output_json_file(self):
        # TODO: 文件太大的话内存会爆，如何将 json 文件像数据库一样读取而不是一次性直接 load 到内存？
        with open(self.ncdu_output_file_path, 'r') as json_file:
            dirs_obj = json.load(json_file)[3]
            for file_to_find, size in self.recurse_ncdu_dir_obj(dirs_obj[0].get('name', ''), dirs_obj):
                print "%s   %s(MB)" % (file_to_find, size)


if __name__ == '__main__':
    finder = FindLargeFiles()
    finder.call_ncdu()
    finder.parse_ncdu_output_json_file()
    finder.remove_ncdu_tmp_file()
