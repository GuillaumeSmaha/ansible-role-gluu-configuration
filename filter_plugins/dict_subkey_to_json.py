#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2020, Guillaume Smaha <guillaume.smaha@gmail.com>
#
ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'Guillaume Smaha'}

DOCUMENTATION = '''
---
filter: dict_subkey_to_json
author: "Guillaume Smaha"
short_description: Convert a dict subkey to json an return the whole dict
description:
Convert a dict subkey to json an return the whole dict
author:
  - Guillaume Smaha
options:
    name: key
        required: true
        description: Key to find the value in the input dict
    name: in_list
        required: false
        description: Fail if dict value is not a list. Apply conversion for each element of the list in the dict value.
    name: ignore_notfound
        required: false
        description: Ignore error if key is not found
'''

EXAMPLES = '''
---
config:
  users:
  - abc
  - def
  - ghi
  teams:
  - name: team1
    memberOf:
    - jean
    - guillaume
  - name: team2
    memberOf:
    - bernard

- hosts: localhost
  tasks:
    - name: Print a message
      debug:
        msg: "{{ my_teams | dict_subkey_to_json(key='teams') }}"

config:
  users:
  - abc
  - def
  - ghi
  teams: [{"name":"team1","memberOf":["jean","guillaume"]},{"name":"team2","memberOf":["bernard"]}]



config:
  users:
  - abc
  - def
  - ghi
  teams:
  - name: team1
    memberOf:
    - jean
    - guillaume
  - name: team2
    memberOf:
    - bernard

- hosts: localhost
  tasks:
    - name: Print a message
      debug:
        msg: "{{ my_teams | dict_subkey_to_json(key='teams', in_list=True) }}"

config:
  users:
  - abc
  - def
  - ghi
  teams:
  - {"name":"team1","memberOf":["jean","guillaume"]}
  - {"name":"team2","memberOf":["bernard"]}

'''

import json
from ansible import errors
from ansible.module_utils.six import string_types


class FilterModule(object):
    def filters(self):
        return {
            'dict_subkey_to_json': self.dict_subkey_to_json
        }

    def dict_subkey_to_json(self, content, key, in_list=False, ignore_notfound=False):
        if not key:
          raise errors.AnsibleFilterError(
            '[dict_subkey_to_json] key is required.')

        if not isinstance(content, dict):
            raise errors.AnsibleFilterError(
              '[dict_subkey_to_json] content is not a dict.')

        if key not in content:
          if ignore_notfound:
            return content
          else:
            raise errors.AnsibleFilterError(
              '[dict_subkey_to_json] key is not found is not a dict.')

        if in_list:
            return self.dict_subkey_to_json_list(content, key)

        return self.dict_subkey_to_json_dict(content, key)

    def dict_subkey_to_json_dict(self, content, key):
        # Add whitespace to avoid implicit conversion to dict by python
        return " " + json.dumps(content[key])

    def dict_subkey_to_json_list(self, content, key):
        for idx, value in enumerate(content[key]):
            # Add whitespace to avoid implicit conversion to dict by python
            content[key][idx] = " " + json.dumps(content[key][idx])

        return content
