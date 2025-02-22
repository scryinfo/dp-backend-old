import json, os
import unittest
import warnings

from api import ScryApiException, ScryApi

from categories import create_category
from model import db, Categories


meta_path = './demo/metadata/'


test_credentials = {'username': '22', 'password': '22'}

def initialize_categories():
    api = ScryApi()
    api.login(**test_credentials)
    for files in os.listdir('./demo/metadata/'):
        metadata = json.load(open('./demo/metadata/' + files))
        api.categories(metadata)

class JWTTest(unittest.TestCase):
    def test_correct_authentication(self):
        ScryApi().login(**test_credentials)

    def test_wrong_authentication(self):
        with self.assertRaises(Exception):
            ScryApi().login(username='22', password='223')

    def test_aut1(self):
        api = ScryApi()
        api.login(**test_credentials)
        with self.assertRaises(ScryApiException):
            api.protected()

    def test_aut2(self):
        api = ScryApi()
        api.login(**test_credentials)
        api.jwt_token += 'a'  # TRICK: corrupt jwt_token value.
        with self.assertRaises(ScryApiException):
           api.protected()


class CategoryTest(unittest.TestCase):

    def setUp(self):
        #db.execute_sql("""DELETE FROM scry2.categories where name='["Aviation6", "Commercial Flights", "Airport Info"]';""")
        return

    def tearDown(self):
        db.execute_sql("""DELETE FROM scry2.categories where name='["Aviation6", "Commercial Flights", "Airport Info"]';""")

    def test_create_new_category(self):
        api = ScryApi()
        api.login(**test_credentials)
        metadata = {
            "CategoryName": ["Aviation6", "Commercial Flights", "Airport Info"],
            "DataStructure":
                [
                    {"AirlineId": {"DataType": "Int", "IsUnique": "true", "IsPrimaryKey": "true"}},
                    {"AirlineName": {"DataType": "String", "IsUnique": "true"}},
                    {"ANA": {"DataType": "String", "IsUnique": "true"}},
                    {"IATA": {"DataType": "String", "IsUnique": "true", "IsNull": "true"}},
                    {"IACAO": {"DataType": "String", "IsUnique": "true", "IsNull": "true"}},
                    {"Callsign": {"DataType": "String", "IsUnique": "true"}},
                    {"Country": {"DataType": "String"}},
                    {"Active": {"DataType": "String"}}
                ]
        }
        response = {"Result": "Category Created"}
        self.assertEqual(api.categories(metadata=metadata), response)
        return api, metadata



    def test_category_exists(self):
        api, metadata = self.test_create_new_category()
        # TRICK: upload the same category again.
        response = api.categories(metadata=metadata)
        self.assertEqual(response, {"Result": "CategoryName already exists"})

    def test_create_categories(self):
        metadata = {  # "CategoryName" key missing. Here written with an "s" --> "CategoryNames"
            "CategoryNames": ["Aviation", "Commercial Flights", "Airport Info"],
            "DataStructure":
                [
                    {"AirlineId": {"DataType": "Int", "IsUnique": "true", "IsPrimaryKey": "true"}}
                ]
        }
        response = {"Result": "No 'CategoryName'"}
        self.assertEqual(ScryApi().categories(metadata=metadata), response)


    def test_no_datastructure(self):
        metadata = {  # "DataStructure" key missing. Here written with an "s" --> "DataStructures"
            "CategoryName": ["Aviation", "Commercial Flights", "Airport Info"],
            "DataStructures":
                [
                    {"AirlineId": {"DataType": "Int", "IsUnique": "true", "IsPrimaryKey": "true"}}
                ]
        }
        response = {"Result": "No 'DataStructure'"}
        self.assertEqual(ScryApi().categories(metadata=metadata), response)

    def test_categories_dirty(self):
        metadata = {
            "CategoryName": ["Aviation", "Commercial Flights", "Airport Info"],
            "DataStructure":
                [  # "DataType" written with an "s" --> "DataTypes"
                    {"AirlineId": {"DataTypes": "Int", "IsUnique": "true", "IsPrimaryKey": "true"}},
                ]
        }

        self.assertEqual(ScryApi().categories(metadata=metadata), {'DataErrors': [['AirlineId', 'DataTypes', 'Int', "KeyError('DataTypes',)"]], 'Result': 'Metadata Error'}
                         )

