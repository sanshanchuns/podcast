#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Whisper音频转文字简单示例
"""

import whisper
import json
from typing import Dict

_MODEL_CACHE: Dict[str, any] = {}

def get_or_load_model(model_name: str):
    """
    进程内模型缓存：同一进程多次调用时复用已加载的模型。
    """
    model = _MODEL_CACHE.get(model_name)
    if model is None:
        model = whisper.load_model(model_name)
        _MODEL_CACHE[model_name] = model
    return model

def simple_transcribe(audio_file_path, model_name: str = "base"):
    """
    简单的音频转文字示例
    
    Args:
        audio_file_path: 音频文件路径
        model_name: Whisper模型名称（tiny/base/small/medium/large），默认 base
    """
    print("正在加载Whisper模型...")
    
    # 加载模型 (可以选择不同大小: tiny, base, small, medium, large) - 使用缓存
    model = get_or_load_model(model_name)
    
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
