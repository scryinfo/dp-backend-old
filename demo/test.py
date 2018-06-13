import json
metadata_path='./metadata/'
test_specification='test_specification.json'

f=open(test_specification).read()
spec=json.loads(f)

for i in spec:
    file_path=spec[i]['FileName']
    ipfs_hash=spec[i]['IPFS_hash']
    print(file_path,ipfs_hash)


    f=open(metadata_path+file_path).read()
    meta=json.loads(f)
    print(f)
    print()
