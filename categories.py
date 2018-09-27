from model import *
import json
from peewee import IntegrityError,OperationalError,InternalError
from flask import jsonify
import peewee as pe



def create_category(db, catname, parent_id, is_structured, meta):
    ''' receives a dictionary "meta" in the python format ex : {'a':'a'}
     postgresql transforms it into jsonb format {"a":"a"}'''
    try:
        cat = CategoryTree.create(name = catname,
            parent_id = parent_id,
            is_structured = is_structured,
            metadata = meta)
        db.close()
        return cat
    except:
        db.close()
        raise


def get_categories_by_name (cat_name):
    query = CategoryTree.select().where(CategoryTree.name == cat_name)
    db.close()
    arr = []
    for i in query:
        arr.append(i.id)
    return arr


def validate_category(ds,):
    ''' This function is used to verify Metadata structure (input from categories)'''

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

def create_cat_tree(db, name, parent_id, is_structured, meta):
    try:
        cat = CategoryTree.create(name = name, parent_id = parent_id, is_structured = is_structured, metadata = meta)
        db.close()
        return cat
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
        return {'name':cat.name, 'id': cat.id, 'metadata' : cat.metadata}
    except IntegrityError as inst:
        print("Dependent Categories")
    except:
        print('Category doesnt exist')
    db.close()
    raise CustomPeeweeError('Not deleted')


def get_child_id(id):
    cat = CategoryTree.get(id=id)
    db.close()
    return model_to_dict(cat, backrefs=True)

def get_parent_id_null():
    query = CategoryTree.select().where(CategoryTree.parent_id.is_null())
    db.close()
    arr = []
    for i in query:
        arr.append(i.id)
    return arr


def get_all(inp):
    '''Receive an array of category ids as an input ex : [1], [2,3]
       To get whole database info pass [None] as argument
    '''
    if inp == [None]:
        inp = get_parent_id_null()
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

def remove_ids_rec(d):
    ''' Receives a dictionary with structure with three keys 'id','name','children'''
    d.pop('id')
    if len(d['children'])>0:
        arr=[]
        for i in d['children']:
            arr.append(remove_ids_rec(i))
    return d

def sort_json(arr):
    i = 1
    while i < len(arr):
        j = i
        while j > 0 and arr[j-1]['name'] > arr[j]['name']:
            arr[j], arr[j-1] = arr[j-1], arr[j]
            j = j - 1
        i = i + 1
    return arr

def sort_all(arr):
    ''' sorts result of category category by name'''
    if arr == []:
        return arr

    if len(arr)>1:
        arr = sort_json(arr)

    arr2=[]
    for i in arr:
        arr2.append({'name': i['name'], 'children': sort_all(i['children'])})
    return arr2

def get_parents(requested_id):
    cat = CategoryTree.get(id=requested_id)
    db.close()
    dic = model_to_dict(cat)
    if dic['parent'] == None:
        dic['parent'] = []
    else:
        a = dic.pop('parent')
        dic['parent'] = get_parents(a['id'])
    return [dic]

def get_last_category_id (cat_list):
    ''' This function receives a list of categories and related subcategories
        ex : ['Aviation','Commercial','Airline']
        Aviations has a child commercial that has a child Airline
        The function will return the id of Airline
    '''
    for i in list(range(0, len(cat_list))):
        if i == 0:
             parent_id = None
        cat = CategoryTree.get(name=cat_list[i], parent_id=parent_id)
        db.close()
        a = model_to_dict(cat)
        if i == len(cat_list)-1:
            return a['id']
        parent_id = a['id']


if __name__ == '__main__':
    try:
#        cat = CategoryTree.get(CategoryTree.name == 'ttt')
        cat = CategoryTree.get(CategoryTree.id == 162)
        cat.delete_instance()
        print("CAT IS :",{'name':cat.name, 'id': cat.id, 'metadata' : cat.metadata})
    except Exception as e:
        print("EXCEPTION      ",type(e))

#    print(get_parents(1471))
    ds = [{'airlineId': {'IsPrimaryKeys': 'true', 'IsUnique': 'trues', 'DataType': 'Int'}}]
    c = Column(ds[0])
    assert c.colname == 'airlineId'
    assert c.val == {'IsUnique': 'trues', 'IsPrimaryKeys': 'true', 'DataType': 'Int'}
#     print(c.validate())
    print(get_categories_by_name('Airline_Float'))
