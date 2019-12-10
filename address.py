# -*- coding: utf-8 -*-
#!/usr/bin/python2.7

#import boto3
import botocore
import urllib3
#import urllib
#import certifi
import json
#import os
import utils
import dynamodb_wrapper
from enum import Enum

'''
AWS Lambda handler
Entry point for Address
/address requensts will flow through here
'''


def lambda_handler(event, context):

    from address import address
    adr_svc = address()

    status_code = 200
    adr_svc.log.info(event)
    try:
        try:
            try:
                if event['context']['resource-path'] == "/address"\
                 and event['context']['http-method'] == "POST":
                    res = adr_svc.create_address(
                    json.dumps({
                        'address': event['body-json'],
                        'stage': event['context']['stage']
                        }).decode('utf-8')
                    )
                elif event['context']['resource-path'] == '/address'\
                and event['context']['http-method'] == "GET"\
                and event['params']['path'].get('addressId') is None:
                    res = adr_svc.list_addresses({
                          'address': None,
                          'stage': event['context']['stage']
                          })
                elif event['body']['context']['resource-path'] ==\
                 "/address/{addressId}"\
                and event['body']['context']['http-method'] == "PUT"\
                and event['path']['params'].get('addressId') is not None:
                    res = adr_svc.update_address({
                        'address': event['body-json'],
                        'stage': event['context']['stage']
                        })
                elif event['context']['resource-path'] ==\
                 '/address/{addressId}'\
                and event['context']['http-method'] == "GET"\
                and event['params']['path'].get('addressId') is not None:
                    res = adr_svc.get_address(
                        {'addressId': event['params']['path']['addressId'],
                          'stage': event['context']['stage']
                          })
                elif  event['context']['resource-path'] ==\
                 '/address/{addressId}'\
                and event['context']['http-method'] == "DELETE"\
                and event['path']['params'].get('addressId') is not None:
                    res = \
                    adr_svc.remove_address({
                        'addressId': event['params']['path']['addressId'],
                        'stage': event['context']['stage']
                          })
                else:
                    status_code = 403
                    res = "Request not valid"
            except KeyError as e:
                status_code = 404
                res = {
                    'Error': e.message,
                    'statusCode': status_code
                    }
                adr_svc.log.error(res)
        except urllib3.exceptions.ProtocolError as e:
            res = {
                'Error': e.message,
                'statusCode': e.status
                }
            adr_svc.log.error(res)
        output = res

    except botocore.exceptions.ClientError as e:
        output = json.dumps(
            {'status': e.response['ResponseMetadata']['HTTPStatusCode'],
                'body': 'Failed to update: %s' % e.response['Error']['Code']}
            )
        adr_svc.log.error(json.dumps(output))

    return output


