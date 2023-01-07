# Proves of concept Documentation

# Models

## ERM

![image](https://user-images.githubusercontent.com/46592735/211150034-9ecb858b-e15b-44ed-9d1d-2b0119ef1583.png)

# API V1 Manual

## To create a School we will need to follow the **hierarchy of the database**

Acronym:

`OTO: OneToOne`

`MTO: ManyToOne`

`OTM: OneToMany`

`MTM: ManyToMany`

**These need to be created in the following order**

- **School**
    
    `Standalone model`
    
- **HeadMaster**
    
    `OTO → School`
    
- **Teacher**
    
    `MTO → School`
    
- **Class**
    
    `OTO (Optional) → Teacher`
    
    `MTO → School`
    
- **Student**
    
    `MTO → Class`
    
    `MTO → School`
    

**These models are for internal use only**

- **Member** (SuperType for HeadMaster, Teacher and Student)
    
    `MTO → School`
    
    `OTO → PersonalInfo`
    
    `Use to connect HeadMaster, Teacher and Student to School and PersonalInfo`
    
- **PersonalInfo**
    
    `Standalone model`
    

### API provided according to CRUD standards

![image](https://user-images.githubusercontent.com/46592735/211150067-90b82e28-534e-4cca-aa7f-f1b5a62fbd94.png)

- GET is public
- PUT PATCH POST DELETE methods are locked behind bearertoken:
    - Token: `42Bangkok42BangkokGUACAMOLE`

## Features

- When POST method is send to the server with correct authentication, User model will also be created username auto-generated from first_name and last_name with default password set to ‘@42Bangkok’, Teacher and HeadMaster will be have staff status while student will not. This User creation can be toggle in the [settings.py](http://settings.py) with CREATE_USER_ON_POST

![image](https://user-images.githubusercontent.com/46592735/211150079-513f2d3e-cff6-44db-ac4e-a89bd8480bcc.png)

## Unit Tests included

48 cases for most endpoints in test.py
```
python3 manage.py test
```
