#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Whisper音频转文字简单示例
"""

import whisper
import json

def simple_transcribe(audio_file_path):
    """
    简单的音频转文字示例
    
    Args:
        audio_file_path: 音频文件路径
    """
    print("正在加载Whisper模型...")
    
    # 加载模型 (可以选择不同大小: tiny, base, small, medium, large)
    model = whisper.load_model("base")
    
    print("开始转录...")
    
    # 转录音频
    result = model.transcribe(
        audio_file_path,
        language="zh",  # 指定中文
        verbose=True    # 显示详细进度
    )
    
    print("\n转录完成！")
    print("=" * 50)
    print("转录文本:")
    print(result["text"])
    
    # 保存结果
    output_file = f"{audio_file_path.split('.')[0]}_whisper_result.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到: {output_file}")
    
    return result

if __name__ == "__main__":
    # 示例用法
    audio_file = "raw_audio/那些年_2025-08-02_high.m4a"  # 替换为实际音频文件路径
    
    try:
        result = simple_transcribe(audio_file)
    except FileNotFoundError:
        print(f"错误: 找不到音频文件 {audio_file}")
        print("请确保音频文件存在，或修改文件路径")
    except Exception as e:
        print(f"转录过程中出现错误: {e}")
