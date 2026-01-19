#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
重要声明 / IMPORTANT DISCLAIMER
================================================================================

本程序仅供学习和娱乐使用，不能提高中奖概率。

原因：
1. 彩票开奖是独立随机事件，每次开奖不受历史结果影响
2. "频次低回补"是典型的赌徒谬误，数学上不成立
3. 历史数据只反映过去，不能预测未来

本程序的价值：
- 让选号过程更有趣
- 提供"策略感"供讨论和娱乐
- 不是赚钱工具，请理性购彩

================================================================================

双色球预测主程序

功能流程：
1. 获取最新彩票数据
2. 分析球号频次
3. 生成两种预测结果
4. 保存预测结果到文件

使用方法：
    python lottery_prediction.py        # 日常更新
    python lottery_prediction.py --all  # 获取所有历史数据
"""

import sys
import os
from datetime import datetime

# 确保导入路径正确
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_fetcher import DataFetcher
from analyzer import FrequencyAnalyzer, LotteryPredictor


def save_prediction_to_file(results: Dict, filename: str = "prediction_result.txt"):
    """
    保存预测结果到文件

    格式：红球：xxx；蓝球xxx

    Args:
        results: 包含预测结果的字典
        filename: 保存的文件名
    """
    # 获取文件所在目录
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

    try:
        with open(file_path, 'a', encoding='utf-8') as f:
            # 写入时间
            f.write(f"预测时间: {results['time']}\n")
            f.write("-" * 40 + "\n")

            # 方式一
            f.write("方式一 - 全局数据分析预测:\n")
            f.write(f"红球：{results['method1']['red_balls']}；蓝球{results['method1']['blue_ball']}\n")

            # 方式二
            f.write("方式二 - 近期加权预测:\n")
            f.write(f"红球：{results['method2']['red_balls']}；蓝球{results['method2']['blue_ball']}\n")

            f.write("=" * 40 + "\n\n")

        print(f"\n预测结果已保存到: {file_path}")
        return True
    except Exception as e:
        print(f"\n保存预测结果失败: {e}")
        return False


def main(fetch_all: bool = False):
    """
    主函数

    Args:
        fetch_all: 是否获取所有历史数据
    """
    print("=" * 50)
    print("双色球数据管理与频次分析系统")
    print("=" * 50)

    # ========== 第一步：获取数据 ==========
    print("\n【步骤1】检查并更新数据...")

    # 创建数据获取器
    fetcher = DataFetcher()

    if fetch_all:
        # 获取所有历史数据
        print("\n【模式】获取所有历史数据...")
        count = fetcher.fetch_and_save_all()
        print(f"\n已获取 {count} 条历史数据")
    else:
        # 日常增量更新
        new_count = fetcher.update()
        print(f"新增 {new_count} 条数据")

    # 加载数据
    data = fetcher.load()
    print(f"已加载 {len(data)} 条历史数据")

    # ========== 第二步：分析频次 ==========
    print("\n【步骤2】分析球号频次...")

    # 创建频次分析器并分析
    analyzer = FrequencyAnalyzer()
    analyzer.data = data
    analyzer.print_report()

    # ========== 第三步：生成预测 ==========
    print("\n【步骤3】生成预测号码...")

    # 创建预测器
    predictor = LotteryPredictor("智能预测器")

    # 方式一：全局数据分析预测（基于全部历史数据的频次）
    result1 = predictor.predict(data)
    print(f"\n方式一 - 全局数据分析预测:")
    print(f"  红球 {result1['red_balls']} | 蓝球 {result1['blue_ball']}")

    # 方式二：近期加权预测（近160期）
    result2 = predictor.predict_by_recent_data(data)
    print(f"\n方式二 - 近期加权预测（近{LotteryPredictor.RECENT_COUNT}期）:")
    print(f"  红球 {result2['red_balls']} | 蓝球 {result2['blue_ball']}")

    # ========== 第四步：保存预测结果 ==========
    print("\n【步骤4】保存预测结果...")

    # 整理预测结果
    prediction_results = {
        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'method1': result1,
        'method2': result2
    }

    # 保存到文件
    save_prediction_to_file(prediction_results)

    print("\n" + "=" * 50)
    print("程序运行完成")
    print("=" * 50)


if __name__ == "__main__":
    # 如果带参数 --all，则获取所有历史数据
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        main(fetch_all=True)
    else:
        main()
