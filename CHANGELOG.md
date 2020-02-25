# 1.2.0

- Update Gluu to 3.1.7

## Breaking change:

- `gluu_scripts` now uses a real dict for key `oxConfigurationProperty` and `oxModuleProperty`.
The keys will be converted by role directly to avoid implicit conversion from string to dict by python/ansible/jinja2.

    Before change:
    ```yaml
    gluu_scripts:
        inum: '2212.0010'
        displayName: basic_multi_ldap_auth
        description: Basic Multiple LDAP"Authentication
        gluuStatus: 'true'
        oxModuleProperty:
        - '{"value1":"location_type","value2":"ldap","description":""}'
        oxConfigurationProperty:
        - '{"value1":"auth_configuration_file","value2":"/etc/certs/basic_multi_ldap_auth.json","description":""}'
        oxLevel: 100
        programmingLanguage: python
        oxScriptType: person_authentication
        oxScript: "{{ lookup('template', 'templates/scripts/PersonAuthentication/BasicMultipleLdapAuth.py') }}"
    ```

    After change:
    ```yaml
    gluu_scripts:
        inum: '2212.0010'
        displayName: basic_multi_ldap_auth
        description: Basic Multiple LDAP"Authentication
        gluuStatus: 'true'
        oxModuleProperty:
        - value1: location_type
            value2: ldap
            description: ""
        oxConfigurationProperty:
        - value1: auth_configuration_file
            value2: /etc/gluu/conf/basic_multi_ldap_auth.json
            description: ""
        oxLevel: 100
        programmingLanguage: python
        oxScriptType: person_authentication
        oxScript: "{{ lookup('template', 'templates/scripts/PersonAuthentication/BasicMultipleLdapAuth.py') }}"
    ```
