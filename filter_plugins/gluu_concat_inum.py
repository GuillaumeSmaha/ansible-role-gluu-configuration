#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2017, Guillaume Smaha <guillaume.smaha@gmail.com>
#
ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'Guillaume Smaha'}

DOCUMENTATION = '''
---
filter: gluu_concat_inum
author: "Guillaume Smaha"
short_description: Look if the key "inum" exists in the object ; then concat inum organization and inum type to the inum
description:
Look if the key "inum" exists in the object ; then concat inum organization and inum type to the inum value
author:
  - Guillaume Smaha
options:
    name: base_inum
        required: true
        description:
            - Base INUM to concat.
    name: inum_type
        required: true
        description:
            - INUM type of the entry.
    name: dn
        required: false
        description:
            - Value of the organizationUnit (ou=...).
              If define, generate a full dn entry scope
'''

EXAMPLES = '''
---

gluu_object:
  inum: '1111!2020'

- hosts: localhost
  tasks:
    - name: Print a message
      debug:
        msg: "{{ gluu_object | gluu_concat_inum(base_inum='@!4025.CA62.9BB6.16C5!0001!2212.0010', type='0011') }}"

gluu_object:
  inum: '@!4025.CA62.9BB6.16C5!0001!2212.0010!0011!1111.2020'



gluu_object:
  inum: '1111!2020'

- hosts: localhost
  tasks:
    - name: Print a message
      debug:
        msg: "{{ gluu_object | gluu_concat_inum(base_inum='@!4025.CA62.9BB6.16C5!0001!2212.0010', type='0011', dn='people') }}"

gluu_object:
  inum: 'inum=@!4025.CA62.9BB6.16C5!0001!2212.0010!0011!1111.2020,ou=people,o=@!4025.CA62.9BB6.16C5!0001!2212.0010,o=gluu'



gluu_object:
  memberOf:
    - '1110'
    - '1120'

- hosts: localhost
  tasks:
    - name: Print a message
      debug:
        msg: "{{ gluu_object | gluu_concat_inum(key='memberOf', base_inum='@!4025.CA62.9BB6.16C5!0001!2212.0010', type='0011') }}"

gluu_object:
  memberOf:
    - '@!4025.CA62.9BB6.16C5!0001!2212.0010!0003!1110'
    - '@!4025.CA62.9BB6.16C5!0001!2212.0010!0003!1120'

'''

from ansible import errors
from ansible.module_utils.six import string_types


class FilterModule(object):
    def filters(self):
        return {
            'gluu_concat_inum': self.gluu_concat_inum
        }

    def render(self, base_inum, inum_type, value, dn=False):
        if dn:
            return 'inum=' + self.render(base_inum, inum_type, value) + ',ou=' + dn + ',o=' + base_inum + ',o=gluu'
        else:
            return base_inum + '!' + inum_type + '!' + value

    def gluu_concat_inum(self, content, key='inum', base_inum='', inum_type='', dn=False, *args, **kw):

        if not base_inum:
            raise errors.AnsibleFilterError(
                '[gluu_concat_inum] base_inum is required.')

        if not inum_type:
            raise errors.AnsibleFilterError(
                '[gluu_concat_inum] inum_type is required.')

        if isinstance(content, dict):
            return self.gluu_concat_inum_dict(content, key, base_inum, inum_type, dn)

        elif isinstance(content, list):
            return self.gluu_concat_inum_list(content, base_inum, inum_type, dn)

        elif isinstance(content, string_types):
            return self.render(base_inum, inum_type, content, dn)

        return content

    def gluu_concat_inum_dict(self, content, key, base_inum, inum_type, dn):
        if key not in content:
            raise errors.AnsibleFilterError(
                '[gluu_concat_inum] key is required for input dict.')

        if isinstance(content[key], list):
            for idx, value in enumerate(content[key]):
                content[key][idx] = self.render(
                    base_inum, inum_type, value, dn)
        else:
            content[key] = self.render(base_inum, inum_type, content[key], dn)

        return content

    def gluu_concat_inum_list(self, content, base_inum, inum_type, dn):

        for idx, value in enumerate(content):
            content[idx] = self.render(base_inum, inum_type, value, dn)

        return content
