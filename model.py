import datetime
from peewee import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from playhouse.postgres_ext import PostgresqlExtDatabase, BinaryJSONField

#db = SqliteDatabase('scry.db')

db =  PostgresqlExtDatabase('scry', user='postgres', host='127.0.0.1', port=5432)



class Categories(Model):
    name =  CharField(unique=True) # CANNOT CREATE UNIQUE ID
    metadata =  BinaryJSONField()
    created_at = TimestampField(utc=True)

    class Meta:
        database = db
        schema='scry2'

class Trader(UserMixin, Model):
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


def create_tables():
    db.connect()
    db.create_tables([Categories,Trader])
    db.close()


create_tables()

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
