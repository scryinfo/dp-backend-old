from model import db, Categories, CategoryTree
import json
from peewee import IntegrityError,OperationalError,InternalError
from flask import jsonify
import peewee as pe


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


class CustomPeeweeError(Exception):
    def __init__(self, message):
        super(CustomPeeweeError, self).__init__('Custom peewee errors')
        self.message = message

def create_cat_tree(name, parent_id=None):
    try:
        cat = CategoryTree.create(name=name, parent_id=parent_id)
        return cat
#        cat.delete_instance()
    except pe.InternalError as e:
        a = e.__context__.pgerror
        if a[0:38] == 'ERROR:  Name exists for this parent_id':
            print('UNIQUE CONSTRAINT : Name already exists for this parent_id')
        error='unique'
    except pe.IntegrityError as e2:
        print('FOREIGN KEY : Parent_id value doesnt exist')
    except:
        print("W")
    db.close()
    raise CustomPeeweeError('unique')


def delete_cat_tree(cat_id):
    try:
        cat = CategoryTree.get(CategoryTree.id == cat_id)
        cat.delete_instance()
        print('Category deleted')
    except IntegrityError:
        print("Dependent Categories")
    except:
        print('Category doesnt exist')
    db.close()

def get_child_id(id):
    cat = CategoryTree.get(id=id)
    return model_to_dict(cat, backrefs=True)

def get_parent_id_null():
    query = CategoryTree.select().where(CategoryTree.parent_id.is_null())
    arr = []
    for i in query:
        arr.append(i.id)
    return arr


def get_all(inp):
    '''Receive an array of category ids as an input ex : [1], [2,3]'''

    if inp == [None]:
        get_parent_id_null()
    if inp == []:
        return []
    arr=[]
    for i in inp:
        c = get_child_id(i)
        children_id = []
        for x in c['children']:
            children_id.append(x['id'])
        arr.append({'name': c['name'], 'id': c['id'], 'children': get_all(children_id)})
    return arr



if __name__ == '__main__':
    ds = [{'airlineId': {'IsPrimaryKey': 'true', 'IsUnique': 'true', 'DataType': 'Int'}}]
    c = Column(ds[0])
    assert c.colname == 'airlineId'
    assert c.val == {'IsPrimaryKey': 'true', 'IsUnique': 'true', 'DataType': 'Int'}
    c.validate()
