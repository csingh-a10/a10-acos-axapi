#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Copyright 2021 A10 Networks
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

REQUIRED_NOT_SET = (False, "One of ({}) must be set.")
REQUIRED_MUTEX = (False, "Only one of ({}) can be set.")
REQUIRED_VALID = (True, "")

DOCUMENTATION = r'''
module: a10_aam_authentication_relay_kerberos
description:
    - Kerberos Authentication Relay
author: A10 Networks
options:
    state:
        description:
        - State of the object to be created.
        choices:
          - noop
          - present
          - absent
        type: str
        required: True
    ansible_host:
        description:
        - Host for AXAPI authentication
        type: str
        required: True
    ansible_username:
        description:
        - Username for AXAPI authentication
        type: str
        required: True
    ansible_password:
        description:
        - Password for AXAPI authentication
        type: str
        required: True
    ansible_port:
        description:
        - Port for AXAPI authentication
        type: int
        required: True
    a10_device_context_id:
        description:
        - Device ID for aVCS configuration
        choices: [1-8]
        type: int
        required: False
    a10_partition:
        description:
        - Destination/target partition for object/command
        type: str
        required: False
    uuid:
        description:
        - "uuid of the object"
        type: str
        required: False
    sampling_enable:
        description:
        - "Field sampling_enable"
        type: list
        required: False
        suboptions:
            counters1:
                description:
                - "'all'= all; 'request-send'= Total Request Send; 'response-get'= Total Response
          Get; 'timeout-error'= Total Timeout; 'other-error'= Total Other Error;
          'request-normal'= Total Normal Request; 'request-dropped'= Total Dropped
          Request; 'response-success'= Total Success Response; 'response-failure'= Total
          Failure Response; 'response-error'= Total Error Response; 'response-timeout'=
          Total Timeout Response; 'response-other'= Total Other Response; 'job-start-
          error'= Total Job Start Error; 'polling-control-error'= Total Polling Control
          Error;"
                type: str
    instance_list:
        description:
        - "Field instance_list"
        type: list
        required: False
        suboptions:
            name:
                description:
                - "Specify Kerberos authentication relay name"
                type: str
            kerberos_realm:
                description:
                - "Specify the kerberos realm"
                type: str
            kerberos_kdc:
                description:
                - "Specify the kerberos kdc ip or host name"
                type: str
            kerberos_kdc_service_group:
                description:
                - "Specify an authentication service group as multiple KDCs"
                type: str
            kerberos_account:
                description:
                - "Specify the kerberos account name"
                type: str
            password:
                description:
                - "Specify password of Kerberos password"
                type: bool
            secret_string:
                description:
                - "The kerberos client password"
                type: str
            encrypted:
                description:
                - "Do NOT use this option manually. (This is an A10 reserved keyword.) (The
          ENCRYPTED secret string)"
                type: str
            port:
                description:
                - "Specify The KDC port, default is 88"
                type: int
            timeout:
                description:
                - "Specify timeout for kerberos transport, default is 10 seconds (The timeout,
          default is 10 seconds)"
                type: int
            uuid:
                description:
                - "uuid of the object"
                type: str
            sampling_enable:
                description:
                - "Field sampling_enable"
                type: list
    stats:
        description:
        - "Field stats"
        type: dict
        required: False
        suboptions:
            request_send:
                description:
                - "Total Request Send"
                type: str
            response_get:
                description:
                - "Total Response Get"
                type: str
            timeout_error:
                description:
                - "Total Timeout"
                type: str
            other_error:
                description:
                - "Total Other Error"
                type: str
            request_normal:
                description:
                - "Total Normal Request"
                type: str
            request_dropped:
                description:
                - "Total Dropped Request"
                type: str
            response_success:
                description:
                - "Total Success Response"
                type: str
            response_failure:
                description:
                - "Total Failure Response"
                type: str
            response_error:
                description:
                - "Total Error Response"
                type: str
            response_timeout:
                description:
                - "Total Timeout Response"
                type: str
            response_other:
                description:
                - "Total Other Response"
                type: str
            job_start_error:
                description:
                - "Total Job Start Error"
                type: str
            polling_control_error:
                description:
                - "Total Polling Control Error"
                type: str
            instance_list:
                description:
                - "Field instance_list"
                type: list

'''

RETURN = r'''
modified_values:
    description:
    - Values modified (or potential changes if using check_mode) as a result of task operation
    returned: changed
    type: dict
axapi_calls:
    description: Sequential list of AXAPI calls made by the task
    returned: always
    type: list
    elements: dict
    contains:
        endpoint:
            description: The AXAPI endpoint being accessed.
            type: str
            sample:
                - /axapi/v3/slb/virtual_server
                - /axapi/v3/file/ssl-cert
        http_method:
            description:
            - HTTP method being used by the primary task to interact with the AXAPI endpoint.
            type: str
            sample:
                - POST
                - GET
        request_body:
            description: Params used to query the AXAPI
            type: complex
        response_body:
            description: Response from the AXAPI
            type: complex
'''

EXAMPLES = """
"""

