# -*- coding: utf-8 -*-
#!/usr/bin/python

import unittest
import json
import xmlrunner
'''
Test Cases for /address API functions
'''


class address_create_tests(unittest.TestCase):

    adr_svc = None

    def setUp(self):
        from address import address
        if self.adr_svc is None:
            self.adr_svc = address()

    def test_create_address_simple(self):

        print('Creating a new address')

        address_obj = {
            'address': {
      'address': '100 King St',
      'zipCode': '3000',
      'city': 'Melbourne'
      },
         'stage': "dev"
    }

        print((json.dumps(address_obj)))

        new_address = self.adr_svc.create_address(json.dumps(address_obj))

        print((json.dumps(new_address)))

        self.assertIsNotNone(new_address)

        self.assertIsNone(new_address.get('state'))

        self.assertIsNone(new_address.get('country'))

        self.assertEqual('100 King St', new_address['address'])

        self.assertEqual('3000', new_address['zipCode'])

        self.assertEqual('Melbourne', new_address['city'])

    def test_create_country_address(self):

        print('Creating a new address')

        address_obj = {
            'address': {
        'country':
        {
            'countryName': 'Australia',
            'countryCode': 'AU'
            },
      'address': '100 King St',
      'zipCode': '3000',
      'city': 'Melbourne'
      },
         'stage': "dev"
    }

        print((json.dumps(address_obj)))

        new_address = self.adr_svc.create_address(json.dumps(address_obj))

        print((json.dumps(new_address)))

        self.assertIsNotNone(new_address)

        self.assertIsNone(new_address.get('state'))

        self.assertIsNotNone(new_address.get('country'))

        self.assertEqual('AU', new_address['country']['countryCode'])

        self.assertEqual('Australia', new_address['country']['countryName'])

        self.assertEqual('100 King St', new_address['address'])

        self.assertEqual('3000', new_address['zipCode'])

        self.assertEqual('Melbourne', new_address['city'])

    def test_create_state_country_address(self):

            print('Creating a new address')

            address_obj = {
                'address': {
          'stateId': 0,
          'state': {
            'stateName': 'Victoria',
            'stateCode': 'VIC'
            },
            'country':
            {
                'countryName': 'Australia',
                'countryCode': 'AU'
                },
          'address': '100 King St',
          'zipCode': '3000',
          'city': 'Melbourne'
          },
             'stage': "dev"
        }

            print((json.dumps(address_obj)))

            new_address = self.adr_svc.create_address(address_obj)

            print((json.dumps(new_address)))

            self.assertIsNotNone(new_address)

            self.assertIsNotNone(new_address.get('state'))

            self.assertIsNotNone(new_address.get('country'))

            self.assertEqual('AU', new_address['country']['countryCode'])

            self.assertEqual('Australia', new_address['country']['countryName'])

            self.assertEqual('100 King St', new_address['address'])

            self.assertEqual('3000', new_address['zipCode'])

            self.assertEqual('Melbourne', new_address['city'])


class state_create_tests(unittest.TestCase):

    state_svc = None

    def setUp(self):
        from address import state
        if self.state_svc is None:
            self.state_svc = state()

    def test_create_state_australia(self):

        state_req_obj = {
            'state_obj': {
            'stateId': None,
            'stateName': 'Victoria',
            'countryCode': 'AU'
            },
            'stage': 'dev'
            }

        state_resp_obj = self.state_svc.create_state(state_req_obj)

        self.assertIsNotNone(state_resp_obj)

        self.assertEqual(state_resp_obj['stateName'],
             state_req_obj['state_obj']['stateName'])

        self.assertIsNotNone(state_resp_obj['stateId'])

        self.assertIsNotNone(state_resp_obj['stateHash'])

    def test_create_state_america(self):

        state_req_obj = {
            'state_obj': {
            'stateId': None,
            'stateName': 'Vermont',
            'countryCode': 'US'
            },
            'stage': 'dev'
            }

        state_resp_obj = self.state_svc.create_state(state_req_obj)

        self.assertIsNotNone(state_resp_obj)

        self.assertEqual(state_resp_obj['stateName'],
             state_req_obj['state_obj']['stateName'])

        self.assertIsNotNone(state_resp_obj['stateId'])

        self.assertIsNotNone(state_resp_obj['stateHash'])

    def test_create_state_no_country(self):
        from botocore.exceptions import ClientError

        state_req_obj = {
            'state_obj': {
            'stateId': None,
            'stateName': 'Vermont'
            },
            'stage': 'dev'
            }

        self.assertRaises(ClientError,
            self.state_svc.create_state,
            state_req_obj
            )


