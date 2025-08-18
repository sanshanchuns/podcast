#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全流程流水线脚本
步骤：
1) 获取云听JSON（最近N天，从昨天起往前），支持节目：那些年 / 财经阅读 / 全部
2) 根据JSON下载音频到 raw_audio/
3) Whisper 将音频转文字
4) 从文字中提取核心关键词与摘要句

复用：
- fetch_yuntin_audio_json.py → YuntinAudioAnalyzer
- download_raw_audio.py → download_from_json / 命名约定
- audio2txt2comic/whisper_example.py → simple_transcribe
"""

import os
import json
import argparse
from typing import List, Dict, Any, Tuple
from concurrent.futures import ProcessPoolExecutor, as_completed

from fetch_yuntin_audio_json import YuntinAudioAnalyzer
from download_raw_audio import download_from_json, get_audio_filename
from audio2txt2comic.whisper_example import simple_transcribe


def ensure_dir_exists(directory_path: str) -> None:
    if directory_path:
        os.makedirs(directory_path, exist_ok=True)


def build_output_json_path(dates: List[str], program: str) -> str:
    ensure_dir_exists("audio_output")
    if len(dates) == 1:
        return f"audio_output/{dates[0]}_{program}.json"
    return f"audio_output/{dates[-1]}-{dates[0]}_{program}.json"


def extract_keywords_and_summary(text: str, top_k: int = 10, summary_sentences: int = 5) -> Dict[str, Any]:
    """
    轻量中文关键词与摘要提取（无第三方依赖）
    - 关键词：基于频次统计长度>=2的中文词片段，过滤常见停用词
    - 摘要：按关键词命中数与句长简单打分，取分数最高的若干句，按原顺序输出
    """
    if not text:
        return {"keywords": [], "summary": []}

    import re

    # 粗分句
    sentence_delimiter = re.compile(r"[。！？!.?\n]+")
    sentences = [s.strip() for s in sentence_delimiter.split(text) if s.strip()]

    # 抽词（中文连续 >=2 字；也保留长度>=2的英文/数字串）
    word_pattern = re.compile(r"[\u4e00-\u9fa5]{2,}|[A-Za-z0-9_]{2,}")
    stopwords = {
        "我们", "你们", "他们", "以及", "因为", "所以", "如果", "但是", "就是", "这个", "那个",
        "然后", "而且", "其实", "可能", "还是", "一些", "这种", "这些", "那些", "一个",
        "可以", "不会", "不是", "没有", "进行", "方面", "情况", "通过", "关于", "需要",
    }

    freq: Dict[str, int] = {}
    for match in word_pattern.finditer(text):
        w = match.group(0)
        if w in stopwords:
            continue
        freq[w] = freq.get(w, 0) + 1

    # 关键词Top-K
    sorted_words: List[Tuple[str, int]] = sorted(freq.items(), key=lambda x: (-x[1], -len(x[0]), x[0]))
    keywords: List[str] = [w for w, _ in sorted_words[:top_k]]

    # 句子打分：关键词命中数*2 + 句长归一化
    keyword_set = set(keywords)
    def score_sentence(s: str) -> float:
        tokens = word_pattern.findall(s)
        hits = sum(1 for t in tokens if t in keyword_set)
        return hits * 2.0 + min(len(s) / 40.0, 1.0)

    scored: List[Tuple[int, float, str]] = []
    for idx, s in enumerate(sentences):
        if len(s) < 6:
            continue
        scored.append((idx, score_sentence(s), s))

    # 取Top-N并按原顺序排序
    top = sorted(sorted(scored, key=lambda x: x[1], reverse=True)[:summary_sentences], key=lambda x: x[0])
    summary = [s for _, _, s in top]

    return {"keywords": keywords, "summary": summary}


def load_audio_items_from_json(json_path: str) -> List[Dict[str, Any]]:
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"读取JSON失败: {e}")
        return []

    items: List[Dict[str, Any]] = []
    for date, audio_list in data.items():
        for it in audio_list:
            items.append(it)
    return items


def _worker_transcribe(args: Tuple[Dict[str, Any], str, str]) -> Dict[str, Any]:
    item, quality, model_name = args
    from download_raw_audio import get_audio_filename
    from audio2txt2comic.whisper_example import simple_transcribe
    import os

    program_name = item.get("program_name")
    release_date = item.get("release_date")
    if not program_name or not release_date:
        return {}

    filename = get_audio_filename(program_name, release_date, quality)
    audio_path = os.path.join("raw_audio", filename)
    if not os.path.exists(audio_path):
        return {}

    whisper_result = simple_transcribe(audio_path, model_name=model_name)
    text: str = whisper_result.get("text", "")

    # 轻量提炼（重复实现以避免子进程依赖父进程闭包）
    import re, json as _json
    sentence_delimiter = re.compile(r"[。！？!.?\n]+")
    sentences = [s.strip() for s in sentence_delimiter.split(text) if s.strip()]
    word_pattern = re.compile(r"[\u4e00-\u9fa5]{2,}|[A-Za-z0-9_]{2,}")
    stopwords = {"我们","你们","他们","以及","因为","所以","如果","但是","就是","这个","那个","然后","而且","其实","可能","还是","一些","这种","这些","那些","一个","可以","不会","不是","没有","进行","方面","情况","通过","关于","需要"}
    freq: Dict[str, int] = {}
    for m in word_pattern.finditer(text):
        w = m.group(0)
        if w in stopwords:
            continue
        freq[w] = freq.get(w, 0) + 1
    sorted_words = sorted(freq.items(), key=lambda x: (-x[1], -len(x[0]), x[0]))
    keywords = [w for w, _ in sorted_words[:10]]
    keyword_set = set(keywords)
    def _score(s: str) -> float:
        tokens = word_pattern.findall(s)
        hits = sum(1 for t in tokens if t in keyword_set)
        return hits * 2.0 + min(len(s) / 40.0, 1.0)
    scored = [(idx, _score(s), s) for idx, s in enumerate(sentences) if len(s) >= 6]
    top = sorted(sorted(scored, key=lambda x: x[1], reverse=True)[:5], key=lambda x: x[0])
    summary = [s for _, _, s in top]

    return {
        "id": item.get("id"),
        "program_name": program_name,
        "release_date": release_date,
        "audio_path": audio_path,
        "transcript_text": text,
        "keywords": keywords,
        "summary": summary,
    }


def transcribe_and_extract(items: List[Dict[str, Any]], quality: str = "high", limit: int = 0, model_name: str = "tiny", max_workers: int = 2) -> List[Dict[str, Any]]:
    """
    对已下载音频按既定命名规则做转写与提炼。
    limit>0 时仅处理前 limit 条。
    """
    results: List[Dict[str, Any]] = []
    tasks: List[Tuple[Dict[str, Any], str, str]] = []
    count = 0
    for it in items:
        if limit > 0 and count >= limit:
            break
        tasks.append((it, quality, model_name))
        count += 1

    if not tasks:
        return results

    print(f"并发转写开始: {len(tasks)} 个任务, workers={max_workers}, model={model_name}")
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(_worker_transcribe, t) for t in tasks]
        for fut in as_completed(futures):
            try:
                res = fut.result()
                if res:
                    results.append(res)
            except Exception as e:
                print(f"子进程任务失败: {e}")

    # 按日期、节目名排序，稳定输出
    results.sort(key=lambda x: (x.get("release_date", ""), x.get("program_name", "")))
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="云听全流程流水线：JSON→音频→转写→提炼")
    parser.add_argument("--days", type=int, default=1, help="最近N天（从昨天起向前N天），默认1")
    parser.add_argument("--program", type=str, default="全部", choices=["那些年", "财经阅读", "全部"], help="节目类型，默认全部")
    parser.add_argument("--quality", type=str, default="high", choices=["high", "low"], help="下载与转写所用音质，默认high")
    parser.add_argument("--force", action="store_true", help="强制更新获取JSON，忽略缓存")
    parser.add_argument("--limit", type=int, default=0, help="最多处理多少条音频，0为不限制")
    parser.add_argument("--whisper-model", type=str, default="tiny", choices=["tiny", "base", "small", "medium", "large"], help="Whisper模型，默认tiny")
    parser.add_argument("--workers", type=int, default=2, help="并发进程数，默认2")

    args = parser.parse_args()

    analyzer = YuntinAudioAnalyzer()
    dates = analyzer.generate_date_list(args.days)
    json_output_path = build_output_json_path(dates, args.program)

    print(f"步骤1/4 获取JSON → {json_output_path}")
    analyzer.run_analysis(dates, json_output_path, args.program, args.force)

    print("步骤2/4 下载音频到 raw_audio/")
    download_from_json(json_output_path, args.quality)

    print("步骤3/4 Whisper转写")
    audio_items = load_audio_items_from_json(json_output_path)
    transcribed = transcribe_and_extract(audio_items, args.quality, args.limit, model_name=args.whisper_model, max_workers=args.workers)

    print("步骤4/4 核心提炼与保存")
    ensure_dir_exists("mindmap_output")
    if len(dates) == 1:
        result_path = f"mindmap_output/{dates[0]}_{args.program}_transcribe_core.json"
    else:
        result_path = f"mindmap_output/{dates[-1]}-{dates[0]}_{args.program}_transcribe_core.json"

    with open(result_path, "w", encoding="utf-8") as f:
        json.dump({"items": transcribed}, f, ensure_ascii=False, indent=2)
    print(f"已保存提炼结果: {result_path}")


if __name__ == "__main__":
    main()


