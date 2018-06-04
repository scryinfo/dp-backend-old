from model import db, Categories
import json
from peewee import IntegrityError,OperationalError,InternalError
from flask import jsonify

masterMetaData={
                 "DataType":["String","Int","Float","Date","Datetime"],
                 "IsNull" : ["true","false"],
                 "IsUnique":["true","false"],
                 "ForeignDataHash":"String",
                 "IsPrimaryKey":["true","false"]
            }




def create_category(db,catname,meta):

    a=json.dumps({"a":"a"})
    print(a)
    db.connect()
    import random
    name=str(random.randint(1,100000))
    cat = Categories.create(name=name, metadata=meta)

#    cat = Categories.create(name=json.dumps(catname), metadata=str(json.dumps(meta)))

    cat.save()
    db.close()
'''
    try:
        db.connect()
        cat = Categories.create(name=json.dumps(catname), metadata=jsonify(meta))

#        cat = Categories.create(name=json.dumps(catname), metadata=json.dumps(meta))
        cat.save()
        db.close()
        result='success'
    except IntegrityError:
        db.rollback()
        result='already exists'
    except OperationalError:
        db.rollback()
        result='operational error'
    except InternalError:
        db.rollback()
        result='internal error'
    except:
        db.rollback()
        result='other error'
    print(result)
    return result
'''


# This function is part of testMetaData (see below)
def verifyStructure(key_,val,master=masterMetaData):
    try:
        masterValues=master[key_]
        if type(masterValues)==list:
            for i in masterValues:
                if i==val:
                    return("Success")
            return('No Match')
    except KeyError:
        return("Key Error")

# This function is used to verify Metadata structure (input from categories)
def testMetaData(ds,master=masterMetaData):
    print("TEST METADATA")
    print(ds)
    testResult=[]
    res=''
    for d in ds:
#        print(d)
        colname=list(d.keys())[0]
        val=next(iter(d.values()))
        for key in val:
            res=verifyStructure(key,val[key],master)
            if res!='Success':
                testResult+=[[colname,key,val[key],res]]
    if len(testResult)==0:
        testResult=['Passed']
    return testResult

#catname=['Aviation3', 'Commercial Flights', 'Airport Info']
#meta={'CategoryName': ['Aviation3', 'Commercial Flights', 'Airport Info'], 'DataStructure': [{'AirlineId': {'DataType': 'Int', 'IsUnique': 'true', 'IsPrimaryKey': 'true'}}, {'AirlineName': {'IsUnique': 'true', 'DataType': 'String'}}, {'ANA': {'IsUnique': 'true', 'DataType': 'String'}}, {'IATA': {'IsNull': 'true', 'IsUnique': 'true', 'DataType': 'String'}}, {'IACAO': {'IsNull': 'true', 'IsUnique': 'true', 'DataType': 'String'}}, {'Callsign': {'IsUnique': 'true', 'DataType': 'String'}}, {'Country': {'DataType': 'String'}}, {'Active': {'DataType': 'String'}}]}

#create_category(db,catname,json.dumps(meta))
