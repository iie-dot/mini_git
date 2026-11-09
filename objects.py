import hashlib
import zlib
import os


def write_object(content: bytes, obj_type: str = "blob") -> str:
    """把内容写入 Git 对象库，并返回它的哈希值"""
    # 1. 拼接对象头：比如 "blob 6\0"
    header = f"{obj_type} {len(content)}".encode() + b"\0"
    data = header + content

    # 2. 计算 SHA1 哈希
    sha = hashlib.sha1(data).hexdigest()

    # 3. 确定存储路径：.git/objects/前两位/后38位
    dir_name = sha[:2]
    file_name = sha[2:]
    obj_dir = os.path.join(".git", "objects", dir_name)
    obj_path = os.path.join(obj_dir, file_name)

    # 4. 如果文件已经存在，就不重复写了（Git 的去重机制）
    if not os.path.exists(obj_path):
        os.makedirs(obj_dir, exist_ok=True)
        # 5. 压缩并用二进制写入文件
        with open(obj_path, "wb") as f:
            f.write(zlib.compress(data))

    return sha


def read_object(sha: str) :
    """根据哈希值读取对象，返回 (类型, 内容)"""
    # 1. 拼出路径
    obj_path = os.path.join(".git", "objects", sha[:2], sha[2:])

    # 2. 读出来并解压
    with open(obj_path, "rb") as f:
        data = zlib.decompress(f.read())

    # 3. 拆分对象头和内容（以 \0 为界）
    header, content = data.split(b"\0", maxsplit=1)
    obj_type = header.split(b" ")[0].decode()

    return obj_type, content