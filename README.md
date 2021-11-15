#  API Endpoints

Method | URL | Ref
------ | --- | ---
POST | /create_employee | Create new Employee
GET | /employee/id | Read one Employee
DELETE | /employee/id | Delete one Employee
GET | /employee | Read all Employees
POST | /schedule | Generate schedule



## Create new Employee

>Additional information about API call

#### URL
`<sever_ip>:<port>/create_employee`

#### Method
`POST`

#### Data Params
 Param | Type | Regular expression | Required
 ----- | ---- | ----------- | ----------
 name | String | `[a-zA-Z0-9]+` | Yes
 email | String | `[^@]+@[^@]+\.[^@]` | Yes
password | String | `[A-Za-z0-9@#$%^&+=]{8,}` | Yes
role | String | `^[-+]?[0-9]+$` | Yes

#### Success Response

Code: `201`

Content type : `application/json`

Content: 

```javascript
{"message" : "Document created"}`
```

## Read one Employee

>Additional information about API call

#### URL
`<sever_ip>:<port>/employee/<id>`

#### Method
`GET`

#### Data Params
 Param | Type | Description | Required
 ----- | ---- | ----------- | ----------
 id | String | 12-byte hexadecimal string value | Yes

#### Success Response

Code: `200`

Content type : `application/json`

Content: 
```javascript
{
    "_id": {
        "$oid": "5c37c4f66a3dd109622baf61"
    },
    "password": "$pbkdf2-sha256$29000$mlPK2TtnbK2Vsvbem9OaMw$KULlU.q5Po1lyq5QFQ2tkOkMVuKWACnDe0LubrbWPvg",
    "email": "mike@mail.com",
    "role": "1",
    "name": "mike"
}
```

## Delete one Employee

>Additional information about API call

#### URL
`<sever_ip>:<port>/employee/<id>`

#### Method
`DELETE`

#### Data Params
 Param | Type | Description | Required
 ----- | ---- | ----------- | ----------
 id | String | 12-byte hexadecimal string value | Yes

#### Success Response

Code: `200`

Content type : `application/json`

Content: 
```javascript
{
    "res": "Document deleted"
}
```

## Read all Employees

>Additional information about API call

#### URL
`<sever_ip>:<port>/employee`

#### Method
`GET`

#### Success Response

Code: `200`

Content type : `application/json`

Content: 
```javascript
[
    {
        "_id": {
            "$oid": "5c37c4966a3dd109622baf5f"
        },
        "password": "$pbkdf2-sha256$29000$8/6f876Xcm6N0XrvPecc4w$HrmhdaSmG1gkj0QmdYv2V7IU8IeXhTWaXNIEXUp94Qg",
        "email": "pantelis@mail.com",
        "role": "1",
        "name": "pantelis"
    },
    {
        "_id": {
            "$oid": "5c37c4f66a3dd109622baf61"
        },
        "password": "$pbkdf2-sha256$29000$mlPK2TtnbK2Vsvbem9OaMw$KULlU.q5Po1lyq5QFQ2tkOkMVuKWACnDe0LubrbWPvg",
        "email": "martha@mail.com",
        "role": "1",
        "name": "martha"
    }
]
```

## Generate schedule

>Additional information about API call

#### URL
`<sever_ip>:<port>/schedule`

#### Method
`POST`

#### Data Params
Param | Type | Regular expression | Required
----- | ---- | ----------- | ----------
weeks | String | `^[-+]?[0-9]+$` | Yes
employees | list | List with 12-byte hexadecimal string values | Yes

#### Success Response

Code: `201`

Content type : `application/json`

Content: 

```javascript
[
    {
        "employee": "5c37c4666a3dd109622baf5d",
        "shifts": [
            {
                "day": "0",
                "shift": "3"
            },
            {
                "day": "1",
                "shift": "3"
            },
            {
                "day": "2",
                "shift": "2"
            },
            {
                "day": "3",
                "shift": "1"
            },
            {
                "day": "4",
                "shift": "2"
            },
            {
                "day": "5",
                "shift": "0"
            },
            {
                "day": "6",
                "shift": "2"
            }
        ]
    },
    {
        "employee": "5c37c47d6a3dd109622baf5e",
        "shifts": [
            {
                "day": "0",
                "shift": "0"
            },
            {
                "day": "1",
                "shift": "0"
            },
            {
                "day": "2",
                "shift": "3"
            },
            {
                "day": "3",
                "shift": "3"
            },
            {
                "day": "4",
                "shift": "3"
            },
            {
                "day": "5",
                "shift": "2"
            },
            {
                "day": "6",
                "shift": "1"
            }
        ]
    },
    {
        "employee": "5c37c4966a3dd109622baf5f",
        "shifts": [
            {
                "day": "0",
                "shift": "2"
            },
            {
                "day": "1",
                "shift": "1"
            },
            {
                "day": "2",
                "shift": "1"
            },
            {
                "day": "3",
                "shift": "2"
            },
            {
                "day": "4",
                "shift": "0"
            },
            {
                "day": "5",
                "shift": "3"
            },
            {
                "day": "6",
                "shift": "0"
            }
        ]
    },
    {
        "employee": "5c37c4f66a3dd109622baf61",
        "shifts": [
            {
                "day": "0",
                "shift": "1"
            },
            {
                "day": "1",
                "shift": "2"
            },
            {
                "day": "2",
                "shift": "0"
            },
            {
                "day": "3",
                "shift": "0"
            },
            {
                "day": "4",
                "shift": "1"
            },
            {
                "day": "5",
                "shift": "1"
            },
            {
                "day": "6",
                "shift": "3"
            }
        ]
    }
]
```