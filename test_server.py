import json, os, unittest, warnings
import pandas as pd
import numpy as np
from api import ScryApiException, ScryApi, publisher_url, scry_url
from test_data import *
from categories import create_category, create_cat_tree,  delete_cat_tree,get_categories_by_name, CustomPeeweeError, get_all, remove_ids_rec, sort_all
from model import db, CategoryTree
import peewee as pe
import requests
import pyhash
from werkzeug.exceptions import HTTPException, NotFound,MethodNotAllowed
hasher = pyhash.fnv1_32()

#scry_path='https://dev.scry.info:443/scry2/'
#publisher_path='https://dev.scry.info:443/meta/'
publisher_url = 'http://localhost:2222/'
scry_url = 'http://localhost:1234/'

# meta = {        "DataStructure":
#             [
#                 {"AirlineId": {"DataType": "Int", "IsUnique": "true", "IsPrimaryKey": "true"}},
#                 {"AirlineName": {"DataType": "String", "IsUnique": "true"}},
#                 {"ANA": {"DataType": "String", "IsUnique": "true"}},
#                 {"IATA": {"DataType": "String", "IsUnique": "true", "IsNull": "true"}},
#                 {"IACAO": {"DataType": "String", "IsUnique": "true", "IsNull": "true"}},
#                 {"Callsign": {"DataType": "String", "IsUnique": "true"}},
#                 {"Country": {"DataType": "String"}},
#                 {"Active": {"DataType": "String"}}
#             ]
#     }
#
#
# # CREATE CATEGORY
# parent_id = create_category(db, hasher('Aviation6'), None, 0, None)
# parent_id = create_category(db, hasher('Commercial flights'), parent_id, 0, None)
# parent_id = create_category(db, hasher('Airport Info'), parent_id, 0, meta)
#
# #DELETE CATEGORY
# delete_cat_tree(get_categories_by_name (hasher('Airport Info'))[0])
# delete_cat_tree(get_categories_by_name (hasher('Commercial flights'))[0])
# delete_cat_tree(get_categories_by_name (hasher('Aviation6'))[0])

meta_path = './demo/metadata/'
test_credentials = {'username': '22', 'password': '22'}


def get_header(credentials):
    r = requests.post(scry_url+'login', json = credentials)
    headers = {"Authorization": "JWT "+json.loads(r.text)['token']}
    return headers


def initialize_categories():
    print("INITIALIZE ")
    headers = get_header(test_credentials)

    for files in os.listdir('./demo/metadata/'):
        fi = open('./demo/metadata/' + files)
        f = json.load(fi)
        fi.close()
        parent_id = None
        for i in f:
            js = i
            js['parent_id'] = parent_id
            r = requests.post(publisher_url+'categories', headers= headers, json = js)
            if r.status_code == 200:
                parent_id = json.loads(r.text)['id']
            else:
                parent_id = CategoryTree.get(CategoryTree.name == i['category_name']).id



class JWTTest(unittest.TestCase):
    def test_correct_authentication(self):
        get_header(test_credentials)

    def test_wrong_authentication(self):
        with self.assertRaises(Exception):
            get_header({'username': 22, 'password': 223})

    # def test_aut1(self):
    #     self.assertEqual(
    #                 requests.post(publisher_url+'protected', headers = get_header(test_credentials)),
    #                 200
    #             )

    def test_aut2(self):
        self.assertEqual(
                    requests.post(publisher_url+'protected').status_code,
                    405
                )


class CategoryTest(unittest.TestCase):

    def setUp(self):
        #db.execute_sql("""DELETE FROM scry2.categories where name='["Aviation6", "Commercial Flights", "Airport Info"]';""")
        return

    def tearDown(self):
