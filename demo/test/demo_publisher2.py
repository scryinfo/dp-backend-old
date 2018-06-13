import json,os,requests

files=['Airport_Metadata.json']

metadata_path='./metadata/'
publisher_path='http://localhost:2222/'
scry_path='http://localhost:1234/'
userpayload={'username':'22','password':'22'}
scry_path='https://dev.scry.info:443/scry2/'
publisher_path='https://dev.scry.info:443/meta/'



def get_jwt_scry(jwt_server_path,payload):
    r = requests.post(jwt_server_path+'login', json = payload)
    rs=json.loads(r.text)
    jwtToken=json.loads(r.text)['token']
    return jwtToken

def publisher(meta_payload,path=publisher_path,jwt_server_path=scry_path,user_payload=userpayload):
    jwtToken=test_jwt_scry(jwt_server_path,user_payload)
    headers = {"Authorization": "JWT "+jwtToken}

    r = requests.post('/publisher'+route,files=meta_payload,headers=headers)
    result=r.text
    return result

def create_category(meta,path=publisher_path,jwt_server_path=scry_path,upayload=userpayload):
    jwtToken=get_jwt_scry(jwt_server_path,upayload)
    headers = {"Authorization": "JWT "+jwtToken}
    r = requests.post(path+'categories', json = meta,headers=headers)
    result=r.text
    print(result)
    return result

def get_categories(path=publisher_path,jwt_server_path=scry_path,user_payload=userpayload):
    jwtToken=get_jwt_scry(jwt_server_path,user_payload)
    headers = {"Authorization": "JWT "+jwtToken}

    r = requests.post(path+'getcategories',json='{"a":"a"}',headers=headers)
    result=r.text
    return result



def publish_data(data_file,listing_file,publisher_path=publisher_path,scry_path=scry_path,userpayload=userpayload):
    jwtToken=get_jwt_scry(scry_path,userpayload)
    headers = {"Authorization": "JWT "+jwtToken}

    f1=open(data_file,'rb')
    f2= open(listing_file)
    files = {'data': f1,'listing_info':f2}

    r = requests.post(publisher_path+'publisher',files=files,headers=headers)
    result=r.text
    print(result)


meta_path='/home/chuck/scry3/publisher/demo/metadata/'
meta_files=os.listdir(meta_path)

# CREATE CATEGORIES
for files in meta_files:
    metadata=json.load(open(meta_path+files))
#    create_category(metadata)


#print(get_categories())

data_path='/home/chuck/scry3/publisher/demo/metadata/'
data_files=os.listdir(meta_path)

listing_path='/home/chuck/scry3/publisher/demo/listing_info/'
path_files=os.listdir(listing_path)

# PUBLISH
for data in data_files:
    print(data)
#publish_data('/home/chuck/scry3/publisher/demo/data/airlines_1line.dat','/home/chuck/scry3/publisher/demo/listing_info/Airports_listing.json')
#publish_data('/home/chuck/scry3/publisher/demo/data/airlines.dat','/home/chuck/scry3/publisher/demo/listing_info/Airports_listing.json')
#publish_data('./schedule.csv','./Schedule_listing.json')
