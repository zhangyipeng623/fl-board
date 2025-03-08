"""数据库操作相关路由

本模块提供了数据库相关的API路由,包括:
- 文件上传接口
- 数据库信息管理
"""

import os
import pandas
import requests
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from config import config
from utils.utils import map_dtype_to_simple_type

db = APIRouter(prefix="/db")


class UploadFileInfo(BaseModel):
    """文件上传信息模型类

    用于接收和验证文件上传请求中的相关信息

    属性:
        user_id: 用户ID
        db_name: 数据库名称
        detail: 数据库详细描述
        file_name: 文件名
        file_type: 文件类型
    """
    user_id: int
    db_name: str
    detail: str
    file_name: str
    file_type: str


@db.post("/upload")
def upload(
    request: Request,
    upload_file_info: UploadFileInfo
):
    # 查找已上传的文件
    file_path = f"static/uploads/files/{upload_file_info.file_name}.{upload_file_info.file_type}"
    if not os.path.exists(file_path):
        raise HTTPException(401, detail=f"文件不存在,{file_path}")
    data_count = 0
    if upload_file_info.file_type == "csv":
        # 使用分块读取CSV文件
        try:
            # 使用分块读取CSV文件
            chunk_size = 100000  # 每次处理10000行
            first_chunk = True

            # 先读取一小部分数据来确定字符串列的最大长度和数据类型
            sample_df = pandas.read_csv(file_path, nrows=1000)

            # 计算每列的最大字符串长度
            min_itemsize = {}
            for col in sample_df.select_dtypes(include=['object']).columns:
                # 为字符串列设置足够大的长度，默认设为100，可以根据实际情况调整
                min_itemsize[col] = 100

            # 创建一个字典来存储每列的数据类型
            dtypes = sample_df.dtypes.to_dict()

            # 使用相同的数据类型读取所有数据块
            for chunk in pandas.read_csv(file_path, chunksize=chunk_size, dtype=dtypes):
                # 确保所有列的数据类型一致
                for col in chunk.columns:
                    if col in dtypes:
                        chunk[col] = chunk[col].astype(dtypes[col])
                mode = 'w' if first_chunk else 'a'
                chunk.to_hdf(
                    f"data/original/{upload_file_info.file_name}.h5",
                    key='df',
                    format='table',
                    mode=mode,
                    append=not first_chunk,
                    min_itemsize=min_itemsize
                )
                data_count += len(chunk)
                first_chunk = False
        except Exception as e:
            os.remove(file_path)
            raise HTTPException(401, detail=f"错误,{e}") from e
    else:
        # 使用分块读取HDF5文件
        chunk_size = 100000
        first_chunk = True
        try:
            # 尝试使用chunks读取
            # 先读取一个样本来确定数据类型
            sample_df = pandas.read_hdf(file_path, stop=1)
            dtypes = sample_df.dtypes.to_dict()
            min_itemsize = {}
            for col in sample_df.select_dtypes(include=['object']).columns:
                min_itemsize[col] = 100

            chunks = pandas.read_hdf(file_path, chunksize=chunk_size)
            for chunk in chunks:
                # 确保所有列的数据类型一致
                for col in chunk.columns:
                    if col in dtypes:
                        chunk[col] = chunk[col].astype(dtypes[col])

                data_count += len(chunk)
                mode = 'w' if first_chunk else 'a'
                chunk.to_hdf(
                    f"data/original/{upload_file_info.file_name}.h5",
                    key='df',
                    format='table',
                    mode=mode,
                    append=not first_chunk,
                    min_itemsize=min_itemsize
                )
                first_chunk = False
        except TypeError as e:
            os.remove(file_path)
            raise HTTPException(
                401, detail=f"文件格式错误(请将其转化为table类型的h5文件),{e}") from e
    # 删除文件
    os.remove(file_path)
    fields = ''
    with pandas.HDFStore(f"data/original/{upload_file_info.file_name}.h5", mode='r') as store:
        # 获取数据类型信息
        # 读取一行数据来获取类型信息
        df_sample = store.select('df', start=0, stop=1)
        fields = df_sample.dtypes.to_dict()
        fields = {col: map_dtype_to_simple_type(
            dtype) for col, dtype in fields.items()}
    db_info = {
        "user_id": upload_file_info.user_id,
        "db_name": upload_file_info.db_name,
        "field": fields,
        "detail": upload_file_info.detail,
        "data_count": int(data_count),
        "file_name": upload_file_info.file_name,
    }
    # 设置5秒超时时间避免请求无限等待
    res = requests.post(
        f"http://{config.center_host}:{config.center_port}/db/upload",
        json=db_info,
        headers={"Authorization": request.headers.get("Authorization")},
        timeout=5
    )
    if res.status_code != 200:
        raise HTTPException(401, detail="数据库上传失败")
    else:
        return {
            "status": "success",
            "message": "文件上传成功",
            "file_id": upload_file_info.file_name,
            "table_name": upload_file_info.db_name
        }
