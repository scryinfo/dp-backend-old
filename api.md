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
  GET https://dev.scry.info:443/meta/getcategories
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




  ## QUERY KEYWORDS


  Get all categories and related metadata.
  The if more than one keyword is provided, a "OR" is applied.
  The function tokenizes using postgresql to vector so plural and verb tenses are handled.

  Ex. aviation and aviations will be considered as the same.

  ```
  GET https://dev.scry.info:443/meta/search_keywords
  ```
  AUTHENTICATION


  Headers :
  ```
  "Authorization : JWT JwtToken"
  ```

INPUT

- keywords : a string of keywords separated by a space
  Ex : 'aviation commercial'
- searchtype: a string containining list of string. As of now there are two options
    - 'keywords' : the keyword specified on publication
        Ex :
        ```
        keywords='schedule airline'
        ```
    - 'searchtype' : area covered in the search. Can be either keywords provided by data publisher, categories name or both.
        Ex :
      ```
              searchtype='["keywords","category"]'
              searchtype='["keywords"]'
              searchtype='["category"]'
      ```


-> note : must be lowercase

```
[
 {
   "categoryId": 51,
   "cid": "QmVdfC5kG7nTf69yaHryPVEcLKhxZNHff49UHSL8YBbYYm",
   "created_at": "Thu, 14 Jun 2018 16:27:00 GMT",
   "id": 16,
   "isstructured": true,
   "keywords": "Aviation,Commercial Flight, Schedule",
   "name": "Schedule.csv",
   "owner": {
     "account": "0xef97584f1a5f98a51d8f8b68dfb3c165045e508e",
     "created_at": "Mon, 28 May 2018 16:55:49 GMT",
     "id": 8,
     "name": "22",
     "password_hash": "pbkdf2:sha256:50000$bf801740b8f08e65$294a006c03083fc08b43bf0d08226d6a2ce91b8cbc5f784dcb7ecf9c756def3e"
   },
   "price": 5000,
   "size": "179831"
 }
]

```
