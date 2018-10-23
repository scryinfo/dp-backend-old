s# API INFORMATION

## INTRODUCTION

The api  allows data being published to scry.info website.

If the data published has a category and this category requires data testing, the application will check data.

Check "category" below for information about how the data is being tested.


Step 1 : Get JWT Token - https://dev.scry.info:443/scry2/login
Step 2 : Send data to the publisher - https://dev.scry.info:443/meta/publisher



## AUTHENTICATION

All requests require JWT authentication.

1. Acquire JWT Token
2. Place jwt token in the header

```
POST https://dev.scry.info:443/scry2/login
```

INPUT

Username and password. Must be created on the dev.scry.info website

```
{
  "username":"user1",
  "password":"admin"
}
```

RESPONSE

```
{
  "token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo4LCJuYW1lIjoiMjIiLCJhY2NvdW50IjoiMHhlZjk3NTg0ZjFhNWY5OGE1MWQ4ZjhiNjhkZmIzYzE2NTA0NWU1MDhlIiwiaWF0IjoxNTI4Njk4NDU5LCJleHAiOjE1Mjg5MTQ0NTl9.7oSaJUFOuZdyUNBrozBrQKs6wZAdPMjxHOz06DMk2vo",
  "id":8,
  "name":"22",
  "account":"0xef97584f1a5f98a51d8f8b68dfb3c165045e508e",
  "created_at":"2018-05-28T08:55:49.838Z"
}
```

## GET CATEGORIES

Get all categories and related metadata

```
POST https://dev.scry.info:443/meta/getcategories
```

AUTHENTICATION

Headers :
```
"Authorization : JWT JwtToken"
```

RESPONSE:

```
[
{
   "CategoryName": [
     "Cat1",
     "Subcategory1",
     "Subcategory2"
   ],
   "DataStructure": [
     {
       "Col1": {
         "DataType": "String"
       }
     }
   ]
 }
 ]
 ```




## DELETE CATEGORY


To delete a category

```
POST https://dev.scry.info:443/meta/delete_categories
```

AUTHENTICATION

Headers :
```
"Authorization : JWT JwtToken"
```
The json must contain the id of the category. Ex:

```
{"Id":32}
```

If some childs depend on parent, the API will return the following error.
```
      {'description': 'DB Error',
      'status_code': 401,
      'error': '{"message": "Dependent Categories"}'}
  )
```

## CREATE CATEGORY


To create a category

```
POST https://dev.scry.info:443/meta/categories
```

AUTHENTICATION

Headers :
```
"Authorization : JWT JwtToken"
```

INPUT

Posts a json containing the following info

Listing info :
- category_name (String): Name of the category. For a parent category, all child names must unique, but different parent categories can have the same child name
- parent_id (Int, Optional): Category_id of the parent category. Can be left NULL.
- IsStructured (Boolean): If True, means the data is structured and must have metedata.
- Metadata (Json): keywords related to the file that can be searched on scry. Json is a list of objects structured as follow : {"ColumnName" : [{"MasterData":"Value"}]}

Ex.: [
      {"Id" : [
        { "DataType": "Int",
          "IsUnique" : "True"
          "IsPrimaryKey":"True"}
        ]},
        {"UserName" : [
          { "DataType": "String",
            "IsUnique" : "True"
            "IsPrimaryKey":"True"}
          ]},
          ,
          {"PhoneNumber" : [
            { "DataType": "Int",
              "IsUnique" : "True"
            ]}
      ]


- DataType (String) : Define the type of the structure for a column
- IsNull (String) : True if the data can be null. If not value is specified, the default is value is False
- IsUnique (String) : Unique constraint on the column. It Default value is False.
 the structure will be checked if it matches the the structure below. "DataType" is compulsory, "IsNull", "IsUnique"  are optional

masterMetaData={
                 "DataType":["String","Int","Float","Date","Datetime","StandardTime"],
                 "IsNull" : ["True","False"],
                 "IsUnique":["True","False"],
                 "IsPrimaryKey":["True","False"]
            }

Ex 1 :
```
 {
   "category_name": "Airline",
   "parent_id": null,
   "IsStructured": False,
   "Metadata": null
 }
```

Ex 2 :
```
 {
   "category_name": "Airport",
   "parent_id": 101,
   "IsStructured": True,
   "Metadata": [
         {"Id" : [
           { "DataType": "Int",
             "IsUnique" : "True"
             "IsPrimaryKey":"True"}
           ]},
           {"UserName" : [
             { "DataType": "String",
               "IsUnique" : "True"
               "IsPrimaryKey":"True"}
             ]},
             ,
             {"PhoneNumber" : [
               { "DataType": "Int",
                 "IsUnique" : "True"
               ]}
         ]
 }
```

## PUBLISH DATA


To publish data

```
POST https://dev.scry.info:443/meta/publisher
```

AUTHENTICATION

Headers :
```
"Authorization : JWT JwtToken"
```

INPUT


Multiple file post, enctype="multiparnt/form-data".

1) The first file should have name "data" and should contain a csv without headers.
2) The second file should be named "listing_info "

Listing info :
- category_name (String): extracted from "/getcategories" above. Must match exact values.
- price (Int): price of the listing
- filename (String) : name of the file that will be listed on scry.info and downloaded
- keyword (String): keywords related to the file that can be searched on scry. Must be separated by a space.

```
 {
   "category_name":["Aviation", "Commercial", "Airline"],
   "price":1000,
   "filename":"Airlines.csv",
   "keywords":"Commercial Airlines"
 }
```
