import requests
import json
from categories import create_category


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

    r = requests.post(path+'categories', json = payload)

    result=r.text
    print(result)
    return result

def test_no_datastructure(path):


    payload={
    "CategoryName": ["Aviation","Commercial Flights","Airport Info"],
    "DataStructures":
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

    r = requests.post(path+'categories', json = payload)

    result=r.text
    print(result)
    return result

def test_categories_dirty(path):


    payload={
    "CategoryName": ["Aviation","Commercial Flights","Airport Info"],
    "DataStructure":
            [
            {"AirlineId": {"DataTypes":"Int", "IsUnique":"true","IsPrimaryKey":"true"}},
            {"AirlineName": {"DataType":"Strings", "IsUnique":"true"}},
            {"ANA": {"DataType":"String", "IsUnique":"true"}},
            {"IATA": {"DataType":"String", "IsUnique":"true", "IsNull":"true"}},
            {"IACAO": {"DataType":"String", "IsUnique":"true", "IsNull":"true"}},
            {"Callsign":{"DataType":"String", "IsUnique":"true"}},
            {"Country": {"DataType":"String"}},
            {"Active": {"DataType":"String"}}
            ]
    }

    r = requests.post(path+'categories', json = payload)

    result=r.text
    print(result)
    return result


def test_categories(path,jwt_server_path,upayload):
    jwtToken=test_jwt_scry(jwt_server_path,upayload)
    headers = {"Authorization": "JWT "+jwtToken}
    payload={
    "CategoryName": ["Aviation", "Commercial Flights", "Airport Info"],
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




#print(test_no_json(publisher_path)=='Not Json')
#print(test_no_categories(publisher_path)=='{"Result": "No Category"}')
#print(test_no_datastructure(publisher_path)=='{"Result": "No Data Structure"}')
#print(test_categories_dirty(publisher_path)=='{"Result": "Metadata Error", "DataErrors": [["AirlineId", "DataTypes", "Int", "Key Error"], ["AirlineName", "DataType", "Strings", "No Match"]]}')


#print(test_jwt_scry(scry_path,userpayload))
#print(test_getcategories(publisher_path,scry_path,userpayload)=='{"Result": "Category Created"}')

#print(test_categories(publisher_path,scry_path,userpayload)=='{"Result": "Category Created"}')
#
#print(test_auth_right_JWT(publisher_path,scry_path,userpayload))

#print(test_categories(publisher_path,scry_path,userpayload)=='{"Result": "Category Name already exists"}')

#print(test_getcategories(publisher_path,scry_path,userpayload)=='{"Result": "Category Created"}')



def test_publisher(publisher_path,jwt_server_path,userpayload):
    jwtToken=test_jwt_scry(jwt_server_path,userpayload)
    headers = {"Authorization": "JWT "+jwtToken}

    payload={
    "category_name":["Aviation","Commercial Flights","Airport Info"]
    , "IPFS_hash":"QmRG9U8akdxckFjm5MYRy9mxcaoMytrD2pE6stwKhzNTSf" #airlines 1 line
#    , "IPFS_hash":"Qmao4wg8KPxqjpcNsN55dJXxJ3kuBwMQSZ26SFemqMBUm7" #airlines all
    ,"price":1000
    ,"filename":"file5"
    ,"keywords":"Aviation,Commercial,Airline"
    }

    r = requests.post(publisher_path+'publisher', json = payload,headers=headers)

    result=r.text
    print(result)
    return result

print(test_publisher(publisher_path,scry_path,userpayload))
