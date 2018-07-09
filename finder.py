#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
import os
import time
import json
import argparse
import commands
from heapq import heappush, heappop


__version__ = 'v0.1.0'

MB = 1 << 20

HELP_TEXT = """调用 ncdu 来定位文件系统中占用了较大空间的文件、目录，使用前请先安装 ncdu，参考： https://dev.yorhel.nl/ncdu """


class FindLargeFiles(object):
    def __init__(self):
        self.files_to_list = list()
        self.parser = argparse.ArgumentParser(description=HELP_TEXT)
        self.parser.add_argument('path', type=str, nargs='?', default='.', help='要查找的路径')
        self.parser.add_argument('--version', '-V', action='version', version=__version__)
        self.parser.add_argument('--larger-than', '-M', type=float, default=100, help='查找大于多少MB的文件')
        self.parser.add_argument('--top', '-T', type=int, default=20, help='最后显示多少个文件')
        self.parser.add_argument('--exclude', help='排除的路径')
        self.parser.add_argument('--exclude-caches', action='store_true', help='排除Cache文件夹')
        self.args = self.parser.parse_args()
        self.ncdu_output_file_path = '/tmp/ncdu_%s.json' % int(time.time())

    def call_ncdu(self):
        path_to_find = self.args.path
        path_exclude = self.args.exclude
        # 调用 ncdu，结果输出到文件
        if path_exclude:
            ncdu_command = "ncdu -qx --exclude=%s -o %s %s" % (path_exclude, self.ncdu_output_file_path, path_to_find)
        else:
            ncdu_command = "ncdu -qxo %s %s" % (self.ncdu_output_file_path, path_to_find)

        if self.args.exclude_caches:
            ncdu_command += ' --exclude-caches'
        commands.getstatusoutput(ncdu_command)

    def remove_ncdu_tmp_file(self):
        if os.path.isfile(self.ncdu_output_file_path):
            os.remove(self.ncdu_output_file_path)

    def select_top_files(self, file_tuple):
        if len(self.files_to_list) < self.args.top:
            heappush(self.files_to_list, file_tuple)
        else:
            heappush(self.files_to_list, file_tuple)
            heappop(self.files_to_list)

    def recurse_ncdu_dir_obj(self, parent_dir_name, file_or_dir_list_obj):
        for file_or_dir_obj in file_or_dir_list_obj:
            if isinstance(file_or_dir_obj, dict):
                file_name = os.path.join(parent_dir_name, file_or_dir_obj.get('name', ''))
                file_size = file_or_dir_obj.get('asize', 0)
                if file_size > self.args.larger_than * MB:
                    self.select_top_files((file_size, file_name))
            else:  # list 的情况
                file_name = os.path.join(parent_dir_name, file_or_dir_obj[0].get('name', ''))
                self.recurse_ncdu_dir_obj(file_name, file_or_dir_obj)

    def parse_ncdu_output_json_file(self):
        # TODO: 文件太大的话内存会爆，如何将 json 文件像数据库一样读取而不是一次性直接 load 到内存？
        with open(self.ncdu_output_file_path, 'r') as json_file:
            dirs_obj = json.load(json_file)[-1]
            dir_name = dirs_obj[0].get('name', '')
            self.recurse_ncdu_dir_obj(dir_name, dirs_obj)

    def output(self):
        self.files_to_list.sort(reverse=True)
        for file_size, file_name in self.files_to_list:
            print "%s   %.2f(MB)" % (file_name, (file_size / MB))


if __name__ == '__main__':
    finder = FindLargeFiles()
    finder.call_ncdu()
    finder.parse_ncdu_output_json_file()
    finder.output()
    finder.remove_ncdu_tmp_file()

