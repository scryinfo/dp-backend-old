# API INFORMATION

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
  	"id": 63,
  	"metadata": {
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
  	},
  	"name": [
  		"Cat1",
  		"Subcategory1",
  		"Subcategory2"
  	]
}
]
  ```



  ## PUBLISH DATA


  Get all categories and related metadata

  ```
  POST https://dev.scry.info:443/meta/getcategories
  ```

  AUTHENTICATION

  Headers :
  ```
  "Authorization : JWT JwtToken"
  ```

INPUT


- category_name : extracted from "/getcategories" above. Must match exact values.
- price : price of the listing
- filename : name of the file that will be listed on scry.info and downloaded
- keyword : keywords related to the file that can be searched on scry.

```
  {
    "category_name":["Aviation", "Commercial", "Airline"],
    "price":1000,
    "filename":"Airlines.csv",
    "keywords":"Commercial Airlines"
  }
```
