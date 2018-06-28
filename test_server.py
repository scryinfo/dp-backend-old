import requests
import json
from categories import create_category
from model import db, Categories
import warnings
import unittest

meta_path='./demo/metadata/'

# "CategoryName" missing. Here written with an "s" --> "CategoryNames"
def test_no_categories(path):
    payload={
    "CategoryNames": ["Aviation","Commercial Flights","Airport Info"],
    "DataStructure":
            [
            {"AirlineId": {"DataType":"Int", "IsUnique":"true","IsPrimaryKey":"true"}}
            ]
    }
    r = requests.post(path+'categories', json = payload)
    return r.text

# "DataStructure" missing. Here written with an "s" --> "DataStructures"
def test_no_datastructure(path):
    payload={
    "CategoryName": ["Aviation","Commercial Flights","Airport Info"],
    "DataStructures":
            [
            {"AirlineId": {"DataType":"Int", "IsUnique":"true","IsPrimaryKey":"true"}}
            ]
    }
    r = requests.post(path+'categories', json = payload)
    return r.text

# "DataType" written with an "s" --> "DataTypes"
def test_categories_dirty(path):
    payload={
    "CategoryName": ["Aviation","Commercial Flights","Airport Info"],
    "DataStructure":
            [
            {"AirlineId": {"DataTypes":"Int", "IsUnique":"true","IsPrimaryKey":"true"}},
            ]
    }
    r = requests.post(path+'categories', json = payload)
    return r.text


def test_categories(path,jwt_server_path,upayload):
    jwtToken=test_jwt_scry(jwt_server_path,upayload)
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

    r = requests.post(path+'categories', json = payload,headers=headers)
    result=r.text
    print(result)
    return result




def test_jwt_scry(jwt_server_path,payload):
    r = requests.post(jwt_server_path+'login', json = payload)
    rs=json.loads(r.text)
    jwtToken=json.loads(r.text)['token']
    return jwtToken


def test_auth_right_JWT(path,jwt_server_path,payload):
    jwtToken=test_jwt_scry(jwt_server_path,payload)
    headers = {"Authorization": "JWT "+jwtToken}
    r = requests.get(path+'protected', headers=headers)
    return('Protected using Scry Token : '+ r.text)





def test_auth_wrong_JWT(path,jwt_server_path,payload):
    jwtToken=test_jwt_scry(jwt_server_path,payload)
    print(jwtToken)
    headers = {"Authorization": "JWT "+jwtToken+'a'}
    r = requests.get(path+'protected', headers=headers)
    return 'Protected using Wrong Token : '+ r.text




def test_json(path):
    payload={"CategoryNames": ["Aviation","Commercial Flights","Airport Info"],"Test":True}
    payload=json.dumps(payload)
    print(payload)
    print(type(payload))
    r = requests.post(path+'test_json', json = payload)
    print(r.text)



def test_getcategories(path,jwt_server_path,payload):
    jwtToken=test_jwt_scry(jwt_server_path,payload)
    headers = {"Authorization": "JWT "+jwtToken}

    r = requests.post(path+'getcategories', headers=headers)

    result=r.text
    print(result)
    return result

publisher_path='http://localhost:2222/'
scry_path='http://localhost:1234/'
userpayload={'username':'22','password':'22'}
#scry_path='https://dev.scry.info:443/scry2/'
#publisher_path='https://dev.scry.info:443/meta/'



class JWT_Test(unittest.TestCase):

    def test_wrong_authentication(self):
        userpayload2={'username':'22','password':'223'}
        r=''
        try:
            test_jwt_scry(scry_path,userpayload2)
        except KeyError:
            r='Wrong Credentials'
        self.assertEqual(r,'Wrong Credentials')

