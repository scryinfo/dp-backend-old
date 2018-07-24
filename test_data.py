import pandas as pd
import numpy as np


masterMetaData={
                 "DataType":["String","Int","Float","Date","Datetime","StandardTime"],
                 "IsNull" : ["True","False"],
                 "IsUnique":["True","False"],
                 "ForeignDataHash":"String",
                 "IsPrimaryKey":["True","False"],
                 "FieldLength":"Int"
            }

def test_standard_time(x):
    return datetime.datetime.strptime(x,"%Y-%m-%dT%H:%M:%S")

def test_int(x):
    assert float(x) % 1.0 == 0

def test_type(x, func):
    try:
        func(x)
        return True
    except:
        return False

# Uses the above function to test data types
def testDataType(s,testValue):
    d={
        'Int' : test_int,
        'Float': float,
        'StandardTime' :test_standard_time,
        'Date' : str,
        'DateTime':str,
        'String':str,
        }

    func=d[testValue]

    if func==str:
        return []
    else:
        return  serie_to_list(s[~s.apply(lambda x: test_type(x, func))])

def testIsNull(s):
    errors=s[s.isnull()]
    return serie_to_list(errors)

def testIsUnique(s):
    dup = s[s.duplicated(keep=False)]
    dup = dup[dup.notnull()] # Eliminate duplicated "Nulls"vprint(errors)
    return serie_to_list(dup)

def serie_to_list(s):
    l=[]
    for x, y in zip(s.index, s.values):
        l.append([x, y])
    return l

def test_column(s,meta):
    test_result=[]
    for i in meta:
        tr=[]
        test_null=True
        testValue=meta[i]
        if i=='DataType':
            tr=testDataType(s,meta[i])
        elif i=='IsUnique':
            tr=testIsUnique(s)
        elif i=='IsNull' and testValue=='true':
            tr=[]
            test_null = False
        if len(tr)>0:
            test_result.append({i:tr})

    if test_null:
        tr=testIsNull(s)
        if len(tr)>0:
            test_result.append({'IsNull':tr})
    return(test_result)

def test_dataframe(df, meta):
    test_result=[]
    for i, j in zip(df.columns, meta):
        test_result.append({i:test_column(df[i], list(j.values())[0]
        )})
    return test_result

def assess_result(result):
    for i in result:
        if len(list(i.values())[0]) > 0:
            return False
        return True

def full_test(df, meta):
    result = test_dataframe(df, meta)
    return assess_result(result), result
