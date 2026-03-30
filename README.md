# Novel to Video

一章小说 → 拆成 N 段文本 → 每段生成 1 张稳定漫画图 → 所有图片转成连贯短视频 → 拼接成片

## 项目简介

这个项目旨在将小说文本自动转换为视频内容。通过一系列的处理流程，实现从文字到视频的自动化转换。

## 功能特性

- **小说管理**：自动导入小说文件到数据库
- **分镜生成**：调用AI API为小说生成漫画分镜Prompt模板
- **角色锁定**：提取并锁定角色特征，确保图像一致性
- **数据库存储**：使用MySQL存储小说内容和分镜信息
- **自动化处理**：支持批量处理和增量更新

## 技术栈

- Python
- MySQL数据库
- Moonshot AI API (kimi-k2.5模型)
- pymysql (数据库连接)
- requests (HTTP请求)

## 安装和使用

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置

1. **API密钥配置**：
   - 删除 `kimi api_key.example.txt` 中的 ".example" 后缀，重命名为 `kimi api_key.txt`
   - 在 `kimi api_key.txt` 文件中写入您的Moonshot API密钥
   - 密钥文件不会被提交到Git

2. **数据库配置**：
   - 删除 `db_config.example.json` 中的 ".example" 后缀，重命名为 `db_config.json`
   - 在 `db_config.json` 文件中配置您的数据库连接信息
   - 配置文件不会被提交到Git

### 使用示例

#### 1. 导入小说到数据库

```bash
# 导入所有小说
python import_novel_to_db.py

# 更新小说标题
python import_novel_to_db.py --update-title "旧小说名" "新小说名"
```

#### 2. 生成分镜Prompt

```bash
# 生成分镜和角色锁定参数
python novel_to_storyboard.py
```

## 项目结构

```
Novel-to-Video/
├── README.md              # 项目说明文档
├── requirements.txt       # Python依赖包
├── novel_to_storyboard.py # 小说转分镜程序
├── import_novel_to_db.py  # 小说导入数据库程序
├── database_schema.sql    # 数据库结构SQL文件
├── .gitignore            # Git忽略配置
├── db_config.example.json # 数据库配置示例文件
├── kimi api_key.example.txt # API密钥示例文件
└── novel/                # 小说存放目录
    └── .gitkeep          # 保持文件夹结构
```

## 小说目录结构

`novel/` 目录用于存放小说文件，结构如下：

```
novel/
├── 小说名1/
│   ├── 第一章.txt
│   ├── 第二章.txt
│   └── ...
├── 小说名2/
│   ├── 第一章.txt
│   ├── 第二章.txt
│   └── ...
└── .gitkeep  # 保持文件夹结构的空文件
```

**说明：**
- 每个小说文件夹以小说名称命名
- 每个章节文件以章节名称命名（如"第一章.txt"、"第二章.txt"）
- 小说内容不会被提交到Git仓库，只保留目录结构

## 数据库表结构

- **novels**: 小说基本信息表
- **chapters**: 小说章节表
- **characters**: 角色锁定参数表
- **storyboards**: 分镜表
- **generated_images**: 生成图像表
- **videos**: 视频表

## 注意事项

1. 小说文件需放在 `novel/小说名/章节名.txt` 格式
2. API密钥文件 `kimi api_key.txt` 不会被提交到Git
3. 数据库表已自动创建，无需手动创建

## 贡献指南

欢迎提交Issue和Pull Request来帮助改进这个项目。

## 许可证

MIT License