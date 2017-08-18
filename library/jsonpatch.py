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
version_added: "1.0"
short_description: Edits JSON files
author:
  - Guillaume Smaha
requirements:
    - dpath
description:
This Ansible module can be used to add, delete, and update elements
within a JSON file.
options:
    name: path
        required: true
'''

EXAMPLES = '''
---
- hosts: all
  gather_facts: no
  become: no

  tasks:
    - name: Update json values
      jsonpatch:
        path: config.json
        target: tmp/config_update.json
        replace:
          path: '/_source/defaultIndex'
          value: 'artifactory-*'
        delete:
          path: '/found'
        insert:
          path: '/_source/__NEW__'
          value: '__TEXT__'

    - name: Update json no change
      jsonpatch:
        path: config.json
        target: tmp/config_nochange.json
        replace:
          path: '/_source/defaultIndex'
          value: 'filebeat-*'

    - name: Update json no change, force
      jsonpatch:
        path: config.json
        target: tmp/config_nochange_forced.json
        replace:
          path: '/_source/defaultIndex'
          value: 'filebeat-*'
        force: True

    - name: Update json indent, only if changed
      jsonpatch:
        path: config.json
        target: tmp/config_indent.json
        indent: 4
        replace:
          path: '/_source/defaultIndex'
          value: 'artifactory-*'

    - name: Execute multiple operation on json
      jsonpatch:
        path: config.json
        target: tmp/config_indent.json
        ops:
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
'''

from ansible.module_utils.basic import *
import os
import json
import codecs
from collections import OrderedDict

try:
    import dpath.util
except ImportError:
    dpath_found = False
else:
    dpath_found = True


def main():
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(required=True, default=None, type='str'),
            target=dict(required=False, default=None, type='str'),
            replace=dict(required=False, default={}, type='dict'),
            delete=dict(required=False, default={}, type='dict'),
            insert=dict(required=False, default={}, type='dict'),
            insertOrReplace=dict(required=False, default={}, type='dict'),
            ops=dict(required=False, default=[], type='list'),

            indent=dict(required=False, default=2, type='int'),
            force=dict(required=False, default=False, type='bool')
        ),
        required_one_of=[['replace', 'delete', 'insert', 'ops']],
        required_together=[
            ['path', 'replace'],
            ['path', 'delete'],
            ['path', 'insert'],
            ['path', 'insertOrReplace'],
            ['path', 'ops'],
        ],
        supports_check_mode=True
    )

    if not dpath_found:
        module.fail_json(msg="the python module dpath is required")

    params = module.params
    changed = False

    # Read JSON file
    json_obj = json.load(codecs.open(params['path'], 'r', 'utf-8-sig'),
                         object_pairs_hook=OrderedDict)

    # Apply operation
    if params['replace'] or params['delete'] or params['insert']:
        current_changed, json_obj = apply_operation(params, json_obj)
        changed = changed or current_changed

    if params['ops'] and params['ops'] != ['']:
        for operation in params['ops']:
            current_changed, json_obj = apply_operation(operation, json_obj)
            changed = changed or current_changed

    # Save output file
    output_file = params['path']
    if params['target']:
        output_file = params['target']

        if not os.path.isfile(output_file):
            changed = True

    if params['force']:
        changed = True

    if changed and not module.check_mode:
        with open(output_file, 'w') as outfile:
            json.dump(json_obj, outfile,
                      indent=params['indent'], sort_keys=False)

    # Send result and exit
    result = {'changed': changed}
    module.exit_json(**result)


def apply_operation(operation, json_obj):
    changed = False

    if 'replace' in operation and operation['replace']:
        old_val = dpath.util.get(json_obj,
                                 operation['replace']['path'])

        if old_val != operation['replace']['value']:
            dpath.util.set(json_obj,
                           operation['replace']['path'],
                           operation['replace']['value'])
            changed = True

    if 'delete' in operation and operation['delete']:
        dpath.util.delete(json_obj,
                          operation['delete']['path'])
        changed = True

    if 'insert' in operation and operation['insert']:
        dpath.util.new(json_obj,
                       operation['insert']['path'],
                       operation['insert']['value'])
        changed = True

    if 'insertOrReplace' in operation and operation['insertOrReplace']:
        try:
            old_val = dpath.util.get(json_obj,
                                     operation['insertOrReplace']['path'])
        except KeyError:
            dpath.util.new(json_obj,
                           operation['insertOrReplace']['path'],
                           operation['insertOrReplace']['value'])
            changed = True
        else:
            if old_val != operation['insertOrReplace']['value']:
                dpath.util.set(json_obj,
                               operation['insertOrReplace']['path'],
                               operation['insertOrReplace']['value'])
                changed = True

    return [changed, json_obj]


if __name__ == '__main__':
    main()
