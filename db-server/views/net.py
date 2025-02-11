from fastapi import APIRouter,Request,HTTPException
from model import DataBase
from model import redis
import json
from datetime import datetime
from pydantic import BaseModel

net = APIRouter(prefix="/net")



