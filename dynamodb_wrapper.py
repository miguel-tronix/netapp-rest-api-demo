#/usr/bin/python2.7
import boto3
from boto3.dynamodb.conditions import Attr, And
import sys
import yaml
import datetime
from yaml import YAMLError
from botocore.exceptions import ClientError
#import jinja2
#from base64 import b64encode
#from os import urandom
import uuid
import hashlib
import utils
import json

'''
Convinience wrapper functions for
handling DynamoDB calls
Eases unit testing and provides
a single point of entry for multiple modules
'''

'''
Get the DynamoDB resource to use in this
environment
'''

log = utils.setup_logging(__name__)


def get_resource():
    dyndb_resource = None
    region = None
    endpoint = None
    yml = get_yaml_as_dict('dbsetup.yml')
    region = yml['dynamodb'].get('region') if not None\
    else 'us-east-1'
    endpoint = yml['dynamodb'].get('endpoint_url') if not None\
    else None

    session = boto3.session.Session(region_name=region)
    if endpoint is not None:
        dyndb_resource = session.resource('dynamodb',
                    endpoint_url=endpoint)
    else:
        dyndb_resource = session.resource('dynamodb')
    return dyndb_resource

'''
Get python dict from Yaml file
'''


def get_yaml_as_dict(file_name):
    yml = None
    try:
        with open('configs/%s' % file_name, 'r') as f:
            try:
                yml = yaml.safe_load(f)
            except YAMLError as err:
                log.debug(err)
    except RuntimeError as err:
        log.debug(err)
    return yml

'''
Create table if does not exist
'''


def create_table(**kwargs):

    tbl_struct = {
        'table': {},
        'attrs': {},
        'defaults': {}
     }

    dynamodb = kwargs['dynamodb']
    tblfile_name = kwargs['table_name']
    stage = kwargs['stage']
    config = get_yaml_as_dict("%s.yml" % tblfile_name)[stage]

    partition_key = config['partition_key']

    if 'sort_key' in config:
        sort_key = config['sort_key']
    else:
        sort_key = ''

    if 'throughput' in config:
        throughput = config['throughput']
    else:
        throughput = 5

    if 'indexes' in config:
        indexes = config['indexes']
    else:
        indexes = ''

    if 'attributedefs' in config:
        attributedefs = config['attributedefs']
        tbl_struct['attrs'] = attributedefs
    else:
        attributedefs = ''

    if 'defaults' in config:
        tbl_struct['defaults'] = config['defaults']

    if dynamodb is None:
        dynamodb = get_resource()

    table = dynamodb.Table(config['table_name'])
    table_exists = False

    try:
        table.creation_date_time
        table_exists = True
    except:
        table_exists = False

    if not table_exists:
        throughput = int(throughput)

        if indexes:
            for index in indexes:
                index['ProvisionedThroughput']['ReadCapacityUnits'] = \
                int((index['ProvisionedThroughput']['ReadCapacityUnits']))
                index['ProvisionedThroughput']['WriteCapacityUnits'] = \
                int((index['ProvisionedThroughput']['WriteCapacityUnits']))

        if not indexes and not sort_key:
                    new_table = dynamodb.create_table(
                    AttributeDefinitions=[
                        {
                            'AttributeName': partition_key,
                            'AttributeType': 'S',
                        },
                    ],
                    KeySchema=[
                        {
                            'AttributeName': partition_key,
                            'KeyType': 'HASH',
                        },
                    ],
                    ProvisionedThroughput={
                        'ReadCapacityUnits': throughput,
                        'WriteCapacityUnits': throughput,
                    },
            TableName=config['table_name']
        )
        elif not indexes and sort_key:
            new_table = dynamodb.create_table(
                    AttributeDefinitions=[
                        {
                            'AttributeName': partition_key,
                            'AttributeType': 'S',
                        },
                        {
                            'AttributeName': sort_key,
                            'AttributeType': 'S',
                        }
                    ],
                    KeySchema=[
                        {
                            'AttributeName': partition_key,
                            'KeyType': 'HASH',
                        },
                        {
                            'AttributeName': sort_key,
                            'KeyType': 'RANGE',
                        }
                    ],
                    ProvisionedThroughput={
                        'ReadCapacityUnits': throughput,
                        'WriteCapacityUnits': throughput,
                    },
                    TableName=config['table_name']
        )
        elif not sort_key and indexes:
            if partition_key == 'Master_UUID':
                attributedefs.append(
                    {
                        'AttributeName': partition_key,
                        'KeyType': 'HASH'
                    }
                )
                try:
                    new_table = dynamodb.create_table(
                        AttributeDefinitions=attributedefs,
                        KeySchema=[
                            {
                                'AttributeName': partition_key,
                                'KeyType': 'HASH',
                            },
                        ],
                        GlobalSecondaryIndexes=indexes,
                        ProvisionedThroughput={
                            'ReadCapacityUnits': throughput,
                            'WriteCapacityUnits': throughput,
                        },
                        TableName=config['table_name']
                        )
                except:
                    error = sys.exc_info()
                    log.debug(("Problem creating table - %s" % error))
        else:
            if partition_key == 'Master_UUID':
                attributedefs.append({
                        'AttributeName': 'Master_UUID',
                        'AttributeType': "S"
                    })
                attributedefs.append({
                        'AttributeName': sort_key,
                        'AttributeType': 'S'
                    })
            else:
                attributedefs.append({
                    'AttributeName': partition_key,
                    'AttributeType': 'S'
                    })
            try:
                new_table = dynamodb.create_table(
                    AttributeDefinitions=attributedefs,
                        KeySchema=[
                            {
                                'AttributeName': partition_key,
                                'KeyType': 'HASH',
                            },
                            {
                                'AttributeName': sort_key,
                                'KeyType': 'RANGE'
                            }
                        ],
                        ProvisionedThroughput={
                            'ReadCapacityUnits': throughput,
                            'WriteCapacityUnits': throughput,
                        },
                        TableName=config['table_name'],
                        GlobalSecondaryIndexes=indexes,
                    )
            except:
                error = sys.exc_info()
                log.error("Error creating table %s" % error, exc_info=True)

        new_table.wait_until_exists()
        tbl_struct['table'] = new_table
        kwargs['table_struct'] = tbl_struct
        add_default_entries(**kwargs)

    else:
        tbl_struct['table'] = table

    return tbl_struct


