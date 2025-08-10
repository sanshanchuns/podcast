# 云听音频分析工具

这个工具用于获取云听音频数据，分析并筛选出指定节目的音频，生成对应的JSON文件。支持"那些年"和"财经阅读"两种节目类型。

## 功能特点

- 自动获取云听音频数据
- 支持多种节目类型（那些年、财经阅读）
- 精确匹配节目名称
- 生成结构化的JSON数据
- 支持多日期批量分析
- 按时间倒序排列输出
- 智能缓存机制，避免重复请求
- 支持强制更新缓存
- 音频文件下载功能
- 音频内容分析和脑图生成

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本使用（获取最近7天数据）

```bash
python fetch_yuntin_audio.py
```

### 获取最近N天数据

```bash
# 获取最近3天数据
python fetch_yuntin_audio.py --days 3

# 获取最近14天数据
python fetch_yuntin_audio.py --days 14

# 获取最近30天数据
python fetch_yuntin_audio.py --days 30
```

### 指定节目类型

```bash
# 获取"那些年"节目数据（默认）
python fetch_yuntin_audio.py --program "那些年"

# 获取"财经阅读"节目数据
python fetch_yuntin_audio.py --program "财经阅读"
```

### 自定义输出文件名

```bash
# 获取最近5天数据，输出到指定文件
python fetch_yuntin_audio.py --days 5 --output my_audio_data.json

# 获取"财经阅读"数据，自定义输出文件
python fetch_yuntin_audio.py --program "财经阅读" --output finance_audio.json

# 输出到audio_output目录（默认）
python fetch_yuntin_audio.py --program "那些年"
# 生成: audio_output/yuntin_those_years_audio.json

python fetch_yuntin_audio.py --program "财经阅读"
# 生成: audio_output/yuntin_finance_audio.json
```

### 缓存管理

```bash
# 正常模式：优先使用缓存，不存在则请求
python fetch_yuntin_audio.py --days 3

# 强制更新：重新请求所有数据并更新缓存
python fetch_yuntin_audio.py --days 3 --force

# 查看帮助信息
python fetch_yuntin_audio.py --help
```

### 音频下载

```bash
# 下载那些年节目音频
python download_audio.py 那些年

# 下载财经阅读节目音频
python download_audio.py 财经阅读

# 下载低质量音频文件
python download_audio.py 那些年 --quality low

# 查看下载帮助
python download_audio.py --help
```

### 音频分析

```bash
# 分析音频内容并生成脑图
python audio_to_mindmap.py

# 查看脑图可视化
python visualize_mindmap.py

# 自定义输出目录
python audio_to_mindmap.py --output my_analysis
```

## 文件结构

### 输出文件
- `audio_output/yuntin_those_years_audio.json`: 那些年节目数据
- `audio_output/yuntin_finance_audio.json`: 财经阅读节目数据

### 缓存文件
- `audio_input/YYYYMMDD.json`: 按日期缓存的原始API响应数据
- 缓存文件按日期命名，如：`audio_input/20250808.json`

### 音频文件
- `raw_audio/节目名_日期_音质.m4a`: 下载的音频文件
- 文件命名格式：`那些年_2025-08-07_high.m4a`

### 分析结果
- `mindmap_output/transcriptions.json`: 音频转录文本和分析结果
- `mindmap_output/mindmap_data.json`: 脑图数据结构

### 音频项目 (audio_items)
每个音频项目包含：
- `id`: 音频ID
- `program_name`: 节目名称
- `release_date`: 发布日期（YYYY-MM-DD格式）
- `play_url_low`: 低质量播放链接
- `play_url_high`: 高质量播放链接

## 筛选规则

脚本会筛选出满足以下条件的音频：
1. 节目名称完全匹配指定的节目类型（"那些年"或"财经阅读"）
2. 精确匹配，不包含重播版本
3. 按时间倒序排列输出（最新日期在前）

## 注意事项

- 脚本会禁用SSL证书验证以避免连接问题
- 每次请求之间有1秒延迟，避免请求过于频繁
- 支持批量分析多个日期
- 自动计算节目时长
- 缓存机制可以避免重复请求，提高效率
- 使用 `--force` 参数可以强制更新缓存数据
- 音频文件较大（约83MB），下载时请确保网络稳定
- 下载的文件会跳过已存在的文件，避免重复下载
- 下载脚本会自动根据节目类型选择对应的JSON文件
- 音频分析支持中文分词和关键词提取
- 脑图可视化展示节目内容和主题分布

## 示例输出

```json
{
  "2025-08-08": [
    {
      "id": "975621059",
      "program_name": "那些年",
      "release_date": "2025-08-08",
      "play_url_low": null,
      "play_url_high": null
    }
  ],
  "2025-08-07": [
    {
      "id": "975621036",
      "program_name": "那些年",
      "release_date": "2025-08-07",
      "play_url_low": "https://ytrecordbroadcast.radio.cn/echo/2/1953214643489157120.m4a?e=0&ps=1&r=3",
      "play_url_high": "https://ytrecordbroadcast.radio.cn/echo/2/1953214643463938048.m4a?e=0&ps=1&r=1"
    }
  ]
}
```
