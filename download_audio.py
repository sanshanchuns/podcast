#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音频下载脚本
根据节目类型自动选择JSON文件并下载音频到raw_audio目录
"""

import json
import os
import requests
import argparse
from urllib.parse import urlparse
from pathlib import Path

def get_json_file_path(program_name: str) -> str:
    """
    根据节目名称获取对应的JSON文件路径
    
    Args:
        program_name: 节目名称
        
    Returns:
        JSON文件路径
    """
    if program_name == "那些年":
        return "audio_output/yuntin_those_years_audio.json"
    elif program_name == "财经阅读":
        return "audio_output/yuntin_finance_audio.json"
    else:
        raise ValueError(f"不支持的节目类型: {program_name}")

def download_audio_file(url: str, filepath: str) -> bool:
    """
    下载音频文件
    
    Args:
        url: 音频文件URL
        filepath: 保存路径
        
    Returns:
        是否下载成功
    """
    if not url:
        return False
        
    try:
        print(f"正在下载: {url}")
        response = requests.get(url, stream=True, timeout=30, verify=False)
        response.raise_for_status()
        
        # 确保目录存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # 写入文件
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"下载完成: {filepath}")
        return True
        
    except Exception as e:
        print(f"下载失败 {url}: {e}")
        return False

def get_audio_filename(program_name: str, release_date: str, quality: str = "high") -> str:
    """
    生成音频文件名
    
    Args:
        program_name: 节目名称
        release_date: 发布日期
        quality: 音质 (high/low)
        
    Returns:
        文件名
    """
    # 清理文件名中的特殊字符
    safe_program_name = program_name.replace('(', '').replace(')', '').replace('（', '').replace('）', '')
    return f"{safe_program_name}_{release_date}_{quality}.m4a"

def check_file_exists(program_name: str, release_date: str, quality: str = "high") -> bool:
    """
    检查音频文件是否已存在
    
    Args:
        program_name: 节目名称
        release_date: 发布日期
        quality: 音质
        
    Returns:
        文件是否存在
    """
    filename = get_audio_filename(program_name, release_date, quality)
    filepath = os.path.join('raw_audio', filename)
    return os.path.exists(filepath)

def download_from_json(json_file: str, quality: str = "high") -> None:
    """
    从JSON文件下载音频
    
    Args:
        json_file: JSON文件路径
        quality: 音质选择 (high/low)
    """
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"读取JSON文件失败: {e}")
        return
    
    download_count = 0
    success_count = 0
    skip_count = 0
    
    for date, audio_items in data.items():
        print(f"\n=== 处理日期: {date} ===")
        
        for item in audio_items:
            program_name = item.get('program_name', '')
            release_date = item.get('release_date', '')
            
            if not program_name or not release_date:
                continue
            
            # 选择音质
            if quality == "high":
                audio_url = item.get('play_url_high')
            else:
                audio_url = item.get('play_url_low')
            
            if not audio_url:
                print(f"跳过 {program_name} {release_date}: 无{quality}音质链接")
                continue
            
            # 检查文件是否已存在
            if check_file_exists(program_name, release_date, quality):
                print(f"文件已存在，跳过: {program_name}_{release_date}_{quality}.m4a")
                skip_count += 1
                continue
            
            # 生成文件名
            filename = get_audio_filename(program_name, release_date, quality)
            filepath = os.path.join('raw_audio', filename)
            
            download_count += 1
            if download_audio_file(audio_url, filepath):
                success_count += 1
    
    print(f"\n下载完成: 成功 {success_count}/{download_count} 个文件，跳过 {skip_count} 个已存在文件")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='音频下载工具')
    parser.add_argument('program_name', choices=['那些年', '财经阅读'], help='节目类型')
    parser.add_argument('--quality', choices=['high', 'low'], default='high', 
                       help='音质选择 (默认: high)')
    
    args = parser.parse_args()
    
    # 根据节目名称获取JSON文件路径
    try:
        json_file = get_json_file_path(args.program_name)
    except ValueError as e:
        print(f"错误: {e}")
        return
    
    if not os.path.exists(json_file):
        print(f"JSON文件不存在: {json_file}")
        print("请先运行 fetch_yuntin_audio.py 生成对应的JSON文件")
        return
    
    print(f"开始下载音频文件...")
    print(f"节目类型: {args.program_name}")
    print(f"JSON文件: {json_file}")
    print(f"音质选择: {args.quality}")
    print(f"输出目录: raw_audio/")
    
    download_from_json(json_file, args.quality)

if __name__ == "__main__":
    main()
