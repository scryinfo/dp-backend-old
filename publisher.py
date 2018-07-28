# TO DO : Verify if master is necessary in publisher
import pandas as pd
import os
import requests
from model import db,Listing, Trader, Categories
from settings import *
import json
from peewee import IntegrityError
import ipfsapi
import simplejson
import datetime
from werkzeug.utils import secure_filename



testdata_path=TEST_DATA_PATH
#Test Hash : --> Hello World
#hash='QmZ4tDuvesekSs4qM5ZBKpXiZGun7S2CYtEZRB3DYXkjGx'

def add_file_to_IPFS(filename, data, upload_folder):
    file_name=secure_filename(filename)
    data.save(os.path.join(upload_folder,file_name))
    api = ipfsapi.connect('127.0.0.1', 5001)
    res = api.add(os.path.join(upload_folder,file_name))
    return res['Hash'], res['Size']


def getIpfsData(hash,test_folder):
    testfile_path=test_folder+'test_data.csv'
    r = requests.get('http://127.0.0.1:8080/ipfs/'+hash)
    if r.status_code != 200:
        result='Wrong Hash'
    else:
        f=open(testfile_path,'w')
        f.write(r.text)
        f.close()
        result=testfile_path
    return result


masterMetaData={
                 "DataType":["String","Int","Float","Date","Datetime","StandardTime"],
                 "IsNull" : ["True","False"],
                 "IsUnique":["True","False"],
                 "ForeignDataHash":"String",
                 "IsPrimaryKey":["True","False"],
                 "FieldLength":"Int"
            }


def getColNames (metadata):
    colNames=[]
    for i in metadata:
        colNames.append(list(i.keys())[0])
    return colNames

# Load data from a csv, requires metadata and no header
def load_data(path,meta):
    colnames = getColNames(meta['DataStructure'])
    df = pd.read_csv(path,header=None)

    cols=df.columns.values

    # Test if number of columns in metadata matches file
    if len(colnames)!=len(cols):
        return None
    else:
    # Rename the DataFrame column names to match metadata
        ren={}
        for i in cols:
            ren[i]=colnames[i]

        df=df.rename(index=str, columns=ren)

        return df


def result_to_csv(wrapped_result,test_folder):
    for i in wrapped_result:
        if len(wrapped_result[i])>0:
            a=pd.concat(wrapped_result[i],axis=1)
            a.to_csv(test_folder+i)


def getMetadata(category_name=None):
    catdata=Categories.get(Categories.name==category_name)
    return catdata.metadata


def record_listing(db,file_cid,trader_id,size,filename,price,catname,keywords):
    # Get category_id
    cat=Categories.get(Categories.name==catname)
    cat_id=cat.id

    listing = Listing(cid=file_cid, size=size,ownerId=trader_id, name=filename, price=price,keywords=keywords,isstructured=1,categoryId=cat_id)#,
    listing.save()
    db.close()

    return 'Success'

# Path is Hard Coded to "/home/chuck/scry2/test_result/test_data.csv", should be dynamic
# catname json as a string with space after "," : '["Airline", "Commercial Airline"]'
# file_cid : ipfs hash of a file
# Username : login NameError
# Price : float
# Filename : string
# Keywords : string (ex. 'Aviation,Flight Route')
# Master : masterData
def publish_data (catname, trader_id,price,filename,IPFS_hash,filesize,keywords, master=masterMetaData,test_folder=testdata_path):

    #1- GET METADATA FROM CATEGORY

    print("STEP 1 : GET METADATA FROM DB CATEGORY TABLE")
    print("Category name : ", catname)
    meta=getMetadata(catname)
    print()
    print("Metadata : ",str(meta))
    print()

    meta=getMetadata(catname)

    if meta=='Fail':
        return 'Category doesnt exist'

    #2 TEST DATA
    print("STEP 4 : VALIDATE DATA")
    test_result,test_failed=fullTest(df, meta, master,test_folder)
    print('Step 4 : Data has been testesd')
    print()
    if test_failed==1:
        return ['Test Failed',test_result]

    #3 IF NO ERROR, PUBLISH LISTING

    publish_result=record_listing(db,IPFS_hash,trader_id,size,filename,price,catname,keywords)

    print ("DATA PUBLISHED SUCCESSFULLY !!!")
    return publish_result
