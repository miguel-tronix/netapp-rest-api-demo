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
Entry point for Transpire ANZ-BlueApp location
/location requensts will flow through here
'''


def lambda_handler(event, context):
    status_code = 200
    print(event)
    try:
        try:
            try:
                if event['body']['context']['resource-path'] == "/location"\
                 and event['body']['context']['http-method'] == "POST":
                    res = create_store(
                    json.dumps(event['body']['body-json'])
                    )
                elif event['body']['context']['resource-path'] == "/location"\
                and event['body']['context']['http-method'] == "PUT":
                    res = update_location(
                        json.dumps(event['body']['body-json'])
                        )
                elif event['body']['context']['http-method'] == "GET":
                    res = \
                    get_location(event['body']['context']['resource-path'])
                elif event['body']['context']['http-method'] == "DELETE":
                    res = \
                    remove_location(event['body']['context']['resource-path'])
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
eg (/location /location /etc)
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


def list_locations():
    token = get_msh_bearer_token()
    get_locations = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',
    ca_certs=certifi.where()).\
    request('GET', '%s%s' % (msh_base_url, 'locations'),
    headers={'Authorization': token})
    if get_locations.status is not 200:
        raise urllib3.exceptions.ConnectionException(get_locations)
    return get_locations.data


def create_msh_store(location_obj):

    token = get_msh_bearer_token()

    trns_location_obj = json.loads(location_obj)

    #location_list = json.loads(list_locations())

    '''
    loop through the list looking for a matching name
    '''

    #for location_item in location_list:
        ##print(location_item['name'])
        #if location_item['name'] == trns_location_obj['locationName']:
            #if trns_location_obj['locationId'] == 0:
                #trns_location_obj['locationId'] = location_item['id']
                #trns_location_obj['programId'] = location_item['acquirerId']
            #return trns_location_obj

    msh_location_obj = {
        'name': '%s' % trns_location_obj['locationName'],
        'timezone': trns_location_obj['timezone'],
        'merchantId': trns_location_obj['merchantId']
        }

    new_location_req =\
    urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where()).\
    request('POST', '%s%s' % (msh_base_url, 'stores'),
    body=json.dumps(msh_location_obj),
    headers={'Content-Type': 'application/json', 'Authorization': token})

    if new_location_req.status != 201:
        raise urllib3.exceptions.ConnectionError(new_location_req)

    #create location in DynamoDB

    trns_location_obj['locationId'] = json.loads(new_location_req.data)['id']

    #trns_location_obj['programId'] =\
    #json.loads(new_location_req.data)['acquirerId']

    return trns_location_obj


def create_store(location_obj):
    return create_msh_store(location_obj)


def update_location(location_obj):

    token = get_msh_bearer_token()

    #trns_location_obj = json.loads(location_obj)

    # check that the location exists in our data store

    # check that the location exists in MSH

    # update to MSH

    # update our data store


def get_location(id):

    token = get_msh_bearer_token()

    #trns_location_obj = json.loads(location_obj)

    # check that the location exists in our data store

    # check that the location exists in MSH

    # update to MSH

    # update our data store


def remove_location(id):

    token = get_bearer_token()

    #trns_location_obj = json.loads(location_obj)

    # check that the location exists in our data store

    # check that the location exists in MSH

    # update to MSH

    # update our data store