import copy

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.a10.acos_axapi.plugins.module_utils import \
    errors as a10_ex
from ansible_collections.a10.acos_axapi.plugins.module_utils import \
    wrapper as api_client
from ansible_collections.a10.acos_axapi.plugins.module_utils import \
    utils
from ansible_collections.a10.acos_axapi.plugins.module_utils.client import \
    client_factory
from ansible_collections.a10.acos_axapi.plugins.module_utils.kwbl import \
    KW_OUT, translate_blacklist as translateBlacklist

# Hacky way of having access to object properties for evaluation
AVAILABLE_PROPERTIES = ["instance_list", "sampling_enable", "stats", "uuid", ]


def get_default_argspec():
    return dict(
        ansible_host=dict(type='str', required=True),
        ansible_username=dict(type='str', required=True),
        ansible_password=dict(type='str', required=True, no_log=True),
        state=dict(type='str', default="present", choices=['noop', 'present', 'absent']),
        ansible_port=dict(type='int', choices=[80, 443], required=True),
        a10_partition=dict(type='str', required=False,
                           ),
        a10_device_context_id=dict(type='int', choices=[1, 2, 3, 4, 5, 6, 7, 8], required=False,
                                   ),
        get_type=dict(type='str', choices=["single", "list", "oper", "stats"]),
        )


def get_argspec():
    rv = get_default_argspec()
    rv.update({
        'uuid': {
            'type': 'str',
            },
        'sampling_enable': {
            'type': 'list',
            'counters1': {
                'type': 'str',
                'choices': ['all', 'request-send', 'response-get', 'timeout-error', 'other-error', 'request-normal', 'request-dropped', 'response-success', 'response-failure', 'response-error', 'response-timeout', 'response-other', 'job-start-error', 'polling-control-error']
                }
            },
        'instance_list': {
            'type': 'list',
            'name': {
                'type': 'str',
                'required': True,
                },
            'kerberos_realm': {
                'type': 'str',
                },
            'kerberos_kdc': {
                'type': 'str',
                },
            'kerberos_kdc_service_group': {
                'type': 'str',
                },
            'kerberos_account': {
                'type': 'str',
                },
            'password': {
                'type': 'bool',
                },
            'secret_string': {
                'type': 'str',
                },
            'encrypted': {
                'type': 'str',
                },
            'port': {
                'type': 'int',
                },
            'timeout': {
                'type': 'int',
                },
            'uuid': {
                'type': 'str',
                },
            'sampling_enable': {
                'type': 'list',
                'counters1': {
                    'type': 'str',
                    'choices': ['all', 'request-send', 'response-receive', 'current-requests-of-user', 'tickets']
                    }
                }
            },
        'stats': {
            'type': 'dict',
            'request_send': {
                'type': 'str',
                },
            'response_get': {
                'type': 'str',
                },
            'timeout_error': {
                'type': 'str',
                },
            'other_error': {
                'type': 'str',
                },
            'request_normal': {
                'type': 'str',
                },
            'request_dropped': {
                'type': 'str',
                },
            'response_success': {
                'type': 'str',
                },
            'response_failure': {
                'type': 'str',
                },
            'response_error': {
                'type': 'str',
                },
            'response_timeout': {
                'type': 'str',
                },
            'response_other': {
                'type': 'str',
                },
            'job_start_error': {
                'type': 'str',
                },
            'polling_control_error': {
                'type': 'str',
                },
            'instance_list': {
                'type': 'list',
                'name': {
                    'type': 'str',
                    'required': True,
                    },
                'stats': {
                    'type': 'dict',
                    'request_send': {
                        'type': 'str',
                        },
                    'response_receive': {
                        'type': 'str',
                        },
                    'current_requests_of_user': {
                        'type': 'str',
                        },
                    'tickets': {
                        'type': 'str',
                        }
                    }
                }
            }
        })
    return rv


def existing_url(module):
    """Return the URL for an existing resource"""
    # Build the format dictionary
    url_base = "/axapi/v3/aam/authentication/relay/kerberos"

    f_dict = {}

    return url_base.format(**f_dict)


def new_url(module):
    """Return the URL for creating a resource"""
    # To create the URL, we need to take the format string and return it with no params
    url_base = "/axapi/v3/aam/authentication/relay/kerberos"

    f_dict = {}

    return url_base.format(**f_dict)


def report_changes(module, result, existing_config, payload):
    change_results = copy.deepcopy(result)
    if not existing_config:
        change_results["modified_values"].update(**payload)
        return change_results

    config_changes = copy.deepcopy(existing_config)
    for k, v in payload["kerberos"].items():
        v = 1 if str(v).lower() == "true" else v
        v = 0 if str(v).lower() == "false" else v

        if config_changes["kerberos"].get(k) != v:
            change_results["changed"] = True
            config_changes["kerberos"][k] = v

    change_results["modified_values"].update(**config_changes)
    return change_results


def create(module, result, payload={}):
    call_result = api_client.post(module.client, new_url(module), payload)
    result["axapi_calls"].append(call_result)
    result["modified_values"].update(**call_result["response_body"])
    result["changed"] = True
    return result


