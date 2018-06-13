import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
import json
import ipfsapi

UPLOAD_FOLDER = './uploaded/'
ALLOWED_EXTENSIONS = set(['csv'])

app = Flask(__name__)
app.debug=True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():

   # EXTRACT FILES FILE FROM REQUEST
   try:
       data = request.files['data']
   except KeyError:
       return 'Missing Data file'

   try:
       listing_info=request.files['listing_info']
   except KeyError:
       return 'Listing missing'

   # GET LISTING INFO
   f=listing_info.read()
   f=f.decode("utf-8")
   listing_info=json.loads(f)

   catname=listing_info['category_name']
   price=listing_info['price']
   filename=listing_info['filename']
   keywords=listing_info['keywords']

   print(catname, price, filename, keywords)

   # SAVE FILE
   file_name=secure_filename(filename)
   data.save(os.path.join(app.config['UPLOAD_FOLDER'],file_name))

   # ADD FILE TO IPFS
   api = ipfsapi.connect('127.0.0.1', 5001)
   res = api.add(os.path.join(app.config['UPLOAD_FOLDER'],file_name))
   IPFS_hash=res['Hash']
   filesize=res['Size']
   print(IPFS_hash,filesize)





   return 'file uploaded successfully'


if __name__ == '__main__':
    app.run(port=2223)
