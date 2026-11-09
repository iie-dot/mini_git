# Mini-Git 🚀

一个使用纯 Python 从零实现的极简 Git 版本控制系统。

## 💡 项目初衷
[为了深入理解 Git 的底层对象模型和版本控制原理，用 Python 写的 mini-git。]

## ✨ 已实现功能
- `init`: 初始化一个空的 Git 仓库
- `hash-object`: 计算文件内容的哈希值并存入对象库
- `add`: 将文件添加到暂存区
- `commit`: 将暂存区的内容提交，并记录父提交链
- `status`: 查看工作区、暂存区与最新提交的状态差异
- `log`: 打印从最新到最旧的提交历史

## 🛠️ 如何使用

1. 克隆本仓库：
   ```bash
   git clone https://github.com/[你的GitHub用户名]/mini-git.git
   cd mini-git