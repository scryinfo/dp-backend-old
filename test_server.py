import json, os, unittest, warnings
import pandas as pd
import numpy as np
from api import ScryApiException, ScryApi
from test_data import *
from categories import create_category, create_cat_tree,   delete_cat_tree, CustomPeeweeError
from model import db, Categories, CategoryTree
import peewee as pe

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
                [{'IATA': [{'IsNull': [['2', 'nan']]}]}, {'ICAO': [{'IsNull': [['0', 'nan'], ['1', 'nan']]}]}, {'Callsign': [{'IsNull': [['1', 'nan']]}]}, {'Country': [{'IsNull': [['1', 'nan']]}]}]

            )


    def test_Duplicates_in_Unique_Column(self):
        with self.assertRaises(ScryApiException) as error:
            self.publish_data("airlines_duplicate.dat", "Airlines_listing.json")

        self.assertEqual(
            error.exception.response['error'],
            [{'AirlineId': [{'IsUnique': [['2', 2], ['3', 2]]}]}]
        )


    def test_Float_and_String_in_int_Column(self):
        with self.assertRaises(ScryApiException) as error:
            self.publish_data(data="airlines_int.dat", listing_info="Airlines_listing.json")

        self.assertEqual(error.exception.response['error']
        ,[{'AirlineId': [{'DataType': [['1', '1.1'], ['2', '2a']]}]}])


    def test_String_in_float_Column(self):
        with self.assertRaises(ScryApiException) as error:
            self.publish_data(data="airlines_float.dat", listing_info="Airlines_listing_float.json")

        self.assertEqual(
                error.exception.response['error'],
                [{'AirlineId': [{'DataType': [['2', '2a']]}]}]
            )


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



class DataTest(unittest.TestCase):

    df  = pd.DataFrame(data={'col1': ['a', 1,np.nan,np.nan], 'col2': [1, 'a',1,2.2]})

    meta=[{"col1":{"DataType": "Int","IsUnique": "true"}},
         {"col2":{"DataType": "Int","IsUnique": "true"}}]


    def test_is_null(self,df=df):
        self.assertEqual(
            serie_to_list (testIsNull(df['col1']).fillna(''))
            ,[[2, ''], [3, '']])


    def test_is_unique(self,df=df):
        self.assertEqual(
            serie_to_list (testIsUnique(df['col2']))
            ,[[0, 1], [2, 1]])


    def test_is_int(self,df=df):
        self.assertEqual(
            serie_to_list (testDataType(df['col2'],'Int'))
            ,[[1, 'a'], [3, 2.2]])


    def test_is_float(self,df=df):
        self.assertEqual(
            serie_to_list (testDataType(df['col2'],'Float'))
            ,[[1, 'a']])


    def test_standard(self):
        s=pd.Series(['2018-07-06T23:45:43','2018-07-06 23:45:43','2018-07-06T24:45:43'])

        self.assertEqual(
            serie_to_list (testDataType(s,'StandardTime'))
            ,[[1, '2018-07-06 23:45:43'], [2, '2018-07-06T24:45:43']])


    def test_all_tests_for_column(self,df=df):
        self.assertEqual(
            test_column(df['col1'],{"DataType": "Int","IsUnique": "true"})
            ,[{'DataType': [[0, 'a'], [2, 'nan'], [3, 'nan']]}, {'IsNull': [[2, 'nan'], [3, 'nan']]}])


    def test_all_tests_for_dataframe_with_errors(self, df=df, meta=meta):
        self.assertEqual(
            full_test(df, meta),
            (False, [{'col1': [{'DataType': [[0, 'a'], [2, 'nan'], [3, 'nan']]}, {'IsNull': [[2, 'nan'], [3, 'nan']]}]}, {'col2': [{'DataType': [[1, 'a'], [3, 2.2]]}, {'IsUnique': [[0, 1], [2, 1]]}]}])
            )


    def test_all_tests_for_dataframe_all_tests_pass_without_error(self, df=df, meta=meta):
        df  = pd.DataFrame(data={'col1': [2, 1,3,4], 'col2': [1, 2,3,4]})

        self.assertEqual(
            full_test(df, meta),
            (True, [])
            )

class CategoryTest(unittest.TestCase):

    def setUp(self):

        cat = create_cat_tree('Parent1')
        cat2 = create_cat_tree('Child1',cat.id)
        cat3 = create_cat_tree('Child2',cat.id)


    def tearDown(self):
        delete_cat_tree(CategoryTree.get(CategoryTree.name == 'Child1').id)
        delete_cat_tree(CategoryTree.get(CategoryTree.name == 'Child2').id)
        delete_cat_tree(CategoryTree.get(CategoryTree.name == 'Parent1').id)

    def test_already_exist_without_parent_id(self):
        with self.assertRaises(CustomPeeweeError) as error:
            a=  create_cat_tree('Parent1')
        db.close()

    def test_already_exist_with_parent_id(self):
        with self.assertRaises(CustomPeeweeError) as error:
            create_cat_tree('Child1',CategoryTree.get(CategoryTree.name == 'Parent1').id)
        db.close()


if __name__ == '__main__':
    initialize_categories()
    unittest.main()


## SEARCH KEYWORDS FUNCTION HAS A BUG
class SearchKeywordsTest(unittest.TestCase):
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
