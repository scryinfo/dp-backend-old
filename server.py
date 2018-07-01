#JWT TOKEN eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJuYW1lIjoiMjIiLCJhY2NvdW50IjoiMHg0MDc4NDA3YzlhNGIxNzNmNjc5ZTQ3MGY1YjE2N2FmMmQ3MTU2NDFiIiwiaWF0IjoxNTI3NTAwNDkzLCJleHAiOjE1Mjc3MTY0OTN9._-HKiuAc_LUJOHrY5hUAOPMaBY2dxAAQAVr7Q0RblOU
from flask import Flask,request, jsonify,make_response, render_template, Response
from flask_cors import CORS
from flask_jwt import JWT, jwt_required, current_identity
from categories import create_category,validate_category
from publisher import publish_data,getMetadata,fullTest, load_data, record_listing
from model import db, Categories, Trader, Listing
from peewee import IntegrityError,OperationalError,InternalError
import simplejson
from werkzeug.utils import secure_filename
import ipfsapi, os
from playhouse.shortcuts import model_to_dict




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

print(app.config['MAX_CONTENT_LENGTH'])

jwt = JWT(app, authenticate, identity)

@app.errorhandler(401)
def server_internal_Error(e):
    return jsonify({
      "description": "Signature verification failed",
      "error": "Invalid token",
      "status_code": 401
    }), 401





# FROM Categories.py : uses validate_category and create_category
@app.route('/categories',methods=['POST'])
#@jwt_required()
def categories():
    print("*******  PRINT JSON *************")
    print(request.json)
    print()

    if not request.is_json:
        return json.dumps({'Result': 'Not Json'})

    data=request.get_json()
    print(data)

    # for key in ['CategoryName', 'DataStructure']:
    #     if key not in data.keys():
    #         return json.dumps({'Result':'No %s' % key})

    try:
        #TEST 4 : Test Metadata
        test_data=validate_category(data['DataStructure'])
        if test_data != []:
            return json.dumps({'Result': 'Metadata Error','DataErrors':test_data})

        #TEST 5 : Create Data
        rs=create_category(db, data['CategoryName'],data)
    #        rs=create_category(db, catname,json_data)
        if rs=='already exists':
            return json.dumps({'Result':'CategoryName already exists'})
        elif rs=='success':
            return json.dumps({'Result':'Category Created'})
        else:
            return json.dumps({'Result':'Category Not Created'})

    except Exception as e:
        key = str(e)
        return json.dumps({'Result': 'No %s' % key})

    return json.dumps(['unexpected end'])


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
    if test_data == []:
        return "Data matches metadata defitinion"
    return json.dumps({'Result': 'Metadata Error', 'DataErrors':test_data})



@app.route('/publisher',methods=['POST'])
@jwt_required()
def  publisher():

    print(request.files)
    print('EXTRACT FILES FOM REQUEST')
    try:
        data = request.files['data']
    except KeyError:
        return make_response(jsonify({'status':'error','message':'Data missing'}),422)
    try:
        listing_info=request.files['listing_info']
    except KeyError:
        return make_response(jsonify({'status':'error','message':'Listing missing'}),422)

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

    if meta == 'Fail':

        return make_response(jsonify({'status':'error','message':'Category doesnt exist'}),422)

    print('TEST DATA')
    df = load_data(os.path.join(app.config['UPLOAD_FOLDER'],file_name),meta)
    if df is None:
        return make_response(jsonify({'status':'error','message':'Data file column number doesnt match metadata'}),422)



    test_result, test_failed=fullTest (df, meta)
    if test_failed == 1:
        return str(simplejson.dumps(['Test Failed',test_result], ignore_nan=True, sort_keys=True))



    print ('PUBLISH DATA')
    trader_id = current_identity
    result = record_listing (db, IPFS_hash, trader_id, filesize, filename, price, catname, keywords)

    print ("DATA PUBLISHED SUCCESSFULLY !!!")

    return str(simplejson.dumps(result, ignore_nan=True)) # Simple json is used to handle Nan values in test result numpy array TestIsNull

@app.route('/getcategories',methods=['GET'])
@jwt_required()
def  getcategories():
    print("GET CATEGORIES")
    cat_list=[]
    for cat in Categories.select():
        c=model_to_dict(cat)
        cat_list.append(c)
    db.close()

    return jsonify(cat_list)

@app.route('/search_keywords',methods=['GET'])
#@jwt_required()
def search_keywords():
    print("SEARCH KEYWORDS")
    # keywords / category
    searchtype = request.args.get('searchtype')
    searchtype=json.loads(searchtype)

    keywords = request.args.get('keywords')
    keywords = keywords.replace(" "," & ")

    print(searchtype)
    query_type=''

    ct=0
    for s in searchtype:
        ct+=1
        if s=='keywords':
            query_type+="to_tsvector(name)"
        elif s=='category':
            query_type+="to_tsvector(metadata->>'CategoryName')"
        if ct != len(searchtype):
            print(ct)
            query_type+='||'


    print('QUERY TYPE')
    print(query_type)


#    return 'a'

    query="""
        SELECT id
        FROM scry2.listing as l
        WHERE "categoryId" in
          (
          SELECT id
          FROM scry2.categories
         WHERE {} @@ to_tsquery('{}')
          );
        """.format(query_type,keywords)

    db.close()
    cursor = db.execute_sql('select id from scry2.listing;')

    listing_ids=[]
    listings=[]
    for row in cursor.fetchall():
        listing_ids.append(row[0])

    if len(listing_ids)>0:
        for l in listing_ids:
            li = Listing.get(Listing.id == l)
            listings.append(model_to_dict(li))

    db.close()

    return jsonify(listings)

@app.route('/listing_by_categories',methods=['GET'])
@jwt_required()
def  listing_by_categories():
    cat_id = request.args.get('category_id')
    print(cat_id)

    cat_list=[]
    for l in Listing.select().where(Listing.categoryId == cat_id):
        li=model_to_dict(l, exclude=[l.cid])
        cat_list.append(li)
    db.close()
    return jsonify(cat_list)



@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity


if __name__ == '__main__':
    app.run(port=2222)
