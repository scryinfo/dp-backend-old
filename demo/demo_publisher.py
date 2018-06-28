import json,os,requests

files=['Airport_Metadata.json']

metadata_path='./metadata/'
publisher_path='http://localhost:2222/'
scry_path='http://localhost:1234/'
userpayload={'username':'22','password':'22'}
#scry_path='https://dev.scry.info:443/scry2/'
#publisher_path='https://dev.scry.info:443/meta/'



def get_jwt_scry(jwt_server_path,payload):
    r = requests.post(jwt_server_path+'login', json = payload)
    rs=json.loads(r.text)
    jwtToken=json.loads(r.text)['token']
    print(r)
    return jwtToken

def publisher(meta_payload,path=publisher_path,jwt_server_path=scry_path,user_payload=userpayload):
    jwtToken=test_jwt_scry(jwt_server_path,user_payload)
    headers = {"Authorization": "JWT "+jwtToken+'a'}

    r = requests.post('/publisher'+route,files=meta_payload,headers=headers)
    return result

def create_category(meta,path=publisher_path,jwt_server_path=scry_path,upayload=userpayload):
    jwtToken=get_jwt_scry(jwt_server_path,upayload)
    headers = {"Authorization": "JWT "+jwtToken}
    r = requests.post(path+'categories', json = meta,headers=headers)
    result=r.text
#    print(result)
    return result

def get_categories(path=publisher_path,jwt_server_path=scry_path,user_payload=userpayload):
    jwtToken=get_jwt_scry(jwt_server_path,user_payload)
    headers = {"Authorization": "JWT "+jwtToken}

    r = requests.get(path+'getcategories',json='{"a":"a"}',headers=headers)
    result=r.text
    return result



def publish_data(data_file_path,listing_file_path,publisher_path=publisher_path,scry_path=scry_path,userpayload=userpayload):
    jwtToken=get_jwt_scry(scry_path,userpayload)
    headers = {"Authorization": "JWT "+jwtToken}

    f1=open(data_file_path,'rb')
    f2= open(listing_file_path)
    files = {'data': f1,'listing_info':f2}

    r = requests.post(publisher_path+'publisher',files=files,headers=headers)

    return r.text

def publish_data_no_data(data_file,listing_file,publisher_path=publisher_path,scry_path=scry_path,userpayload=userpayload):
    jwtToken=get_jwt_scry(scry_path,userpayload)
    headers = {"Authorization": "JWT "+jwtToken}

    f1=open(data_file,'rb')
    f2= open(listing_file)
    files ={'listing_info':f2}

    r = requests.post(publisher_path+'publisher',files=files,headers=headers)
    result=r.text
    return result

def publish_data_no_listing(data_file,listing_file,publisher_path=publisher_path,scry_path=scry_path,userpayload=userpayload):
    jwtToken=get_jwt_scry(scry_path,userpayload)
    headers = {"Authorization": "JWT "+jwtToken}

    f1=open(data_file,'rb')
    f2= open(listing_file)
    files ={'data': f1}

    r = requests.post(publisher_path+'publisher',files=files,headers=headers)
    result=r.text
    return result

def listing_category_id(cat_id,publisher_path=publisher_path,scry_path=scry_path,userpayload=userpayload):
    jwtToken=get_jwt_scry(scry_path,userpayload)
    headers = {"Authorization": "JWT "+jwtToken}

    payload = {'category_id': cat_id}
    r = requests.get(publisher_path+'listing_by_categories',params=payload,headers=headers)


    result=r.text
    print(result)





#print(get_categories())


#publish_data('/home/chuck/scry3/publisher/demo/data/airlines_1line.dat','/home/chuck/scry3/publisher/demo/listing_info/Airports_listing.json')
#publish_data('/home/chuck/scry3/publisher/demo/data/airlines.dat','/home/chuck/scry3/publisher/demo/listing_info/Airports_listing.json')
#publish_data('/home/chuck/scry3/publisher/demo/data/schedule.csv','/home/chuck/scry3/publisher/demo/listing_info/Schedule_listing.json')

#publish_data_no_data('/home/chuck/scry3/publisher/demo/data/schedule.csv','/home/chuck/scry3/publisher/demo/listing_info/Schedule_listing.json')
#publish_data_no_listing('/home/chuck/scry3/publisher/demo/data/schedule.csv','/home/chuck/scry3/publisher/demo/listing_info/Schedule_listing.json')



# CREATE CATEGORIES

meta_path='/home/chuck/scry3/publisher/demo/metadata/'
meta_files=os.listdir(meta_path)
for files in meta_files:
    metadata=json.load(open(meta_path+files))
    create_category(metadata)


data_path='/home/chuck/scry3/publisher/demo/data/'
listing_path='/home/chuck/scry3/publisher/demo/listing_info/'

with open('./demo.json') as jsonfile:
    test_scenario=json.load(jsonfile)

for i in test_scenario:
#    try:
#        assert(publish_data(data_path+i['Data'],listing_path+i['Listing'])==i['TestResult'])
#    except:
    print(publish_data(data_path+i['Data'],listing_path+i['Listing'])==i['TestResult'])
    print(publish_data(data_path+i['Data'],listing_path+i['Listing']))


#print(listing_category_id(51))
#print(listing_category_id(217))

def all_listings (owner_id,publisher_path=publisher_path,scry_path=scry_path,userpayload=userpayload):
    jwtToken=get_jwt_scry(scry_path,userpayload)
    headers = {"Authorization": "JWT "+jwtToken}

    payload = {'owner': owner_id}
    r = requests.get(scry_path+'listing',params=payload,headers=headers)


    result=r.text
    print(result)


#print(all_listings(8))