class address():

    log = None

    adr_response = None

    country_svc = None

    state_svc = None

    def __init__(self):
        from address import state
        from address import country
        self.log = utils.setup_logging(__name__)
        self.adr_response = {}
        self.country_svc = country(self.log)
        self.state_svc = state(self.log)

    def create_address(self, address_req_obj):

        self.log.debug(address_req_obj)
        print("CRTADR: %s" % address_req_obj)

        if type(address_req_obj) is not dict:
            address_req_obj = json.loads(address_req_obj)

        trns_address_obj = None
        st_obj = None
        ctry_obj = None

        trns_address_obj = address_req_obj['address']
        stg = address_req_obj['stage']

        if trns_address_obj.get('country') is not None:
                ctry_obj = self.country_svc.create_country({
                    'country_obj': trns_address_obj['country'],
                    'stage': address_req_obj['stage']
                    })

        if trns_address_obj.get('state') is not None\
         and trns_address_obj.get('country') is not None:
            state_obj = trns_address_obj['state']
            state_obj['countryCode'] =\
             trns_address_obj['country']['countryCode']

            st_obj = self.state_svc.create_state({
                    'state_obj': state_obj,
                    'stage': address_req_obj['stage']
                })

        if st_obj is not None:
            self.log.debug("ST_OBJ: %s" % st_obj)
            trns_address_obj['stateId'] = st_obj['stateId']
        if ctry_obj is not None:
            self.log.debug("CTRY_OBJ: %s" % ctry_obj)
            trns_address_obj['countryId'] = ctry_obj['countryId']

        adr_table = dynamodb_wrapper.create_table(**{
                                'dynamodb': dynamodb_wrapper.get_resource(),
                                'table_name': "address",
                                'stage': stg
                            })
        adr_obj = dynamodb_wrapper.add_item(**{
                        'table_struct': adr_table,
                        'item': {
                                'Item': trns_address_obj
                            }
                    })

        trns_address_obj['addressId'] = adr_obj['addressId']

        return trns_address_obj

    def update_address(self, address_req_obj):
        from address import merchant_type
        import utils

        st_obj = None

        ctry_obj = None

        trns_address_obj = address_req_obj['address']

        address_req_obj['id'] = trns_address_obj['addressId']

        adr_obj = self.get_address(address_req_obj)

        self.log.debug("UPDADR: %s" % adr_obj)

        if trns_address_obj.get('country') is not None:
                cntry_obj = trns_address_obj['country']
                ctry_obj = self.country_svc.create_country({
                    'country_obj': {
                        'countryName':
                        cntry_obj['countryName'],
                        'countryCode':
                        cntry_obj.get('countryCode')
                        },
                    'stage': address_req_obj['stage']
                    })

        if trns_address_obj.get('state') is not None:
            state_obj = trns_address_obj['state']
            if trns_address_obj['state'].get('countryCode') is None \
            and trns_address_obj.get('country') is not None:
                state_obj['countryCode'] =\
                     trns_address_obj['country']['countryCode']

            self.log.debug("CRTST: %s" % state_obj)

            st_obj = self.state_svc.create_state({
                    'state_obj': {
                        'stateName': state_obj['stateName'],
                        'countryCode': state_obj['countryCode']
                        },
                    'stage': address_req_obj['stage']
                })

            self.log.debug("STC: %s" % st_obj)

        if st_obj is not None:
            self.log.debug("ST_OBJ: %s" % st_obj)
            trns_address_obj['stateId'] = st_obj['stateId']
        if ctry_obj is not None:
            self.log.debug("CTRY_OBJ: %s" % ctry_obj)
            trns_address_obj['countryId'] = ctry_obj['countryId']

        adr_obj = utils.update_old_with_new(
            merchant_type.TRANSPIRE['address']
             if type(merchant_type.TRANSPIRE) is dict
             else merchant_type.TRANSPIRE.value['address'],
            adr_obj,
            trns_address_obj
            )

        address_table_opts = {}
        address_item_opts = {}
        address_table_opts['dynamodb'] = dynamodb_wrapper.get_resource()
        address_table_opts['table_name'] = "address"
        address_table_opts['stage'] = address_req_obj['stage']
        address_item_opts['table_struct'] = dynamodb_wrapper.create_table(
            **address_table_opts)
        address_item_opts['item'] = {'Item': adr_obj}

        self.log.debug("UPDARDOBJ %s" % adr_obj)

        upd_adr = dynamodb_wrapper.add_item(**address_item_opts)

        self.log.debug("UPDARD_ITM: %s" % upd_adr)

        return upd_adr

    def get_address(self, req_obj):
        self.log.debug("GETADR: %s" % req_obj)
        tbl_opts = {
            'dynamodb': dynamodb_wrapper.get_resource(),
            'table_name': 'address',
            'stage': req_obj['stage']
            }
        itm_opts = {
            'table_struct': dynamodb_wrapper.create_table(**tbl_opts),
            'item': {
                 'Item': {
                     'addressId': req_obj['id']
                     }
                }
            }

        return dynamodb_wrapper.get_item(**itm_opts)

    def list_addresses(self, req_obj):

        tbl_opts = {
            'dynamodb': dynamodb_wrapper.get_resource(),
            'table_name': 'address',
            'stage': req_obj['stage']
            }
        itm_opts = {
            'table_struct': dynamodb_wrapper.create_table(**tbl_opts),
            'item': {
                 'Item': {
                     }
                }
            }

        return dynamodb_wrapper.scan_item(**itm_opts)

    def remove_address(self, req_obj):
        tbl_opts = {
            'dynamodb': dynamodb_wrapper.get_resource(),
            'table_name': 'address',
            'stage': req_obj['stage']
            }
        itm_opts = {
            'table_struct': dynamodb_wrapper.create_table(**tbl_opts),
            'item': {
                 'Item': {
                         'addressId': req_obj['id']
                     }
                }
            }

        return dynamodb_wrapper.remove_item(**itm_opts)


