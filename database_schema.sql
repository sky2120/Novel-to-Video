-- Novel to Video 数据库结构
-- 创建时间：2026-03-30

-- 小说基本信息表
CREATE TABLE IF NOT EXISTS novels (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL COMMENT '小说标题',
    author VARCHAR(100) COMMENT '作者',
    description TEXT COMMENT '小说简介',
    cover_url VARCHAR(500) COMMENT '封面图片URL',
    status ENUM('ongoing', 'completed', 'paused') DEFAULT 'ongoing' COMMENT '状态',
    total_chapters INT DEFAULT 0 COMMENT '总章节数',
    progress_chapters INT DEFAULT 0 COMMENT '进度章节数（已处理的章节数）',
    visual_style VARCHAR(100) COMMENT '视觉风格（漫画风、写实风、水彩风等）',
    art_style VARCHAR(100) COMMENT '艺术风格（日式、美式、中式等）',
    background_setting VARCHAR(200) COMMENT '背景设置（现代都市、古代仙侠、未来科幻等）',
    style_prompt TEXT COMMENT '风格提示词（用于AI生成的详细风格描述）',
    genre VARCHAR(100) COMMENT '小说类型（玄幻、仙侠、都市、科幻等）',
    language VARCHAR(50) DEFAULT '中文' COMMENT '语言类型（中文、英文等）',
    word_count INT DEFAULT 0 COMMENT '总字数',
    publish_date DATE COMMENT '发布日期',
    source_url VARCHAR(500) COMMENT '来源链接',
    import_status ENUM('pending', 'imported', 'failed') DEFAULT 'pending' COMMENT '导入状态',
    analysis_status ENUM('pending', 'analyzed', 'failed') DEFAULT 'pending' COMMENT '分析状态',
    storyboard_status ENUM('pending', 'generating', 'completed', 'failed') DEFAULT 'pending' COMMENT '分镜生成状态',
    video_status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending' COMMENT '视频生成状态',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    last_processed_at TIMESTAMP NULL COMMENT '最后处理时间',
    INDEX idx_title (title)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='小说基本信息表';

-- 小说章节表
CREATE TABLE IF NOT EXISTS chapters (
    id INT AUTO_INCREMENT PRIMARY KEY,
    novel_id INT NOT NULL COMMENT '小说ID',
    chapter_number INT NOT NULL COMMENT '章节编号',
    title VARCHAR(255) NOT NULL COMMENT '章节标题',
    content TEXT NOT NULL COMMENT '章节内容',
    word_count INT DEFAULT 0 COMMENT '字数',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE,
    UNIQUE KEY idx_novel_chapter (novel_id, chapter_number),
    INDEX idx_novel_id (novel_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='小说章节表';

-- 角色锁定参数表
CREATE TABLE IF NOT EXISTS characters (
    id INT AUTO_INCREMENT PRIMARY KEY,
    novel_id INT NOT NULL COMMENT '小说ID',
    name VARCHAR(100) NOT NULL COMMENT '角色名称',
    appearance TEXT COMMENT '外貌描述',
    clothing TEXT COMMENT '服装描述',
    hairstyle VARCHAR(100) COMMENT '发型描述',
    expression TEXT COMMENT '表情特征',
    other_features TEXT COMMENT '其他特征',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE,
    UNIQUE KEY idx_novel_character (novel_id, name),
    INDEX idx_novel_id (novel_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色锁定参数表';

-- 分镜表
CREATE TABLE IF NOT EXISTS storyboards (
    id INT AUTO_INCREMENT PRIMARY KEY,
    chapter_id INT NOT NULL COMMENT '章节ID',
    scene_number INT NOT NULL COMMENT '场景编号',
    scene_description VARCHAR(500) NOT NULL COMMENT '场景描述',
    prompt TEXT NOT NULL COMMENT '图像生成Prompt',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE CASCADE,
    UNIQUE KEY idx_chapter_scene (chapter_id, scene_number),
    INDEX idx_chapter_id (chapter_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='分镜表';

-- 生成图像表
CREATE TABLE IF NOT EXISTS generated_images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    storyboard_id INT NOT NULL COMMENT '分镜ID',
    image_path VARCHAR(500) NOT NULL COMMENT '图像保存路径',
    image_url VARCHAR(500) COMMENT '图像URL',
    width INT COMMENT '图像宽度',
    height INT COMMENT '图像高度',
    status ENUM('pending', 'generating', 'completed', 'failed') DEFAULT 'pending' COMMENT '生成状态',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (storyboard_id) REFERENCES storyboards(id) ON DELETE CASCADE,
    INDEX idx_storyboard_id (storyboard_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='生成的图像表';

-- 视频表
CREATE TABLE IF NOT EXISTS videos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    chapter_id INT NOT NULL COMMENT '章节ID',
    video_path VARCHAR(500) NOT NULL COMMENT '视频保存路径',
    video_url VARCHAR(500) COMMENT '视频URL',
    duration INT COMMENT '视频时长（秒）',
    resolution VARCHAR(50) COMMENT '分辨率',
    status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending' COMMENT '处理状态',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE CASCADE,
    INDEX idx_chapter_id (chapter_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='生成的视频表';

-- 索引优化
CREATE INDEX idx_novels_status ON novels(status);
CREATE INDEX idx_novels_genre ON novels(genre);
CREATE INDEX idx_novels_import_status ON novels(import_status);
CREATE INDEX idx_novels_analysis_status ON novels(analysis_status);
CREATE INDEX idx_novels_storyboard_status ON novels(storyboard_status);
CREATE INDEX idx_novels_video_status ON novels(video_status);
CREATE INDEX idx_chapters_chapter_number ON chapters(chapter_number);
CREATE INDEX idx_characters_name ON characters(name);
CREATE INDEX idx_generated_images_width_height ON generated_images(width, height);
CREATE INDEX idx_videos_resolution ON videos(resolution);

-- 注释说明
-- 1. novels表：存储小说的基本信息，包括标题、作者、状态等
-- 2. chapters表：存储小说的章节内容，关联到novels表
-- 3. characters表：存储角色的特征信息，用于图像生成时保持角色一致性
-- 4. storyboards表：存储分镜信息，每个分镜对应一个场景和一个图像生成Prompt
-- 5. generated_images表：存储生成的图像信息，关联到storyboards表
-- 6. videos表：存储生成的视频信息，关联到chapters表
