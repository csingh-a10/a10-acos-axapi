#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Copyright 2021 A10 Networks
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

REQUIRED_NOT_SET = (False, "One of ({}) must be set.")
REQUIRED_MUTEX = (False, "Only one of ({}) can be set.")
REQUIRED_VALID = (True, "")


DOCUMENTATION = r'''
module: a10_cgnv6_lsn_rule_list
description:
    - Configure LSN Rule-List
author: A10 Networks 2021
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
    name:
        description:
        - "LSN Rule-List Name"
        type: str
        required: True
    http_match_domain_name:
        description:
        - "Enable match domain name in http request"
        type: bool
        required: False
    uuid:
        description:
        - "uuid of the object"
        type: str
        required: False
    user_tag:
        description:
        - "Customized tag"
        type: str
        required: False
    domain_ip:
        description:
        - "Field domain_ip"
        type: dict
        required: False
        suboptions:
            uuid:
                description:
                - "uuid of the object"
                type: str
            sampling_enable:
                description:
                - "Field sampling_enable"
                type: list
    default:
        description:
        - "Field default"
        type: dict
        required: False
        suboptions:
            rule_cfg:
                description:
                - "Field rule_cfg"
                type: list
            uuid:
                description:
                - "uuid of the object"
                type: str
            sampling_enable:
                description:
                - "Field sampling_enable"
                type: list
    domain_name_list:
        description:
        - "Field domain_name_list"
        type: list
        required: False
        suboptions:
            name_domain:
                description:
                - "Configure a Specific Rule-Set (Domain Name)"
                type: str
            rule_cfg:
                description:
                - "Field rule_cfg"
                type: list
            uuid:
                description:
                - "uuid of the object"
                type: str
            user_tag:
                description:
                - "Customized tag"
                type: str
            sampling_enable:
                description:
                - "Field sampling_enable"
                type: list
    domain_list_name_list:
        description:
        - "Field domain_list_name_list"
        type: list
        required: False
        suboptions:
            name_domain_list:
                description:
                - "Configure a Specific Rule-Set (Domain List Name)"
                type: str
            rule_cfg:
                description:
                - "Field rule_cfg"
                type: list
            uuid:
                description:
                - "uuid of the object"
                type: str
            user_tag:
                description:
                - "Customized tag"
                type: str
            sampling_enable:
                description:
                - "Field sampling_enable"
                type: list
    ip_list:
        description:
        - "Field ip_list"
        type: list
        required: False
        suboptions:
            ipv4_addr:
                description:
                - "Configure a Specific Rule-Set (IP Network Address)"
                type: str
            rule_cfg:
                description:
                - "Field rule_cfg"
                type: list
            uuid:
                description:
                - "uuid of the object"
                type: str
            user_tag:
                description:
                - "Customized tag"
                type: str
            sampling_enable:
                description:
                - "Field sampling_enable"
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

# standard ansible module imports
from ansible.module_utils.basic import AnsibleModule

from ansible_collections.a10.acos_axapi.plugins.module_utils import \
    errors as a10_ex
from ansible_collections.a10.acos_axapi.plugins.module_utils import \
    wrapper as api_client
from ansible_collections.a10.acos_axapi.plugins.module_utils import \
    utils
from ansible_collections.a10.acos_axapi.plugins.module_utils.axapi_client import \
    client_factory
from ansible_collections.a10.acos_axapi.plugins.module_utils.kwbl import \
    KW_OUT, translate_blacklist as translateBlacklist


# Hacky way of having access to object properties for evaluation
AVAILABLE_PROPERTIES = ["default", "domain_ip", "domain_list_name_list", "domain_name_list", "http_match_domain_name", "ip_list", "name", "user_tag", "uuid", ]


def get_default_argspec():
    return dict(
        ansible_host=dict(type='str', required=True),
        ansible_username=dict(type='str', required=True),
        ansible_password=dict(type='str', required=True, no_log=True),
        state=dict(type='str', default="present", choices=['noop', 'present', 'absent']),
        ansible_port=dict(type='int', choices=[80, 443], required=True),
        a10_partition=dict(type='str', required=False, ),
        a10_device_context_id=dict(type='int', choices=[1, 2, 3, 4, 5, 6, 7, 8], required=False, ),
        get_type=dict(type='str', choices=["single", "list", "oper", "stats"]),
    )


def get_argspec():
    rv = get_default_argspec()
    rv.update({'name': {'type': 'str', 'required': True, },
        'http_match_domain_name': {'type': 'bool', },
        'uuid': {'type': 'str', },
        'user_tag': {'type': 'str', },
        'domain_ip': {'type': 'dict', 'uuid': {'type': 'str', }, 'sampling_enable': {'type': 'list', 'counters1': {'type': 'str', 'choices': ['all', 'placeholder']}}},
        'default': {'type': 'dict', 'rule_cfg': {'type': 'list', 'proto': {'type': 'str', 'choices': ['tcp', 'udp', 'icmp', 'others', 'dscp']}, 'tcp_cfg': {'type': 'dict', 'start_port': {'type': 'int', }, 'end_port': {'type': 'int', }, 'action_cfg': {'type': 'str', 'choices': ['action', 'no-action']}, 'action_type': {'type': 'str', 'choices': ['dnat', 'drop', 'one-to-one-snat', 'pass-through', 'snat', 'set-dscp', 'template']}, 'ipv4_list': {'type': 'str', }, 'port_list': {'type': 'str', }, 'no_snat': {'type': 'bool', }, 'vrid': {'type': 'int', }, 'pool': {'type': 'str', }, 'shared': {'type': 'bool', }, 'http_alg': {'type': 'str', }, 'dscp_direction': {'type': 'str', 'choices': ['inbound', 'outbound']}, 'dscp_value': {'type': 'str', 'choices': ['default', 'af11', 'af12', 'af13', 'af21', 'af22', 'af23', 'af31', 'af32', 'af33', 'af41', 'af42', 'af43', 'cs1', 'cs2', 'cs3', 'cs4', 'cs5', 'cs6', 'cs7', 'ef', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62', '63']}}, 'udp_cfg': {'type': 'dict', 'start_port': {'type': 'int', }, 'end_port': {'type': 'int', }, 'action_cfg': {'type': 'str', 'choices': ['action', 'no-action']}, 'action_type': {'type': 'str', 'choices': ['dnat', 'drop', 'one-to-one-snat', 'pass-through', 'snat', 'set-dscp']}, 'ipv4_list': {'type': 'str', }, 'port_list': {'type': 'str', }, 'no_snat': {'type': 'bool', }, 'vrid': {'type': 'int', }, 'pool': {'type': 'str', }, 'shared': {'type': 'bool', }, 'dscp_direction': {'type': 'str', 'choices': ['inbound', 'outbound']}, 'dscp_value': {'type': 'str', 'choices': ['default', 'af11', 'af12', 'af13', 'af21', 'af22', 'af23', 'af31', 'af32', 'af33', 'af41', 'af42', 'af43', 'cs1', 'cs2', 'cs3', 'cs4', 'cs5', 'cs6', 'cs7', 'ef', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62', '63']}}, 'icmp_others_cfg': {'type': 'dict', 'action_cfg': {'type': 'str', 'choices': ['action', 'no-action']}, 'action_type': {'type': 'str', 'choices': ['dnat', 'drop', 'one-to-one-snat', 'pass-through', 'snat', 'set-dscp']}, 'ipv4_list': {'type': 'str', }, 'no_snat': {'type': 'bool', }, 'vrid': {'type': 'int', }, 'pool': {'type': 'str', }, 'shared': {'type': 'bool', }, 'dscp_direction': {'type': 'str', 'choices': ['inbound', 'outbound']}, 'dscp_value': {'type': 'str', 'choices': ['default', 'af11', 'af12', 'af13', 'af21', 'af22', 'af23', 'af31', 'af32', 'af33', 'af41', 'af42', 'af43', 'cs1', 'cs2', 'cs3', 'cs4', 'cs5', 'cs6', 'cs7', 'ef', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62', '63']}}, 'dscp_cfg': {'type': 'dict', 'dscp_match': {'type': 'str', 'choices': ['default', 'af11', 'af12', 'af13', 'af21', 'af22', 'af23', 'af31', 'af32', 'af33', 'af41', 'af42', 'af43', 'cs1', 'cs2', 'cs3', 'cs4', 'cs5', 'cs6', 'cs7', 'ef', 'any', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62', '63']}, 'action_cfg': {'type': 'str', 'choices': ['action']}, 'action_type': {'type': 'str', 'choices': ['set-dscp']}, 'dscp_direction': {'type': 'str', 'choices': ['inbound', 'outbound']}, 'dscp_value': {'type': 'str', 'choices': ['default', 'af11', 'af12', 'af13', 'af21', 'af22', 'af23', 'af31', 'af32', 'af33', 'af41', 'af42', 'af43', 'cs1', 'cs2', 'cs3', 'cs4', 'cs5', 'cs6', 'cs7', 'ef', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62', '63']}}}, 'uuid': {'type': 'str', }, 'sampling_enable': {'type': 'list', 'counters1': {'type': 'str', 'choices': ['all', 'placeholder']}}},
        'domain_name_list': {'type': 'list', 'name_domain': {'type': 'str', 'required': True, }, 'rule_cfg': {'type': 'list', 'proto': {'type': 'str', 'choices': ['tcp', 'udp', 'icmp', 'others', 'dscp']}, 'tcp_cfg': {'type': 'dict', 'start_port': {'type': 'int', }, 'end_port': {'type': 'int', }, 'action_cfg': {'type': 'str', 'choices': ['action', 'no-action']}, 'action_type': {'type': 'str', 'choices': ['dnat', 'drop', 'one-to-one-snat', 'pass-through', 'snat', 'set-dscp', 'template']}, 'ipv4_list': {'type': 'str', }, 'port_list': {'type': 'str', }, 'no_snat': {'type': 'bool', }, 'vrid': {'type': 'int', }, 'pool': {'type': 'str', }, 'shared': {'type': 'bool', }, 'http_alg': {'type': 'str', }, 'dscp_direction': {'type': 'str', 'choices': ['inbound', 'outbound']}, 'dscp_value': {'type': 'str', 'choices': ['default', 'af11', 'af12', 'af13', 'af21', 'af22', 'af23', 'af31', 'af32', 'af33', 'af41', 'af42', 'af43', 'cs1', 'cs2', 'cs3', 'cs4', 'cs5', 'cs6', 'cs7', 'ef', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62', '63']}}, 'udp_cfg': {'type': 'dict', 'start_port': {'type': 'int', }, 'end_port': {'type': 'int', }, 'action_cfg': {'type': 'str', 'choices': ['action', 'no-action']}, 'action_type': {'type': 'str', 'choices': ['dnat', 'drop', 'one-to-one-snat', 'pass-through', 'snat', 'set-dscp']}, 'ipv4_list': {'type': 'str', }, 'port_list': {'type': 'str', }, 'no_snat': {'type': 'bool', }, 'vrid': {'type': 'int', }, 'pool': {'type': 'str', }, 'shared': {'type': 'bool', }, 'dscp_direction': {'type': 'str', 'choices': ['inbound', 'outbound']}, 'dscp_value': {'type': 'str', 'choices': ['default', 'af11', 'af12', 'af13', 'af21', 'af22', 'af23', 'af31', 'af32', 'af33', 'af41', 'af42', 'af43', 'cs1', 'cs2', 'cs3', 'cs4', 'cs5', 'cs6', 'cs7', 'ef', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62', '63']}}, 'icmp_others_cfg': {'type': 'dict', 'action_cfg': {'type': 'str', 'choices': ['action', 'no-action']}, 'action_type': {'type': 'str', 'choices': ['dnat', 'drop', 'one-to-one-snat', 'pass-through', 'snat', 'set-dscp']}, 'ipv4_list': {'type': 'str', }, 'no_snat': {'type': 'bool', }, 'vrid': {'type': 'int', }, 'pool': {'type': 'str', }, 'shared': {'type': 'bool', }, 'dscp_direction': {'type': 'str', 'choices': ['inbound', 'outbound']}, 'dscp_value': {'type': 'str', 'choices': ['default', 'af11', 'af12', 'af13', 'af21', 'af22', 'af23', 'af31', 'af32', 'af33', 'af41', 'af42', 'af43', 'cs1', 'cs2', 'cs3', 'cs4', 'cs5', 'cs6', 'cs7', 'ef', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62', '63']}}, 'dscp_cfg': {'type': 'dict', 'dscp_match': {'type': 'str', 'choices': ['default', 'af11', 'af12', 'af13', 'af21', 'af22', 'af23', 'af31', 'af32', 'af33', 'af41', 'af42', 'af43', 'cs1', 'cs2', 'cs3', 'cs4', 'cs5', 'cs6', 'cs7', 'ef', 'any', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62', '63']}, 'action_cfg': {'type': 'str', 'choices': ['action']}, 'action_type': {'type': 'str', 'choices': ['set-dscp']}, 'dscp_direction': {'type': 'str', 'choices': ['inbound', 'outbound']}, 'dscp_value': {'type': 'str', 'choices': ['default', 'af11', 'af12', 'af13', 'af21', 'af22', 'af23', 'af31', 'af32', 'af33', 'af41', 'af42', 'af43', 'cs1', 'cs2', 'cs3', 'cs4', 'cs5', 'cs6', 'cs7', 'ef', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62', '63']}}}, 'uuid': {'type': 'str', }, 'user_tag': {'type': 'str', }, 'sampling_enable': {'type': 'list', 'counters1': {'type': 'str', 'choices': ['all', 'placeholder']}}},
        'domain_list_name_list': {'type': 'list', 'name_domain_list': {'type': 'str', 'required': True, }, 'rule_cfg': {'type': 'list', 'proto': {'type': 'str', 'choices': ['tcp', 'udp', 'icmp', 'others', 'dscp']}, 'tcp_cfg': {'type': 'dict', 'start_port': {'type': 'int', }, 'end_port': {'type': 'int', }, 'action_cfg': {'type': 'str', 'choices': ['action', 'no-action']}, 'action_type': {'type': 'str', 'choices': ['dnat', 'drop', 'one-to-one-snat', 'pass-through', 'snat', 'set-dscp', 'template']}, 'ipv4_list': {'type': 'str', }, 'port_list': {'type': 'str', }, 'no_snat': {'type': 'bool', }, 'vrid': {'type': 'int', }, 'pool': {'type': 'str', }, 'shared': {'type': 'bool', }, 'http_alg': {'type': 'str', }, 'dscp_direction': {'type': 'str', 'choices': ['inbound', 'outbound']}, 'dscp_value': {'type': 'str', 'choices': ['default', 'af11', 'af12', 'af13', 'af21', 'af22', 'af23', 'af31', 'af32', 'af33', 'af41', 'af42', 'af43', 'cs1', 'cs2', 'cs3', 'cs4', 'cs5', 'cs6', 'cs7', 'ef', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62', '63']}}, 'udp_cfg': {'type': 'dict', 'start_port': {'type': 'int', }, 'end_port': {'type': 'int', }, 'action_cfg': {'type': 'str', 'choices': ['action', 'no-action']}, 'action_type': {'type': 'str', 'choices': ['dnat', 'drop', 'one-to-one-snat', 'pass-through', 'snat', 'set-dscp']}, 'ipv4_list': {'type': 'str', }, 'port_list': {'type': 'str', }, 'no_snat': {'type': 'bool', }, 'vrid': {'type': 'int', }, 'pool': {'type': 'str', }, 'shared': {'type': 'bool', }, 'dscp_direction': {'type': 'str', 'choices': ['inbound', 'outbound']}, 'dscp_value': {'type': 'str', 'choices': ['default', 'af11', 'af12', 'af13', 'af21', 'af22', 'af23', 'af31', 'af32', 'af33', 'af41', 'af42', 'af43', 'cs1', 'cs2', 'cs3', 'cs4', 'cs5', 'cs6', 'cs7', 'ef', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62', '63']}}, 'icmp_others_cfg': {'type': 'dict', 'action_cfg': {'type': 'str', 'choices': ['action', 'no-action']}, 'action_type': {'type': 'str', 'choices': ['dnat', 'drop', 'one-to-one-snat', 'pass-through', 'snat', 'set-dscp']}, 'ipv4_list': {'type': 'str', }, 'no_snat': {'type': 'bool', }, 'vrid': {'type': 'int', }, 'pool': {'type': 'str', }, 'shared': {'type': 'bool', }, 'dscp_direction': {'type': 'str', 'choices': ['inbound', 'outbound']}, 'dscp_value': {'type': 'str', 'choices': ['default', 'af11', 'af12', 'af13', 'af21', 'af22', 'af23', 'af31', 'af32', 'af33', 'af41', 'af42', 'af43', 'cs1', 'cs2', 'cs3', 'cs4', 'cs5', 'cs6', 'cs7', 'ef', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62', '63']}}, 'dscp_cfg': {'type': 'dict', 'dscp_match': {'type': 'str', 'choices': ['default', 'af11', 'af12', 'af13', 'af21', 'af22', 'af23', 'af31', 'af32', 'af33', 'af41', 'af42', 'af43', 'cs1', 'cs2', 'cs3', 'cs4', 'cs5', 'cs6', 'cs7', 'ef', 'any', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62', '63']}, 'action_cfg': {'type': 'str', 'choices': ['action']}, 'action_type': {'type': 'str', 'choices': ['set-dscp']}, 'dscp_direction': {'type': 'str', 'choices': ['inbound', 'outbound']}, 'dscp_value': {'type': 'str', 'choices': ['default', 'af11', 'af12', 'af13', 'af21', 'af22', 'af23', 'af31', 'af32', 'af33', 'af41', 'af42', 'af43', 'cs1', 'cs2', 'cs3', 'cs4', 'cs5', 'cs6', 'cs7', 'ef', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62', '63']}}}, 'uuid': {'type': 'str', }, 'user_tag': {'type': 'str', }, 'sampling_enable': {'type': 'list', 'counters1': {'type': 'str', 'choices': ['all', 'placeholder']}}},
        'ip_list': {'type': 'list', 'ipv4_addr': {'type': 'str', 'required': True, }, 'rule_cfg': {'type': 'list', 'proto': {'type': 'str', 'choices': ['tcp', 'udp', 'icmp', 'others', 'dscp']}, 'tcp_cfg': {'type': 'dict', 'start_port': {'type': 'int', }, 'end_port': {'type': 'int', }, 'action_cfg': {'type': 'str', 'choices': ['action', 'no-action']}, 'action_type': {'type': 'str', 'choices': ['dnat', 'drop', 'one-to-one-snat', 'pass-through', 'snat', 'set-dscp', 'template', 'idle-timeout']}, 'ipv4_list': {'type': 'str', }, 'port_list': {'type': 'str', }, 'no_snat': {'type': 'bool', }, 'vrid': {'type': 'int', }, 'pool': {'type': 'str', }, 'shared': {'type': 'bool', }, 'http_alg': {'type': 'str', }, 'timeout_val': {'type': 'int', }, 'fast': {'type': 'str', 'choices': ['fast']}, 'dscp_direction': {'type': 'str', 'choices': ['inbound', 'outbound']}, 'dscp_value': {'type': 'str', 'choices': ['default', 'af11', 'af12', 'af13', 'af21', 'af22', 'af23', 'af31', 'af32', 'af33', 'af41', 'af42', 'af43', 'cs1', 'cs2', 'cs3', 'cs4', 'cs5', 'cs6', 'cs7', 'ef', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62', '63']}}, 'udp_cfg': {'type': 'dict', 'start_port': {'type': 'int', }, 'end_port': {'type': 'int', }, 'action_cfg': {'type': 'str', 'choices': ['action', 'no-action']}, 'action_type': {'type': 'str', 'choices': ['dnat', 'drop', 'one-to-one-snat', 'pass-through', 'snat', 'set-dscp', 'idle-timeout']}, 'ipv4_list': {'type': 'str', }, 'port_list': {'type': 'str', }, 'no_snat': {'type': 'bool', }, 'vrid': {'type': 'int', }, 'pool': {'type': 'str', }, 'shared': {'type': 'bool', }, 'timeout_val': {'type': 'int', }, 'fast': {'type': 'str', 'choices': ['fast']}, 'dscp_direction': {'type': 'str', 'choices': ['inbound', 'outbound']}, 'dscp_value': {'type': 'str', 'choices': ['default', 'af11', 'af12', 'af13', 'af21', 'af22', 'af23', 'af31', 'af32', 'af33', 'af41', 'af42', 'af43', 'cs1', 'cs2', 'cs3', 'cs4', 'cs5', 'cs6', 'cs7', 'ef', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62', '63']}}, 'icmp_others_cfg': {'type': 'dict', 'action_cfg': {'type': 'str', 'choices': ['action', 'no-action']}, 'action_type': {'type': 'str', 'choices': ['dnat', 'drop', 'one-to-one-snat', 'pass-through', 'snat', 'set-dscp']}, 'ipv4_list': {'type': 'str', }, 'no_snat': {'type': 'bool', }, 'vrid': {'type': 'int', }, 'pool': {'type': 'str', }, 'shared': {'type': 'bool', }, 'dscp_direction': {'type': 'str', 'choices': ['inbound', 'outbound']}, 'dscp_value': {'type': 'str', 'choices': ['default', 'af11', 'af12', 'af13', 'af21', 'af22', 'af23', 'af31', 'af32', 'af33', 'af41', 'af42', 'af43', 'cs1', 'cs2', 'cs3', 'cs4', 'cs5', 'cs6', 'cs7', 'ef', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62', '63']}}, 'dscp_cfg': {'type': 'dict', 'dscp_match': {'type': 'str', 'choices': ['default', 'af11', 'af12', 'af13', 'af21', 'af22', 'af23', 'af31', 'af32', 'af33', 'af41', 'af42', 'af43', 'cs1', 'cs2', 'cs3', 'cs4', 'cs5', 'cs6', 'cs7', 'ef', 'any', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62', '63']}, 'action_cfg': {'type': 'str', 'choices': ['action']}, 'action_type': {'type': 'str', 'choices': ['set-dscp']}, 'dscp_direction': {'type': 'str', 'choices': ['inbound', 'outbound']}, 'dscp_value': {'type': 'str', 'choices': ['default', 'af11', 'af12', 'af13', 'af21', 'af22', 'af23', 'af31', 'af32', 'af33', 'af41', 'af42', 'af43', 'cs1', 'cs2', 'cs3', 'cs4', 'cs5', 'cs6', 'cs7', 'ef', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62', '63']}}}, 'uuid': {'type': 'str', }, 'user_tag': {'type': 'str', }, 'sampling_enable': {'type': 'list', 'counters1': {'type': 'str', 'choices': ['all', 'placeholder']}}}
    })
    return rv


def existing_url(module):
    """Return the URL for an existing resource"""
    # Build the format dictionary
    url_base = "/axapi/v3/cgnv6/lsn-rule-list/{name}"

    f_dict = {}
    f_dict["name"] = module.params["name"]

    return url_base.format(**f_dict)


def new_url(module):
    """Return the URL for creating a resource"""
    # To create the URL, we need to take the format string and return it with no params
    url_base = "/axapi/v3/cgnv6/lsn-rule-list/{name}"

    f_dict = {}
    f_dict["name"] = ""

    return url_base.format(**f_dict)


def report_changes(module, result, existing_config, payload):
    change_results = copy.deepcopy(result)
    if not existing_config:
        change_results["modified_values"].update(**payload)
        return change_results

    config_changes = copy.deepcopy(existing_config)
    for k, v in payload["lsn-rule-list"].items():
        v = 1 if str(v).lower() == "true" else v
        v = 0 if str(v).lower() == "false" else v

        if config_changes["lsn-rule-list"].get(k) != v:
            change_results["changed"] = True
            config_changes["lsn-rule-list"][k] = v

    change_results["modified_values"].update(**config_changes)
    return change_results


def create(module, result, payload={}):
    call_result = api_client.post(module.client, new_url(module), payload)
    result["axapi_calls"].append(call_result)
    result["modified_values"].update(
        **call_result["response_body"])
    result["changed"] = True
    return result


def update(module, result, existing_config, payload={}):
    call_result = api_client.post(module.client, existing_url(module), payload)
    result["axapi_calls"].append(call_result)
    if call_result["response_body"] == existing_config:
        result["changed"] = False
    else:
        result["modified_values"].update(
            **call_result["response_body"])
        result["changed"] = True
    return result


def present(module, result, existing_config):
    payload = utils.build_json("lsn-rule-list", module.params, AVAILABLE_PROPERTIES)
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
    result = dict(
        changed=False,
        messages="",
        modified_values={},
        axapi_calls=[]
    )

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

    module.client = client_factory(ansible_host, ansible_port,
                                   protocol, ansible_username,
                                   ansible_password)

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
            result["axapi_calls"].append(
                api_client.active_partition(module.client, a10_partition))

        if a10_device_context_id:
             result["axapi_calls"].append(
                api_client.switch_device_context(module.client, a10_device_context_id))

        existing_config = api_client.get(module.client, existing_url(module))
        result["axapi_calls"].append(existing_config)
        if existing_config['response_body'] != 'Not Found':
            existing_config = existing_config["response_body"]
        else:
            existing_config = None

        if state == 'present':
            result = present(module, result, existing_config)

        if state == 'absent':
            result = absent(module, result, existing_config)

        if state == 'noop':
            if module.params.get("get_type") == "single":
                result["axapi_calls"].append(
                    api_client.get(module.client, existing_url(module)))
            elif module.params.get("get_type") == "list":
                result["axapi_calls"].append(
                    api_client.get_list(module.client, existing_url(module)))
    except a10_ex.ACOSException as ex:
        module.fail_json(msg=ex.msg, **result)
    except Exception as gex:
        raise gex
    finally:
        if module.client.session.session_id:
            module.client.session.close()

    return result


def main():
    module = AnsibleModule(argument_spec=get_argspec(), supports_check_mode=True)
    result = run_command(module)
    module.exit_json(**result)


if __name__ == '__main__':
    main()