def item_to_find(**kwargs):

    table = kwargs['table_struct']['table']
    itm = kwargs['item']['Item']
    tmp = {'table_struct': kwargs['table_struct'],
         'item': {
                'Key': {}
            }
        }
    if itm is not None:
        for key in table.key_schema:
            k = key['AttributeName']
            if itm.get(key['AttributeName']) is not None:
                v = itm[key['AttributeName']]
            else:
                continue
            tmp['item']['Key'][k] = v
    #log.debug("ITM2FND: %s" % tmp)
    return tmp


def get_filter_expression(filter_expression_list):
    filter_expression = None
    first = True
    for filter in filter_expression_list:
        if first:
            filter_expression = filter
            first = False
        else:
            filter_expression = filter_expression & filter
    return filter_expression


def item_to_scan(**kwargs):
    table = kwargs['table_struct']['table']
    attrs = kwargs['table_struct']['attrs']
    itm = kwargs['item']['Item']
    tmp = {'table': table,
        'item': {
            }
       }
    expr_list = []
    #never return deleted items
    expr_list.append(Attr('deleted').ne(1))
    tmp['item']['TableName'] = table.table_name

    for attr in attrs:
        k = attr['AttributeName']
        if itm.get(k) is not None:
            v = itm[k]
        else:
            continue
        expr_list.append(Attr(k).eq(v))

    tmp['item']['FilterExpression'] = get_filter_expression(expr_list)

    return tmp


def get_partition_key(**kwargs):
    table = kwargs['table_struct']['table']
    for key in table.key_schema:
        if key['KeyType'] == 'HASH':
            return key['AttributeName']


def get_sort_key(**kwargs):
    table = kwargs['table_struct']['table']
    for key in table.key_schema:
        if key['KeyType'] == 'RANGE':
            return key['AttributeName']


def get_hash_key(**kwargs):
    attrs = kwargs['table_struct']['attrs']
    for attr in attrs:
        if attr.get('AttributeType') is not None\
        and attr['AttributeType'] == 'HASH':
            return attr['AttributeName']


