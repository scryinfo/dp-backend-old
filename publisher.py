# TO DO : Verify if master is necessary in publisher
import pandas as pd
import os
import requests
from model import db,Listing, Trader, Categories
from settings import *
import json
from peewee import IntegrityError
import ipfsapi

testdata_path=TEST_DATA_PATH
#Test Hash : --> Hello World
#hash='QmZ4tDuvesekSs4qM5ZBKpXiZGun7S2CYtEZRB3DYXkjGx'


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
                 "DataType":["String","Int","Float","Date","Datetime"],
                 "IsNull" : ["True","False"],
                 "IsUnique":["True","False"],
                 "ForeignDataHash":"String",
                 "IsPrimaryKey":["True","False"]
            }

airlineMetaRight={
"CategoryName": ["Aviation","Commercial Flights","Airport Info"],
"DataStructure":
        [
        {"AirlineId": {"DataType":"Int", "IsUnique":"True","IsPrimaryKey":"True"}},
        {"AirlineName": {"DataType":"String", "IsUnique":"True"}},
        {"ANA": {"DataType":"String", "IsUnique":"True"}},
        {"IATA": {"DataType":"String", "IsUnique":"True", "IsNull":"True"}},
        {"IACAO": {"DataType":"String", "IsUnique":"True", "IsNull":"True"}},
        {"Callsign":{"DataType":"String", "IsUnique":"True"}},
        {"Country": {"DataType":"String"}},
        {"Active": {"DataType":"String"}}
        ]
}





def getColNames (metadata):
    colNames=[]
    for i in metadata:
        colNames.append(list(i.keys())[0])
    return colNames

# Load data from a csv, requires metadata and no header
def load_data(path,meta):
    colnames = getColNames(meta['DataStructure'])
    df = pd.read_csv(path,names=colnames)
    return df


# The following functions are used to test different aspect of the data
def testInt(df,colname):
    count=0
    errors=[]
    for i in df[colname]:
        try:
            int(i)
        except ValueError:
            errors.append(count)
        count+=1
    return errors

def testFloat(df, colname):
    count=0
    errors=[]
    for i in df[colname]:
        try:
            float(i)
        except ValueError:
            errors.append(count)
        count+=1
    return errors


# Uses the above function to test data types
def testDataType(df,colname,testValue):
    if testValue=='Int':
         testResult=testInt(df,colname)

    elif testValue=='Numeric':
        testResult=testFloat(df,colname)

    elif testValue=='Date':
        testResult=testFloat(df,[])

    elif testValue=='DateTime':
        testResult=testFloat(df,[])


    else:
        testResult=testFloat(df,[])
    return testResult

def testIsNull(df,colname):
    errors=(list(df[df[colname].isnull()].index))
    return errors

def testIsUnique(df,colname):
    dup = df[colname][df[colname].duplicated(keep=False)]
    dup = dup[dup.notnull()] # Eliminate duplicated "Nulls"
    return list(dup.index)

# FUNCTION TO TEST THE DATA

def testData(df,meta):
    testResult=[]
    tr=[]
    testFailed=0
    print(meta['DataStructure'])
    for i in meta['DataStructure']:
        colname=list(i.keys())[0]
        dataTest=list(i.values())[0]

        for test in dataTest:
            testValue=dataTest[test]
            if test=='DataType':
                tr=testDataType(df,colname,testValue)
            elif test=='IsUnique':
                tr=testIsUnique(df,colname)
            elif test=='IsNull':
                tr=testIsUnique(df,colname)

            testResult.append((colname,test,tr))
            if len(tr)>0:
                testFailed=1
    return testResult,testFailed #TestResult format [Column name, TestName, Rows that failed the text (array)]



def wrapResult(df, testResult,master):
    dataFrames={}
    for j in master:
        dataFrames[j]=[]


    for i in testResult:
        if len(i[2])>0:
            dataFrames[i[1]].append(pd.DataFrame(df.loc[i[2],i[0]]))

    return dataFrames

