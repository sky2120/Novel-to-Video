# Novel to Video

一章小说 → 拆成 N 段文本 → 每段生成 1 张稳定漫画图 → 所有图片转成连贯短视频 → 拼接成片

## 项目简介

这个项目旨在将小说文本自动转换为视频内容。通过一系列的处理流程，实现从文字到视频的自动化转换。

## 功能特性

- 文本分段：将小说章节拆分为多个段落
- 图像生成：为每个段落生成稳定的漫画风格图像
- 视频转换：将图像序列转换为连贯的短视频
- 视频拼接：将多个短视频拼接成完整的视频作品

## 技术栈

- Python
- AI图像生成API
- 视频处理库

## 安装和使用

### 安装依赖

```bash
pip install -r requirements.txt
```

### 使用示例

```python
from novel_to_video import convert_novel_to_video

# 将小说转换为视频
convert_novel_to_video(
    novel_path="path/to/novel.txt",
    output_path="output/video.mp4",
    num_segments=10  # 将小说拆分为10段
)
```

## 项目结构

```
Novel-to-Video/
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── text_splitter.py    # 文本分段模块
│   ├── image_generator.py  # 图像生成模块
│   ├── video_creator.py    # 视频创建模块
│   └── video_concatenator.py  # 视频拼接模块
└── examples/
    └── example.py          # 使用示例
```

## 贡献指南

欢迎提交Issue和Pull Request来帮助改进这个项目。

## 许可证

MIT License
