#JWT TOKEN eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJuYW1lIjoiMjIiLCJhY2NvdW50IjoiMHg0MDc4NDA3YzlhNGIxNzNmNjc5ZTQ3MGY1YjE2N2FmMmQ3MTU2NDFiIiwiaWF0IjoxNTI3NTAwNDkzLCJleHAiOjE1Mjc3MTY0OTN9._-HKiuAc_LUJOHrY5hUAOPMaBY2dxAAQAVr7Q0RblOU
from model import db, Categories, Trader
from peewee import IntegrityError,OperationalError,InternalError
from flask import Flask,request
from flask_cors import CORS
from flask_jwt import JWT, jwt_required, current_identity
from categories import create_category,testMetaData

#from werkzeug.security import safe_str_cmp
import json



masterMetaData={
                 "DataType":["String","Int","Float","Date","Datetime"],
                 "IsNull" : ["True","False"],
                 "IsUnique":["True","False"],
                 "ForeignDataHash":"String",
                 "IsPrimaryKey":["True","False"]
            }


def authenticate(username, password):
    try:
        user = Trader.select().where(Trader.name == username).get()
    except:
        user = None

    return user

def identity(payload):
    try:
        user_id = payload['identity']
    except:
        user_id = payload['user_id']
    user = Trader.select().where(Trader.id == user_id).get()
    return user_id


app = Flask(__name__)
CORS(app)

app.debug = True
app.config['SECRET_KEY'] = 'secret'
app.config['JWT_VERIFY_CLAIMS']=['signature', 'exp',  'iat']
app.config['JWT_REQUIRED_CLAIMS']=['exp',  'iat']

#jwt = JWT(app, authenticate, identity)

@app.errorhandler(500)
def server_internal_Error(e):
    return 'interal error', 500


@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity


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

@app.route("/hello")
def helloWorld():
  return "Hello, cross-origin-world!"

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
#        print ("AAAAAAAAAAAAAAAAAAAa")
#        rs='aa'
        rs=create_category(db, catname,meta)
        if rs=='already exists':
            return json.dumps({'Result':'Category Name already exists'})
        else:
            return json.dumps({'Result':'Category Created'})
    else:
        return json.dumps({'Result':'Not Json'})


if __name__ == '__main__':
    app.run(port=2222)
