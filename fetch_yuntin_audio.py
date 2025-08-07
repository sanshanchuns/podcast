#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
云听音频数据获取和分析脚本
获取云听所有音频链接，分析那些年非重播的音频
"""

import requests
import json
import re
import argparse
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
import time
from collections import defaultdict

class YuntinAudioAnalyzer:
    def __init__(self):
        self.base_url = "https://60.205.171.165/contentBiz/appProgram/listByDate"
        self.session = requests.Session()
        # 设置请求头，模拟浏览器访问
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
    
    def generate_date_list(self, days: int) -> List[str]:
        """
        生成最近N天的日期列表，格式为YYYYMMDD
        
        Args:
            days: 要获取的天数
            
        Returns:
            日期列表
        """
        date_list = []
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            date_str = date.strftime('%Y%m%d')
            date_list.append(date_str)
        return date_list

    def get_cache_file_path(self, date: str) -> str:
        """
        获取缓存文件路径
        
        Args:
            date: 日期字符串，格式为YYYYMMDD
            
        Returns:
            缓存文件路径
        """
        return f"audio_input/{date}.json"
    
    def load_cached_data(self, date: str) -> Dict[str, Any]:
        """
        从缓存加载数据
        
        Args:
            date: 日期字符串，格式为YYYYMMDD
            
        Returns:
            缓存的音频数据字典
        """
        cache_file = self.get_cache_file_path(date)
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"从缓存加载 {date} 的数据，共 {len(data.get('data', []))} 条音频记录")
                return data
            except Exception as e:
                print(f"读取缓存文件失败: {e}")
        return {}
    
    def save_cached_data(self, date: str, data: Dict[str, Any]) -> None:
        """
        保存数据到缓存
        
        Args:
            date: 日期字符串，格式为YYYYMMDD
            data: 音频数据字典
        """
        cache_file = self.get_cache_file_path(date)
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"数据已缓存到 {cache_file}")
        except Exception as e:
            print(f"保存缓存文件失败: {e}")
    
    def fetch_audio_data(self, broadcast_id: str = "640", date: str = "20240724", force_update: bool = False) -> Dict[str, Any]:
        """
        获取指定日期的音频数据，支持缓存机制
        
        Args:
            broadcast_id: 广播ID
            date: 日期字符串，格式为YYYYMMDD
            force_update: 是否强制更新缓存
            
        Returns:
            音频数据字典
        """
        # 如果不强制更新，先尝试从缓存加载
        if not force_update:
            cached_data = self.load_cached_data(date)
            if cached_data:
                return cached_data
        
        params = {
            'broadcastId': broadcast_id,
            'date': date
        }
        
        try:
            print(f"正在获取 {date} 的音频数据...")
            # 禁用SSL证书验证
            response = self.session.get(self.base_url, params=params, timeout=30, verify=False)
            response.raise_for_status()
            
            data = response.json()
            print(f"成功获取数据，共 {len(data.get('data', []))} 条音频记录")
            
            # 保存到缓存
            self.save_cached_data(date, data)
            
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            return {}
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            return {}
    
    def analyze_audio_items(self, audio_data: Dict[str, Any], program_type: str = "那些年") -> List[Dict[str, Any]]:
        """
        分析音频数据，筛选出指定类型的音频，并增加 release_date 字段
        Args:
            audio_data: 原始音频数据
            program_type: 节目类型 ("那些年" 或 "财经阅读")
        Returns:
            筛选后的音频列表
        """
        if not audio_data or 'data' not in audio_data:
            return []
        
        audio_items = audio_data['data']
        filtered_items = []
        
        for item in audio_items:
            program_name = item.get('programName', '')
            if program_name != program_type:
                continue
            # 解析日期
            program_date = item.get('programDate')
            if program_date:
                # program_date 是毫秒时间戳
                release_date = datetime.fromtimestamp(program_date / 1000).strftime('%Y-%m-%d')
            else:
                release_date = ''
            # 计算时长（毫秒转分钟）
            start_time = item.get('startTime', 0)
            end_time = item.get('endTime', 0)
            duration_minutes = (end_time - start_time) / (1000 * 60) if end_time > start_time else 0
            filtered_item = {
                'id': item.get('id'),
                'program_name': program_name,
                'release_date': release_date,
                'play_url_low': item.get('playUrlLow'),
                'play_url_high': item.get('playUrlHigh')
            }
            filtered_items.append(filtered_item)
        return filtered_items
    
    def save_to_json(self, data: List[Dict[str, Any]], filename: str = "audio_output/yuntin_those_years_audio.json"):
        """
        按 release_date 分组输出，结构为 {日期: [audio_items]}，按时间倒序排列
        """
        grouped = defaultdict(list)
        for item in data:
            date = item.get('release_date', '')
            if date:
                grouped[date].append(item)
        # 转为普通dict，按日期倒序排列（最新的在前）
        grouped = dict(sorted(grouped.items(), reverse=True))
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(grouped, f, ensure_ascii=False, indent=2)
            print(f"数据已保存到 {filename}")
            print(f"共找到 {sum(len(v) for v in grouped.values())} 条音频")
        except Exception as e:
            print(f"保存文件失败: {e}")
    
    def run_analysis(self, dates: List[str] = None, output_file: str = "audio_output/yuntin_those_years_audio.json", program_type: str = "那些年", force_update: bool = False):
        """
        运行完整的分析流程
        
        Args:
            dates: 要分析的日期列表，如果为None则使用默认日期
            output_file: 输出文件名
            program_type: 节目类型 ("那些年" 或 "财经阅读")
            force_update: 是否强制更新缓存
        """
        if dates is None:
            dates = ["20240724"]  # 默认日期
        
        all_filtered_items = []
        
        for date in dates:
            print(f"\n=== 分析日期: {date} ===")
            
            # 获取音频数据
            audio_data = self.fetch_audio_data(date=date, force_update=force_update)
            
            if audio_data:
                # 分析音频项目
                filtered_items = self.analyze_audio_items(audio_data, program_type)
                all_filtered_items.extend(filtered_items)
                
                print(f"日期 {date} 找到 {len(filtered_items)} 条符合条件的音频")
                
                # 显示找到的音频标题
                for i, item in enumerate(filtered_items, 1):
                    print(f"  {i}. {item['program_name']}")
            
            # 添加延迟避免请求过于频繁
            time.sleep(1)
        
        # 保存结果
        if all_filtered_items:
            self.save_to_json(all_filtered_items, output_file)
        else:
            print("未找到符合条件的音频")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='云听音频分析工具')
    parser.add_argument('--days', type=int, required=True, help='获取最近N天的数据 (必填)')
    parser.add_argument('--output', type=str, required=True, help='输出文件名 (必填)')
    parser.add_argument('--program', type=str, required=True, choices=['那些年', '财经阅读'], help='节目类型 (必填)')
    parser.add_argument('--force', action='store_true', help='强制更新缓存，重新请求所有数据')

    # 如果没有参数，输出help并退出
    import sys
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    analyzer = YuntinAudioAnalyzer()

    # 生成最近N天的日期列表
    dates_to_analyze = analyzer.generate_date_list(args.days)

    print(f"开始分析云听{args.program}音频，获取最近 {args.days} 天的数据...")
    print(f"分析日期: {', '.join(dates_to_analyze)}")
    if args.force:
        print("强制更新模式：将重新请求所有数据")

    analyzer.run_analysis(dates_to_analyze, args.output, args.program, args.force)

if __name__ == "__main__":
    main() 