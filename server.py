#JWT TOKEN eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJuYW1lIjoiMjIiLCJhY2NvdW50IjoiMHg0MDc4NDA3YzlhNGIxNzNmNjc5ZTQ3MGY1YjE2N2FmMmQ3MTU2NDFiIiwiaWF0IjoxNTI3NTAwNDkzLCJleHAiOjE1Mjc3MTY0OTN9._-HKiuAc_LUJOHrY5hUAOPMaBY2dxAAQAVr7Q0RblOU
from model import db, Categories
from peewee import IntegrityError,OperationalError
from flask import Flask,request
from werkzeug.security import safe_str_cmp
import json



masterMetaData={
                 "DataType":["String","Int","Float","Date","Datetime"],
                 "IsNull" : ["True","False"],
                 "IsUnique":["True","False"],
                 "ForeignDataHash":"String",
                 "IsPrimaryKey":["True","False"]
            }


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
        print(d)
        colname=list(d.keys())[0]
        val=next(iter(d.values()))
        for key in val:
            res=verifyStructure(key,val[key],master)
            if res!='Success':
                testResult+=[[colname,key,val[key],res]]
    if len(testResult)==0:
        testResult=['Passed']
    return testResult

def create_category(db,catname,meta):
    try:
        db.close()
        db.connect()
        cat = Categories.create(name=json.dumps(catname), metadata=meta)
        cat.save()
        db.close()
        result='success'
    except IntegrityError:
        result='already exists'
    except OperationalError:
        result='operational error'
    return result

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'SECRET'


@app.route('/test_post',methods=['POST'])
def test_post():
    if request.is_json:
        data=request.get_json()
        print(data['username'])
        print(data)
        print(type(data))
        result =str(data)
    else:
        result ='Not Json'

    return result


@app.route('/categories',methods=['POST'])
def  categories():

    # TEST 1 : Is it a JSON
    if request.is_json:
        data=request.get_json()

        # TEST 2 : Category Name True
        try:
            catname=data['CategoryName']
        except KeyError:
            return json.dumps({'Result':'No Category'})


        # TEST 3 : DataStructure True
        try:
            meta=data['DataStructure']
        except:
            return json.dumps({'Result':'No Data Structure'})

        #TEST 4 : Test Metadata
        test_data=testMetaData(meta)
        if testMetaData(data['DataStructure'])!=['Passed']:
            return json.dumps({'Result': 'Metadata Error','DataErrors':test_data})

        #TEST 5 : Create Data

        rs=create_category(db, catname,meta)
        if rs=='already exists':
            return json.dumps({'Result':'Category Name already exists'})
        else:
            return json.dumps({'Result':'Category Created'})
    else:
        return json.dumps({'Result':'Not Json'})



if __name__ == '__main__':
    app.run(port=2222)
