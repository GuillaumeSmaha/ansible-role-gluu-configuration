#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2017, Guillaume Smaha <guillaume.smaha@gmail.com>
#
ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'Guillaume Smaha'}

DOCUMENTATION = '''
---
module: jsonpatch
author: "Guillaume Smaha"
short_description: Filter to apply operation on JSON object to add, update or delete elements
requirements:
    - dpath
description:
Filter to apply operation on JSON object to add, update or delete elements
author:
  - Guillaume Smaha
options:
    name: operations
        required: true
        description: List of the operations on the JSON object
'''

EXAMPLES = '''
---
- hosts: all
  gather_facts: no
  become: no

  tasks:
    - set_fact:
        operations:
            - delete:
                path: '/found'
            - replace:
                path: '/_source/defaultIndex'
                value: 'artifactory-*'
            - insert:
                path: '/_source/__NEW2__'
                value: 'TEST'
            - insertOrReplace:
                path: '/author'
                value: 'TEST'
            - replace:
                path: '/version'
                value: '3'



    - name: Print JSON updated
      debug:
        msg: "{{'test'| jsonpatch(ops=operations, to_json=True)}}"
'''

from ansible import errors
from ansible.module_utils.basic import *
import json
from collections import OrderedDict
from ansible.module_utils.six import string_types

try:
    import dpath.util
except ImportError:
    dpath_found = False
else:
    dpath_found = True


class FilterModule(object):
    def filters(self):
        return {
            'jsonpatch': self.jsonpatch
        }

    def jsonpatch(self, content, operations=None, to_json=False, *args, **kw):

        if not dpath_found:
            raise errors.AnsibleFilterError(
                '[jsonpatch] The python module dpath is required.')

        if isinstance(content, string_types):
            content = json.loads(content, encoding='utf-8-sig',
                                 object_pairs_hook=OrderedDict)

        if not isinstance(content, list) and not isinstance(content, dict):
            raise errors.AnsibleFilterError(
                '[jsonpatch] Input must be a list or an object. type: %s.' % (type(content)))

        if not isinstance(operations, list):
            raise errors.AnsibleFilterError('operations must be a list.')

        if not operations or operations == ['']:
            raise errors.AnsibleFilterError(
                '[jsonpatch] One operation is required at least.')

        for operation in operations:
            content = self.apply_operation(operation, content)

        if to_json:
            # Avoid whitespace to avoid implicit conversion to dict by python
            content = " " + json.dumps(content)

        return content

    def apply_operation(self, operation, json_obj):
        if 'replace' in operation and operation['replace']:
            old_val = dpath.util.get(json_obj,
                                     operation['replace']['path'])

            if old_val != operation['replace']['value']:
                dpath.util.set(json_obj,
                               operation['replace']['path'],
                               operation['replace']['value'])

        if 'delete' in operation and operation['delete']:
            dpath.util.delete(json_obj,
                              operation['delete']['path'])

        if 'insert' in operation and operation['insert']:
            dpath.util.new(json_obj,
                           operation['insert']['path'],
                           operation['insert']['value'])

        if 'insertOrReplace' in operation and operation['insertOrReplace']:
            try:
                old_val = dpath.util.get(json_obj,
                                         operation['insertOrReplace']['path'])
            except KeyError:
                dpath.util.new(json_obj,
                               operation['insertOrReplace']['path'],
                               operation['insertOrReplace']['value'])
            else:
                if old_val != operation['insertOrReplace']['value']:
                    dpath.util.set(json_obj,
                                   operation['insertOrReplace']['path'],
                                   operation['insertOrReplace']['value'])

        return json_obj
