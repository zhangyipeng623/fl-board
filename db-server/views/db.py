from fastapi import APIRouter,Request
from model import DataBase
import requests

db = APIRouter(prefix="/db")


@db.get("/original")
def original():
    database = DataBase.select()
    db_list = list(database.dicts())

    return {"db_list": db_list}