class state_access_tests(unittest.TestCase):

    state_svc = None

    states = []

    def setUp(self):
        from address import state
        if self.state_svc is None:
            self.state_svc = state()

    def test_get_states(self):

        state_req_obj = {
            'state_obj': None,
            'stage': 'dev'
            }

        state_resp_obj = self.state_svc.get_states(state_req_obj)

        self.states = state_resp_obj

        print("STS: %s" % self.states)

        self.assertIsNotNone(state_resp_obj)

        self.assertTrue(len(state_resp_obj) > 0)

    def test_get_state(self):

        if len(self.states) is 0:
            self.test_get_states()

        state_req_obj = {
            'id': self.states[0]['stateId'],
            'state_obj': {
            'stateName': self.states[0]['stateName'],
            'countryCode': self.states[0]['countryCode']
            },
            'stage': 'dev'
            }

        state_resp_obj = self.state_svc.get_state(state_req_obj)

        self.assertIsNotNone(state_resp_obj)

        self.assertIsNotNone(state_resp_obj['stateId'])

        self.assertIsNotNone(state_resp_obj['stateHash'])


class country_create_tests(unittest.TestCase):

    country_svc = None

    def setUp(self):
        from address import country
        if self.country_svc is None:
            self.country_svc = country()

    def test_create_country_australia(self):

        country_req_obj = {
            'country_obj': {
            'countryId': None,
            'countryName': 'Australia',
            'countryCode': 'AU'
            },
            'stage': 'dev'
            }

        country_resp_obj = self.country_svc.create_country(country_req_obj)

        self.assertIsNotNone(country_resp_obj)

        self.assertEqual(country_resp_obj['countryName'],
             country_req_obj['country_obj']['countryName'])

        self.assertEqual(country_resp_obj['countryCode'],
             country_req_obj['country_obj']['countryCode'])

        self.assertIsNotNone(country_resp_obj['countryId'])

        self.assertIsNotNone(country_resp_obj['countryHash'])

    def test_create_country_america(self):

        country_req_obj = {
            'country_obj': {
            'countryId': None,
            'countryName': 'United States',
            'countryCode': 'US'
            },
            'stage': 'dev'
            }

        country_resp_obj = self.country_svc.create_country(country_req_obj)

        self.assertIsNotNone(country_resp_obj)

        self.assertEqual(country_resp_obj['countryName'],
             country_req_obj['country_obj']['countryName'])

        self.assertEqual(country_resp_obj['countryCode'],
             country_req_obj['country_obj']['countryCode'])

        self.assertIsNotNone(country_resp_obj['countryId'])

        self.assertIsNotNone(country_resp_obj['countryHash'])

    def test_create_country_no_country(self):
        from botocore.exceptions import ClientError

        country_req_obj = {
            'country_obj': {
            'countryId': None,
            'countryName': 'United Kingdom'
            },
            'stage': 'dev'
            }

        self.assertRaises(ClientError,
            self.country_svc.create_country,
            country_req_obj
            )


class country_access_tests(unittest.TestCase):

    country_svc = None

    countrys = []

    def setUp(self):
        from address import country
        if self.country_svc is None:
            self.country_svc = country()

    def test_get_countrys(self):

        country_req_obj = {
            'country_obj': None,
            'stage': 'dev'
            }

        country_resp_obj = self.country_svc.get_countries(country_req_obj)

        self.countrys = country_resp_obj

        print("CTRS: %s" % self.countrys)

        self.assertIsNotNone(country_resp_obj)

        self.assertTrue(len(country_resp_obj) > 0)

    def test_get_country(self):

        if len(self.countrys) is 0:
            self.test_get_countrys()

        country_req_obj = {
            'id': self.countrys[0]['countryId'],
            'country_obj': {
            'countryName': self.countrys[0]['countryName'],
            'countryCode': self.countrys[0]['countryCode']
            },
            'stage': 'dev'
            }

        country_resp_obj = self.country_svc.get_country(country_req_obj)

        print("CTR: %s" % country_resp_obj)

        self.assertIsNotNone(country_resp_obj)

        self.assertIsNotNone(country_resp_obj['countryId'])

        self.assertIsNotNone(country_resp_obj['countryHash'])


class address_access_tests(unittest.TestCase):

    adr_svc = None

    adrs = []

    def setUp(self):
        from address import address
        if self.adr_svc is None:
            self.adr_svc = address()

    def test_get_address_list(self):

        adr_list = self.adr_svc.list_addresses({
                 'address': None,
                 'stage': 'dev'
                 })

        self.assertIsNotNone(adr_list)

        self.assertTrue(len(adr_list) > 0)

        self.adrs = adr_list

    def test_get_address_by_id(self):

        if len(self.adrs) is 0:
            self.test_get_address_list()

        adr = self.adr_svc.get_address({
            'id': self.adrs[0]['addressId'],
            'address': None,
            'stage': 'dev'
            })

        self.assertIsNotNone(adr)

        self.assertEqual(adr['addressId'], self.adrs[0]['addressId'])


