-- Novel to Video 数据库结构
-- 创建时间：2026-03-30

-- 删除所有表（按依赖关系倒序删除）
DROP TABLE IF EXISTS videos;
DROP TABLE IF EXISTS generated_images;
DROP TABLE IF EXISTS storyboards;
DROP TABLE IF EXISTS characters;
DROP TABLE IF EXISTS chapters;
DROP TABLE IF EXISTS novels;

-- 小说基本信息表
CREATE TABLE novels (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL COMMENT '小说标题',
    author VARCHAR(100) COMMENT '作者名称',
    status ENUM('ongoing', 'completed', 'paused') DEFAULT 'ongoing' COMMENT '小说状态（ongoing进行中、completed已完成、paused暂停）',
    visual_style VARCHAR(100) COMMENT '视觉风格（漫画风、写实风、水彩风等）',
    art_style VARCHAR(100) COMMENT '艺术风格（日式、美式、中式等）',
    background_setting VARCHAR(200) COMMENT '背景设置（现代都市、古代仙侠、未来科幻等）',
    style_prompt TEXT COMMENT '风格提示词（用于AI生成的详细风格描述）',
    genre VARCHAR(100) COMMENT '小说类型（玄幻、仙侠、都市、科幻等）',
    import_status ENUM('pending', 'imported', 'failed') DEFAULT 'pending' COMMENT '导入状态（pending等待导入、imported已导入、failed导入失败）',
    analysis_status ENUM('pending', 'analyzed', 'failed') DEFAULT 'pending' COMMENT '分析状态（pending等待分析、analyzed已分析、failed分析失败）',
    video_status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending' COMMENT '视频生成状态（pending等待生成、processing处理中、completed已完成、failed生成失败）',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    last_processed_at TIMESTAMP NULL COMMENT '最后处理时间',
    INDEX idx_title (title)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='小说基本信息表';

-- 索引优化
CREATE INDEX idx_novels_status ON novels(status);
CREATE INDEX idx_novels_genre ON novels(genre);
CREATE INDEX idx_novels_import_status ON novels(import_status);
CREATE INDEX idx_novels_analysis_status ON novels(analysis_status);
CREATE INDEX idx_novels_video_status ON novels(video_status);

-- 注释说明
-- 1. novels表：存储小说的基本信息，包括标题、作者、状态等
