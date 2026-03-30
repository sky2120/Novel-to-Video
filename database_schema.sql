-- Novel to Video 数据库结构
-- 创建时间：2026-03-30

-- 删除所有表（按依赖关系倒序删除）
DROP TABLE IF EXISTS videos;
DROP TABLE IF EXISTS generated_images;
DROP TABLE IF EXISTS storyboards;
DROP TABLE IF EXISTS characters;
DROP TABLE IF EXISTS items;
DROP TABLE IF EXISTS chapters;
DROP TABLE IF EXISTS novels;

-- 小说基本信息表
CREATE TABLE novels (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL COMMENT '小说标题',
    author VARCHAR(100) COMMENT '作者名称',
    protagonist VARCHAR(100) COMMENT '主角名称',
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

-- 角色表
CREATE TABLE characters (
    id INT AUTO_INCREMENT PRIMARY KEY,
    novel_id INT NOT NULL COMMENT '小说ID',
    name VARCHAR(100) NOT NULL COMMENT '姓名',
    age INT COMMENT '年龄',
    gender VARCHAR(20) COMMENT '性别',
    personality VARCHAR(50) COMMENT '性格（高冷 / 温柔 / 腹黑 / 阳光 / 病娇等）',
    identity VARCHAR(50) COMMENT '身份（学生 / 总裁 / 修仙者 / 刺客 / 反派等）',
    hairstyle VARCHAR(100) COMMENT '发型：长度、颜色、样式（直发 / 卷发 / 高马尾 / 齐刘海）',
    face_shape VARCHAR(50) COMMENT '脸型：瓜子脸 / 圆脸 / 方脸 / 少年感窄脸',
    eyes VARCHAR(100) COMMENT '眼睛：颜色、形状（杏眼 / 桃花眼 / 丹凤眼）',
    eyebrows VARCHAR(50) COMMENT '眉毛：平眉 / 剑眉 / 细眉',
    nose_mouth VARCHAR(50) COMMENT '鼻子/嘴巴：精致/薄唇等',
    skin_color VARCHAR(20) COMMENT '肤色：冷白 / 正常 / 小麦色',
    height_atmosphere VARCHAR(50) COMMENT '身高氛围（高挑 / 娇小 / 少年感 / 强壮）',
    body_type VARCHAR(20) COMMENT '体型（纤细 / 匀称 / 肌肉）',
    temperament VARCHAR(50) COMMENT '气质（清冷 / 魅惑 / 阳光 / 阴郁 / 霸气）',
    clothing_style VARCHAR(50) COMMENT '主服装风格（校服 / 西装 / 古风 / 现代休闲 / 赛博）',
    color_scheme VARCHAR(50) COMMENT '固定配色（黑 + 白、蓝 + 灰、红 + 黑）',
    signature_decoration VARCHAR(100) COMMENT '标志性装饰（眼镜 / 发带 / 项链 / 耳钉 / 披风 / 手套）',
    art_style VARCHAR(50) COMMENT '漫画风格',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE,
    UNIQUE KEY idx_novel_character (novel_id, name),
    INDEX idx_novel_id (novel_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色表';

-- 物品表
CREATE TABLE items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    novel_id INT NOT NULL COMMENT '小说ID',
    name VARCHAR(100) NOT NULL COMMENT '物品名称',
    description TEXT COMMENT '物品详细描述',
    item_type VARCHAR(50) COMMENT '物品类型（武器/道具/法器/药品/食物/交通工具等）',
    item_function TEXT COMMENT '物品功能和作用',
    rarity VARCHAR(20) COMMENT '稀有度（普通/稀有/史诗/传说等）',
    appearance VARCHAR(200) COMMENT '物品外观描述',
    origin VARCHAR(100) COMMENT '物品来源',
    owner VARCHAR(100) COMMENT '物品持有者',
    importance INT COMMENT '重要性等级（1-10）',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE,
    UNIQUE KEY idx_novel_item (novel_id, name),
    INDEX idx_novel_id (novel_id),
    INDEX idx_item_type (item_type),
    INDEX idx_importance (importance)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='物品表';

-- 索引优化
CREATE INDEX idx_novels_status ON novels(status);
CREATE INDEX idx_novels_genre ON novels(genre);
CREATE INDEX idx_novels_import_status ON novels(import_status);
CREATE INDEX idx_novels_analysis_status ON novels(analysis_status);
CREATE INDEX idx_novels_video_status ON novels(video_status);

-- 注释说明
-- 1. novels表：存储小说的基本信息，包括标题、作者、状态等
-- 2. characters表：存储角色信息，关联到novels表，包含角色的详细特征描述
-- 3. items表：存储小说中的物品信息，关联到novels表，包含物品的详细描述和属性