#        db.execute_sql("""DELETE FROM scry2.categories where name='["Aviation6", "Commercial Flights", "Airport Info"]';""")
        try:
            delete_cat_tree(get_categories_by_name ('Airport Info')[0])
        except:
            pass
        try:
            delete_cat_tree(get_categories_by_name ('Commercial flights')[0])
        except:
            pass
        try:
            delete_cat_tree(get_categories_by_name ('Aviation6')[0])
        except:
            pass

    def create_cat(self, meta):
        return requests.post(publisher_url+'categories',
            headers = get_header(test_credentials),
            json = meta
            )


    def test_create_new_category(self):

        r = self.create_cat({'category_name': 'Aviation6', 'parent_id':None,'is_structured':False})
        self.assertEqual(r.status_code, 200)

    def test_category_exists(self):
        meta ={'category_name': 'Aviation6', 'parent_id':None,'is_structured':False}
        self.create_cat(meta)
        response =  self.create_cat(meta)
        self.assertEqual(response.status_code,500)


    def test_no_name(self):
        r = self.create_cat({'parent_id':None,'is_structured':False})
        self.assertEqual(r.status_code,500)

    def test_no_datastructure(self):
        r = self.create_cat({'category_name': 'Aviation6', 'parent_id': None, 'is_structured': True})
        self.assertEqual(r.status_code, 500)

    def test_invalid_metadata(self):
        r = self.create_cat({'category_name': 'Aviation6'
            , 'parent_id': None
            , 'is_structured': True
            , 'metadata':[{'airlineId': {'IsPrimaryKeys': 'true', 'IsUnique': 'trues', 'DataType': 'Int'}}] })

        self.assertEqual(r.status_code, 422)
#        print(json.loads(r.text))
#        m = [[ "airlineId","IsUnique","trues","Exception(\'No Match\',)"],["airlineId","IsPrimaryKeys","true","KeyError(\'IsPrimaryKeys\',)"]]
        m = [['airlineId', 'IsPrimaryKeys', 'true', "KeyError('IsPrimaryKeys',)"], ['airlineId', 'IsUnique', 'trues', "Exception('No Match',)"]]

        self.assertEqual(json.loads(r.text),m)




#
# def search_keywords(keywords, searchtype, userpayload=test_credentials):
#     api = ScryApi()
#     api.login(userpayload)
#     payload = {
#         'keywords': keywords,
#         'searchtype' : searchtype
#     h    }
#     return api.search(payload)


class PublisherTest(unittest.TestCase):

    data_path = './demo/data/'
    listing_path = './demo/listing_info/'
    def make_api(self):
        api = ScryApi()
        api.data_path = './demo/data/'
        api.listing_path = './demo/listing_info/'
        return api

    def last_cat_id(cat_list):
        '''cat_list expected format
                {'cat_list':['Aviation','Commercial','Airline']}
        '''
        return requests.post(publisher_url+'get_last_category_id',
            headers=get_header(test_credentials),
            json= cat_list
            )

    def publish_data(self, data=None, listing_info=None):
        api = self.make_api()
        api.login(**test_credentials)
        return api.publisher2(data=data, listing_info=listing_info)

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

        self.assertEqual(error.exception.response['error'],
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
            self.publish_data(listing_info="Airlines_listing.json")

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
            full_test(df, meta)[1],
                [{'col1': [{'DataType': [[0, 'a'], [2, 'nan'], [3, 'nan']]}, {'IsNull': [[2, 'nan'], [3, 'nan']]}]}, {'col2': [{'IsUnique': [[0, 1], [2, 1]]}, {'DataType': [[1, 'a'], [3, 2.2]]}]}]
            )


    def test_all_tests_for_dataframe_all_tests_pass_without_error(self, df=df, meta=meta):
        df  = pd.DataFrame(data={'col1': [2, 1,3,4], 'col2': [1, 2,3,4]})

        self.assertEqual(
            full_test(df, meta),
            (True, [])
            )

