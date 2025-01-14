from fastapi import APIRouter,Form,UploadFile,File,HTTPException
from model import insert_data_from_csv
import csv
import shutil

db = APIRouter(prefix="/db")

@db.post("/upload")
def upload(table_name: str = Form(...),hasHeader: bool = Form(...), file: UploadFile = File(...)):
    if file is None or file == "":
        return HTTPException(status_code=401, detail="没有上传文件")
    if hasHeader:
        column_name = None
    else:
        with open(f"static/uploads/{file.filename}", "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_path = f"static/uploads/{file.filename}"
        reader = csv.reader(open(file_path))
        column_names = next(reader)
        column_name = []
        for index,column_name in enumerate(column_names):
            column_name.append("field"+str(index))
    try:
        # 获得文件中数据量
        reader = csv.reader(open(file_path))
        data_count = len(reader)
        if hasHeader:
            data_count = data_count - 1
        insert_data_from_csv("static/uploads/"+file.filename,table_name,column_name,data_count)
        return {"message": "上传成功"}
    except Exception as e:
        return HTTPException(status_code=401, detail=str(e))
