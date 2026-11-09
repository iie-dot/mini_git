import os
import time
from objects import write_object, read_object
from index import read_index


def create_tree_from_index() -> str:
    """把暂存区的字典变成一棵树对象，返回树的哈希"""
    index_data = read_index()
    if not index_data:
        raise ValueError("Nothing to commit (create/copy files and use 'add' to track)")

    # 简化版：把 index 按字母排序后转成字符串
    # 格式：sha 路径\n
    lines = []
    for filepath, sha in sorted(index_data.items()):
        lines.append(f"{sha} {filepath}")

    tree_content = "\n".join(lines).encode()
    # 把树内容存为 "tree" 类型的对象
    tree_sha = write_object(tree_content, "tree")
    return tree_sha


def create_commit(message: str) -> str:
    """创建一次提交，返回 commit 对象的哈希"""
    tree_sha = create_tree_from_index()

    # 1. 读取当前的 HEAD（也就是上一次的 commit 哈希）
    parent_sha = ""
    head_path = ".git/refs/heads/main"
    if os.path.exists(head_path):
        with open(head_path, "r") as f:
            parent_sha = f.read().strip()

    author = "student <student@example.com>"
    timestamp = int(time.time())

    # 2. 如果有父提交，在内容里加上 parent 行
    commit_content = f"tree {tree_sha}\n"
    if parent_sha:
        commit_content += f"parent {parent_sha}\n"
    commit_content += f"author {author} {timestamp}\n"
    commit_content += f"committer {author} {timestamp}\n\n"
    commit_content += f"{message}\n"

    commit_sha = write_object(commit_content.encode(), "commit")
    return commit_sha


def get_log() -> list:
    """通过 parent 链读取所有提交历史"""
    head_path = ".git/refs/heads/main"
    if not os.path.exists(head_path):
        return []

    with open(head_path, "r") as f:
        current_sha = f.read().strip()

    logs = []
    # 只要还有 commit 哈希，就一直往回找
    while current_sha:
        obj_type, content = read_object(current_sha)
        logs.append((current_sha, content.decode()))

        # 解析内容，找下一级的 parent
        next_sha = ""
        for line in content.decode().split("\n"):
            if line.startswith("parent "):
                next_sha = line.split(" ")[1]
                break
        current_sha = next_sha

    return logs


def get_status():
    """检查文件状态"""
    # 1. 获取暂存区
    index_data = read_index()

    # 2. 获取最后一次 commit 的 tree 对象内容（简化处理，直接读 JSON）
    # 因为我们的 tree 是基于 index 排序生成的，所以对比起来很容易
    head_path = ".git/refs/heads/main"
    last_commit_tree = {}
    if os.path.exists(head_path) and os.path.getsize(head_path) > 0:
        with open(head_path, "r") as f:
            commit_sha = f.read().strip()
        if commit_sha:
            _, commit_content = read_object(commit_sha)
            # 找 tree 哈希
            tree_sha = ""
            for line in commit_content.decode().split("\n"):
                if line.startswith("tree "):
                    tree_sha = line.split(" ")[1]
                    break
            if tree_sha:
                _, tree_content = read_object(tree_sha)
                # 解析我们简化版的 tree 内容
                for line in tree_content.decode().split("\n"):
                    if line.strip():
                        sha, filepath = line.split(" ", 1)
                        last_commit_tree[filepath] = sha

    # 3. 扫描当前目录下的所有文件（排除 .git 目录）
    current_files = []
    for root, dirs, files in os.walk("."):
        if ".git" in dirs:
            dirs.remove(".git")
        for file in files:
            # 统一路径格式
            filepath = os.path.join(root, file).replace(".\\", "").replace("\\", "/")
            current_files.append(filepath)

    # 4. 开始对比
    print("Changes not staged for commit:")
    # 找出在 index 中，但当前磁盘上被删除或修改的文件
    for filepath, old_sha in index_data.items():
        if not os.path.exists(filepath):
            print(f"  deleted:    {filepath}")
        else:
            with open(filepath, "rb") as f:
                current_sha = write_object(f.read(), "blob")
            if current_sha != old_sha:
                print(f"  modified:   {filepath}")

    print("\nUntracked files:")
    # 找出在磁盘上，但还没被 add 进 index 的文件
    for filepath in current_files:
        if filepath not in index_data:
            print(f"  {filepath}")

    # 找出已经 add 了，但还没 commit 的文件（对比 index 和最后一次 commit）
    staged = []
    for filepath, sha in index_data.items():
        if last_commit_tree.get(filepath) != sha:
            staged.append(filepath)

    if staged:
        print("\nChanges to be committed:")
        for filepath in staged:
            print(f"  new file:   {filepath}")