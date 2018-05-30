#JWT TOKEN eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJuYW1lIjoiMjIiLCJhY2NvdW50IjoiMHg0MDc4NDA3YzlhNGIxNzNmNjc5ZTQ3MGY1YjE2N2FmMmQ3MTU2NDFiIiwiaWF0IjoxNTI3NTAwNDkzLCJleHAiOjE1Mjc3MTY0OTN9._-HKiuAc_LUJOHrY5hUAOPMaBY2dxAAQAVr7Q0RblOU
from model import db, Categories, Trader
from peewee import IntegrityError,OperationalError,InternalError
from flask import Flask,request
from flask_cors import CORS
from flask_jwt import JWT, jwt_required, current_identity
from categories import create_category,testMetaData

#from werkzeug.security import safe_str_cmp
import json


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

jwt = JWT(app, authenticate, identity)

@app.errorhandler(500)
def server_internal_Error(e):
    return 'interal error', 500


@app.route('/categories',methods=['POST'])
@jwt_required()
def  categories():

    # TEST 1 : Is it a JSON
    if request.is_json:
        data=request.get_json()
        print(data)
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
        rs=create_category(db, catname,json.dumps(data))
        if rs=='already exists':
            return json.dumps({'Result':'Category Name already exists'})
        else:
            return json.dumps({'Result':'Category Created'})
    else:
        return json.dumps({'Result':'Not Json'})



@app.route('/getcategories',methods=['POST'])
def  getcategories():
    cat_list=[]
    for cat in Categories.select():
        cat_list.append(cat.metadata)

    return str(cat_list)


if __name__ == '__main__':
    app.run(port=2222)
