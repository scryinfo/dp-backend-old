import json
import unittest
import warnings

from api import api_categories, ScryApiException, ScryApi, api_protected, api_publisher, api_search, api_getcategories, \
    api_test_json
from categories import create_category
from model import db, Categories

meta_path='./demo/metadata/'

# "CategoryName" missing. Here written with an "s" --> "CategoryNames"
def test_no_categories():
    payload={
    "CategoryNames": ["Aviation","Commercial Flights","Airport Info"],
    "DataStructure":
            [
            {"AirlineId": {"DataType":"Int", "IsUnique":"true","IsPrimaryKey":"true"}}
            ]
    }
    return api_categories(payload, headers=None)

# "DataStructure" missing. Here written with an "s" --> "DataStructures"
def test_no_datastructure():
    payload={
    "CategoryName": ["Aviation","Commercial Flights","Airport Info"],
    "DataStructures":
            [
            {"AirlineId": {"DataType":"Int", "IsUnique":"true","IsPrimaryKey":"true"}}
            ]
    }
    return api_categories(payload, headers=None)

# "DataType" written with an "s" --> "DataTypes"
def test_categories_dirty():
    payload={
    "CategoryName": ["Aviation","Commercial Flights","Airport Info"],
    "DataStructure":
            [
            {"AirlineId": {"DataTypes":"Int", "IsUnique":"true","IsPrimaryKey":"true"}},
            ]
    }
    return api_categories(payload=payload, headers=None)


def test_categories(upayload):
    jwtToken= ScryApi().login(**upayload)
    headers = {"Authorization": "JWT "+jwtToken}
    payload={
    "CategoryName": ["Aviation6", "Commercial Flights", "Airport Info"],
    "DataStructure":
            [
            {"AirlineId": {"DataType":"Int", "IsUnique":"true","IsPrimaryKey":"true"}},
            {"AirlineName": {"DataType":"String", "IsUnique":"true"}},
            {"ANA": {"DataType":"String", "IsUnique":"true"}},
            {"IATA": {"DataType":"String", "IsUnique":"true", "IsNull":"true"}},
            {"IACAO": {"DataType":"String", "IsUnique":"true", "IsNull":"true"}},
            {"Callsign":{"DataType":"String", "IsUnique":"true"}},
            {"Country": {"DataType":"String"}},
            {"Active": {"DataType":"String"}}
            ]
    }
    return api_categories(payload, headers)


def test_json():
    payload={"CategoryNames": ["Aviation","Commercial Flights","Airport Info"],"Test":True}
    payload=json.dumps(payload)
    print(payload)
    print(type(payload))
    print(api_test_json(payload))


def test_getcategories(payload):
    jwtToken= ScryApi().login(**payload)
    headers = {"Authorization": "JWT "+jwtToken}
    return api_getcategories(headers)


userpayload={'username':'22', 'password':'22'}
#scry_path='https://dev.scry.info:443/scry2/'
#publisher_path='https://dev.scry.info:443/meta/'


class JWTTest(unittest.TestCase):
    def test_correct_authentication(self):
        ScryApi().login(**userpayload)

    def test_wrong_authentication(self):
        with self.assertRaises(Exception):
            ScryApi().login(username='22', password='223')

    def test_aut1(self):
        jwtToken = ScryApi().login(**userpayload)
        headers = {"Authorization": "JWT " + jwtToken}
        with self.assertRaises(ScryApiException):
            r = api_protected(headers)

    def test_aut2(self):
        jwtToken = ScryApi().login(**userpayload)
        jwtToken = jwtToken + 'a'
        with self.assertRaises(ScryApiException):
           api_protected({"Authorization": "JWT " + jwtToken})


class CategoryTest(unittest.TestCase):

    def setUp(self):
        #db.execute_sql("""DELETE FROM scry2.categories where name='["Aviation6", "Commercial Flights", "Airport Info"]';""")
        return

    def tearDown(self):
        db.execute_sql("""DELETE FROM scry2.categories where name='["Aviation6", "Commercial Flights", "Airport Info"]';""")

    def test_create_new_category(self):
        self.assertEqual(test_categories(userpayload),'{"Result": "Category Created"}')

    def test_category_exists(self):
        test_categories(userpayload)
        self.assertEqual(test_categories(userpayload),'{"Result": "CategoryName already exists"}')

    def test_create_categories(self):
        self.assertEqual(test_no_categories(), '{"Result": "No \'CategoryName\'"}')

    def test_no_datastructure(self):
        self.assertEqual(test_no_datastructure(),'{"Result": "No \'DataStructure\'"}')

    def test_categories_dirty(self):
        self.assertEqual(test_categories_dirty(),'{"Result": "Metadata Error", "DataErrors": [["AirlineId", "DataTypes", "Int", "KeyError(\'DataTypes\',)"]]}')
#        '{"DataErrors": [["AirlineId", "DataTypes", "Int", "Key Error"], ["AirlineName", "DataType", "Strings", "No Match"]], "Result": "Metadata Error"}')


def publish_data(data_file_path, listing_file_path, userpayload=userpayload):
    jwtToken= ScryApi().login(**userpayload)
    headers = {"Authorization": "JWT "+jwtToken}

    f1=open(data_file_path,'rb')
    f2= open(listing_file_path)
    files = {'data': f1,'listing_info':f2}

    return api_publisher(files, headers)


def publish_data_no_data(data_file,listing_file):
    jwtToken= ScryApi().login(**userpayload)
    headers = {"Authorization": "JWT "+jwtToken}

    f1=open(data_file,'rb')
    f2= open(listing_file)
    files ={'listing_info':f2}
    return api_publisher(files, headers)


