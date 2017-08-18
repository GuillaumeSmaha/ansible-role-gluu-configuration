Ansible Gluu: configuration role
==========

**gluu-configuration** is an Ansible role to easily configure Gluu by creating or updating the entries in the LDAP server.

With this role, you can create or update:

- Global settings (applicances)
- oxAuth JSON configuration
- oxTrust JSON configuration
- Attributes
- OpenId Connect Scopes
- OpenId Connect Clients
- Groups
- Users
- Custom scripts

In cluster mode, this role also update the default authentication mode to use all servers with the 'LDAP' module.
To do this automaticly, the role will use the variable `gluu_internal_hostname` of each server with the 'LDAP' module.

This role can be used only on one node of the cluster.

To use the functionalities of the cluster mode in this role, all gluu servers have to be in the group `gluu-servers`
 and the Gluu Cluster Manager have to be in the group `gluu-cluster-manager`.


- [Requirements](#requirements)
- [Installation](#installation)
- [Update](#update)
- [Role Variables](#role-variables)
- [Deploying](#deploying)
- [Example Playbook](#example-playbook)
- [Sample projects](#sample-projects)

History
-------

Gluu's open source authentication & API access management server enables organizations to offer single sign-on, strong authentication, and centralize.

Requirements
------------

In order to deploy, you will need:

* Ansible in your deployer machine
* You also need to install this python dependencies:
  - dpath
  - pyDes
  - python3-ldap
  - ldap3
  - dnspython

```
$ pip install -r requirements.txt
```


Installation
------------

**gluu-configuration** is an Ansible role distributed globally using [Ansible Galaxy](https://galaxy.ansible.com/). In order to install **gluu-configuration** role you can use the following command.

```
$ ansible-galaxy install GuillaumeSmaha.gluu-configuration
```


Update
------

If you want to update the role, you need to pass **--force** parameter when installing. Please, check the following command:

```
$ ansible-galaxy install --force GuillaumeSmaha.gluu-configuration
```


Role Variables
--------------


```yaml
vars:

  # Define a custom version of the package to install.
  # To get a list of available package versions visit: https://gluu.org/docs/ce/
  gluu_version: 3.0.2


  # Global parameters:
  #   - **gluuScimEnabled**: Enable SCIM ? (enabled/disabled)
  #   - **gluuPassportEnabled**: Enable Passport ? (enabled/disabled)
  #   - **passwordResetAllowed**: Allow users to reset password ? (enabled/disabled)
  #   - **gluuOrgProfileMg**t: Allow users to edit their own profile ? (enabled/disabled)
  #   - **gluuVdsCacheRefreshPollingInterval**: Interval for cache refresh synchronization (value in minutes)
  #   - **gluuVdsCacheRefreshEnabled**: Enable cache refresh ? (enabled/disabled)
  #   - **oxTrustCacheRefreshServerIpAddress**: IP address of the recipient server for the cache refresh
  #   - **oxAuthenticationMode**: Authentication mode for the common authentication (default: auth_ldap_server)
  #   - **oxTrustAuthenticationMode**: Authentication mode for the oxTurst GUI authentication (default: auth_ldap_server)
  # *See https://github.com/GluuFederation/community-edition-setup/blob/version_3.0.2.1/templates/appliance.ldif*
  # Example to enable SCIM and set a custom script for authenticatio:
  # gluu_appliances:
  #   gluuScimEnabled: 'enabled'
  #   oxAuthenticationMode: 'basic_multi_ldap_auth'
  gluu_appliances:


  # This parameter allow to apply JSON operation on the oxTrust configuration for an attribute defined.
  #
  # It possible to use these operations:
  # - insert: Insert a new key. Throw an error if key already exist
  # - replace: Update a key. Throw an error if key doesn't exist
  # - delete: Delete a key
  # - insertOrReplace: Insert or update a key.
  #
  # List of the attributes and keys (not complete):
  # - oxTrustConfApplication *(See https://github.com/GluuFederation/community-edition-setup/blob/version_3.0.2.1/templates/oxtrust-config.json)*
  #   - oxAuthIssuer
  #   - umaIssuer
  #   - clientWhiteList
  #   - clientBlackList
  # - oxTrustConfCacheRefresh *(See https://github.com/GluuFederation/community-edition-setup/blob/version_3.0.2.1/templates/oxtrust-cache-refresh.json)*
  #   - sourceConfigs
  #   - inumConfig
  #   - targetConfig
  #   - keyAttributes
  #   - keyObjectClasses
  #   - sourceAttributes
  #   - customLdapFilter
  #   - updateMethod
  #   - keepExternalPerson
  #   - useSearchLimit
  #   - attributeMapping
  #   - snapshotFolder
  #   - snapshotMaxCount
  # - oxTrustConfImportPerson *(See https://github.com/GluuFederation/community-edition-setup/blob/version_3.0.2.1/templates/oxtrust-import-person.json)*
  #   - mappings
  #
  # Example to update ldap search size limit on the cache refrest configuration:
  # gluu_oxtrust_json_operations:
  #   oxTrustConfCacheRefresh:
  #     - insertOrReplace:
  #         path: '/ldapSearchSizeLimit'
  #         value: 1000
  gluu_oxtrust_json_operations:


  # This parameter allow to apply JSON operation on the oxAuth configuration for a defined attribute.
  #
  # It possible to use these operations:
  # - insert: Insert a new key. Throw an error if key already exist
  # - replace: Update a key. Throw an error if key doesn't exist
  # - delete: Delete a key
  # - insertOrReplace: Insert or update a key.
  #
  # List of the attributes and keys (not complete):
  # - oxAuthConfDynamic *(See https://github.com/GluuFederation/community-edition-setup/blob/version_3.0.2.1/templates/oxauth-config.json)*
  #   - shortLivedAccessTokenLifetime
  #   - umaIssuer
  #   - clientWhiteList
  #   - clientBlackList
  # - oxAuthConfStatic *(See https://github.com/GluuFederation/community-edition-setup/blob/version_3.0.2.1/templates/oxauth-static-conf.json)*
  # - oxAuthConfErrors *(See https://github.com/GluuFederation/community-edition-setup/blob/version_3.0.2.1/static/oxauth/oxauth-errors.json)*
  # - oxAuthConfWebKeys
  #
  # Example to update id token lifetimen:
  # gluu_oxauth_json_operations:
  #   oxAuthConfDynamic:
  #     - insertOrReplace:
  #         path: '/idTokenLifetime'
  #         value: 1000
  gluu_oxauth_json_operations:


  # Allow to add or update attributes.
  #
  # Example to add the last connection date:
  # gluu_attributes:
  #   -
  #     inum: '2213'
  #     displayName: Last Connection Date
  #     gluuAttributeName: oxLastLogonTime
  #     gluuAttributeOrigin: gluuPerson
  #     gluuAttributeType: generalizedTime
  #     gluuAttributeViewType:
  #       - user
  #       - admin
  #     gluuAttributeEditType:
  #       - user
  #     gluuStatus: active
  #     oxAuthClaimName: lastConnectionAt
  #     oxMultivaluedAttribute: false
  #     oxSCIMCustomAttribute: false
  #     gluuSAML1URI: urn:mace:dir:attribute-def:oxLastLogonTime
  #     gluuSAML2URI: oxAttribute:210
  #     description: Last Connection Date
  #
  # If `inum` is not set, the attribute `gluuAttributeName` will be used to search and update an existing entry.
  # _Note:_ The `inum` only need the value part of the inum value. The inum organization and type will be automaticly added.
  gluu_attributes:


  # Allow to add or update OpenId Connect Scopes.
  #
  # Example to update `openid` scope to add `inum` and `lastConnectionAt` attributes (`lastConnectionAt` comes from the previous attribute added):
  # gluu_openid_connect_scopes:
  #   -
  #     displayName: openid
  #     inum: 'F0C4'
  #     oxAuthClaim:
  #       - '29DA'
  #       - '2213'
  #
  # If `inum` is not set, the attribute `displayName` will be used to search and update an existing entry.
  # _Note:_ The `inum` only need the value part of the inum value. The inum organization and type will be automaticly added.
  # _Note 2:_ The list of inum for `oxAuthClaim` is available here: https://github.com/GluuFederation/community-edition-setup/blob/version_3.0.2.1/templates/attributes.ldif
  gluu_openid_connect_scopes:


  # Allow to add or update OpenId Connect Clients.
  #
  # Example to add a client:
  # gluu_openid_connect_clients:
  #   -
  #     displayName: Admin Client
  #     oxAuthClientSecret: admin
  #     inum: '2212.0010'
  #     oxAuthGrantType: implicit
  #     oxAuthAppType: native
  #     oxAuthResponseType:
  #       - id_token
  #       - token
  #     oxAuthScope:
  #       - '341A'
  #       - '764C'
  #       - 'F0C4'
  #       - 'C4F5.F66C'
  #       - '43F1'
  #       - '6D98'
  #       - '6D99'
  #       - '10B2'
  #     oxAuthTokenEndpointAuthMethod: client_secret_basic
  #     oxAuthTrustedClient: true
  #     oxAuthSubjectType: public
  #     oxAuthLogoutSessionRequired: false
  #     oxPersistClientAuthorizations: false
  #
  # If `inum` is not set, the attribute `displayName` will be used to search and update an existing entry.
  # _Note:_ The `inum` only need the value part of the inum value. The inum organization and type will be automaticly added.
  # _Note 2:_ The list of inum for `oxAuthScope` is available here: https://github.com/GluuFederation/community-edition-setup/blob/version_3.0.2.1/templates/scopes.ldif
  gluu_openid_connect_clients:


  # Allow to add or update Groups.
  #
  # Example to add a group:
  # gluu_groups:
  #   -
  #     inum: '0010'
  #     displayName: Admin users
  #     gluuGroupVisibility: private
  #     gluuStatus: active
  #     member:
  #       - '0000.1111.0010'
  #
  # If `inum` is not set, the attribute `displayName` will be used to search and update an existing entry.
  # _Note:_ The `inum` only need the value part of the inum value. The inum organization and type will be automaticly added.
  # _Note 2:_ To add an user into a group, you have to add it to the group and set the user as member of the group
  # _Note 3:_ Even if the member is not created yet, you can add it in the `member` list
  gluu_groups:


  # Allow to add or update Users.
  #
  # Example to add an user:
  # gluu_users:
  #   -
  #     inum: '0000.1111.0010'
  #     uid: myUser
  #     userPassword: test
  #     displayName: My User
  #     givenName: Guillaume
  #     sn: Smaha
  #     mail: gsmaha@mail.fr
  #     gluuStatus: active
  #     memberOf:
  #       - '0010'
  #
  # If `inum` is not set, the attribute `uid` will be used to search and update an existing entry.
  # _Note:_ The `inum` only need the value part of the inum value. The inum organization and type will be automaticly added.
  # _Note 2:_ To add an user into a group, you have to add it to the group and set the user as member of the group
  gluu_users:


  # Allow to add or update Scripts.
  #
  # Example to enable, update and add scripts:
  #   - Enable `basic_lock` script and set 10 maximun invalid login attemps
  #   - Update UMA authorization to update allowed clients (`Admin Client` created before)
  #   - Add a script for multiple LDAP authentication
  # gluu_scripts:
  #   -
  #     displayName: basic_lock
  #     gluuStatus: 'true'
  #     oxConfigurationProperty:
  #       - '{"value1":"invalid_login_count_attribute","value2":"oxCountInvalidLogin","description":""}'
  #       - '{"value1":"maximum_invalid_login_attemps","value2":"10","description":""}'
  #   -
  #     displayName: uma_authorization_policy
  #     gluuStatus: 'true'
  #     oxConfigurationProperty:
  #       - '{"value1":"allowed_clients","value2":"{{ gluu_inum_org }}!0008!2212.0010","description":""}'
  #   -
  #     inum: '2212.0010'
  #     displayName: basic_multi_ldap_auth
  #     description: Basic Multiple LDAP"Authentication
  #     gluuStatus: 'true'
  #     oxModuleProperty:
  #       - '{"value1":"location_type","value2":"ldap","description":""}'
  #     oxConfigurationProperty:
  #       - '{"value1":"auth_configuration_file","value2":"/etc/certs/basic_multi_ldap_auth.json","description":""}'
  #     oxLevel: 100
  #     programmingLanguage: python
  #     oxScriptType: person_authentication
  #     oxScript: "{{ lookup('template', 'templates/scripts/PersonAuthentication/BasicMultipleLdapAuth.py') }}"
  #
  # If `inum` is not set, the attribute `displayName` will be used to search and update an existing entry.
  # _Note:_ The `inum` only need the value part of the inum value. The inum organization and type will be automaticly added.
  # _Note 2:_ After Gluu 3.1.x, `uma_authorization_policy` becomes `uma_rpt_policy`.
  gluu_scripts:


  # ===================================
  # Gluu on multiple nodes (cluster)
  # ===================================


  # Define if the server is in a cluster.
  # When gluu_cluster = True, the default authentication mode to use all servers with the 'LDAP' module or the defined list.
  gluu_cluster: False


  # When gluu_cluster = True, you can set the hostnames of external LDAP servers of Gluu.
  # By default, List of all servers with the LDAP module installed
  # For example, a simple consumer server installed only with oxauth module will use this parameter with the hostname of the two mains servers.
  # Example:
  #   gluu_ldap_hostname: 192.168.1.101:1636,192.168.1.102:1636
  gluu_ldap_hostname:


  # Only when gluu_cluster = True.
  # The aim of this parameter is to distingish the internal hostname and the external hostname (gluu_hostname).
  # External hostname will be called from outside and it is a load balancer like nginx. All Gluu servers will be setup with the external hostname.
  # But to connect all nodes of the cluster to the LDAP servers, it needs to have an internal hostname that will not call the external hostname.
  # By default, it is equal to the gluu_hostname
  gluu_internal_hostname: '{{ gluu_hostname }}'
```

Deploying
---------

In order to deploy, you need to perform some steps:

* Create a new `hosts` file. Check [ansible inventory documentation](http://docs.ansible.com/intro_inventory.html) if you need help.
* Create a new playbook for deploying your app, for example, `deploy.yml`
* Set up role variables (see [Role Variables](#role-variables))
* Include the `GuillaumeSmaha.gluu-configuration` role as part of a play
* Run the deployment playbook

```ansible-playbook -i hosts deploy.yml```

If everything has been set up properly, this command will install Gluu Cluster Manager on the host.


Example Playbook
----------------

In the folder, example you can check an example project that shows how to deploy.

In order to run it, you will need to have Vagrant and the role installed. Please check https://www.vagrantup.com for more information about Vagrant and our Installation section.

```
$ cd example
$ vagrant plugin install vagrant-lxc
$ vagrant plugin install vagrant-hostmanager
$ vagrant up --provider=lxc
$ ansible-galaxy install GuillaumeSmaha.gluu-setup GuillaumeSmaha.gluu-configuration
$ ansible-playbook -i env/ubuntu deploy.yml
$ ansible-playbook -i env/centos deploy.yml
```

Access to Gluu by going to:

https://gluu-configuration-ubuntu/

or

https://gluu-configuration-centos/


You can connect on GLuu with this user credentials:

- Username: myUser
- Password: test


Sample projects
---------------
You can find a full example of a playbook here:

https://github.com/GuillaumeSmaha/ansible-gluu-playbook