def result_to_csv(wrapped_result,test_folder):
    for i in wrapped_result:
        if len(wrapped_result[i])>0:
            a=pd.concat(wrapped_result[i],axis=1)
            a.to_csv(test_folder+i)


def fullTest(df, meta, master, test_folder):
    testResult,testFailed=testData(df,json.loads(meta))
    print("FULL TEST DONE")

    wrapped_result=wrapResult(df, testResult, master)
    print('RESULT WRAPPED')

    result_to_csv(wrapped_result,test_folder)
    print('RESULT TO CSV :'+test_folder)

    return wrapped_result,testFailed




def getMetadata(category_name=None,file_path=None):
    if category_name is None:
        if file_path is None:
            print("Please provide a file path or category name")
        else:
            print("file path :"+file_path)
    else:
        #catname='sdsds'
        print(category_name)
        try:
            catdata= Categories.select().where(Categories.name == category_name).get()
            result=catdata.metadata
        except:
            result='Fail'
    return result

def record_listing(db,file_cid,trader_id,size,filename,price,catname,keywords):
    # Get category_id
    try:
        cat=Categories.get(Categories.name==catname)
        cat_id=cat.id
        print(cat_id)
    except:
        return 'Category doesnt exist'

    try:
        listing = Listing(cid=file_cid, size=size,ownerId=trader_id, name=filename, price=price,keywords=keywords,isstructured=1,categoryId=cat_id)#,
        listing.save()
        db.close()
        return 'Success'
    except IntegrityError:
        db.close()
        return 'IntegrityError'

# Path is Hard Coded to "/home/chuck/scry2/test_result/test_data.csv", should be dynamic
# catname json as a string with space after "," : '["Airline", "Commercial Airline"]'
# file_cid : ipfs hash of a file
# Username : login NameError
# Price : float
# Filename : string
# Keywords : string (ex. 'Aviation,Flight Route')
# Master : masterData
def publish_data (catname, file_cid,trader_id,price,filename,keywords, master=masterMetaData,test_folder=testdata_path):
    #0 get account
#    try:
#        trader= Trader.select().where(Trader.name ==username).get()
#        account=trader.id
#        print('Step 1 : Account id :'+str(account))
#    except:
#        return 'User doesnt exist'


    #1- Get metadata from Category
    meta=getMetadata(catname)
    print('Step 2 : metadata  :'+ str(meta))
    print(type(meta))
    print(meta)
    if meta=='Fail':
        return 'Category doesnt exist'

    #2- get data from ipfs and save it to a local folder
    file_path=getIpfsData(file_cid,test_folder) #file_cid = ipfs hash


    if file_path=='Wrong Hash':
        return ('IPFS hash erroneous')
    else:
        api = ipfsapi.connect('127.0.0.1', 5001)
        res = api.add(file_path)
        print(res)
        #QmZ4tDuvesekSs4qM5ZBKpXiZGun7S2CYtEZRB3DYXkjGx helloworlds
        size=res['Size']
        file_cid=res['Hash']

        print(file_cid)
        df=load_data(file_path,json.loads(meta))
        print('Test 3 : successfully loaded file from IPFS')


    #3  data tested
    test_result,test_failed=fullTest(df, meta, master,test_folder)
    print('Step 4 : Data has been testesds')
    if test_failed==1:
        return ['Test Failed',test_result]

    #4 If no error, publish listing

    publish_result=record_listing(db,file_cid,trader_id,size,filename,price,catname,keywords)
    return publish_result




# File with errors
#file_cid='Qmao4wg8KPxqjpcNsN55dJXxJ3kuBwMQSZ26SFemqMBUm7'

#file without errors
#file_cid='QmRG9U8akdxckFjm5MYRy9mxcaoMytrD2pE6stwKhzNTSf'


#ipfs pin add -r QmRG9U8akdxckFjm5MYRy9mxcaoMytrD2pE6stwKhzNTSf
#catname='["Aviation", "Commercial Flights", "Airport Info"]'

#print(publisher(catname,file_cid,'22','1','file1','Aviation,Commercial'))
