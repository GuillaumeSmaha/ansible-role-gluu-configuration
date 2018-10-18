#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2017, Guillaume Smaha <guillaume.smaha@gmail.com>
#
ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'Guillaume Smaha'}

DOCUMENTATION = '''
---
filter: line
author: "Guillaume Smaha"
short_description: Return a line of an input content
description:
Return a line of an input content by using lineNumber or regex
author:
  - Guillaume Smaha
'''

EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - name: Print a message
      debug:
        msg: "{{'test'| line(lineNumber=1)}}"
        msg: "{{'test'| line(regex=^d)}}"
'''


import re


class FilterModule(object):
    def filters(self):
        return {
            'line': self.line
        }

    def line(self, content, lineNumber=None, regexp=None, *args, **kw):

        lines = content.splitlines()
        if lineNumber:
            lines = [lines[lineNumber]]

        result = []
        if regexp:
            for line in lines:
                if re.match(regexp, line):
                    result.append(line)

        return '\n'.join(result)
