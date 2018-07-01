from model import db, Categories
import json
from peewee import IntegrityError,OperationalError,InternalError
from flask import jsonify

# receives a dictionary "meta" in the python format ex : {'a':'a'}
# postgresql transforms it into jsonb format {"a":"a"}
def create_category(db,catname,meta):
    try:
        db.close()
        db.connect()
        cat = Categories.create(name=json.dumps(catname), metadata=meta)
        cat.save()
        db.close()
        result='success'
    except IntegrityError:
        db.rollback()
        result='already exists'
    except OperationalError:
        db.rollback()
        result='operational error'
    except InternalError:
        db.rollback()
        result='internal error'
    except:
        db.rollback()
        result='other error'
    print(result)
    return result


# This function is used to verify Metadata structure (input from categories)
def validate_category(ds, master=None):
    print("TEST METADATA")
    testResult=[]
    for d in ds:
        testResult += Column(d, master).validate_column()
    return testResult


class Column(object):
    def __init__(self, d, master=None):
        self.d = d
        if master == None:
            master = {
                "DataType": ["String", "Int", "Float", "Date", "Datetime", "StandardTime"],
                "IsNull": ["true", "false"],
                "IsUnique": ["true", "false"],
                "ForeignDataHash": "String",
                "IsPrimaryKey": ["true", "false"],
                "FieldLength": "Int",
            }
        self.master = master

    @property
    def colname(self):
        return list(self.d.keys())[0]

    @property
    def val(self):
        return next(iter(self.d.values()))

    def validate_column(self):
        column_result = []
        for key in self.val:
            column_result += self._validate_attribute(key)
        return column_result

    def _validate_attribute(self, key):
        res = verifyElement(key, self.val[key], self.master)
        if res != 'Success':
            column_result = [[(self.colname), key, self.val[key], res]]
        else:
            column_result = []
        return column_result



# This function is part of testMetaData (see below)
def verifyElement(key, val, master):
    try:
        masterValues=master[key]
        if type(masterValues)==list:
            for i in masterValues:
                if i==val:
                    return("Success")
            return('No Match')
        else:
            if masterValues=="Int":
                try:
                    int(val)
                    return ("Success")
                except:
                    return("Not an int")
            return ("No test for this format yet")

    except KeyError:
        return("Key Error")


if __name__ == '__main__':
    ds = [{'airlineId': {'IsPrimaryKey': 'true', 'IsUnique': 'true', 'DataType': 'Int'}}]
    c = Column(ds[0])
    assert c.colname == 'airlineId'
    assert c.val == {'IsPrimaryKey': 'true', 'IsUnique': 'true', 'DataType': 'Int'}
    c.validate_column()
