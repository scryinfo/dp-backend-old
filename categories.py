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
    except:
        db.rollback()
        raise


# This function is used to verify Metadata structure (input from categories)
def validate_category(ds,):
    print("TEST METADATA")
    testResult=[]
    for d in ds:
        testResult += Column(d).validate()
    return testResult


class Column(object):
    def __init__(self, d):
        self.d = d
        self.master = {
            "DataType": ["String", "Int", "Float", "Date", "Datetime", "StandardTime"],
            "IsNull": ["true", "false"],
            "IsUnique": ["true", "false"],
            "ForeignDataHash": "String",
            "IsPrimaryKey": ["true", "false"],
            "FieldLength": "Int",
        }

    @property
    def colname(self):
        return list(self.d.keys())[0]

    @property
    def val(self):
        return next(iter(self.d.values()))

    def validate(self):
        column_result = []
        for key in self.val:
            try:
                self._validate_attribute(key)
            except Exception as e:
                column_result += [[(self.colname), key, self.val[key], (repr(e))]]
        return column_result

    def _validate_attribute(self, key):
        """ if return without raising any exception, the attribute is correct"""
        masterValues = self.master[key]
        if type(masterValues) is list:
            if self.val[key] not in masterValues:
                raise Exception('No Match')
        # else:
        #     raise Exception("No test for this format yet")
        #



if __name__ == '__main__':
    ds = [{'airlineId': {'IsPrimaryKey': 'true', 'IsUnique': 'true', 'DataType': 'Int'}}]
    c = Column(ds[0])
    assert c.colname == 'airlineId'
    assert c.val == {'IsPrimaryKey': 'true', 'IsUnique': 'true', 'DataType': 'Int'}
    c.validate()
