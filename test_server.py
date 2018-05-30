import requests
import json
import data_testing
from categories import create_category

publisher_path='http://localhost:2222/'
scry_path='http://localhost:1234/'
payload={'username':'22','password':'22'}

#path='https://dev.scry.info:443/meta/'


def test_post(path):
    payload={'username':'1','password':'1','account':'1'}
    r = requests.post(path+'test_post', json = payload)
    print (r)
    print (r.text)


def test_no_json(path):
    payload={'username':'1','password':'1','account':'1'}
    r = requests.post(path+'test_post', data = payload)
    result=r.text
    print(result)
    return result

def test_no_categories(path):


    payload={
    "CategoryNames": ["Aviation","Commercial Flights","Airport Info"],
    "DataStructure":
            [
            {"AirlineId": {"DataType":"Int", "IsUnique":"True","IsPrimaryKey":"True"}},
            {"AirlineName": {"DataType":"String", "IsUnique":"True"}},
            {"ANA": {"DataType":"String", "IsUnique":"True"}},
            {"IATA": {"DataType":"String", "IsUnique":"True", "IsNull":"True"}},
            {"IACAO": {"DataType":"String", "IsUnique":"True", "IsNull":"True"}},
            {"Callsign":{"DataType":"String", "IsUnique":"True"}},
            {"Country": {"DataType":"String"}},
            {"Active": {"DataType":"String"}}
            ]
    }

    r = requests.post(path+'categories', json = payload)

    result=r.text
    print(result)
    return result

def test_no_datastructure(path):


    payload={
    "CategoryName": ["Aviation","Commercial Flights","Airport Info"],
    "DataStructures":
            [
            {"AirlineId": {"DataType":"Int", "IsUnique":"True","IsPrimaryKey":"True"}},
            {"AirlineName": {"DataType":"String", "IsUnique":"True"}},
            {"ANA": {"DataType":"String", "IsUnique":"True"}},
            {"IATA": {"DataType":"String", "IsUnique":"True", "IsNull":"True"}},
            {"IACAO": {"DataType":"String", "IsUnique":"True", "IsNull":"True"}},
            {"Callsign":{"DataType":"String", "IsUnique":"True"}},
            {"Country": {"DataType":"String"}},
            {"Active": {"DataType":"String"}}
            ]
    }

    r = requests.post(path+'categories', json = payload)

    result=r.text
    print(result)
    return result

def test_categories_dirty(path):


    payload={
    "CategoryName": ["Aviation","Commercial Flights","Airport Info"],
    "DataStructure":
            [
            {"AirlineId": {"DataTypes":"Int", "IsUnique":"True","IsPrimaryKey":"True"}},
            {"AirlineName": {"DataType":"Strings", "IsUnique":"True"}},
            {"ANA": {"DataType":"String", "IsUnique":"True"}},
            {"IATA": {"DataType":"String", "IsUnique":"True", "IsNull":"True"}},
            {"IACAO": {"DataType":"String", "IsUnique":"True", "IsNull":"True"}},
            {"Callsign":{"DataType":"String", "IsUnique":"True"}},
            {"Country": {"DataType":"String"}},
            {"Active": {"DataType":"String"}}
            ]
    }

    r = requests.post(path+'categories', json = payload)

    result=r.text
    print(result)
    return result


def test_categories(path):
    payload={
    "CategoryName": ["Aviation","Commercial Flights","Airport Info"],
    "DataStructure":
            [
            {"AirlineId": {"DataType":"Int", "IsUnique":"True","IsPrimaryKey":"True"}},
            {"AirlineName": {"DataType":"String", "IsUnique":"True"}},
            {"ANA": {"DataType":"String", "IsUnique":"True"}},
            {"IATA": {"DataType":"String", "IsUnique":"True", "IsNull":"True"}},
            {"IACAO": {"DataType":"String", "IsUnique":"True", "IsNull":"True"}},
            {"Callsign":{"DataType":"String", "IsUnique":"True"}},
            {"Country": {"DataType":"String"}},
            {"Active": {"DataType":"String"}}
            ]
    }

    r = requests.post(path+'categories', json = payload)

    result=r.text
    print(result)
    return result



def test_auth_right_JWT(path,jwt_server_path,payload):
    jwtToken=test_jwt_scry(jwt_server_path,payload)
    headers = {"Authorization": "JWT "+jwtToken}
    r = requests.get(path+'protected', headers=headers)
    print( 'Protected using Scry Token : '+ r.text)


def test_jwt_scry(jwt_server_path,payload):
    r = requests.post(jwt_server_path+'login', json = payload)
    rs=json.loads(r.text)
    jwtToken=json.loads(r.text)['token']
    return jwtToken



def test_auth_wrong_JWT(path,jwt_server_path,payload):
    jwtToken=test_jwt_scry(jwt_server_path,payload)
    headers = {"Authorization": "JWT "+jwtToken+'a'}
    r = requests.get(path+'protected', headers=headers)
    return 'Protected using Wrong Token : '+ r.text







print(test_no_json(publisher_path)=='Not Json')
print(test_no_categories(publisher_path)=='{"Result": "No Category"}')
print(test_no_datastructure(publisher_path)=='{"Result": "No Data Structure"}')
print(test_categories_dirty(publisher_path)=='{"Result": "Metadata Error", "DataErrors": [["AirlineId", "DataTypes", "Int", "Key Error"], ["AirlineName", "DataType", "Strings", "No Match"]]}')
print(test_categories(publisher_path)=='{"Result": "Category Created"}')
print(test_categories(publisher_path)=='{"Result": "Category Name already exists"}')
print(test_jwt_scry(scry_path,payload))
print(test_auth_right_JWT(publisher_path,scry_path,payload))

#test_auth_wrong_JWT(publisher_path,scry_path,payload)
