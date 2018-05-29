import datetime
from peewee import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from playhouse.postgres_ext import PostgresqlExtDatabase, BinaryJSONField

#db = SqliteDatabase('scry.db')

db =  PostgresqlExtDatabase('scry', user='postgres', host='127.0.0.1', port=5432)

db = PostgresqlDatabase('scry')


class Categories(Model):
    name =  CharField(unique=True) # CANNOT CREATE UNIQUE ID
    metadata =  BinaryJSONField()
    created_at = TimestampField(utc=True)

    class Meta:
        database = db
        schema='scry2'


def create_tables():
    db.connect()
    db.create_tables([Categories])
    db.close()


create_tables()

def test_create_categories():
    #catname=["FF"]
    def create_category(db,meta):
        try:
            db.connect()

            cat = Categories.create(name=catname, metadata=meta)
            cat.save()
            db.close()
            result='success'
        except IntegrityError:
            result='already exists'
        except OperationalError:
            result='operational error'
        return result
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
            ],
        "Keywords":"Airline,Commercial Airline"

    }

#test_create_categories()
