import requests
import json
jwtToken='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJuYW1lIjoiMjIiLCJhY2NvdW50IjoiMHg0MDc4NDA3YzlhNGIxNzNmNjc5ZTQ3MGY1YjE2N2FmMmQ3MTU2NDFiIiwiaWF0IjoxNTI3NTAwNDkzLCJleHAiOjE1Mjc3MTY0OTN9._-HKiuAc_LUJOHrY5hUAOPMaBY2dxAAQAVr7Q0RblOU'

headers = {"Authorization": "JWT "+jwtToken}


#r = requests.post('http://127.0.0.1:1234/login', data = {'usernaname':'1','password':'1','account':'1'})
path='http://localhost:2222/'
payload={'username':'22','password':'22'}

path='https://dev.scry.info:443/meta/'

r = requests.post('http://localhost:5000', json = payload, headers=headers)
#r = requests.get(path, json = payload, headers=headers)

def test_post(path):
    payload={'username':'1','password':'1','account':'1'}
    r = requests.post(path+'test_post', json = payload)
    print (r)
    print (r.text)



def test_no_json(path):
    payload={'username':'1','password':'1','account':'1'}
    r = requests.post(path+'test_post', data = payload)
    print (r)
    print (r.text)

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
    print (r.text)


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
    print (r.text)


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
    print (r.text)



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
    print (r.text)

test_no_json(path)
test_no_categories(path)
test_no_datastructure(path)
test_categories_dirty(path)
test_categories(path)
test_categories(path)
