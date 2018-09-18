import unittest
import requests
import json
import os

# Can create a new user by going on the website. Dev.scry.info
userpayload={'username':'22','password':'22'}

# Dev Environment paths
publisher_path='http://localhost:2222/'
scry_path='https://dev.scry.info:443/scry2/'

# Production Environment paths
scry_path='http://localhost:1234/'
publisher_path='https://dev.scry.info:443/meta/'





def get_jwt_scry():
    r = requests.post(scry_path+'login', json = userpayload)
    rs=json.loads(r.text)
    jwtToken=json.loads(r.text)['token']
    return jwtToken


def test_jwt():
    try:
        get_jwt_scry()
        return True
    except:
        return False



jwtToken=get_jwt_scry()
headers = {"Authorization": "JWT "+jwtToken}

def publisher(meta_payload):
    r = requests.post(publisher_path+'publisher'+route,files=meta_payload,headers=headers)
    return result

def create_category(meta):
    r = requests.post(publisher_path+'categories', json = meta,headers=headers)
    result=r.text
    print(result)
    return result

def get_categories():
    r = requests.get(publisher_path+'getcategories',json='{"a":"a"}',headers=headers)
    result=r.text
    return result

def publish_data(data_file,listing_file):
    f1=open(data_file,'rb')
    f2= open(listing_file)
    files = {'data': f1,'listing_info':f2}

    print (files)
    r = requests.post(publisher_path+'publisher',files=files,headers=headers)
    result=r.text
    print(result)

def publish_data_no_data(data_file,listing_file):
    f1=open(data_file,'rb')
    f2= open(listing_file)
    files ={'listing_info':f2}

    r = requests.post(publisher_path+'publisher',files=files,headers=headers)
    result=r.text
    print(result)

def publish_data_no_listing(data_file,listing_file):
    f1=open(data_file,'rb')
    f2= open(listing_file)
    files ={'data': f1}

    r = requests.post(publisher_path+'publisher',files=files,headers=headers)
    result=r.text
    print(result)

def listing_category_id(cat_id):
    payload = {'category_id': cat_id}
    r = requests.get(publisher_path+'listing_by_categories',params=payload,headers=headers)
    result=r.text
    print(result)






# No "CategoryName" --> in this case mispelled with an "s" at the end
def test_no_categories():

    payload={
    "CategoryNames": ["Aviation","Commercial Flights","Airport Info"],
    "DataStructure":
            [
                {"AirlineId":
                    {"DataType":"Int", "IsUnique":"true","IsPrimaryKey":"true"}
                }
            ]
    }

    r = requests.post(publisher_path+'categories', json = payload,headers=headers)

    result=r.text
    print(result)
    return result

# No "DataStructure" --> in this case mispelled with an "s" at the end
def test_no_datastructure():
    payload={
    "CategoryName": ["Aviation","Commercial Flights","Airport Info"],
    "DataStructures":
            [
                {"AirlineId": {"DataType":"Int", "IsUnique":"true","IsPrimaryKey":"true"}},
            ]
    }

    r = requests.post(publisher_path+'categories', json = payload)

    result=r.text
    print(result)
    return result

# No "DataType" --> in this case mispelled with an "s" at the end# "DataType" written with a "s"
def test_categories_no_datatype():
    payload={
    "CategoryName": ["Aviation","Commercial Flights","Airport Info"],
    "DataStructure":
            [
                {"AirlineId": {"DataTypes":"Int", "IsUnique":"true","IsPrimaryKey":"true"}},
            ]
    }

    r = requests.post(publisher_path+'categories', json = payload)

    result=r.text
    print(result)
    return result

# This one is supposed to work
def test_categories():
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

    r = requests.post(publisher_path+'categories', json = payload,headers=headers)
    return r.text

def test_categories_wrong_datatype_int():
    payload={
    "CategoryName": ["Aviation","Commercial Flights","Airport Info"],
    "DataStructure":
            [
                {"AirlineId": {"DataType":"int", "IsUnique":"true","IsPrimaryKey":"true"}},
            ]
    }

    r = requests.post(publisher_path+'categories', json = payload)

    result=r.text
    print(result)
    return result



# TESTING CATEGORIES CREATION

#assert (test_jwt)
#assert (test_no_categories()=='{"Result": "No Category"}')
#assert (test_no_datastructure()=='{"Result": "No Data Structure"}')
#assert(test_categories_no_datatype()=='{"DataErrors": [["AirlineId", "DataTypes", "Int", "Key Error"]], "Result": "Metadata Error"}')
#assert(test_categories_wrong_datatype_int()=='{"DataErrors": [["AirlineId", "DataType", "int", "No Match"]], "Result": "Metadata Error"}')


data_path='/home/chuck/scry3/publisher/demo/data/'
listing_path='/home/chuck/scry3/publisher/demo/listing_info/'

with open('./demo.json') as jsonfile:
    test_data=json.load(jsonfile)

meta_path='/home/chuck/scry3/publisher/demo/metadata/'
meta_files=os.listdir(meta_path)

# CREATE CATEGORIES
#for files in meta_files:
#    metadata=json.load(open(meta_path+files))
#    create_category(metadata)


for i in test_data:
    print(i)
#    print (i['Listing'])
#    print(publish_data(data_path+i['Data'],listing_path+i['Listing']))

#print(listing_category_id(51))
#print(listing_category_id(217))
