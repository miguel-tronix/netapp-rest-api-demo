import unittest
import dynamodb_wrapper
import xmlrunner


class dbwrapper_resource_tests(unittest.TestCase):

    test_id = None

    def test_get_yaml_as_dict(self):
        yml = dynamodb_wrapper.get_yaml_as_dict('dbsetup.yml')
        self.assertIsNotNone(yml)
        self.assertEqual("http://localhost:8000",
        yml['dynamodb']['endpoint_url'])
        self.assertIsNotNone(yml['dynamodb']['region'])

    def test_get_resource(self):
        dynamodb_resource = dynamodb_wrapper.get_resource()
        self.assertIsNotNone(dynamodb_resource)


class dbwrapper_table_create_tests(unittest.TestCase):

    test_id = None

    def test_create_table(self):
        dynamodb_test = dynamodb_wrapper.get_resource()
        dynamodb_options = {
            'dynamodb': dynamodb_test,
            'table_name': 'TestTable',
            'stage': 'dev'
            }
        test_table = dynamodb_wrapper.create_table(**dynamodb_options)

        self.assertIsNotNone(
                test_table['table']
            )


class dbwrapper_item_access_tests(unittest.TestCase):

    test_id = None

    item_list = None

    def test_scan_items(self):

        dynamodb_test = dynamodb_wrapper.get_resource()
        dynamodb_options = {
            'dynamodb': dynamodb_test,
            'table_name': 'TestTable',
            'stage': 'dev'
            }
        test_table = dynamodb_wrapper.create_table(**dynamodb_options)

        scan_all_items = {
            'Item': {
                }
            }

        insert_opts = {
            'table_struct': test_table,
            'item': scan_all_items
            }

        self.item_list = dynamodb_wrapper.scan_item(**insert_opts)

        self.assertIsNotNone(self.item_list)

        self.assertTrue(len(self.item_list) > 0)

        return self.item_list

    def test_get_item_not_available(self):
        dynamodb_test = dynamodb_wrapper.get_resource()
        dynamodb_options = {
            'dynamodb': dynamodb_test,
            'table_name': 'TestTable',
            'stage': 'dev'
            }
        test_table = dynamodb_wrapper.create_table(**dynamodb_options)

        get_test_item = {
            'Item': {
                'id': '0',
                'testName': "0000-999-090909-090909090"
                }
            }

        insert_opts = {
            'table_struct': test_table,
            'item': get_test_item
            }

        existing_item = dynamodb_wrapper.get_item(**insert_opts)

        print('item: %s ' % existing_item)
        self.assertIsNone(existing_item)

    def test_get_item_available(self):
        if self.item_list is None:
            self.test_scan_items()

        print("ID IN GET: %s" % self.item_list)

        dynamodb_test = dynamodb_wrapper.get_resource()
        dynamodb_options = {
            'dynamodb': dynamodb_test,
            'table_name': 'TestTable',
            'stage': 'dev'
            }
        test_table = dynamodb_wrapper.create_table(**dynamodb_options)

        get_test_item = {
            'Item': {
                'id': self.item_list[0]['id']
            }
        }

        insert_opts = {
            'table_struct': test_table,
            'item': get_test_item
            }
        print("GET %s" % insert_opts)
        existing_item = dynamodb_wrapper.get_item(**insert_opts)

        print('found item: %s ' % existing_item)
        self.assertIsNotNone(existing_item)
        self.assertEqual(existing_item['id'],
            self.item_list[0]['id'])
        self.assertEqual(int(existing_item['deleted']), 0)


class dbwrapper_item_create_tests(unittest.TestCase):

    test_id = None

    def test_insert_item(self):
        dynamodb_test = dynamodb_wrapper.get_resource()
        dynamodb_options = {
            'dynamodb': dynamodb_test,
            'table_name': 'TestTable',
            'stage': 'dev'
            }

        test_table = dynamodb_wrapper.create_table(**dynamodb_options)

        test_item = {
            'Item':
                {
                'id': '0',
                'testName': 'uuid',
                'secondTestId': "hello",
                'thirdTestId': int(11),
                'forthTestId': "world"
                }
            }

        insert_opts = {
            'table_struct': test_table,
            'item': test_item
            }

        new_item = dynamodb_wrapper.add_item(**insert_opts)

        self.test_id = str(new_item['id'])

        self.assertNotEqual(0, test_table['table'].item_count)
        self.assertNotEqual('0', new_item['id'])
        print("ID IN INSERT: %s" % self.test_id)