def get_uuid_key(**kwargs):
    attrs = kwargs['table_struct']['attrs']
    for attr in attrs:
        log.debug("ATTR: %s" % attr)
        if attr.get('AttributeType') is not None\
        and attr['AttributeType'] == 'UUID':
            return attr['AttributeName']


def add_item(**kwargs):

    table = kwargs['table_struct']['table']
    itm = kwargs['item']['Item']
    log.debug("ADDITM: %s" % itm)
    try:
        find_item = get_item(**kwargs)
    except ClientError:
        find_item = None

    if find_item is not None and find_item.get("Item") is not None:
        find_item = find_item.get("Item")
    if find_item is not None:
        if find_item.get('deleted') is None:
            find_item['deleted'] = int(0)
        elif find_item['deleted'] == int(1):
            return None
        itm = utils.update_old_with_new(
            None,
            find_item,
             itm)
        itm['updateTimestamp'] =\
         datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    else:
        #p_key = get_partition_key(**kwargs)
        hash_key = get_hash_key(**kwargs)
        s_key = get_sort_key(**kwargs)
        uuid_key = get_uuid_key(**kwargs)
        if hash_key is not None and hash_key is not s_key:
            itm[hash_key] = str(hashlib.md5(
                json.dumps(itm, default=(lambda k: int(k)))
                ).hexdigest())
        if s_key is not None and s_key is hash_key and itm.get(s_key) is None:
            itm[s_key] = str(hashlib.md5(
                json.dumps(itm, default=(lambda k: int(k)))
                ).hexdigest())
        if uuid_key is not None:
            itm[uuid_key] = str(uuid.uuid4())
        itm['origTimestamp'] = \
        datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        itm['deleted'] = int(0)
    kwargs['item']['Item'] = itm
    log.debug("ITM2PUT: %s" % itm)
    resp = table.put_item(**kwargs['item'])

    if resp['ResponseMetadata']['HTTPStatusCode'] != 200:
        log.debug(resp['ResponseMetadata']['HTTPStatusCode'])
        log.error(resp['ResponseMetadata']['HTTPStatusCode'])
        raise ClientError

    return itm


def get_item(**kwargs):
    itm = None
    try:
        table = kwargs['table_struct']['table']
        find = item_to_find(**kwargs)
        if find is not None:
            get_res = table.get_item(**find['item'])
            if get_res is not None\
            and get_res['ResponseMetadata']['HTTPStatusCode'] == 200:
                itm = get_res.get("Item")
        if itm is None:
            itms = scan_item(**kwargs)
            if len(itms) > 0:
                itm = itms[0]
    except ClientError as e:
        log.error(e.message)

    if itm is not None\
    and itm['deleted'] is 1:
        itm = None

    return itm


def scan_item(**kwargs):
    itms = []
    #log.debug("2SCN: %s" % kwargs)
    to_scan = item_to_scan(**kwargs)
    log.debug("SCN: %s" % to_scan)
    try:
        table = kwargs['table_struct']['table']
        itms = table.scan(**to_scan['item'])
    except ClientError as e:
        log.debug(e.message)
        log.error(e.message)
        raise(e)
    #log.debug("SCND: %s" % itms['Items'])
    return itms['Items']


def remove_item(**kwargs):
    log.debug("RMVITM %s" % kwargs)
    set_to_remove = get_item(**kwargs)
    if set_to_remove is not None:
        set_to_remove['deleted'] = int(1)
        set_to_remove['updateTimestamp'] =\
        datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        kwargs['item']['Item'] = set_to_remove
        remove_resp = \
        kwargs['table_struct']['table'].put_item(**kwargs['item'])
        if remove_resp['ResponseMetadata']['HTTPStatusCode'] != 200:
            set_to_remove = None
    return set_to_remove


def add_default_entries(**kwargs):

    for default in kwargs['table_struct']['defaults']:
        print('adding: %s' % default)
        tmp_args = {}
        tmp_args['table_struct'] = kwargs['table_struct']
        tmp_args['item'] = {}
        tmp_args['item']['Item'] = {}
        for key in default.keys():
            tmp_args['item']['Item'][key] = default[key]
        add_item(**tmp_args)