def publish_data(data_file,listing_file,userpayload=userpayload,publisher_path=publisher_path,scry_path=scry_path):
    jwtToken=get_jwt_scry(scry_path,userpayload)
    headers = {"Authorization": "JWT "+jwtToken}

    f1=open(data_file,'rb')
    f2= open(listing_file)
    files = {'data': f1,'listing_info':f2}

    r = requests.post(publisher_path+'publisher',files=files,headers=headers)
    return r.text


class CategoryTest(unittest.TestCase):

    def setUp(self):
        #db.execute_sql("""DELETE FROM scry2.categories where name='["Aviation6", "Commercial Flights", "Airport Info"]';""")
        return

    def tearDown(self):
        db.execute_sql("""DELETE FROM scry2.categories where name='["Aviation6", "Commercial Flights", "Airport Info"]';""")

    def test_create_new_category(self):
        self.assertEqual(test_categories(publisher_path,scry_path,userpayload),'{"Result": "Category Created"}')

    def test_category_exists(self):
        test_categories(publisher_path,scry_path,userpayload)
        self.assertEqual(test_categories(publisher_path,scry_path,userpayload),'{"Result": "Category Name already exists"}')

    def test_create_categories(self):
        self.assertEqual(test_no_categories(publisher_path), '{"Result": "No Category"}')

    def test_no_datastructure(self):
        self.assertEqual(test_no_datastructure(publisher_path),'{"Result": "No Data Structure"}')

    def test_categories_dirty(self):
        self.assertEqual(test_categories_dirty(publisher_path),'{"Result": "Metadata Error", "DataErrors": [["AirlineId", "DataTypes", "Int", "Key Error"]]}')
#        '{"DataErrors": [["AirlineId", "DataTypes", "Int", "Key Error"], ["AirlineName", "DataType", "Strings", "No Match"]], "Result": "Metadata Error"}')



def publish_data(data_file_path,listing_file_path,userpayload=userpayload,publisher_path=publisher_path,scry_path=scry_path):
    jwtToken=test_jwt_scry(scry_path,userpayload)
    headers = {"Authorization": "JWT "+jwtToken}

    f1=open(data_file_path,'rb')
    f2= open(listing_file_path)
    files = {'data': f1,'listing_info':f2}

    r = requests.post(publisher_path+'publisher',files=files,headers=headers)

    return r.text

def publish_data_no_data(data_file,listing_file,publisher_path=publisher_path,scry_path=scry_path,userpayload=userpayload):
    jwtToken=test_jwt_scry(scry_path,userpayload)
    headers = {"Authorization": "JWT "+jwtToken}

    f1=open(data_file,'rb')
    f2= open(listing_file)
    files ={'listing_info':f2}

    r = requests.post(publisher_path+'publisher',files=files,headers=headers)
    result=r.text
    return result

def publish_data_no_JWT(data_file,listing_file,publisher_path=publisher_path,scry_path=scry_path,userpayload=userpayload):
    jwtToken=test_jwt_scry(scry_path,userpayload)
    headers = {"Authorization": "JWT "+jwtToken}


    f1=open(data_file,'rb')
    f2= open(listing_file)
    files ={'listing_info':f2}

    r = requests.post(publisher_path+'publisher',files=files)
    return r.text


def publish_data_wrong_JWT(data_file,listing_file,publisher_path=publisher_path,scry_path=scry_path,userpayload=userpayload):
    jwtToken=test_jwt_scry(scry_path,userpayload)

    f1=open(data_file,'rb')
    f2= open(listing_file)
    files ={'listing_info':f2}

    r = requests.post(publisher_path+'publisher',files=files)
    return r.text



def publish_data_no_listing(data_file,listing_file,publisher_path=publisher_path,scry_path=scry_path,userpayload=userpayload):
    jwtToken=test_jwt_scry(scry_path,userpayload)
    headers = {"Authorization": "JWT "+jwtToken}

    f1=open(data_file,'rb')
    f2= open(listing_file)
    files ={'data': f1}

    r = requests.post(publisher_path+'publisher',files=files,headers=headers)
    result=r.text
    return result


