#JWT TOKEN eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJuYW1lIjoiMjIiLCJhY2NvdW50IjoiMHg0MDc4NDA3YzlhNGIxNzNmNjc5ZTQ3MGY1YjE2N2FmMmQ3MTU2NDFiIiwiaWF0IjoxNTI3NTAwNDkzLCJleHAiOjE1Mjc3MTY0OTN9._-HKiuAc_LUJOHrY5hUAOPMaBY2dxAAQAVr7Q0RblOU
from flask import Flask,request, jsonify,make_response, render_template, Response, g
from flask_cors import CORS
from flask_jwt import JWT, jwt_required, current_identity
from categories import create_category,validate_category, get_all, CustomPeeweeError, get_last_category_id, get_parents
from publisher import publish_data,getMetadata, load_data, record_listing,add_file_to_IPFS
from model import db, CategoryTree, Trader, Listing
from peewee import IntegrityError,OperationalError,InternalError
import simplejson
from werkzeug.utils import secure_filename
import ipfsapi, os
from playhouse.shortcuts import model_to_dict
from playhouse.postgres_ext import PostgresqlExtDatabase, BinaryJSONField
from settings import *
from test_data import full_test


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


@app.before_request
def before_request():
    db.connect()


@app.after_request
def after_request(response):
    db.close()
    return response

@app.errorhandler(401)
def server_internal_Error(e):
    return jsonify({
      "description": "Signature verification failed",
      "error": "Invalid token",
      "status_code": 401
    }), 401

@app.errorhandler(InternalError)
def peewee_internal(e):
    return jsonify({
      "description": "DB Error",
      "error": e,
      "status_code": 401
    }), 401

    _
@app.errorhandler(400)
def page_not_found(e):
    print(e)
    return make_response(jsonify(error=400, text=str(e)), 400)


@app.errorhandler(500)
def page_not_found(e):
    print(e)
    return make_response(jsonify(error=500, text=str(e)), 500)


# FROM Categories.py : uses validate_category and create_category
@app.route('/categories',methods=['POST'])
@jwt_required()
def categories():
    if not request.is_json:
        return json.dumps({'Result': 'Not Json'})

    data = request.get_json()
    if data['is_structured'] == False:
        r = model_to_dict(create_category(db, data['category_name'], data['parent_id'],data['is_structured'],None))
        db.close()
        return make_response(jsonify(r),200)
    else:
        v = validate_category(data['metadata'])
        if v == []:
            r = model_to_dict(create_category(db, data['category_name'], data['parent_id'],data['is_structured'],data['metadata']))
            db.close()
            return make_response(jsonify(r),200)
        else:
            return make_response(jsonify(v), 422)


@app.route('/get_categories',methods=['POST'])
@jwt_required()
#'''returns all categories and their childs'''
def  getcategories():
    cat_list=json.loads(request.get_json())
    return jsonify(get_all(cat_list))


@app.route('/get_categories_parents',methods=['POST'])
@jwt_required()
#''' Post a Json {"id": id} returns all parents'''
def get_categories_parents():
    parent_id = json.loads(request.get_json())['id']
    return make_response(jsonify(get_parents(parent_id)), 200)


@app.route('/validate_category',methods=['POST'])
@jwt_required()
def validate_metadata():
    data=request.get_json()

    # TEST 3 : DataStructure True
    try:
        meta=data['DataStructure']
    except:
        return make_response(jsonify({'message': 'No Data Structure'}),422)


    test_data=validate_category(meta)
    if test_data == []:
        return make_response(jsonify({'message': 'Data matches metadata defitinion'}),200)

    return make_response(jsonify({'message': 'Metadata Error', 'error':test_data}),422)
#    return json.dumps({'Result': 'Metadata Error', 'DataErrors':test_data})



@app.route('/publisher',methods=['POST'])
@jwt_required()
def  publisher():
    '''Requires : listing_info () "Category_id", "filename", "price","keywords" "data" '''
    f=request.files['listing_info'].read().decode("utf-8")
    print("LISTING INFO", f)
    listing_info=json.loads(f)

    IPFS_hash, filesize = add_file_to_IPFS(
        listing_info['filename'],
        request.files['data'], app.config['UPLOAD_FOLDER'])

#    meta = getMetadata(json.dumps(listing_info.['category_id']))
    meta = getMetadata(json.dumps(listing_info['category_id']))


    df = load_data(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(listing_info['filename'])),meta)
    print("SUCCESS  !!!!!!!!!!!")
    if df is None:
        print("NO DF")
        return make_response(jsonify({'message':'Data file column number doesnt match metadata'}),422)

    test_detail=full_test (df, meta)
    if test_detail == []:

        result = record_listing (db,
            IPFS_hash,
            current_identity,
            filesize,
            listing_info['filename'],
            listing_info['price'],
            json.dumps(listing_info['category_id']),
            listing_info['keywords'])

        return make_response(simplejson.dumps({'message':'Success'}, ignore_nan=True), 200) # Simple json is used to handle Nan values in test result numpy array TestIsNull
    else:
        return make_response(simplejson.dumps({
            'message':'test failed',
            'error': test_detail
            }, ignore_nan=True, sort_keys=True
            ), 422)



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

    if len(listing_ids) > 0:
        for l in listing_ids:
            li = Listing.get(Listing.id == l)
            listings.append(model_to_dict(li))

    db.close()

    return jsonify(listings)


@app.route('/get_last_category_id', methods=['POST'])
@jwt_required()
def last_category_id():
    '''Expects a json 'cat_list' that contains an array'''
    data = request.get_json()
    print(data)
    a = get_last_category_id(data['cat_list'])
    return make_response(jsonify({'cat_id': a}), 200)



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