class PublisherTest(unittest.TestCase):

    def make_api(self):
        api = ScryApi()
        api.data_path = './demo/data/'
        api.listing_path = './demo/listing_info/'
        return api

    def publish_data(self, data=None, listing_info=None):
        api = self.make_api()
        api.login(**test_credentials)
        return api.publisher(data=data, listing_info=listing_info)

    def test_publish_with_no_jwt(self):
        api = self.make_api()
        with self.assertRaises(ScryApiException):
            return api.publisher(data="airlines_null.dat", listing_info="Airlines_listing.json")

    def test_publish_data_with_wrong_jwt(self):
        api = self.make_api()
        api.login(**test_credentials)
        api.jwt_token += 'a'
        with self.assertRaises(ScryApiException):
            return api.publisher(data="airlines_null.dat", listing_info="Airlines_listing.json")

    def test_null_in_not_null_column(self):
        with self.assertRaises(ScryApiException) as error:
            self.publish_data(data="airlines_null.dat", listing_info="Airlines_listing.json")


        self.assertEqual(
                error.exception.response['error'],
                {'IsUnique': [], 'IsNull': [['IATA', ['2', None]], ['ICAO', ['0', None], ['1', None]], ['Callsign', ['1', None]], ['Country', ['1', None]]], 'DataType': [], 'FieldLength': [], 'IsPrimaryKey': [], 'ForeignDataHash': []}
            )


    def test_Duplicates_in_Unique_Column(self):
        with self.assertRaises(ScryApiException) as error:
            self.publish_data("airlines_duplicate.dat", "Airlines_listing.json")

        self.assertEqual(
            {'FieldLength': [], 'IsUnique': [['AirlineId', ['2', 2], ['3', 2]]], 'DataType': [], 'IsNull': [], 'ForeignDataHash': [], 'IsPrimaryKey': []}
            ,
            error.exception.response['error']
        )

    def test_Float_and_String_in_int_Column(self):
        with self.assertRaises(ScryApiException) as error:
            self.publish_data(data="airlines_int.dat", listing_info="Airlines_listing.json")

        self.assertEqual(
        error.exception.response['error']
        ,
        {'ForeignDataHash': [], 'IsNull': [], 'IsUnique': [], 'FieldLength': [], 'DataType': [['AirlineId', ['1', '1.1'], ['2', '2a']]], 'IsPrimaryKey': []}
        )

    def test_String_in_float_Column(self):
        with self.assertRaises(ScryApiException) as error:
            self.publish_data(data="airlines_float.dat", listing_info="Airlines_listing_float.json")

        self.assertEqual(
                error.exception.response['error'],
                {'FieldLength': [], 'IsUnique': [], 'IsPrimaryKey': [], 'ForeignDataHash': [], 'DataType': [['AirlineId', ['2', '2a']]], 'IsNull': []}
            )

    def test_insert_schedule_data_successfully(self):
        self.assertEqual(
            self.publish_data(data="schedule.csv", listing_info="Schedule_listing.json"),
            "Success")

    def test_data_file_missing(self):
        with self.assertRaises(ScryApiException) as error:
            self.publish_data(listing_info="Schedule_listing.json")

        self.assertEqual(
            error.exception.response
            ,{'text': "400 Bad Request: KeyError: 'data'", 'error': 400}
            )

    def test_listing_file_missing(self):
        warnings.simplefilter("ignore")
        with self.assertRaises(ScryApiException) as error:
            response = self.publish_data(data="schedule.csv")

        self.assertEqual(
            error.exception.response
            ,{'text': "400 Bad Request: KeyError: 'listing_info'", 'error': 400}
            )

    def test_insert_schedule_data_successfully(self):
        self.assertEqual(self.publish_data("schedule.csv", "Schedule_listing.json"),
                         {'message': 'Success'})


if __name__ == '__main__':
    initialize_categories()
    unittest.main()
