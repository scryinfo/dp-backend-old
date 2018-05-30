from model import db,Categories
import json
from peewee import IntegrityError,OperationalError,InternalError

masterMetaData={
                 "DataType":["String","Int","Float","Date","Datetime"],
                 "IsNull" : ["True","False"],
                 "IsUnique":["True","False"],
                 "ForeignDataHash":"String",
                 "IsPrimaryKey":["True","False"]
            }


def create_category(db,catname,meta):
    try:
        db.connect()
        cat = Categories.create(name=json.dumps(catname), metadata=meta)
        cat.save()
        db.close()
        result='success'
    except IntegrityError:
        db.rollback()
        result='already exists'
    except OperationalError:
        result='operational error'
    except InternalError:
        db.rollback()
        result='internal error'
    return result



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
