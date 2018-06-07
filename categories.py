from model import db, Categories
import json
from peewee import IntegrityError,OperationalError,InternalError
from flask import jsonify

masterMetaData={
                 "DataType":["String","Int","Float","Date","Datetime","StandardTime"],
                 "IsNull" : ["true","false"],
                 "IsUnique":["true","false"],
                 "ForeignDataHash":"String",
                 "IsPrimaryKey":["true","false"],
                 "FieldLength":"Int",


            }



# receives a dictionary "meta" in the python format ex : {'a':'a'}
# postgresql transforms it into jsonb format {"a":"a"}
def create_category(db,catname,meta):
    try:
        db.close()
        db.connect()
        cat = Categories.create(name=json.dumps(catname), metadata=meta)
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


# This function is part of testMetaData (see below)
def verifyElement(key_,val,master=masterMetaData):
    try:
        masterValues=master[key_]
        if type(masterValues)==list:
            for i in masterValues:
                if i==val:
                    return("Success")
            return('No Match')
        else:
            if masterValues=="Int":
                try:
                    int(val)
                    return ("Success")
                except:
                    return("Not an int")
            return ("No test for this format yet")

    except KeyError:
        return("Key Error")

# This function is used to verify Metadata structure (input from categories)
def validate_category(ds,master=masterMetaData):
    print("TEST METADATA")
    print(ds)
    testResult=[]
    res=''
    for d in ds:
    #ex : d= {airlineId : {'IsPrimaryKey': 'true', 'IsUnique': 'true', 'DataType': 'Int'}}
        colname=list(d.keys())[0] # Ex : airlineId
        val=next(iter(d.values())) # Ex : {'IsPrimaryKey': 'true', 'IsUnique': 'true', 'DataType': 'Int'}
        for key in val:
            res=verifyElement(key,val[key],master)
            if res!='Success':
                testResult+=[[colname,key,val[key],res]]
    if len(testResult)==0:
        testResult=['Passed']
    return testResult
