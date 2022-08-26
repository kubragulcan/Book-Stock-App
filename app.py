from fastapi import FastAPI,HTTPException
from pymongo import MongoClient
import pymongo
import pydantic
from bson.objectid import ObjectId
from enum import Enum

pydantic.json.ENCODERS_BY_TYPE[ObjectId] = str

myclient = pymongo.MongoClient("mongodb://localhost:27017/") 
bookstockdb = myclient["LOGOBOOKSTOCK"] 


class Bookgenre(str, Enum):
    Adventure = "Adventure"
    Classics = "Classics"
    Crime = "Crime"
    Fantasy = "Fantasy"
    Humor = "Humor"
    Romance = "Romance"
    Tragedy = "Tragedy"


app = FastAPI()

@app.get("/add_book")
async def addbook(book_genre: Bookgenre, book_name: str, stock :int):
    if stock > 0:
        book_type = bookstockdb[book_genre]
        book_data = {"book_name": book_name, "stock" : stock}
    
        book_temp = book_type.find_one({"book_name": book_name})
        if str(book_temp) != "None":
            stock1 = book_temp["stock"]
            filter = {"book_name": book_name}
            newvalues = {"$set":{"stock": stock+stock1}}
            updated_stock = book_type.update_one(filter, newvalues)
            new_stock = stock+stock1
            return{"book_genre": book_genre ,"book_name": book_name, "added_stock" : stock,"message" : "The book stock is updated to " + str(new_stock)}
        else:
            book_type.insert_one(book_data)
            return{"book_genre": book_genre ,"book_name": book_name, "added_stock" : stock,"message" : "The book is added."}
    else: return{"message":"Given stock number is not valid " }


@app.get("/delete_book")
async def deletebook(book_genre: Bookgenre, book_name: str, deleted_stock :int):
    book_data = {"book_name": book_name, "stock" : deleted_stock}
    book_type = bookstockdb[book_genre]

    book_temp = book_type.find_one({"book_name": book_name})
    if str(book_temp) != "None":
        stock1 = book_temp["stock"]
        filter = {"book_name": book_name}
        newvalues = {"$set":{"stock": stock1 - deleted_stock}}
        newstock = stock1 - deleted_stock 
        if newstock < 0 or deleted_stock < 0:
            return{"message":"Deleted stock number is not valid"}
        elif newstock == 0:
            book_type.delete_one(book_data)
            return{"book_genre": book_genre ,"book_name": book_name, "deleted_stock" : deleted_stock,"message" : "Out of stock"}
        else:
            updated_stock = book_type.update_one(filter, newvalues)
            return{"book_genre": book_genre ,"book_name": book_name, "deleted_stock" : deleted_stock,"message" : "The book stock is updated."}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@app.get("/list_book/{book_genre}")
async def booklist(book_genre: Bookgenre):
    book_type = bookstockdb[book_genre]
    mylist = book_type.find({})
    result = []
    for doc in mylist:
        result.append(doc)
    return result

