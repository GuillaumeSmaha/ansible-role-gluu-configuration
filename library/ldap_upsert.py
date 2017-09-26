#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2017, Guillaume Smaha <guillaume.smaha@gmail.com>
#
ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'Guillaume Smaha'}


DOCUMENTATION = """
---
module: ldap_upsert
short_description: Add or update LDAP entries.
description:
  - Add or update attributes LDAP entries.
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
  attributes:
    required: true
    default: null
    description:
      - Attributes necessary to create or update an entry.
        Each key can either be a string or an actual list of
        strings.
        It must contains the following key:
         - objectClass
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
"""


EXAMPLES = """
- name: Make sure we have a parent entry for users
  ldap_upsert:
    dn: ou=users,dc=example,dc=com
    attributes:
      objectClass: organizationalUnit

- name: Make sure we have an admin user
  ldap_upsert:
    dn: cn=admin,dc=example,dc=com
    attributes:
      objectClass:
        - simpleSecurityObject
        - organizationalRole
      description: An LDAP administrator
      userPassword: "{SSHA}tabyipcHzhwESzRaGA7oQ/SDoBZQOGND"

#
# The same as in the previous example but with the authentication details
# stored in the ldap_auth variable:
#
# ldap_auth:
#   server_uri: ldap://localhost/
#   bind_dn: cn=admin,dc=example,dc=com
#   bind_pw: password
- name: Make sure we have an admin user
  ldap_upsert:
    dn: cn=admin,dc=example,dc=com
    params: "{{ ldap_auth }}"
    attributes:
      objectClass:
        - simpleSecurityObject
        - organizationalRole
      description: An LDAP administrator
      userPassword: "{SSHA}tabyipcHzhwESzRaGA7oQ/SDoBZQOGND"
"""


RETURN = """
modlist:
  description: list of modified parameters
  returned: success
  type: list
  sample: '[[2, "olcRootDN", ["cn=root,dc=example,dc=com"]]]'
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.pycompat24 import get_exception
from ansible.module_utils.six import string_types

try:
    import ldap
    import ldap.modlist
    import ldap.sasl

    HAS_LDAP = True
except ImportError:
    HAS_LDAP = False


class LdapAttr(object):
    def __init__(self, module, connection, dn, name, values):
        # Shortcuts
        self.module = module
        self.connection = connection
        self.dn = dn
        self.name = name

        # Normalize values
        if isinstance(values, list):
            self.values = map(str, values)
        else:
            self.values = [str(values)]

    def update(self):
        try:
            results = self.connection.search_s(
                self.dn, ldap.SCOPE_BASE, attrlist=[self.name])
        except ldap.LDAPError:
            e = get_exception()
            self.module.fail_json(
                msg="Cannot search for attribute %s" % self.name,
                details=str(e))

        current = results[0][1].get(self.name, [])
        modlist = None

        if frozenset(self.values) != frozenset(current):
            if len(current) == 0:
                modlist = (ldap.MOD_ADD, self.name, self.values)
            elif len(self.values) == 0:
                modlist = (ldap.MOD_DELETE, self.name, None)
            else:
                modlist = (ldap.MOD_REPLACE, self.name, self.values)

        return modlist


class LdapEntry(object):
    def __init__(self, module, connection, dn):
        # Shortcuts
        self.module = module
        self.connection = connection
        self.dn = dn

        # Load attributes
        self.attrs = self._load_attrs()

    def _load_attrs(self):
        """ Turn attribute's value to array. """
        attrs = {}

        for name, value in self.module.params['attributes'].items():
            if name not in attrs:
                attrs[name] = []

            if isinstance(value, list):
                attrs[name] = value
            else:
                attrs[name].append(str(value))

        return attrs

    def exists(self):
        """ Return if self.dn exist. """
        return self._is_entry_present()

    def add(self):
        """ If self.dn does not exist, returns a callable that will add it. """
        def _add():
            self.connection.add_s(self.dn, modlist)
            return modlist

        modlist = ldap.modlist.addModlist(self.attrs)

        action = None
        if modlist:
            action = _add

        return action

    def update(self):
        """ If self.dn exist, returns a callable that will update it. """
        def _update():
            self.connection.modify_s(self.dn, modlist)
            return modlist

        modlist = []
        for (attr_name, attr_values) in self.attrs.items():
            ldap_attr = LdapAttr(self.module, self.connection,
                                 self.dn, attr_name, attr_values)
            op = ldap_attr.update()
            if op:
                modlist.append(op)

        action = None
        if modlist:
            action = _update

        return action

    def _is_entry_present(self):
        try:
            self.connection.search_s(self.dn, ldap.SCOPE_BASE)
        except ldap.NO_SUCH_OBJECT:
            is_present = False
        else:
            is_present = True

        return is_present


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
        """ Search with the serach_filter and return an array of dn """
        if self.dn:
            return [self.dn]

        try:
            result = self.connection.search_s(
                self.base_scope, ldap.SCOPE_SUBTREE, self.search_filter)
        except ldap.NO_SUCH_OBJECT:
            result = None
        else:
            # Get dn for each entry
            result = [res[0] for res in result]

        if not result:
            self.module.fail_json(
                msg="No entry found for this search_filter %s" % self.search_filter,
                search_filter=self.search_filter)

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
            'attributes': dict(required=True, type='dict'),
            'params': dict(type='dict'),
        },
        required_one_of=[['dn', 'search_filter']],
        supports_check_mode=True,
    )

    if not HAS_LDAP:
        module.fail_json(
            msg="Missing required 'ldap' module (pip install python-ldap).")

    # Check if objectClass is present when needed
    if 'objectClass' not in module.params['attributes']:
        module.fail_json(msg="At least one objectClass must be provided.")

    # Check if objectClass is of the correct type
    if (
            module.params['attributes']['objectClass'] is not None and not (
                isinstance(module.params['attributes']['objectClass'], string_types) or
                isinstance(module.params['attributes']['objectClass'], list))):
        module.fail_json(msg="objectClass must be either a string or a list.")

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

    entries_modlist = {}
    for dn_entry in entries:
        # Instantiate the LdapEntry object
        ldap_entry = LdapEntry(module, ldap_entries.connection, dn_entry)

        # Get the action function
        if ldap_entry.exists():
            action = ldap_entry.update()
        else:
            action = ldap_entry.add()

        # Perform the action
        if action is not None and not module.check_mode:
            try:
                modlist = action()
            except Exception:
                e = get_exception()
                # module.fail_json(msg="Entry action failed.", details=str(e))
                module.fail_json(msg="Entry action failed.", details=e)
            else:
                entries_modlist[dn_entry] = modlist

    count_modlist = sum(len(v) for v in entries_modlist.items())
    module.exit_json(changed=(count_modlist > 0), modlist=entries_modlist)


if __name__ == '__main__':
    main()
