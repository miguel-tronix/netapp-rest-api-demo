# -*- coding: utf-8 -*-
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
    #api_key =  os.environ["apiKey"]
    #api_cred = os.environ["apiCred"]
    #api_region = os.environ["apiReg"]
    msh_user = os.environ['mshUser']
    msh_pwd = os.environ['mshPwd']
    msh_base_url = os.environ['mshBaseUrl']

except KeyError:
    #api_key = None
    #api_cred = None
    #api_region = None
    msh_user = 'anz-demo2-transpire-miguel'
    msh_pwd = 'bkdr4#@NZ!ng'
    msh_base_url = \
    'https://provisioning.demo.msh.apac.services.ingenico.com/v1/'

'''
AWS Lambda handler
Entry point for Transpire ANZ-BlueApp terminal
/terminal requensts will flow through here
'''


def lambda_handler(event, context):
    status_code = 200
    print(event)
    try:
        try:
            try:
                if event['body']['context']['resource-path'] == "/terminal"\
                 and event['body']['context']['http-method'] == "POST":
                    res = create_terminal(
                    json.dumps(event['body']['body-json'])
                    )
                elif event['body']['context']['resource-path'] == "/terminal"\
                and event['body']['context']['http-method'] == "PUT":
                    res = update_terminal(
                        json.dumps(event['body']['body-json'])
                        )
                elif event['body']['context']['http-method'] == "GET":
                    res = \
                    get_terminal(event['body']['context']['resource-path'])
                elif event['body']['context']['http-method'] == "DELETE":
                    res = \
                    remove_terminal(event['body']['context']['resource-path'])
            except KeyError:
                status_code = 504
                res = 'Could not find parameters'
        except urllib3.exceptions.ConnectionError as e:
            res = 'Connection failed %s' % e
            status_code = e.status

        output = json.dumps(
        {'statusCode': status_code, 'body': 'Updated %s!' % res}
        )

    except botocore.exceptions.ClientError as e:
        output = json.dumps(
            {'statusCode': e.response['ResponseMetadata']['HTTPStatusCode'],
                'body': 'Failed to update: %s' % e.response['Error']['Code']}
            )

    return output

'''
Get a valid bearer token for Ingenico MSH
This functionality will be common to all API base paths
eg (/terminal /location /etc)
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


def list_terminals():
    token = get_msh_bearer_token()
    get_terminals = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',
    ca_certs=certifi.where()).\
    request('GET', '%s%s' % (msh_base_url, 'terminals'),
    headers={'Authorization': token})
    if get_terminals.status is not 200:
        raise urllib3.exceptions.ConnectionException(get_terminals)
    return get_terminals.data


def create_msh_terminal(terminal_obj):

    token = get_msh_bearer_token()

    trns_terminal_obj = json.loads(terminal_obj)

    #terminal_list = json.loads(list_terminals())

    '''
    loop through the list looking for a matching name
    '''

    #for terminal_item in terminal_list:
        ##print(terminal_item['name'])
        #if terminal_item['name'] == trns_terminal_obj['terminalName']:
            #if trns_terminal_obj['terminalId'] == 0:
                #trns_terminal_obj['terminalId'] = terminal_item['id']
                #trns_terminal_obj['programId'] = terminal_item['acquirerId']
            #return trns_terminal_obj

    msh_terminal_obj = {
        'manufacturerId': trns_terminal_obj['manufacturerId'],
        'serialNumber': trns_terminal_obj['serialNumber'],
        'merchantId': trns_terminal_obj['merchantId']
        }

    new_terminal_req =\
    urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where()).\
    request('POST', '%s%s' % (msh_base_url, 'pois'),
    body=json.dumps(msh_terminal_obj),
    headers={'Content-Type': 'application/json', 'Authorization': token})

    if new_terminal_req.status != 201:
        raise urllib3.exceptions.ConnectionError(new_terminal_req)

    #create terminal in DynamoDB

    trns_terminal_obj['terminalId'] = json.loads(new_terminal_req.data)['id']

    return trns_terminal_obj


def create_terminal(terminal_obj):
    return create_msh_terminal(terminal_obj)


def update_terminal(terminal_obj):

    token = get_bearer_token()

    trns_terminal_obj = json.loads(terminal_obj)

    # check that the terminal exists in our data store

    # check that the terminal exists in MSH

    # update to MSH

    # update our data store


def get_terminal(id):
    token = get_bearer_token()

    #trns_terminal_obj = json.loads(terminal_obj)

    # check that the terminal exists in our data store

    # check that the terminal exists in MSH

    # update to MSH

    # update our data store


def remove_terminal(id):

    token = get_bearer_token()

    #trns_terminal_obj = json.loads(terminal_obj)

    # check that the terminal exists in our data store

    # check that the terminal exists in MSH

    # update to MSH

    # update our data store

