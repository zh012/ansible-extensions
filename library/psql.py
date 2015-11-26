#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import tempfile
import datetime

DOCUMENTATION = '''
---
module: psql
version_added: "historical"
short_description: Run psql command.
description:
     - The M(psql) module run sql script with postgresql client program psql.
options:
  host:
    description:
      - Postgresql host
    required: false
    default: localhost
  port:
    description:
      - Database connection port.
    required: false
    default: 5432
  dbname:
    description:
      - Database name
    required: false
    default: template1
  user:
    description:
      - Database user
    required: false
    default: postgres
  password:
    description:
      - Password of given user.
    required: false
    default: ""
  sql:
    description:
      - The sql to be run.
    required: true
author:
    - "Jerry Zhang"
notes:
   - The "psql" module require postgresql client program psql is installed in the remote machine.
'''

EXAMPLES = '''
# Example from Ansible Playbooks
- psql:
    sql: "select rolname from pg_roles;"
    host: db.server.address
    user: master
    password: youguess
'''

RETURN = '''
msg:
    description: the result of sql or error message
    returned: always
    type: string
'''


def main():

    module = AnsibleModule(
        # not checking because of daisy chain to file module
        argument_spec=dict(
            host=dict(required=False),
            port=dict(required=False),
            dbname=dict(required=False),
            user=dict(required=False),
            password=dict(required=False),
            options=dict(required=False, type='list'),
            sql=dict(required=True, type='str'),
        ),
    )

    host = module.params.get('host', 'localhost')
    port = module.params.get('port', '5432')
    dbname = module.params.get('dbname', 'postgres')
    user = module.params.get('user', 'postgres')
    password = module.params.get('password', '')
    options = module.params.get('options', [])
    sql = module.params['sql']

    if password:
        os.environ['PGPASSWORD'] = module.params['password']
    with tempfile.NamedTemporaryFile(mode='w', delete=True) as tf:
        tf.write(sql)
        tf.flush()
        args = ['psql', '-h', host, '-p', port, '-U', user, '-d', dbname, '-f', tf.name]
        args.extend(options)
        startd = datetime.datetime.now()
        rc, out, err = module.run_command(args, check_rc=True)
        endd = datetime.datetime.now()

    result = dict(
        rc=rc,
        start=str(startd),
        end=str(endd),
        delta=str(endd-startd),
        host=host,
        port=port,
        dbname=dbname,
        user=user
    )

    if 'ERROR' in err:
        result['failed'] = True
        result['msg'] = err.rstrip("\r\n")
        module.fail_json(**result)
    else:
        result['changed'] = True
        result['msg'] = out.rstrip("\r\n")
        module.exit_json(**result)

# import module snippets
from ansible.module_utils.basic import *
main()
