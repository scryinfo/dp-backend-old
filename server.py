#JWT TOKEN eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJuYW1lIjoiMjIiLCJhY2NvdW50IjoiMHg0MDc4NDA3YzlhNGIxNzNmNjc5ZTQ3MGY1YjE2N2FmMmQ3MTU2NDFiIiwiaWF0IjoxNTI3NTAwNDkzLCJleHAiOjE1Mjc3MTY0OTN9._-HKiuAc_LUJOHrY5hUAOPMaBY2dxAAQAVr7Q0RblOU
from model import db, Categories, Trader
from peewee import IntegrityError,OperationalError,InternalError
from flask import Flask,request
from flask_cors import CORS
from flask_jwt import JWT, jwt_required, current_identity
from categories import create_category,testMetaData
from publisher import publish_data


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
#@jwt_required()
def  categories():

    # TEST 1 : Is it a JSON
    if request.is_json:
        data=request.get_json()
        json_data=data

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
        rs=create_category(db, catname,data)
#        rs=create_category(db, catname,json_data)
        if rs=='already exists':
            return json.dumps({'Result':'Category Name already exists'})
        elif rs=='success':
            return json.dumps({'Result':'Category Created'})
        else:
            return json.dumps({'Result':'Category Not Created'})
    else:
        return json.dumps({'Result':'Not Json'})



@app.route('/publisher',methods=['POST'])
@jwt_required()
def  publisher():
    json_data=request.get_json()

    print(json_data)
    catname=json.dumps(json_data['category_name'])
    file_cid=json_data['IPFS_hash']
    price=json_data['price']
    filename=json_data['filename']
    keywords=json_data['keywords']
    trader_id=current_identity


    print(catname)
    print(file_cid)
    print(price)
    print(filename)
    print(keywords)
    print(trader_id)

    result=publish_data (catname, file_cid,trader_id,price,filename,keywords)

    return result

@app.route('/getcategories',methods=['POST'])
@jwt_required()
def  getcategories():
    cat_list=[]
    for cat in Categories.select():
        cat_list.append(cat.metadata)
    db.close()

    return str(cat_list)



@app.route('/protected')
@jwt_required()
def protected():


    return '%s' % current_identity

if __name__ == '__main__':
    app.run(port=2222)