class CategoryTest(unittest.TestCase):
    def get_header(self, credentials):
        r = requests.post(scry_url+'login', json = credentials)
        headers = {"Authorization": "JWT "+json.loads(r.text)['token']}
        return headers

    def get_cat(self, cat_id):
        ''' cat_id is an array, [None] if wants to get all'''
        r = requests.post(publisher_url+'getcategories',headers=self.get_header(test_credentials),json=cat_id)
        return r.text

    def setUp(self):
        cat = create_category(db,'Parent1',None,False,{})
        cat2 = create_category(db,'Child1',cat.id,False,{})
        cat3 = create_category(db,'Child2',cat.id,False,{})
        cat4 = create_category(db,'Child3',cat2.id,False,{})
        cat4 = create_category(db,'Child4',cat2.id,False,{})
        cat = create_category(db,'Parent2',None,False,{})


    def tearDown(self):
        delete_cat_tree(CategoryTree.get(CategoryTree.name == 'Child4').id)
        delete_cat_tree(CategoryTree.get(CategoryTree.name == 'Child3').id)
        delete_cat_tree(CategoryTree.get(CategoryTree.name == 'Child1').id)
        delete_cat_tree(CategoryTree.get(CategoryTree.name == 'Child2').id)
        delete_cat_tree(CategoryTree.get(CategoryTree.name == 'Parent1').id)
        delete_cat_tree(CategoryTree.get(CategoryTree.name == 'Parent2').id)
#
    def test_already_exist_without_parent_id(self):


        with self.assertRaises(pe.InternalError) as error:
            a=  create_category(db,'Parent1',None,False,{})
            db.close()


    def test_already_exist_with_parent_id(self):
        with self.assertRaises(pe.InternalError) as error:
            create_category(db,'Child1',CategoryTree.get(CategoryTree.name == 'Parent1').id,False,{})
        db.close()

    def test_api_get_all_categories(self):
        self.maxDiff = None

        d =remove_ids_rec( get_all([CategoryTree.get(CategoryTree.name == 'Parent1').id])[0])
        d = sort_all([d])

        self.assertEqual(
            d,[{'children': [{'children': [{'children': [], 'name': 'Child3'}, {'children': [], 'name': 'Child4'}], 'name': 'Child1'}, {'children': [], 'name': 'Child2'}], 'name': 'Parent1'}]
            )


    def test_api_get_all_categories_none(self):
        self.maxDiff = None

        d = get_all([None])
        for i in d:
            if i['name'] == 'Parent1':
                break
        i = remove_ids_rec(i)
        i = sort_all([i])

        self.assertEqual(
            i, [{'children': [{'children': [{'children': [], 'name': 'Child3'}, {'children': [], 'name': 'Child4'}], 'name': 'Child1'}, {'children': [], 'name': 'Child2'}], 'name': 'Parent1'}]
            )




if __name__ == '__main__':
    initialize_categories()
    unittest.main()


# ## SEARCH KEYWORDS FUNCTION HAS A BUG
# class SearchKeywordsTest(unittest.TestCase):
#         userpayload={'username':'22','password':'22'}
#         api = ScryApi()
#         api.login(**userpayload)
#
#         #Create category
#         metadata=json.load(open(meta_path+'Schedule_Metadata.json'))
#         metadata['CategoryName']=["Search Keywords"]
#         create_category(db,["Search Keywords"],metadata)
#
#         #Create Listing
#         f1=open(data_path+"schedule.csv",'rb')
#         f2= json.loads='{"category_name":["Search Keywords"],"price":1000,"filename":"Airlines_float.csv","keywords":"blabla"}'
#         files = {'data': f1,'listing_info':f2}
#         api.publisher(files=files)
#
#         def tearDown(self):
#             cat=Categories.get(Categories.name=='["Search Keywords"]')
#             cat_id=cat.id
#             db.execute_sql("""DELETE FROM scry2.listing WHERE "categoryId"={};""".format(cat_id))
#             db.execute_sql("""DELETE FROM scry2.categories WHERE name='["Search Keywords"]';""")

    #WIP: "Charles" <chuck>
    # def test_search_keywords(self):
    #     print(search_keywords('blabla','["category","keywords"]'))
    #
    #     self.assertEqual(test_categories(publisher_path,scry_path,userpayload),'{"Result": "Category Created"}')
