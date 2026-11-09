import json
import os

INDEX_FILE = ".git/index.json"

def read_index() -> dict:
    """读取暂存区，如果不存在则返回空字典"""
    if not os.path.exists(INDEX_FILE):
        return {}
    with open(INDEX_FILE, "r") as f:
        return json.load(f)

def write_index(index_data: dict):
    """把字典写回暂存区文件"""
    with open(INDEX_FILE, "w") as f:
        json.dump(index_data, f, indent=4)

def add_to_index(filepath: str, sha: str):
    """把文件路径和对应的哈希存入暂存区"""
    index_data = read_index()
    # 统一把 Windows 的反斜杠换成斜杠，保持和 Git 一致
    filepath = filepath.replace("\\", "/")
    index_data[filepath] = sha
    write_index(index_data)