def publish_data_no_JWT(data_file, listing_file, userpayload=userpayload):
    f1=open(data_file,'rb')
    f2= open(listing_file)
    files ={'listing_info':f2}

    return api_publisher(files, headers=None)


def publish_data_wrong_JWT(data_file, listing_file, userpayload=userpayload):
    jwtToken= ScryApi().login(**userpayload)
    jwtToken = jwtToken + 'a'
    headers = {"Authorization": "JWT " + jwtToken}

    f1=open(data_file,'rb')
    f2= open(listing_file)
    files ={'listing_info':f2}

    return api_publisher(files, headers)


def publish_data_no_listing(data_file, listing_file, userpayload=userpayload):
    jwtToken= ScryApi().login(**userpayload)
    headers = {"Authorization": "JWT "+jwtToken}

    f1=open(data_file,'rb')
    f2= open(listing_file)
    files ={'data': f1}

    return api_publisher(files, headers)


def search_keywords(keywords, searchtype, userpayload=userpayload):
    jwtToken= ScryApi().login(**userpayload)
    headers = {"Authorization": "JWT "+jwtToken}

    payload = {
        'keywords': keywords,
        'searchtype' : searchtype
        }
    return api_search(payload, headers)


data_path='./demo/data/'
listing_path='./demo/listing_info/'


class PublisherTest(unittest.TestCase):

    def test_publish_with_no_JWT(self):
        warnings.simplefilter("ignore")
        with self.assertRaises(ScryApiException):
            publish_data_no_JWT(data_path+"airlines_null.dat",listing_path+"Airlines_listing.json")

    def test_Null_in_NotNull_Column(self):
        warnings.simplefilter("ignore")
        self.assertEqual(publish_data(data_path+"airlines_null.dat",listing_path+"Airlines_listing.json"),"[\"Test Failed\", {\"DataType\": [], \"FieldLength\": [], \"ForeignDataHash\": [], \"IsNull\": [[\"IATA\", [\"2\", null]], [\"ICAO\", [\"0\", null], [\"1\", null]], [\"Callsign\", [\"1\", null]], [\"Country\", [\"1\", null]]], \"IsPrimaryKey\": [], \"IsUnique\": []}]")

    def test_Duplicates_in_Unique_Column(self):
        warnings.simplefilter("ignore")
        publish_data(data_path+"airlines_duplicate.dat",listing_path+"Airlines_listing.json")
        self.assertEqual(publish_data(data_path+"airlines_duplicate.dat",listing_path+"Airlines_listing.json"),"[\"Test Failed\", {\"DataType\": [], \"FieldLength\": [], \"ForeignDataHash\": [], \"IsNull\": [], \"IsPrimaryKey\": [], \"IsUnique\": [[\"AirlineId\", [\"2\", 2], [\"3\", 2]]]}]")

    def test_Float_and_String_in_int_Column(self):
        warnings.simplefilter("ignore")
        self.assertEqual(publish_data(data_path+"airlines_int.dat",listing_path+"Airlines_listing.json"),"[\"Test Failed\", {\"DataType\": [[\"AirlineId\", [\"1\", \"1.1\"], [\"2\", \"2a\"]]], \"FieldLength\": [], \"ForeignDataHash\": [], \"IsNull\": [], \"IsPrimaryKey\": [], \"IsUnique\": []}]")

    def test_String_in_float_Column(self):
        warnings.simplefilter("ignore")
        self.assertEqual(publish_data(data_path+"airlines_float.dat",listing_path+"Airlines_listing_float.json"),"[\"Test Failed\", {\"DataType\": [[\"AirlineId\", [\"2\", \"2a\"]]], \"FieldLength\": [], \"ForeignDataHash\": [], \"IsNull\": [], \"IsPrimaryKey\": [], \"IsUnique\": []}]")

    def test_insert_schedule_data_successfully(self):
        warnings.simplefilter("ignore")
        self.assertEqual(publish_data(data_path+"schedule.csv",listing_path+"Schedule_listing.json"),"\"Success\"")

    def test_data_file_missing(self):
        warnings.simplefilter("ignore")
        with self.assertRaises(ScryApiException):
            publish_data_no_data(data_path + "schedule.csv", listing_path + "Schedule_listing.json")

    def test_data_listing_missing(self):
        warnings.simplefilter("ignore")
        with self.assertRaises(ScryApiException):
            json.loads(publish_data_no_listing(data_path+"schedule.csv",listing_path+"Schedule_listing.json"))

    def test_insert_schedule_data_successfully(self):
        warnings.simplefilter("ignore")
        self.assertEqual(publish_data(data_path+"schedule.csv", listing_path+"Schedule_listing.json"), "\"Success\"")


if __name__ == '__main__':
    unittest.main()


## SEARCH KEYWORDS FUNCTION HAS A BUG
class SearchKeywordsTest(unittest.TestCase):


    def setUp(self):
        userpayload={'username':'22','password':'22'}
        jwtToken= ScryApi().login(**userpayload)
        headers = {"Authorization": "JWT "+jwtToken}

        #Create category
        metadata=json.load(open(meta_path+'Schedule_Metadata.json'))
        metadata['CategoryName']=["Search Keywords"]
        create_category(db,["Search Keywords"],metadata)

        #Create Listing
        f1=open(data_path+"schedule.csv",'rb')
        f2= json.loads='{"category_name":["Search Keywords"],"price":1000,"filename":"Airlines_float.csv","keywords":"blabla"}'
        files = {'data': f1,'listing_info':f2}
        api_publisher(files=files, headers=headers)

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
