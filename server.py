#JWT TOKEN eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJuYW1lIjoiMjIiLCJhY2NvdW50IjoiMHg0MDc4NDA3YzlhNGIxNzNmNjc5ZTQ3MGY1YjE2N2FmMmQ3MTU2NDFiIiwiaWF0IjoxNTI3NTAwNDkzLCJleHAiOjE1Mjc3MTY0OTN9._-HKiuAc_LUJOHrY5hUAOPMaBY2dxAAQAVr7Q0RblOU
from flask import Flask,request, jsonify
from flask_cors import CORS
from flask_jwt import JWT, jwt_required, current_identity
from categories import create_category,validate_category
from publisher import publish_data,getMetadata,fullTest, load_data, record_listing
from model import db, Categories, Trader
from peewee import IntegrityError,OperationalError,InternalError
import simplejson
from werkzeug.utils import secure_filename
import ipfsapi, os


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

UPLOAD_FOLDER = './uploaded/'


app = Flask(__name__)
CORS(app)

app.debug = True
app.config['SECRET_KEY'] = 'secret'
app.config['JWT_VERIFY_CLAIMS']=['signature', 'exp',  'iat']
app.config['JWT_REQUIRED_CLAIMS']=['exp',  'iat']
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


jwt = JWT(app, authenticate, identity)

@app.errorhandler(500)
def server_internal_Error(e):
    return 'interal error', 500


# FROM Categories.py : uses validate_category and create_category
@app.route('/categories',methods=['POST'])
#@jwt_required()
def  categories():
    print("*******  PRINT JSON *************")
    print(request.json)
    print()
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
        test_data=validate_category(meta)
        if validate_category(data['DataStructure'])!=['Passed']:
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

@app.route('/validate_category',methods=['POST'])
@jwt_required()
def validate_metadata():
    data=request.get_json()

    # TEST 3 : DataStructure True
    try:
        meta=data['DataStructure']
    except:
        return json.dumps({'Result':'No Data Structure'})


    test_data=validate_category(meta)
    if validate_category(data['DataStructure'])!=['Passed']:
        return json.dumps({'Result': 'Metadata Error','DataErrors':test_data})
    else:
         return "Data matches metadata defitinion"



@app.route('/publisher',methods=['POST'])
@jwt_required()
def  publisher():

    print(request.files)
    print('EXTRACT FILES FOM REQUEST')
    try:
        data = request.files['data']
    except KeyError:
        return 'Missing Data file'

    try:
        listing_info=request.files['listing_info']
    except KeyError:
        return 'Listing missing'

    print('GET LISTING INFO')
    f=listing_info.read()
    f=f.decode("utf-8")
    listing_info=json.loads(f)

    catname=json.dumps(listing_info['category_name'])
    price=listing_info['price']
    filename=listing_info['filename']
    keywords=listing_info['keywords']

    print(catname, price, filename, keywords)

    print('SAVE FILE')
    file_name=secure_filename(filename)
    data.save(os.path.join(app.config['UPLOAD_FOLDER'],file_name))

    print('ADD FILE TO IPFS')
    api = ipfsapi.connect('127.0.0.1', 5001)
    res = api.add(os.path.join(app.config['UPLOAD_FOLDER'],file_name))
    IPFS_hash=res['Hash']
    filesize=res['Size']



    print(catname)
    print('GET METADATA')
    meta=getMetadata(catname)

    if meta=='Fail':
        return 'Category doesnt exist'

    print('TEST DATA')
    df=load_data(os.path.join(app.config['UPLOAD_FOLDER'],file_name),meta)
    test_result,test_failed=fullTest(df, meta)
    if test_failed==1:
        return str(simplejson.dumps(['Test Failed',test_result]))

    print('PUBLISH DATA')
    trader_id=current_identity
    result=record_listing(db,IPFS_hash,trader_id,filesize,filename,price,catname,keywords)

    print ("DATA PUBLISHED SUCCESSFULLY !!!")

    return str(simplejson.dumps(result, ignore_nan=True)) # Simple json is used to handle Nan values in test result numpy array TestIsNull

@app.route('/getcategories',methods=['POST'])
@jwt_required()
def  getcategories():
    print("GET CATEGORIES")
    cat_list=[]
    for cat in Categories.select():
        cat_list.append(cat.metadata)
    db.close()

    return jsonify(cat_list)

@app.route('/protected')
@jwt_required()
def protected():


    return '%s' % current_identity


if __name__ == '__main__':
    app.run(port=2222)