class address_update_tests(unittest.TestCase):

    adr_svc = None

    adrs = []

    def setUp(self):
        from address import address
        if self.adr_svc is None:
            self.adr_svc = address()
        if len(self.adrs) is 0:
            self.adrs =\
             self.adr_svc.list_addresses({
                 'address': None,
                 'stage': 'dev'
                 })

    def test_update_address_simple(self):

        print('Creating a new address')
        tmp = None
        for adr in self.adrs:
            if 'stateId' not in adr and 'countryId' not in adr:
                tmp = adr
                break

        address_obj = {
            'id': tmp['addressId'],
            'address': {
        'addressId': tmp['addressId'],
      'address': '101 Pitt St',
      'zipCode': '2000',
      'city': 'Sydney'
      },
         'stage': "dev"
    }

        print("ADR: %s" % tmp)

        upd_address = self.adr_svc.update_address(address_obj)

        print(upd_address)

        self.assertIsNotNone(upd_address)

        self.assertIsNone(upd_address.get('state'))

        self.assertIsNone(upd_address.get('country'))

        self.assertEqual(upd_address['addressId'], tmp['addressId'])

        self.assertEqual('101 Pitt St', upd_address['address'])

        self.assertEqual('2000', upd_address['zipCode'])

        self.assertEqual('Sydney', upd_address['city'])

    def test_update_address_state(self):

        tmp = None
        for adr in self.adrs:
            if 'stateId' in adr:
                tmp = adr
                break

        address_obj = {
            'address': {
                'addressId': tmp['addressId'],
        'state':
        {
            'stateName': 'Western Australia',
            'stateCode': 'WA',
            'countryCode': 'AU'
            },
      'address': '10 Wellington St',
      'zipCode': '6000',
      'city': 'Perth'
      },
         'stage': "dev"
    }

        print(address_obj)

        upd_address = self.adr_svc.update_address(address_obj)

        print(upd_address)

        self.assertIsNotNone(upd_address)

        self.assertIsNotNone(upd_address.get('stateId'))

        self.assertEqual(upd_address['addressId'], tmp['addressId'])

        self.assertEqual('Western Australia',
             upd_address['state']['stateName'])

        self.assertEqual('10 Wellington St', upd_address['address'])

        self.assertEqual('6000', upd_address['zipCode'])

        self.assertEqual('Perth', upd_address['city'])

    def test_update_address_state_country(self):

        print('Creating a new address')

        tmp = None
        for adr in self.adrs:
            if 'stateId' in adr and 'countryId' in adr:
                tmp = adr
                break

        address_obj = {
            'address': {
                'addressId': tmp['addressId'],
        'state':
        {
            'stateName': 'Gauteng',
            'countryCode': 'ZA'
            },
         'country':
        {
            'countryName': 'South Africa',
            'countryCode': 'ZA'
            },
      'address': '500 Blink St',
      'zipCode': '2001',
      'city': 'Johannesburg'
      },
         'stage': "dev"
    }

        print((json.dumps(address_obj)))

        upd_address = self.adr_svc.update_address(address_obj)

        print(upd_address)

        self.assertIsNotNone(upd_address)

        self.assertIsNotNone(upd_address.get('stateId'))

        self.assertIsNotNone(upd_address.get('countryId'))

        self.assertEqual(upd_address['addressId'], tmp['addressId'])

        self.assertEqual('Gauteng',
             upd_address['state']['stateName'])

        self.assertEqual('South Africa',
             upd_address['country']['countryName'])

        self.assertEqual('500 Blink St', upd_address['address'])

        self.assertEqual('2001', upd_address['zipCode'])

        self.assertEqual('Johannesburg', upd_address['city'])


def address_test_suite():
    msuite = []
    mloader = unittest.TestLoader()

    msuite.append(mloader.loadTestsFromTestCase(country_create_tests))
    msuite.append(mloader.loadTestsFromTestCase(country_access_tests))
    msuite.append(mloader.loadTestsFromTestCase(state_create_tests))
    msuite.append(mloader.loadTestsFromTestCase(state_access_tests))
    msuite.append(mloader.loadTestsFromTestCase(address_create_tests))
    msuite.append(mloader.loadTestsFromTestCase(address_access_tests))
    msuite.append(mloader.loadTestsFromTestCase(address_update_tests))

    return msuite

if __name__ == "__main__":

    #runner = unittest.TextTestRunner()
    runner = xmlrunner.XMLTestRunner(output='msh-merchant-test-reports')
    for tsuite in address_test_suite():
        runner.run(tsuite)
