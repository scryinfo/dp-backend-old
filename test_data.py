import pandas as pd
import numpy as np
import datetime

masterMetaData={
                 "DataType":["String","Int","Float","Date","Datetime","StandardTime"],
                 "IsNull" : ["True","False"],
                 "IsUnique":["True","False"],
                 "ForeignDataHash":"String",
                 "IsPrimaryKey":["True","False"],
                 "FieldLength":"Int"
            }


def test_standard_time(x):
    return datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S")


def test_int(x):
    assert float(x) % 1.0 == 0


def test_type(x, func):
    try:
        func(x)
        return True
    except:
        return False


# Uses the above function to test data types
def testDataType(s, testValue):
    d={
        'Int' : test_int,
        'Float': float,
        'StandardTime' :test_standard_time,
        'Date' : str, # not implemented yet so we use str
        'DateTime':str, # not implemented yet so we use str
        'String':str,
        }

    func=d[testValue]

    if func==str:
        return []
    else:
        return s[~s.apply(lambda x: test_type(x, func))]


def testIsNull(s):
    errors=s[s.isnull()]
    return errors


def testIsUnique(s):
    dup = s[s.duplicated(keep=False)]
    dup = dup[dup.notnull()] # Eliminate duplicated "Nulls"vprint(errors)
    return dup


def serie_to_list(s):
    l=[]
    for x, y in zip(s.index, s.values):
        l.append([x, y])
    return l


def test_column(s,meta):
    test_result=[]
    tr=[]
    for i in meta:
        testValue=meta[i]
        if i=='DataType':
            tr=testDataType(s,meta[i])
        elif i=='IsUnique':
            tr=testIsUnique(s)
        if len(tr)>0:
            test_result.append({i:serie_to_list(tr.fillna('nan').astype('object'))})
            tr=[]
    if not bool(meta.get('IsNull')):
        tr=testIsNull(s)
        if len(tr)>0:
            test_result.append({'IsNull':serie_to_list(tr.fillna('nan').astype('object'))})
        tr=[]

    return(test_result)


def test_dataframe(df, meta):
    test_result=[]
    for i, j in zip(df.columns, meta):
        tr=test_column(df[i], list(j.values())[0])
        if len(tr)>0:
            test_result.append({i:  tr})
    return test_result


def assess_result(result):
    '''This function return True if all the test passed'''
    for i in result:
        if len(list(i.values())[0]) > 0:
            return False
        return True


def full_test(df, meta):
    result = test_dataframe(df, meta)
    return result
    # print("FULL TEST")
    # print(result)
    # return assess_result(result), result