def search_keywords(keywords,searchtype,publisher_path=publisher_path,scry_path=scry_path,userpayload=userpayload):
    jwtToken=test_jwt_scry(scry_path,userpayload)
    headers = {"Authorization": "JWT "+jwtToken}

    payload = {
        'keywords': keywords,
        'searchtype' : searchtype
        }
    r = requests.get(publisher_path+'search_keywords',params=payload,headers=headers)
    return r.text


data_path='./demo/data/'
listing_path='./demo/listing_info/'


class PublisherTest(unittest.TestCase):

    def test_publish_with_no_JWT(self):
        warnings.simplefilter("ignore")
        self.assertEqual(json.loads(publish_data_no_JWT(data_path+"airlines_null.dat",listing_path+"Airlines_listing.json")),{'description': 'Request does not contain an access token', 'error': 'Authorization Required', 'status_code': 401}        )

    def test_Null_in_NotNull_Column(self):
        warnings.simplefilter("ignore")
        self.assertEqual(publish_data(data_path+"airlines_null.dat",listing_path+"Airlines_listing.json"),"[\"Test Failed\", {\"DataType\": [], \"FieldLength\": [], \"ForeignDataHash\": [], \"IsNull\": [[\"IATA\", [\"2\", null]], [\"ICAO\", [\"0\", null], [\"1\", null]], [\"Callsign\", [\"1\", null]], [\"Country\", [\"1\", null]]], \"IsPrimaryKey\": [], \"IsUnique\": []}]")

    def test_Duplicates_in_Unique_Column(self):
        warnings.simplefilter("ignore")
        print(publish_data(data_path+"airlines_duplicate.dat",listing_path+"Airlines_listing.json"))
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
        self.assertEqual(json.loads(publish_data_no_data(data_path+"schedule.csv",listing_path+"Schedule_listing.json")),{'status': 'error', 'message': 'Data missing'})

    def test_data_listing_missing(self):
        warnings.simplefilter("ignore")
        self.assertEqual(json.loads(publish_data_no_listing(data_path+"schedule.csv",listing_path+"Schedule_listing.json")),{'message': 'Listing missing', 'status': 'error'})

    def test_insert_schedule_data_successfully(self):
        warnings.simplefilter("ignore")
        self.assertEqual(publish_data(data_path+"schedule.csv",listing_path+"Schedule_listing.json"),"\"Success\"")










if __name__ == '__main__':
    unittest.main()


## SEARCH KEYWORDS FUNCTION HAS A BUG
class SearchKeywordsTest(unittest.TestCase):


    def setUp(self):
        userpayload={'username':'22','password':'22'}
        jwtToken=test_jwt_scry(scry_path,userpayload)
        headers = {"Authorization": "JWT "+jwtToken}

        #Create category
        metadata=json.load(open(meta_path+'Schedule_Metadata.json'))
        metadata['CategoryName']=["Search Keywords"]
        create_category(db,["Search Keywords"],metadata)

        #Create Listing
        f1=open(data_path+"schedule.csv",'rb')
        f2= json.loads='{"category_name":["Search Keywords"],"price":1000,"filename":"Airlines_float.csv","keywords":"blabla"}'
        files = {'data': f1,'listing_info':f2}
        requests.post(publisher_path+'publisher',files=files,headers=headers)

    def tearDown(self):
        cat=Categories.get(Categories.name=='["Search Keywords"]')
        cat_id=cat.id
        db.execute_sql("""DELETE FROM scry2.listing WHERE "categoryId"={};""".format(cat_id))
        db.execute_sql("""DELETE FROM scry2.categories WHERE name='["Search Keywords"]';""")

    def test_search_keywords(self):
        print(search_keywords('blabla','["category","keywords"]'))

        self.assertEqual(test_categories(publisher_path,scry_path,userpayload),'{"Result": "Category Created"}')