class dbwrapper_item_remove_tests(unittest.TestCase):

    test_id = None

    def setUp(self):
        if self.test_id is None:
            dynamodb_test = dynamodb_wrapper.get_resource()
            dynamodb_options = {
                'dynamodb': dynamodb_test,
                'table_name': 'TestTable',
                'stage': 'dev'
                }
            test_table = dynamodb_wrapper.create_table(**dynamodb_options)

            scan_all_items = {
                'Item': {
                    }
                }

            insert_opts = {
                'table_struct': test_table,
                'item': scan_all_items
                }

            item_list = dynamodb_wrapper.scan_item(**insert_opts)

            self.test_id = item_list[0]['id']

    def test_remove_item(self):

        dynamodb_test = dynamodb_wrapper.get_resource()
        dynamodb_options = {
            'dynamodb': dynamodb_test,
            'table_name': 'TestTable',
            'stage': 'dev'
            }
        test_table = dynamodb_wrapper.create_table(**dynamodb_options)

        get_test_item = {
            'Item': {
                'id': self.test_id
            }
        }

        insert_opts = {
            'table_struct': test_table,
            'item': get_test_item
            }

        print("OPTS %s" % insert_opts)
        removed_item = dynamodb_wrapper.remove_item(**insert_opts)
        print('item removed: %s ' % removed_item)
        self.assertIsNotNone(removed_item)
        self.assertEqual(removed_item['deleted'],
             1)


class dbwrapper_defaults_create_tests(unittest.TestCase):

    defaults_list = None

    table = None

    def setUp(self):
        if self.table is None:
            dynamodb_test = dynamodb_wrapper.get_resource()
            dynamodb_options = {
            'dynamodb': dynamodb_test,
            'table_name': 'TestTable',
            'stage': 'dev'
            }

            self.table = dynamodb_wrapper.create_table(**dynamodb_options)

            self.defaults_list = self.table['defaults']

    def test_defaults_created(self):

        scan_all_items = {
                'Item': {
                    }
                }

        insert_opts = {
            'table_struct': self.table,
            'item': scan_all_items
            }

        item_list = dynamodb_wrapper.scan_item(**insert_opts)

        self.assertIsNotNone(item_list)

        self.assertTrue(len(item_list) > 0)

        self.assertEqual(len(item_list), len(self.defaults_list))

        #for default in self.defaults_list:
            #tmp = {}
            #for k in default.keys():
                #tmp[k] = default[k]
            #self.assertTrue(tmp in item_list)


def dbwrapper_test_suite():
    msuite = []
    mloader = unittest.TestLoader()

    msuite.append(
        mloader.loadTestsFromTestCase(dbwrapper_resource_tests)
        )
    msuite.append(mloader.loadTestsFromTestCase(dbwrapper_table_create_tests))
    msuite.append(mloader.loadTestsFromTestCase(dbwrapper_item_create_tests))
    msuite.append(mloader.loadTestsFromTestCase(dbwrapper_item_access_tests))
    #msuite.append(mloader.loadTestsFromTestCase(dbwrapper_item_update_tests))
    msuite.append(mloader.loadTestsFromTestCase(dbwrapper_item_remove_tests))
    msuite.append(
        mloader.loadTestsFromTestCase(dbwrapper_defaults_create_tests)
        )

    return msuite

if __name__ == "__main__":

    #runner = unittest.TextTestRunner()
    runner = xmlrunner.XMLTestRunner(output='dbwrapper-test-reports')
    for tsuite in dbwrapper_test_suite():
        runner.run(tsuite)
