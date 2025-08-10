# Whisper 音频转文字指南

## 🎵 什么是Whisper？

Whisper是OpenAI开发的开源语音识别系统，支持多种语言的音频转文字，包括中文。它完全离线运行，无需网络连接。

## 📦 安装步骤

### 1. 安装依赖
```bash
pip install -r requirements_whisper.txt
```

### 2. 安装FFmpeg (必需)
Whisper需要FFmpeg来处理音频文件。

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
下载并安装 [FFmpeg](https://ffmpeg.org/download.html)

## 🚀 使用方法

### 方法1: 使用完整脚本
```bash
# 转录单个文件
python audio_transcription_whisper.py --audio raw_audio/那些年_2025-08-02_high.m4a

# 批量转录目录
python audio_transcription_whisper.py --audio raw_audio --output transcriptions

# 使用不同模型大小
python audio_transcription_whisper.py --audio audio.mp3 --model large
```

### 方法2: 使用简单示例
```bash
python whisper_example.py
```

## 📊 模型大小对比

| 模型 | 大小 | 速度 | 准确率 | 内存使用 |
|------|------|------|--------|----------|
| tiny | 39MB | 最快 | 较低 | 1GB |
| base | 74MB | 快 | 中等 | 1GB |
| small | 244MB | 中等 | 高 | 2GB |
| medium | 769MB | 慢 | 很高 | 5GB |
| large | 1550MB | 最慢 | 最高 | 10GB |

**推荐**: 对于中文音频，建议使用 `base` 或 `small` 模型。

## 🎯 支持的文件格式

- MP3 (.mp3)
- WAV (.wav)
- M4A (.m4a)
- FLAC (.flac)
- AAC (.aac)
- OGG (.ogg)

## 📝 输出格式

转录结果会保存为JSON格式，包含：

```json
{
  "audio_file": "那些年_2025-08-02_high.m4a",
  "transcription": "转录的文本内容...",
  "segments": [
    {
      "start": 0.0,
      "end": 5.0,
      "text": "这段文本..."
    }
  ],
  "language": "zh"
}
```

## 🔧 常见问题

### Q: 安装时出现错误？
A: 确保已安装FFmpeg，并且Python版本 >= 3.8

### Q: 转录速度很慢？
A: 可以尝试使用更小的模型（如 `tiny` 或 `base`）

### Q: 中文识别不准确？
A: 确保指定了正确的语言参数 `language="zh"`

### Q: 内存不足？
A: 使用更小的模型，或增加系统内存

## 💡 使用技巧

1. **批量处理**: 使用目录模式批量转录多个文件
2. **模型选择**: 根据需求平衡速度和准确率
3. **语言指定**: 明确指定语言可以提高识别准确率
4. **分段信息**: 利用segments信息获取时间戳

## 📚 更多资源

- [Whisper GitHub](https://github.com/openai/whisper)
- [Whisper 论文](https://cdn.openai.com/papers/whisper.pdf)
- [官方文档](https://github.com/openai/whisper#readme)
