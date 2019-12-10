#!/usr/bin/python2.7

import boto3
import botocore
import urllib3
import urllib
import certifi
import json
import os
import dynamodb_wrapper

try:
    api_key = os.environ["apiKey"]
    api_cred = os.environ["apiCred"]
    api_region = os.environ["apiReg"]
    msh_user = os.environ['mshUser']
    msh_pwd = os.environ['mshUserPwd']
    msh_base_url = os.environ['mshBaseUrl']

except KeyError:
    api_key = None
    api_cred = None
    api_region = None
    msh_user = 'anz-demo2-transpire-miguel'
    msh_pwd = 'bkdr4#@NZ!ng'
    msh_base_url = \
    'https://provisioning.demo.msh.apac.services.ingenico.com/v1/'

'''
AWS Lambda handler
Entry point for Transpire ANZ-BlueApp Merchant
/merchant requensts will flow through here
'''


def lambda_handler(event, context):
    status_code = 200

    try:
        try:
            try:
                if event['body']['context']['resource-path'] == "/merchant"\
                 and event['body']['context']['http-method'] == "POST":
                    res = create_msh_merchant(
                    json.dumps(event['body']['body-json'])
                    )
                elif event['body']['context']['resource-path'] == "/merchant"\
                and event['body']['context']['http-method'] == "PUT":
                    res = update_anzpaid_merchant(
                        json.dumps(event['body']['body-json'])
                        )
                elif event['body']['context']['resource-path'] == "/merchant"\
                and event['body']['context']['http-method'] == "GET":
                    res = \
                    get_anzpaid_merchant(
                        event['body']['params']['path']['merchantId']
                        )
                elif event['body']['context']['resource-path'] == "/merchant"\
                and event['body']['context']['http-method'] == "DELETE":
                    res = \
                    remove_anzpaid_merchant(
                        event['body']['params']['path']['merchantId']
                        )
            except KeyError:
                status_code = 504
                res = {'Error': 'Could not find parameters',
                    'status': status_code}
        except urllib3.exceptions.ConnectionError as e:
            res = {'Error': 'Connection failed',
                 'status': e.status}

        output = json.loads(res)

    except botocore.exceptions.ClientError as e:
        output = json.dumps(
            {'statusCode': e.response['ResponseMetadata']['HTTPStatusCode'],
                'body': 'Failed to update: %s' % e.response['Error']['Code']}
            )

    return output

'''
Get a valid bearer token for Ingenico MSH
This functionality will be common to all API base paths
eg (/merchant /location /etc)
The bearer token needs to be passed in for all MSH API calls
'''


def get_msh_bearer_token():
    login_req = {'login': msh_user, 'password': msh_pwd, 'captcha': 'null'}
    body_encoded = urllib.urlencode(login_req)
    login_resp = urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED', ca_certs=certifi.where()).\
    request('POST', '%s%s' % (msh_base_url, 'login'),
    body=body_encoded,
    headers={'Content-Type': 'application/x-www-form-urlencoded'})
    if login_resp.status is not 200:
        raise urllib3.exceptions.ConnectionException(login_resp)
    token = login_resp.headers
    return token['authorization']


def list_msh_merchants():
    token = get_msh_bearer_token()
    get_merchants = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',
    ca_certs=certifi.where()).\
    request('GET', '%s%s' % (msh_base_url, 'merchants'),
    headers={'Authorization': token})
    if get_merchants.status is not 200:
        raise urllib3.exceptions.ConnectionException(get_merchants)
    return get_merchants.data


def create_msh_merchant(merchant_obj):

    token = get_msh_bearer_token()

    trns_merchant_obj = json.loads(merchant_obj)

    merchant_list = json.loads(list_msh_merchants())

    '''
    loop through the list looking for a matching name
    '''

    #for merchant_item in merchant_list:
        ##print(merchant_item['name'])
        #if merchant_item['name'] == trns_merchant_obj['merchantName']:
            #if trns_merchant_obj['merchantId'] == 0:
                #trns_merchant_obj['merchantServiceId'] = merchant_item['id']
                #trns_merchant_obj['programId'] = merchant_item['acquirerId']
            #return trns_merchant_obj

    msh_merchant_obj = {'merchant': {
        'name': '%s' % trns_merchant_obj['merchantName'],
        'programId': None,
        'address': None,
        'city': None,
        'zipCode': None,
        'state': None,
        'country': None,
        'selectedTags': {},
        'commercialContact': None,
        'supportContact': None,
        'merchantReference': None,
        'alipayMerchantId': None,
        'permissions':
            [
                'merchantSettingsManagement',
                'mPosUserManagement',
                'mPosEnrollment',
                'userManagement',
                'terminalManagement',
                'storeManagement',
                'posManagement',
                'tagManagement'
            ]
        }
    }

    new_merchant_req =\
    urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where()).\
    request('POST', '%s%s' % (msh_base_url, 'merchants'),
    body=json.dumps(msh_merchant_obj),
    headers={'Content-Type': 'application/json', 'Authorization': token})

    if new_merchant_req.status != 201:
        raise urllib3.exceptions.ConnectionError(new_merchant_req)

    #create merchant in DynamoDB
    print(new_merchant_req.data)
    trns_merchant_obj['merchantId'] = json.loads(new_merchant_req.data)['id']

    #trns_merchant_obj['programId'] =\
    #json.loads(new_merchant_req.data)['programId'] if not None else ""

    return trns_merchant_obj

'''
Create a new ANZPaidMerchant or return it if it exists
'''


def create_anzpaid_merchant(merchant_obj):
    merchant_table = get_anzpaid_merchant_table()
    msh_merchant_obj = create_msh_merchant(merchant_obj)
    merchant_obj['merchantServiceId'] = msh_merchant_obj['id']
    merchant_table.put_item(merchant_obj)

'''
Get the ANZPaid Merchant table via the wrapper functions
which will create it if it does not exist
and return the DynamoDB Table resource
'''


def get_anzpaid_merchant_table(**kwargs):

    kwargs.append('dynamodb', dynamodb_wrapper.get_resource())

    merchant_table = dynamodb_wrapper.create_table(**kwargs)

    return merchant_table

def update_anzpaid_merchant(merchant_obj):

    token = get_msh_bearer_token()

    trns_merchant_obj = json.loads(merchant_obj)

    # check that the merchant exists in our data store

    # check that the merchant exists in MSH

    # update to MSH

    # update our data store


def get_anzpaid_merchant(id):
    token = get_msh_bearer_token()

    #trns_merchant_obj = json.loads(merchant_obj)

    # check that the merchant exists in our data store

    # check that the merchant exists in MSH

    # update to MSH

    # update our data store


def remove_anzpaid_merchant(id):

    token = get_msh_bearer_token()

    #trns_merchant_obj = json.loads(merchant_obj)

    # check that the merchant exists in our data store

    # check that the merchant exists in MSH

    # update to MSH

    # update our data store