class state():

    state_lst = None

    state_obj = None

    log = None

    def __init__(self, log=None):
        self.state_lst = []
        if log is not None:
            self.log = log
        else:
            self.log = utils.setup_logging(__name__)

    def create_state(self, state_req_obj):

        st_obj = self.get_state(state_req_obj)

        self.log.debug("STOBJ: %s" % st_obj)

        if st_obj is not None:
            return st_obj

        st_table = dynamodb_wrapper.create_table(**{
                            'dynamodb': dynamodb_wrapper.get_resource(),
                            'table_name': "state",
                            'stage': state_req_obj['stage']
                        })

        st_obj = dynamodb_wrapper.add_item(**{
                        'table_struct': st_table,
                        'item': {
                                'Item': state_req_obj['state_obj']
                            }
                    })

        return st_obj

    def get_state(self, state_req_obj):
        st_table = dynamodb_wrapper.create_table(**{
                            'dynamodb': dynamodb_wrapper.get_resource(),
                            'table_name': "state",
                            'stage': state_req_obj['stage']
                        })

        st_obj = dynamodb_wrapper.scan_item(**{
                        'table_struct': st_table,
                        'item': {
                                'Item': state_req_obj['state_obj']
                            }
                    })

        if type(st_obj) is list:
            if len(st_obj) > 0:
                st_obj = st_obj[0]
            else:
                st_obj = None

        return st_obj

    def get_states(self, state_req_obj):
        st_table = dynamodb_wrapper.create_table(**{
                            'dynamodb': dynamodb_wrapper.get_resource(),
                            'table_name': "state",
                            'stage': state_req_obj['stage']
                        })

        sts_obj = dynamodb_wrapper.scan_item(**{
                        'table_struct': st_table,
                        'item': {
                                'Item': {
                                    }
                            }
                    })

        return sts_obj


class country():

    country_lst = None

    country_obj = None

    log = None

    def __init__(self, log=None):
        self.country_lst = []
        if log is not None:
            self.log = log
        else:
            self.log = utils.setup_logging(__name__)

    def create_country(self, country_req_obj):

        ct_obj = self.get_country(country_req_obj)

        self.log.debug("CTROBJ: %s" % ct_obj)

        if ct_obj is not None:
            return ct_obj

        ct_table = dynamodb_wrapper.create_table(**{
                            'dynamodb': dynamodb_wrapper.get_resource(),
                            'table_name': 'country',
                            'stage': country_req_obj['stage']
                        })

        self.country_obj = dynamodb_wrapper.add_item(**{
                        'table_struct': ct_table,
                        'item': {
                                'Item': country_req_obj['country_obj']
                            }
                    })

        return self.country_obj

    def get_country(self, country_req_obj):

        ct_table = dynamodb_wrapper.create_table(**{
                            'dynamodb': dynamodb_wrapper.get_resource(),
                            'table_name': 'country',
                            'stage': country_req_obj['stage']
                        })

        self.country_obj = dynamodb_wrapper.get_item(**{
                        'table_struct': ct_table,
                        'item': {
                                'Item': country_req_obj['country_obj']
                            }
                    })

        return self.country_obj

    def get_countries(self, country_req_obj):

        ct_table = dynamodb_wrapper.create_table(**{
                            'dynamodb': dynamodb_wrapper.get_resource(),
                            'table_name': 'country',
                            'stage': country_req_obj['stage']
                        })

        self.country_lst = dynamodb_wrapper.scan_item(**{
                        'table_struct': ct_table,
                        'item': {
                                'Item': {}
                            }
                    })

        return self.country_lst


class merchant_type(Enum):

    TRANSPIRE = {
        'addressId': None,
        'address': {
            'address': None,
            'city': None,
            'zipCode': None,
            'stateId': None,
            'countryId': None,
            'state': {
                'stateName': None,
                'stateCode': None,
                'countryCode': None,
            },
            'country': {
               'countryName': None,
               'countryCode': None
                 }
            },
        'origTimestamp': None,
        'updatedTimestamp': None,
        'deleted': None
        }
