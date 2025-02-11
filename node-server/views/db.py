from fastapi import APIRouter,Form,UploadFile,File,HTTPException,Request
from model import insert_data_from_csv
import csv, shutil, requests,json,uuid
from config import config
from model import db as mysql_db
db = APIRouter(prefix="/db")

@db.post("/upload")
def upload(user_id: int = Form(...),table_name: str = Form(...),hasHeader: bool = Form(...), file: UploadFile = File(...),request: Request=None):
    if file is None or file == "":
        raise HTTPException(status_code=401, detail="没有上传文件")
    column_name = []
    file_name = uuid.uuid4()
    file_path = f"static/uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    data_count = 0
    original_file = f"data/original/{str(file_name)}.csv"
    with open(original_file, "w") as writer_file, open(file_path, "r") as reader_file:
        reader = csv.reader(reader_file)
        writer = csv.writer(writer_file)
        if hasHeader:
            column_name = next(reader)
            writer.writerow(column_name)
        else:
            column_names = next(reader)
            column_name = ["field" + str(index) for index in range(len(column_names))]
            writer.writerow(column_name)
        for row in reader:
            writer.writerow(row)
            data_count += 1
        
    try:
        # 获得文件中数据量
        db_info= {
            "user_id": user_id,
            "db_name": table_name,
            "data_count": data_count,
            "field": json.dumps(column_name),
            "file_name": str(file_name)
        }
        user_session = request.query_params.get("userSession")
        res = requests.post(f"http://{config.center_host}:{config.center_port}/db/upload?session={user_session}",json=db_info)
        if res.status_code != 200:
            import os
            os.remove(original_file)
            os.remove(file_path)
            raise HTTPException(status_code=402, detail="数据管理中心上传失败")     
        else:
            return {"message": "上传成功"}
    except Exception as e:
        import os
        os.remove(original_file)
        os.remove(file_path)
        raise HTTPException(status_code=401, detail=str(e))
