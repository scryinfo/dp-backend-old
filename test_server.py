import json
import unittest
import warnings

from api import ScryApiException, ScryApi

from categories import create_category
from model import db, Categories


meta_path = './demo/metadata/'


test_credentials = {'username': '22', 'password': '22'}


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
        payload = {
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
        self.assertEqual(api.categories(payload=payload), response)
        return api, payload



    def test_category_exists(self):
        api, payload = self.test_create_new_category()
        # TRICK: upload the same category again.
        response = api.categories(payload=payload)
        self.assertEqual(response, {"Result": "CategoryName already exists"})

    def test_create_categories(self):
        payload = {  # "CategoryName" key missing. Here written with an "s" --> "CategoryNames"
            "CategoryNames": ["Aviation", "Commercial Flights", "Airport Info"],
            "DataStructure":
                [
                    {"AirlineId": {"DataType": "Int", "IsUnique": "true", "IsPrimaryKey": "true"}}
                ]
        }
        response = {"Result": "No 'CategoryName'"}
        self.assertEqual(ScryApi().categories(payload=payload), response)


    def test_no_datastructure(self):
        payload = {  # "DataStructure" key missing. Here written with an "s" --> "DataStructures"
            "CategoryName": ["Aviation", "Commercial Flights", "Airport Info"],
            "DataStructures":
                [
                    {"AirlineId": {"DataType": "Int", "IsUnique": "true", "IsPrimaryKey": "true"}}
                ]
        }
        response = {"Result": "No 'DataStructure'"}
        self.assertEqual(ScryApi().categories(payload=payload), response)

    def test_categories_dirty(self):
        payload = {
            "CategoryName": ["Aviation", "Commercial Flights", "Airport Info"],
            "DataStructure":
                [  # "DataType" written with an "s" --> "DataTypes"
                    {"AirlineId": {"DataTypes": "Int", "IsUnique": "true", "IsPrimaryKey": "true"}},
                ]
        }

        self.assertEqual(ScryApi().categories(payload=payload),  {'DataErrors': [['AirlineId', 'DataTypes', 'Int', "KeyError('DataTypes',)"]], 'Result': 'Metadata Error'}
)


def search_keywords(keywords, searchtype, userpayload=test_credentials):
    api = ScryApi()
    api.login(userpayload)
    payload = {
        'keywords': keywords,
        'searchtype' : searchtype
        }
    return api.search(payload)


class PublisherTest(unittest.TestCase):

    def make_api(self):
        api = ScryApi()
        api.data_path = './demo/data/'
        api.listing_path = './demo/listing_info/'
        return api

    def publish_data(self, data_file=None, listing_file=None):
        api = self.make_api()
        api.login(**test_credentials)
        payload = api.from_filenames_to_publisher_payload(data=data_file, listing_info=listing_file)
        return api.publisher(payload)

    def test_publish_with_no_jwt(self):
        warnings.simplefilter("ignore")
        api = self.make_api()
        with self.assertRaises(ScryApiException):
            return api.publisher(self.make_publisher_default_payload(api))

    def make_publisher_default_payload(self, api):
        return api.from_filenames_to_publisher_payload(data="airlines_null.dat", listing_info="Airlines_listing.json")

    def test_publish_data_with_wrong_jwt(self):
        api = self.make_api()
        api.login(**test_credentials)
        api.jwt_token += 'a'
        with self.assertRaises(ScryApiException):
            return api.publisher(self.make_publisher_default_payload(api))

    def test_null_in_not_null_column(self):
        warnings.simplefilter("ignore")

        with self.assertRaises(ScryApiException) as error:
            self.publish_data(data_file="airlines_null.dat", listing_file="Airlines_listing.json")


        self.assertEqual(
                error.exception.response['error'],
                {'IsUnique': [], 'IsNull': [['IATA', ['2', None]], ['ICAO', ['0', None], ['1', None]], ['Callsign', ['1', None]], ['Country', ['1', None]]], 'DataType': [], 'FieldLength': [], 'IsPrimaryKey': [], 'ForeignDataHash': []}
            )


    def test_Duplicates_in_Unique_Column(self):
        warnings.simplefilter("ignore")

        with self.assertRaises(ScryApiException) as error:
            self.publish_data("airlines_duplicate.dat", "Airlines_listing.json")

        self.assertEqual(
            {'FieldLength': [], 'IsPrimaryKey': [], 'IsNull': [['AirlineId', ['2', 2], ['3', 2]]], 'IsUnique': [['AirlineId', ['2', 2], ['3', 2]]], 'ForeignDataHash': [], 'DataType': []}

            ,
            error.exception.response['error']
        )

    def test_Float_and_String_in_int_Column(self):
        warnings.simplefilter("ignore")
        with self.assertRaises(ScryApiException) as error:
            self.publish_data(data_file="airlines_int.dat", listing_file="Airlines_listing.json")

        self.assertEqual(
        error.exception.response['error']
        ,
        {'ForeignDataHash': [], 'IsNull': [], 'IsUnique': [], 'FieldLength': [], 'DataType': [['AirlineId', ['1', '1.1'], ['2', '2a']]], 'IsPrimaryKey': []}
        )

    def test_String_in_float_Column(self):
        warnings.simplefilter("ignore")

        with self.assertRaises(ScryApiException) as error:
            self.publish_data(data_file="airlines_float.dat", listing_file="Airlines_listing_float.json")

        self.assertEqual(
                error.exception.response['error'],
                {'FieldLength': [], 'IsUnique': [], 'IsPrimaryKey': [], 'ForeignDataHash': [], 'DataType': [['AirlineId', ['2', '2a']]], 'IsNull': []}
            )

    def test_insert_schedule_data_successfully(self):
        warnings.simplefilter("ignore")
        self.assertEqual(
            self.publish_data(data_file="schedule.csv", listing_file="Schedule_listing.json"),
            "Success")

    def test_data_file_missing(self):
        warnings.simplefilter("ignore")
        with self.assertRaises(ScryApiException):
            self.publish_data(listing_file="Schedule_listing.json")

    def test_listing_file_missing(self):
        warnings.simplefilter("ignore")
        with self.assertRaises(ScryApiException):
            response = self.publish_data(data_file="schedule.csv")

    def test_insert_schedule_data_successfully(self):
        warnings.simplefilter("ignore")
        self.assertEqual(self.publish_data("schedule.csv", "Schedule_listing.json"),
                         {'message': 'Success'})


if __name__ == '__main__':
    unittest.main()


## SEARCH KEYWORDS FUNCTION HAS A BUG
class SearchKeywordsTest(unittest.TestCase):


    def setUp(self):
        userpayload={'username':'22','password':'22'}
        api = ScryApi()
        api.login(**userpayload)

        #Create category
        metadata=json.load(open(meta_path+'Schedule_Metadata.json'))
        metadata['CategoryName']=["Search Keywords"]
        create_category(db,["Search Keywords"],metadata)

        #Create Listing
        f1=open(data_path+"schedule.csv",'rb')
        f2= json.loads='{"category_name":["Search Keywords"],"price":1000,"filename":"Airlines_float.csv","keywords":"blabla"}'
        files = {'data': f1,'listing_info':f2}
        api.publisher(files=files)

    def tearDown(self):
        cat=Categories.get(Categories.name=='["Search Keywords"]')
        cat_id=cat.id
        db.execute_sql("""DELETE FROM scry2.listing WHERE "categoryId"={};""".format(cat_id))
        db.execute_sql("""DELETE FROM scry2.categories WHERE name='["Search Keywords"]';""")

    #WIP: "Charles" <chuck>
    # def test_search_keywords(self):
    #     print(search_keywords('blabla','["category","keywords"]'))
    #
    #     self.assertEqual(test_categories(publisher_path,scry_path,userpayload),'{"Result": "Category Created"}')
