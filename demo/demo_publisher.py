import json,os,requests

files=['Airport_Metadata.json']

from api import ScryApi


userpayload={'username': '22', 'password': '22'}  # duplicate with test_server
publisher_path='http://localhost:2222/'  # duplicate with test_server
scry_path='http://localhost:1234/'  # duplicate with test_server

# scry_path='https://dev.scry.info:443/scry2/'
# publisher_path='https://dev.scry.info:443/meta/'


# publish_data('/home/chuck/scry3/publisher/demo/data/airlines_1line.dat','/home/chuck/scry3/publisher/demo/listing_info/Airports_listing.json')
# publish_data('/home/chuck/scry3/publisher/demo/data/airlines.dat','/home/chuck/scry3/publisher/demo/listing_info/Airports_listing.json')
# publish_data('/home/chuck/scry3/publisher/demo/data/schedule.csv','/home/chuck/scry3/publisher/demo/listing_info/Schedule_listing.json')

# publish_data_no_data('/home/chuck/scry3/publisher/demo/data/schedule.csv','/home/chuck/scry3/publisher/demo/listing_info/Schedule_listing.json')
# publish_data_no_listing('/home/chuck/scry3/publisher/demo/data/schedule.csv','/home/chuck/scry3/publisher/demo/listing_info/Schedule_listing.json')


# CREATE CATEGORIES

api = ScryApi()
api.login(**userpayload)
for files in os.listdir('./demo/metadata/'):
    metadata = json.load(open('./demo/metadata/' + files))
    api.categories(metadata)


api.data_path = './demo/data/'
api.listing_path = './demo/listing_info/'

with open('./demo/demo.json') as jsonfile:
    test_scenario = json.load(jsonfile)

for i in test_scenario:

    payload = api.from_filenames_to_publisher_payload(i['Data'], i['Listing'])
    response = api.publisher(payload)
    print(response == i['TestResult'])
    print(response)

print(api.listing_by_categories(51))
print(api.listing_by_categories(217))


#  FIXME: legacy test pointing to a non existing endpoint on backend
def get_categories(path=publisher_path,jwt_server_path=scry_path,user_payload=userpayload):
    jwtToken=get_jwt_scry(jwt_server_path,user_payload)
    headers = {"Authorization": "JWT "+jwtToken}

    r = requests.get(path+'getcategories',json='{"a":"a"}',headers=headers)
    result=r.text
    return result


#  FIXME: legacy test pointing to a non existing endpoint on backend
def all_listings(owner_id, publisher_path='http://localhost:2222/', scry_path='http://localhost:1234/',
                 userpayload=userpayload):
    jwtToken = get_jwt_scry(scry_path, userpayload)
    headers = {"Authorization": "JWT " + jwtToken}

    payload = {'owner': owner_id}
    r = requests.get(scry_path + 'listing', params=payload, headers=headers)

    result = r.text
    print(result)


#print(all_listings(8))