def update(module, result, existing_config, payload={}):
    call_result = api_client.post(module.client, existing_url(module), payload)
    result["axapi_calls"].append(call_result)
    if call_result["response_body"] == existing_config:
        result["changed"] = False
    else:
        result["modified_values"].update(**call_result["response_body"])
        result["changed"] = True
    return result


def present(module, result, existing_config):
    payload = utils.build_json("kerberos", module.params, AVAILABLE_PROPERTIES)
    change_results = report_changes(module, result, existing_config, payload)
    if module.check_mode:
        return change_results
    elif not existing_config:
        return create(module, result, payload)
    elif existing_config and change_results.get('changed'):
        return update(module, result, existing_config, payload)
    return result


def delete(module, result):
    try:
        call_result = api_client.delete(module.client, existing_url(module))
        result["axapi_calls"].append(call_result)
        result["changed"] = True
    except a10_ex.NotFound:
        result["changed"] = False
    return result


def absent(module, result, existing_config):
    if not existing_config:
        result["changed"] = False
        return result

    if module.check_mode:
        result["changed"] = True
        return result

    return delete(module, result)


def run_command(module):
    result = dict(changed=False, messages="", modified_values={}, axapi_calls=[], ansible_facts={}, acos_info={})

    state = module.params["state"]
    ansible_host = module.params["ansible_host"]
    ansible_username = module.params["ansible_username"]
    ansible_password = module.params["ansible_password"]
    ansible_port = module.params["ansible_port"]
    a10_partition = module.params["a10_partition"]
    a10_device_context_id = module.params["a10_device_context_id"]

    if ansible_port == 80:
        protocol = "http"
    elif ansible_port == 443:
        protocol = "https"

    module.client = client_factory(ansible_host, ansible_port, protocol, ansible_username, ansible_password)

    valid = True

    run_errors = []
    if state == 'present':
        requires_one_of = sorted([])
        valid, validation_errors = utils.validate(module.params, requires_one_of)
        for ve in validation_errors:
            run_errors.append(ve)

    if not valid:
        err_msg = "\n".join(run_errors)
        result["messages"] = "Validation failure: " + str(run_errors)
        module.fail_json(msg=err_msg, **result)

    try:
        if a10_partition:
            result["axapi_calls"].append(api_client.active_partition(module.client, a10_partition))

        if a10_device_context_id:
            result["axapi_calls"].append(api_client.switch_device_context(module.client, a10_device_context_id))

        if state == 'present' or state == 'absent':
            existing_config = api_client.get(module.client, existing_url(module))
            result["axapi_calls"].append(existing_config)
            if existing_config['response_body'] != 'NotFound':
                existing_config = existing_config["response_body"]
            else:
                existing_config = None
        if state == 'present':
            result = present(module, result, existing_config)

        if state == 'absent':
            result = absent(module, result, existing_config)

        if state == 'noop':
            if module.params.get("get_type") == "single" or module.params.get("get_type") is None:
                get_result = api_client.get(module.client, existing_url(module))
                result["axapi_calls"].append(get_result)
                info = get_result["response_body"]
                result["acos_info"] = info["kerberos"] if info != "NotFound" else info
            elif module.params.get("get_type") == "list":
                get_list_result = api_client.get_list(module.client, existing_url(module))
                result["axapi_calls"].append(get_list_result)

                info = get_list_result["response_body"]
                result["acos_info"] = info["kerberos-list"] if info != "NotFound" else info
            elif module.params.get("get_type") == "stats":
                get_type_result = api_client.get_stats(module.client, existing_url(module), params=module.params)
                result["axapi_calls"].append(get_type_result)
                info = get_type_result["response_body"]
                result["acos_info"] = info["kerberos"]["stats"] if info != "NotFound" else info
    except a10_ex.ACOSException as ex:
        module.fail_json(msg=ex.msg, **result)
    except Exception as gex:
        raise gex
    finally:
        if module.client.auth_session.session_id:
            module.client.auth_session.close()

    return result


"""
    Custom class which override the _check_required_arguments function to check check required arguments based on state and get_type.
"""


class AcosAnsibleModule(AnsibleModule):

    def __init__(self, *args, **kwargs):
        super(AcosAnsibleModule, self).__init__(*args, **kwargs)

    def _check_required_arguments(self, spec=None, param=None):
        if spec is None:
            spec = self.argument_spec
        if param is None:
            param = self.params
        # skip validation if state is 'noop' and get_type is 'list'
        if not (param.get("state") == "noop" and param.get("get_type") == "list"):
            missing = []
            if spec is None:
                return missing
            # Check for missing required parameters in the provided argument spec
            for (k, v) in spec.items():
                required = v.get('required', False)
                if required and k not in param:
                    missing.append(k)
            if missing:
                self.fail_json(msg="Missing required parameters: {}".format(", ".join(missing)))


def main():
    module = AcosAnsibleModule(argument_spec=get_argspec(), supports_check_mode=True)
    result = run_command(module)
    module.exit_json(**result)


if __name__ == '__main__':
    main()
