import datetime
from peewee import *
from werkzeug.security import generate_password_hash, check_password_hash
from playhouse.postgres_ext import PostgresqlExtDatabase, BinaryJSONField
from settings import *
import psycopg2 as pg2
import peewee as pe
from playhouse.shortcuts import model_to_dict
from flask import jsonify


#db =  PostgresqlExtDatabase('scry', user=DB_USER,port=5432)
db =  PostgresqlExtDatabase('scry', user='scry', password='scry',host='localhost', port=5432)

class Categories(Model):
    name =  CharField(unique=True) # CANNOT CREATE UNIQUE ID
    metadata =  BinaryJSONField()
#    created_at = TimestampField(utc=True)

    class Meta:
        database = db
        schema='scry2'

class Trader(Model):
    name = CharField(unique=True)
    account = CharField()
    created_at = TimestampField(utc=True)
    password_hash = CharField(128)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    class Meta:
        database = db
        schema = 'scry2'
        indexes = (
            # create a unique constraint
            (('name', 'account'), True),
        )


class Listing(Model):
    cid = CharField()
    size = CharField()
    owner = ForeignKeyField(Trader, db_column='ownerId', related_name='listings',  to_field=Trader.id)

#    ownerId = IntegerField()#ForeignKeyField(Trader, related_name='listings')
    name = CharField()
    price = DecimalField(constraints=[Check('price > 0')])
#    created_at = TimestampField()
    keywords = CharField(null=True)
    isstructured = BooleanField(null=True)
    categoryId = IntegerField()

    class Meta:
        database = db
        schema = 'scry2'


def create_tables():
    db.connect()
    db.create_tables([Category,Trader,Listing,Category])
    db.close()


#create_tables()

def test_create_categories():
    #catname=["FF"]
    def create_category(db,meta):
        try:
            db.connect()

            cat = Categories.create(name=catname, metadeata=meta)
            cat.save()
            db.close()
            result='success'
        except IntegrityError:
            result='already exists'
        except OperationalError:
            result='operational error'
        return result

file_cid='adsadad213dfd'
account=1
size=10
filename='file6'
price='10'
catname='["Aviation", "Commercial Flights", "Airport Info"]'
keywords='Aviation,Commercial,Airlines'

def record_listing(file_cid,account,size,filename,price,catname,keywords):
    # Get category_id
    try:
        cat=Categories.get(Categories.name==catname)
        cat_id=cat.id
        print(cat_id)
    except:
        return 'Category doesnt exist'

    try:
        listing = Listing(cid=file_cid, size=10,ownerId=account, name=filename, price=price,keywords=keywords,isstructured=1,categoryId=cat_id)#,
        listing.save()
        db.close()
        return 'Listing Created'
    except IntegrityError:
        db.close()
        return 'IntegrityError'
