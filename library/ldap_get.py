#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2017, Guillaume Smaha <guillaume.smaha@gmail.com>
#
ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'Guillaume Smaha'}


DOCUMENTATION = """
---
module: ldap_get
short_description: Search for an LDAP entries.
description:
  - Search for an LDAP entries by dn or filter and return the result
notes:
  - The default authentication settings will attempt to use a SASL EXTERNAL
    bind over a UNIX domain socket. This works well with the default Ubuntu
    install for example, which includes a cn=peercred,cn=external,cn=auth ACL
    rule allowing root to modify the server configuration. If you need to use
    a simple bind to access your server, pass the credentials in I(bind_dn)
    and I(bind_pw).
author:
  - Guillaume Smaha
requirements:
  - python-ldap
options:
  bind_dn:
    required: false
    default: null
    description:
      - A DN to bind with. If this is omitted, we'll try a SASL bind with
        the EXTERNAL mechanism. If this is blank, we'll use an anonymous
        bind.
  bind_pw:
    required: false
    default: null
    description:
      - The password to use with I(bind_dn).
  dn:
    required: false
    description:
      - The DN of the entry to add or update.
  base_scope:
    required: false
    description:
      - The base scope for the search_filter to search the entries.
  search_filter:
    required: false
    description:
      - The filter to search the entries to update ONLY.
  params:
    required: false
    default: null
    description:
      - List of options which allows to overwrite any of the task or the
        I(attributes) options. To remove an option, set the value of the option
        to C(null).
  server_uri:
    required: false
    default: ldapi:///
    description:
      - A URI to the LDAP server. The default value lets the underlying
        LDAP client library look for a UNIX domain socket in its default
        location.
  start_tls:
    required: false
    choices: ['yes', 'no']
    default: 'no'
    description:
      - If true, we'll use the START_TLS LDAP extension.
  validate_certs:
    required: false
    choices: ['yes', 'no']
    default: 'yes'
    description:
      - If C(no), SSL certificates will not be validated. This should only be
        used on sites using self-signed certificates.
  only_first:
    required: false
    choices: ['yes', 'no']
    default: 'no'
    description:
      - Define if the first is only returned.
        It is set to true when dn is defined
        
"""


EXAMPLES = """
- name: Return entry with dn
  ldap_get:
    dn: ou=users,dc=example,dc=com

- name: Return entry with dn
  ldap_get:
    dn: ou=users,dc=example,dc=com
    first_only: true

- name: Seach with a filter
  ldap_get:
    scope_base: "o=gluu"
    search_filter: "(objectClass=gluuPerson)"

#
# The same as in the previous example but with the authentication details
# stored in the ldap_auth variable:
#
# ldap_auth:
#   server_uri: ldap://localhost/
#   bind_dn: cn=admin,dc=example,dc=com
#   bind_pw: password
- name: Make sure we have an admin user
  ldap_get:
    params: "{{ ldap_auth }}"
    scope_base: "o=gluu"
    search_filter: "(objectClass=gluuPerson)"
"""


RETURN = """
entries:
  description: list of modified parameters
  returned: success
  type: list
  sample: '[[2, "olcRootDN", ["cn=root,dc=example,dc=com"]]]'
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.pycompat24 import get_exception

try:
    import ldap
    import ldap.modlist
    import ldap.sasl

    HAS_LDAP = True
except ImportError:
    HAS_LDAP = False


class LdapEntries(object):
    def __init__(self, module):
        # Shortcuts
        self.module = module
        self.server_uri = self.module.params['server_uri']
        self.bind_dn = self.module.params['bind_dn']
        self.bind_pw = self.module.params['bind_pw']
        self.start_tls = self.module.params['start_tls']
        self.verify_cert = self.module.params['validate_certs']
        self.dn = self.module.params['dn']
        self.base_scope = self.module.params['base_scope']
        self.search_filter = self.module.params['search_filter']

        # Establish connection
        self.connection = self._connect_to_ldap()

    def search_entries(self):
        """ Search with the serach_filter and return an array of entries """
        result = None
        if self.dn:
            try:
                result = self.connection.search_s(
                    self.dn, ldap.SCOPE_SUBTREE)
            except ldap.NO_SUCH_OBJECT:
                result = None
        else:
            try:
                result = self.connection.search_s(
                    self.search_filter, ldap.SCOPE_SUBTREE)
            except ldap.NO_SUCH_OBJECT:
                result = None

        return result

    def _connect_to_ldap(self):
        if not self.verify_cert:
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

        connection = ldap.initialize(self.server_uri)

        if self.start_tls:
            try:
                connection.start_tls_s()
            except ldap.LDAPError:
                e = get_exception()
                self.module.fail_json(msg="Cannot start TLS.", details=str(e))

        try:
            if self.bind_dn is not None:
                connection.simple_bind_s(self.bind_dn, self.bind_pw)
            else:
                connection.sasl_interactive_bind_s('', ldap.sasl.external())
        except ldap.LDAPError:
            e = get_exception()
            self.module.fail_json(
                msg="Cannot bind to the server.", details=str(e))

        return connection


def main():
    module = AnsibleModule(
        argument_spec={
            'server_uri': dict(default='ldapi:///'),
            'bind_dn': dict(),
            'bind_pw': dict(default='', no_log=True),
            'start_tls': dict(default=False, type='bool'),
            'validate_certs': dict(default=True, type='bool'),
            'dn': dict(),
            'base_scope': dict(),
            'search_filter': dict(),
            'first_only': dict(default='unknow'),
            'params': dict(type='dict'),
        },
        required_one_of=[['dn', 'search_filter']],
        supports_check_mode=True,
    )

    if module.params['first_only'] == 'unknow':
        if module.params['dn']:
            module.params['first_only'] = 'yes'
        else:
            module.params['first_only'] = 'no'

    if not HAS_LDAP:
        module.fail_json(
            msg="Missing required 'ldap' module (pip install python-ldap).")

    # Update module parameters with user's parameters if defined
    if 'params' in module.params and isinstance(module.params['params'], dict):
        for key, val in module.params['params'].items():
            if key in module.argument_spec:
                module.params[key] = val
            else:
                module.params['attributes'][key] = val

        # Remove the params
        module.params.pop('params', None)

    # Instantiate the LdapEntries object
    ldap_entries = LdapEntries(module)

    # Search for all entries
    entries = ldap_entries.search_entries()

    if not entries:
        if module.params['dn']:
            module.fail_json(
                msg="No entry found for this dn %s" % module.params['dn'],
                dn=module.params['dn'])
        else:
            module.fail_json(
                msg="No entry found for this search_filter %s" % module.params['search_filter'],
                base_scope=module.params['base_scope'],  search_filter=module.params['search_filter'])

    if module.params['first_only'] == 'yes':
        entries = entries[0]

    module.exit_json(results=entries)


if __name__ == '__main__':
    main()
