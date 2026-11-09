import argparse
import os
from commit import create_commit, get_log, get_status
from objects import write_object
from index import add_to_index
from commit import create_commit, get_log
def cmd_status(args):
    get_status()


def cmd_init(args):

    if os.path.exists(".git"):
        print("Reinitialized existing Git repository.")
        return
    os.makedirs(".git/objects", exist_ok=True)
    os.makedirs(".git/refs/heads", exist_ok=True)
    with open(".git/HEAD", "w") as f:
        f.write("ref: refs/heads/main\n")
    print(f"Initialized empty mini-git repository.")

def cmd_hash_object(args):
    with open(args.file, "rb") as f:
        content = f.read()
    sha = write_object(content, "blob")
    if args.write:
        print(sha)

def cmd_add(args):
    if not os.path.exists(args.file):
        print(f"fatal: pathspec '{args.file}' did not match any files")
        return
    with open(args.file, "rb") as f:
        content = f.read()
    sha = write_object(content, "blob")
    add_to_index(args.file, sha)


def cmd_commit(args):
    try:
        commit_sha = create_commit(args.message)
        # 把最新的 commit 哈希写入 main 分支
        with open(".git/refs/heads/main", "w") as f:
            f.write(commit_sha)
        print(f"[main {commit_sha[:7]}] {args.message}")
    except ValueError as e:
        print(e)

def cmd_log(args):
    logs = get_log()
    if not logs:
        print("fatal: your current branch 'main' does not have any commits yet")
        return
    for sha, content in logs:
        print(f"commit {sha}")
        print(content)

def main():
    parser = argparse.ArgumentParser(description="My mini-git")
    subparsers = parser.add_subparsers(dest="command", required=True)

    parser_init = subparsers.add_parser("init")
    parser_init.set_defaults(func=cmd_init)

    parser_hash = subparsers.add_parser("hash-object")
    parser_hash.add_argument("-w", dest="write", action="store_true")
    parser_hash.add_argument("file")
    parser_hash.set_defaults(func=cmd_hash_object)

    parser_add = subparsers.add_parser("add")
    parser_add.add_argument("file")
    parser_add.set_defaults(func=cmd_add)

    parser_commit = subparsers.add_parser("commit")
    parser_commit.add_argument("-m", dest="message", required=True, help="Commit message")
    parser_commit.set_defaults(func=cmd_commit)

    parser_log = subparsers.add_parser("log")
    parser_log.set_defaults(func=cmd_log)

    parser_status = subparsers.add_parser("status")
    parser_status.set_defaults(func=cmd_status)


    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()