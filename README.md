# AI漫剧 - Novel to Video

一章小说 → AI分析内容 → 提取角色/场景/物品 → 生成稳定漫画图 → 所有图片转成连贯短视频 → 拼接成片

## 项目简介

这个项目旨在将小说文本自动转换为漫画视频内容。通过AI分析和图像生成技术，实现从文字到视频的自动化转换流程。

## 功能特性

- **小说管理**：自动导入小说文件到数据库
- **内容分析**：调用AI分析小说风格、角色、场景和物品
- **角色锁定**：提取并锁定角色特征，确保图像一致性（正面、侧面、四分之三角度）
- **场景提取**：提取出现三次以上的重要场景并生成场景插画
- **物品提取**：提取出现三次以上的重要物品并生成物品立绘
- **图像生成**：调用Wanx2.0-t2i-turbo API生成高质量漫画图像
- **数据库存储**：使用MySQL存储小说内容和分析结果
- **自动化处理**：支持批量处理和增量更新

## 技术栈

- Python 3.x
- MySQL数据库
- Moonshot AI API (文本分析)
- Wanx2.0-t2i-turbo API (图像生成)
- pymysql (数据库连接)
- requests (HTTP请求)

## 安装和使用

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置

1. **API密钥配置**：
   - 删除 `qwen_apk_key.example.txt` 中的 ".example" 后缀，重命名为 `qwen_apk_key.txt`
   - 在 `qwen_apk_key.txt` 文件中写入您的API密钥
   - 密钥文件不会被提交到Git
2. **数据库配置**：
   - 删除 `db_config.example.json` 中的 ".example" 后缀，重命名为 `db_config.json`
   - 在 `db_config.json` 文件中配置您的数据库连接信息
   - 配置文件不会被提交到Git

### 使用示例

#### 1. 导入小说到数据库

```bash
# 导入所有小说
python py/import_novel_to_db.py
```

#### 2. 分析小说风格和背景

```bash
# 分析所有小说的风格、背景、主角和视觉风格
python py/analyze_novel_style.py
```

#### 3. 提取角色信息

```bash
# 提取小说中的角色详细信息
python py/analyze_novel_characters.py
```

#### 4. 提取物品信息

```bash
# 提取出现三次以上的重要物品
python py/analyze_frequent_items.py
```

#### 5. 提取场景信息

```bash
# 提取出现三次以上的重要场景
python py/analyze_frequent_scenes.py
```

#### 6. 生成角色图像

```bash
# 为所有未生成的角色生成图像（每个角色3个角度）
python py/generate_role_images.py
```

#### 7. 生成场景图像

```bash
# 为所有未生成的场景生成图像
python py/generate_scene_images.py
```

#### 8. 生成物品图像

```bash
# 为所有未生成的物品生成图像
python py/generate_item_images.py
```

#### 9. 运行完整流程（推荐）

```bash
# 按照顺序自动运行所有脚本
python py/main.py
```

## 项目结构

```
AI漫剧/
├── README.md                 # 项目说明文档
├── requirements.txt          # Python依赖包
├── database_schema.sql       # 数据库结构SQL文件
├── db_config.example.json    # 数据库配置示例文件
├── qwen_apk_key.example.txt  # API密钥示例文件
├── .gitignore               # Git忽略配置
├── novel/                   # 小说存放目录
│   ├── 小说名1/
│   │   ├── 第一章.txt
│   │   ├── 第二章.txt
│   │   └── ...
│   └── .gitkeep
├── images/                  # 生成的图像存放目录
│   ├── 小说名1/
│   │   ├── 角色名_标准脸1_时间戳.png
│   │   ├── 场景名_场景_时间戳.png
│   │   └── 物品名_物品_时间戳.png
│   └── .gitkeep
└── py/                      # Python脚本目录
    ├── main.py                        # 主程序（自动运行完整流程）
    ├── import_novel_to_db.py          # 小说导入数据库
    ├── analyze_novel_style.py         # 小说风格分析
    ├── analyze_novel_characters.py    # 角色信息提取
    ├── analyze_frequent_items.py      # 物品信息提取
    ├── analyze_frequent_scenes.py     # 场景信息提取
    ├── generate_role_images.py        # 角色图像生成
    ├── generate_scene_images.py       # 场景图像生成
    └── generate_item_images.py        # 物品图像生成
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

- **novels**: 小说基本信息表（标题、作者、风格、状态等）
- **characters**: 角色详细信息表（外貌、体型、服装等）
- **items**: 物品信息表（类型、功能、稀有度等）
- **scenes**: 场景信息表（类型、视觉细节、氛围等）

## 注意事项

1. 小说文件需放在 `novel/小说名/章节名.txt` 格式
2. API密钥文件 `qwen_apk_key.txt` 不会被提交到Git
3. 数据库表已自动创建，无需手动创建
4. 生成的图像会保存在 `images/小说名/` 目录下
5. 每个角色会生成3个角度的标准脸（正面、侧面、四分之三角度）

## 贡献指南

欢迎提交Issue和Pull Request来帮助改进这个项目。

## 许可证

MIT License
