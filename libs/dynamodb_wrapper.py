#/usr/bin/python2.7
import boto3
import sys
import yaml
import jinja2

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


def get_resource():
    dyndb_resource = None
    session = boto3.session.Session(region_name='us-east-1')
    dyndb_resource = session.resource('dynamodb',
        endpoint_url='http://localhost:8000')
    return dyndb_resource

'''
Create table if does not exist
'''


def create_table(**kwargs):

    # if mock is not none we use mock at a lambda function
    dynamodb = kwargs['dynamodb']
    tbl_name = kwargs['table_name']
    partition_key = kwargs['partition_key']

    if 'sort_key' in kwargs:
        sort_key = kwargs['sort_key']
    else:
        sort_key = ''

    if 'throughput' in kwargs:
        throughput = kwargs['throughput']
    else:
        throughput = 5

    if 'indexes' in kwargs:
        indexes = kwargs['indexes']
    else:
        indexes = ''

    if 'attributedefs' in kwargs:
        attributedefs = kwargs['attributedefs']
    else:
        attributedefs = ''

    if dynamodb is None:
        dynamodb = get_resource()

    table = dynamodb.Table(tbl_name)
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
            TableName=tbl_name
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
                    TableName=tbl_name
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
                        TableName=tbl_name
                        )
                except:
                    error = sys.exc_info()
                    print(("Problem creating table - %s" % error))
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
                        TableName=tbl_name,
                        GlobalSecondaryIndexes=indexes,
                    )
            except:
                error = sys.exc_info()
                print(("Error creating table %s" % error))

        new_table.wait_until_exists()
        return new_table
    else:
        print("Table exists")
        return table


def add_item(**kwargs):
    session = boto3.session.Session(profile_name=kwargs['profile'])
    dynamodb = session.resource('dynamodb', region_name=kwargs['region'])
    table = dynamodb.Table(kwargs['table_name'])
    table.put_item(kwargs['item'])


#def add_attribute(**kwargs):
    #dynamodb = kwargs['dynamodb']
    #table = dynamodb.Table(kwargs['table_name'])


def remove_item(**kwargs):
    dynamodb = kwargs['dynamodb']
    table = dynamodb.Table(kwargs['table_name'])
    set_to_remove = table.get_item(Key={kwargs['partition_key']})
    set_to_remove['deleted'] = 1
    set_to_remove[kwargs['partion_key']] = "new_hash"
