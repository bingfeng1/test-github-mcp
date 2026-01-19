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

分析测试层 - 负责数据分析、频次统计和预测

本模块包含三个主要类：
1. FrequencyAnalyzer - 频次分析器（分析历史数据中各球号出现次数）
2. WeightedFrequencyAnalyzer - 加权频次分析器（近期数据权重更高）
3. LotteryPredictor - 彩票预测器（生成预测号码）

双色球基本知识：
- 红球：从 1-33 中选 6 个（不重复）
- 蓝球：从 1-16 中选 1 个
"""

import random
from datetime import datetime
from typing import List, Dict, Optional


# =============================================================================
# 第一部分：FrequencyAnalyzer - 频次分析器
# =============================================================================

class FrequencyAnalyzer:
    """
    频次分析器

    功能：统计历史数据中，每个球号出现了多少次

    使用示例：
        analyzer = FrequencyAnalyzer(data)           # 创建传入数据分析器，
        result = analyzer.analyze()                   # 开始分析
        min_info = analyzer.get_min_frequency()       # 获取最小频次
        analyzer.print_report()                       # 打印分析报告
    """

    def __init__(self, data: List[Dict] = None):
        """
        初始化频次分析器

        Args:
            data: 历史彩票数据列表，每条数据包含：
                - issue: 期号
                - red_balls: 红球列表（6个数字）
                - blue_ball: 蓝球数字
                - date: 开奖日期
        """
        # data 参数可以有默认值 None，这样创建对象时可以不带参数
        self.data = data if data is not None else []

    def load_from_fetcher(self, fetcher):
        """
        从 DataFetcher 加载数据

        这是另一种获取数据的方式，传入一个 DataFetcher 对象

        Args:
            fetcher: DataFetcher 对象，它有 load() 方法可以返回数据
        """
        self.data = fetcher.load()

    def analyze(self) -> Dict:
        """
        分析球号出现频次

        核心算法：
        1. 创建两个字典，分别统计红球和蓝球的频次
        2. 遍历所有历史数据
        3. 统计每个红球和蓝球出现的次数

        Returns:
            Dict: 包含以下内容
                - red: 红球频次字典 {球号: 出现次数}
                - blue: 蓝球频次字典 {球号: 出现次数}
                - total_records: 数据总条数
        """
        # 如果没有数据，返回空结果
        if not self.data:
            return {'red': {}, 'blue': {}, 'total_records': 0}

        # 初始化频次字典
        # range(1, 34) 生成 1 到 33 的数字
        red_frequency = {i: 0 for i in range(1, 34)}
        blue_frequency = {i: 0 for i in range(1, 17)}

        # 遍历每一条历史数据
        for item in self.data:
            # 遍历该期的 6 个红球
            for ball in item['red_balls']:
                # 如果球号在字典中，计数加 1
                if ball in red_frequency:
                    red_frequency[ball] += 1

            # 蓝球只有一个，直接计数
            blue_frequency[item['blue_ball']] += 1

        # 返回统计结果
        return {
            'red': red_frequency,
            'blue': blue_frequency,
            'total_records': len(self.data)
        }

    def get_min_frequency(self) -> Dict:
        """
        获取最小频次的球号

        功能：找出哪些球号出现次数最少

        Returns:
            Dict: 包含
                - red: 红球最小频次信息 {'balls': [球号列表], 'frequency': 次数}
                - blue: 蓝球最小频次信息
                - total_records: 数据总条数
        """
        # 先获取频次统计
        freq = self.analyze()

        # 找出红球的最小频次值
        # min() 函数找出字典中的最小值
        min_red_freq = min(freq['red'].values()) if freq['red'] else 0
        # 找出所有等于最小频次的球号
        min_red_balls = [k for k, v in freq['red'].items() if v == min_red_freq]

        # 同理处理蓝球
        min_blue_freq = min(freq['blue'].values()) if freq['blue'] else 0
        min_blue_balls = [k for k, v in freq['blue'].items() if v == min_blue_freq]

        return {
            'red': {'balls': min_red_balls, 'frequency': min_red_freq},
            'blue': {'balls': min_blue_balls, 'frequency': min_blue_freq},
            'total_records': freq['total_records']
        }

    def print_report(self):
        """
        打印频次分析报告

        将分析结果以易读的格式打印到控制台
        """
        # 先进行分析
        freq = self.analyze()
        min_info = self.get_min_frequency()

        print("\n" + "=" * 50)
        print("彩票频次分析报告")
        print("=" * 50)
        print(f"数据记录数: {freq['total_records']}")
        print()

        print("【红球最小频次】")
        print(f"  频次: {min_info['red']['frequency']}")
        print(f"  球号: {sorted(min_info['red']['balls'])}")
        print()

        print("【蓝球最小频次】")
        print(f"  频次: {min_info['blue']['frequency']}")
        print(f"  球号: {sorted(min_info['blue']['balls'])}")
        print()

        print("【红球频次分布（前10）】")
        # sorted() 排序，key=lambda x: x[1] 表示按值排序
        sorted_red = sorted(freq['red'].items(), key=lambda x: x[1])[:10]
        for ball, count in sorted_red:
            # :2d 表示占2位宽度，不足补空格
            print(f"  球号 {ball:2d}: {count} 次")
        print()

        print("【蓝球频次分布】")
        sorted_blue = sorted(freq['blue'].items(), key=lambda x: x[1])
        for ball, count in sorted_blue:
            print(f"  球号 {ball:2d}: {count} 次")
        print("=" * 50)


# =============================================================================
# 第二部分：WeightedFrequencyAnalyzer - 加权频次分析器
# =============================================================================

class WeightedFrequencyAnalyzer:
    """
    加权频次分析器 - 用于方法二

    方法二逻辑：
    1. 先计算全部历史数据的频次（基础）
    2. 再用近160期数据加权（近期权重=3倍）

    这样做的好处：
    - 既考虑了整体趋势（全部数据）
    - 又重视近期走势（近160期×3倍）

    与方法一的区别：
    - 方法一：只看全部历史数据的频次
    - 方法二：全部历史 + 近160期加权
    """

    def __init__(self, data: List[Dict] = None, recent_weight: float = 3.0,
                 name: str = "加权分析器"):
        """
        初始化加权频次分析器

        Args:
            data: 历史数据列表
            recent_weight: 近期数据的权重倍数（默认3倍）
            name: 分析器名称
        """
        self.data = data if data is not None else []
        self.recent_weight = recent_weight
        self.name = name
        self.prediction_history = []

    def get_recent_data(self, count: int) -> List[Dict]:
        """
        获取最近的 N 条数据

        列表切片语法：[-count:] 表示取最后 count 条

        Args:
            count: 要获取的数据条数

        Returns:
            最近 count 条数据的列表
        """
        # 如果要求的数据量大于实际数据量，返回全部数据
        return self.data[-count:] if count <= len(self.data) else self.data

    def analyze_weighted(self, recent_count: int = 160) -> Dict:
        """
        加权分析 - 方法二的实现逻辑

        步骤：
        1. 先计算全部历史数据的频次作为基础（早期数据权重=1）
        2. 再用近 N 期数据进行加权（近期权重=3）

        例如：
        - 某个红球在历史数据中出现 100 次（前 3900 期）
        - 最近 160 期中出现 10 次
        - 加权频次 = 100 × 1 + 10 × 3 = 130

        Args:
            recent_count: 近期数据条数（默认 160 = 蓝球16种 × 10）

        Returns:
            加权后的频次统计
        """
        if not self.data:
            return {'red': {}, 'blue': {}, 'total_records': 0, 'recent_count': 0}

        # 初始化频次字典
        red_frequency = {i: 0 for i in range(1, 34)}
        blue_frequency = {i: 0 for i in range(1, 17)}

        # 获取近期数据
        recent_data = self.get_recent_data(recent_count)
        recent_count = len(recent_data)  # 实际获取到的数量

        # 计算早期数据范围
        # data[:-recent_count] 表示排除最后 recent_count 条
        early_data = self.data[:-recent_count] if recent_count > 0 else []

        # 统计早期数据（权重 = 1）
        for item in early_data:
            for ball in item['red_balls']:
                if ball in red_frequency:
                    red_frequency[ball] += 1
            blue_frequency[item['blue_ball']] += 1

        # 统计近期数据（权重 = recent_weight）
        for item in recent_data:
            for ball in item['red_balls']:
                if ball in red_frequency:
                    # 每出现一次，计数增加权重值
                    red_frequency[ball] += self.recent_weight
            blue_frequency[item['blue_ball']] += self.recent_weight

        return {
            'red': red_frequency,
            'blue': blue_frequency,
            'total_records': len(self.data),
            'recent_count': recent_count
        }

    def predict_by_weighted_frequency(self, red_count: int = 6,
                                       red_max: int = 33,
                                       blue_max: int = 16,
                                       recent_count: int = 160) -> Dict:
        """
        基于加权频次生成预测

        核心思想：频次越低，回补概率越高

        算法步骤：
        1. 进行加权频次统计
        2. 计算每个球的权重 = 最大频次 - 当前频次 + 1
           （频次越低，权重越高）
        3. 基于权重随机选择

        Args:
            red_count: 红球数量（6个）
            red_max: 红球最大值（33）
            blue_max: 蓝球最大值（16）
            recent_count: 近期数据条数

        Returns:
            预测结果字典
        """
        if not self.data:
            # 没有数据时使用随机预测
            return self.predict(red_count, red_max, blue_max)

        # 步骤1：加权分析
        weighted_freq = self.analyze_weighted(recent_count)

        # 步骤2：计算权重（频次越低，权重越高）
        red_weights = {}
        blue_weights = {}

        # 找出最大频次
        max_red_freq = max(weighted_freq['red'].values()) if weighted_freq['red'] else 1
        max_blue_freq = max(weighted_freq['blue'].values()) if weighted_freq['blue'] else 1

        # 计算每个球的权重
        # 例如：最大频次是 100，某球频次是 80，则权重 = 100 - 80 + 1 = 21
        for ball in range(1, red_max + 1):
            freq = weighted_freq['red'].get(ball, 0)
            red_weights[ball] = max_red_freq - freq + 1

        for ball in range(1, blue_max + 1):
            freq = weighted_freq['blue'].get(ball, 0)
            blue_weights[ball] = max_blue_freq - freq + 1

        # 步骤3：基于权重随机选择
        red_balls = self._weighted_sample(red_weights, red_count, red_max)
        blue_ball = self._weighted_sample_one(blue_weights, blue_max)

        prediction = {
            "red_balls": red_balls,
            "blue_ball": blue_ball,
            "timestamp": datetime.now().isoformat(),
            "predictor": f"{self.name}-加权预测",
            "method": "weighted_frequency",
            "recent_count": recent_count
        }

        self.prediction_history.append(prediction)
        return prediction

    def _weighted_sample(self, weights: Dict, count: int, max_val: int) -> List[int]:
        """
        加权随机选择（不重复）

        算法：轮盘赌选择法
        1. 计算所有权重总和
        2. 随机生成一个 0 到总和之间的数
        3. 依次累加权重，找到第一个超过随机数的选项

        Args:
            weights: 权重字典 {球号: 权重}
            count: 要选几个
            max_val: 球号最大值

        Returns:
            选中的球号列表（已排序）
        """
        # 可选球号列表
        available = list(range(1, max_val + 1))
        selected = []

        # 重复选择 count 次
        for _ in range(count):
            # 计算总权重
            total_weight = sum(weights.get(i, 1) for i in available)
            # 随机生成一个数
            r = random.uniform(0, total_weight)

            # 累加权重，找到目标
            cumsum = 0
            for i in available:
                cumsum += weights.get(i, 1)
                if cumsum >= r:
                    # 选中了这个球
                    selected.append(i)
                    # 从可选列表中移除，避免重复
                    available.remove(i)
                    break

        return sorted(selected)

    def _weighted_sample_one(self, weights: Dict, max_val: int) -> int:
        """加权随机选择一个"""
        total_weight = sum(weights.get(i, 1) for i in range(1, max_val + 1))
        r = random.uniform(0, total_weight)

        cumsum = 0
        for i in range(1, max_val + 1):
            cumsum += weights.get(i, 1)
            if cumsum >= r:
                return i
        return 1

    def print_weighted_report(self, recent_count: int = 160):
        """打印加权分析报告"""
        weighted_freq = self.analyze_weighted(recent_count)

        print("\n" + "=" * 50)
        print(f"加权频次分析报告（近期{recent_count}期权重更高）")
        print("=" * 50)
        print(f"总记录数: {weighted_freq['total_records']}")
        print(f"近期数据: {weighted_freq['recent_count']} 条")
        print(f"权重倍数: {self.recent_weight}x")
        print()

        print("【红球加权频次（频次越低=权重越高）】")
        sorted_red = sorted(weighted_freq['red'].items(),
                           key=lambda x: x[1])[:10]
        for ball, count in sorted_red:
            print(f"  球号 {ball:2d}: 加权值 {count:.1f}")
        print()

        print("【蓝球加权频次】")
        sorted_blue = sorted(weighted_freq['blue'].items(),
                            key=lambda x: x[1])
        for ball, count in sorted_blue:
            print(f"  球号 {ball:2d}: 加权值 {count:.1f}")
        print("=" * 50)

    def predict(self, red_count: int = 6, red_max: int = 33,
                blue_max: int = 16) -> Dict:
        """随机预测（备用方法）"""
        red_balls = sorted(random.sample(range(1, red_max + 1), red_count))
        blue_ball = random.randint(1, blue_max)

        return {
            "red_balls": red_balls,
            "blue_ball": blue_ball,
            "timestamp": datetime.now().isoformat(),
            "predictor": self.name
        }


# =============================================================================
# 第三部分：LotteryPredictor - 彩票预测器
# =============================================================================

class LotteryPredictor:
    """
    彩票预测器

    提供两种预测方式：
    1. predict() - 全局随机预测
    2. predict_by_recent_data() - 近期加权预测

    常量：
    - RECENT_COUNT = 160（蓝球种类16 * 10）
    """

    # 近期数据条数 = 蓝球种类 * 10 = 16 * 10 = 160
    RECENT_COUNT = 160

    def __init__(self, name: str = "默认预测器"):
        """
        初始化预测器

        Args:
            name: 预测器名称（用于标识预测来源）
        """
        self.name = name
        self.prediction_history = []

    def predict(self, data: List[Dict] = None, red_count: int = 6,
                red_max: int = 33, blue_max: int = 16) -> Dict:
        """
        方式一：全局数据分析预测

        基于全部历史数据进行分析，选取出现频次最低的球号。

        核心思想：
        - 统计所有历史数据中每个球号的出现次数
        - 频次越低的球号，"回补"概率越高
        - 基于逆向权重随机选择（频次越低越容易被选中）

        Args:
            data: 历史数据列表（可选，如果不传则随机选择）
            red_count: 红球数量（6个）
            red_max: 红球最大值（33）
            blue_max: 蓝球最大值（16）

        Returns:
            预测结果字典
        """
        # 如果没有数据，回退到随机选择
        if not data:
            red_balls = sorted(random.sample(range(1, red_max + 1), red_count))
            blue_ball = random.randint(1, blue_max)
        else:
            # 创建频次分析器
            analyzer = FrequencyAnalyzer(data)
            freq = analyzer.analyze()

            # 计算逆向权重：频次越低，权重越高
            # 权重 = 最大频次 - 当前频次 + 1
            max_red_freq = max(freq['red'].values())
            max_blue_freq = max(freq['blue'].values())

            red_weights = {i: max_red_freq - freq['red'].get(i, 0) + 1 for i in range(1, red_max + 1)}
            blue_weights = {i: max_blue_freq - freq['blue'].get(i, 0) + 1 for i in range(1, blue_max + 1)}

            # 使用加权选择
            red_balls = self._weighted_sample(red_weights, red_count, red_max)
            blue_ball = self._weighted_sample_one(blue_weights, blue_max)

        prediction = {
            "red_balls": red_balls,
            "blue_ball": blue_ball,
            "timestamp": datetime.now().isoformat(),
            "predictor": self.name,
            "method": "global_frequency"
        }

        self.prediction_history.append(prediction)
        return prediction

    def predict_by_recent_data(self, data: List[Dict],
                               red_count: int = 6,
                               red_max: int = 33,
                               blue_max: int = 16,
                               recent_count: int = None) -> Dict:
        """
        方式二：近期加权数据分析预测

        特点：基于近期数据分析，频次越低的球回补概率越高

        Args:
            data: 历史数据列表
            red_count: 红球数量（6个）
            red_max: 红球最大值（33）
            blue_max: 蓝球最大值（16）
            recent_count: 近期数据条数（默认160期）

        Returns:
            预测结果字典
        """
        if recent_count is None:
            recent_count = self.RECENT_COUNT

        # 创建加权分析器并生成预测
        analyzer = WeightedFrequencyAnalyzer(data, recent_weight=3.0)
        result = analyzer.predict_by_weighted_frequency(
            red_count=red_count,
            red_max=red_max,
            blue_max=blue_max,
            recent_count=recent_count
        )
        result["predictor"] = self.name

        self.prediction_history.append(result)
        return result

    def predict_both_methods(self, data: List[Dict],
                             red_count: int = 6,
                             red_max: int = 33,
                             blue_max: int = 16) -> Dict:
        """
        同时生成两种预测结果

        Returns:
            包含两种预测结果的字典
        """
        recent_count = self.RECENT_COUNT

        # 方式一：全局随机
        method1 = self.predict(red_count, red_max, blue_max)
        method1["method_name"] = "全局随机预测"

        # 方式二：近期加权
        method2 = self.predict_by_recent_data(
            data, red_count, red_max, blue_max, recent_count
        )
        method2["method_name"] = f"近期加权预测（近{recent_count}期）"

        return {
            "method1": method1,
            "method2": method2,
            "timestamp": datetime.now().isoformat()
        }

    def _weighted_sample(self, weights: Dict, count: int, max_val: int) -> List[int]:
        """加权随机选择（不重复）"""
        available = list(range(1, max_val + 1))
        selected = []

        for _ in range(count):
            total_weight = sum(weights.get(i, 1) for i in available)
            r = random.uniform(0, total_weight)

            cumsum = 0
            for i in available:
                cumsum += weights.get(i, 1)
                if cumsum >= r:
                    selected.append(i)
                    available.remove(i)
                    break

        return sorted(selected)

    def _weighted_sample_one(self, weights: Dict, max_val: int) -> int:
        """加权随机选择一个"""
        total_weight = sum(weights.get(i, 1) for i in range(1, max_val + 1))
        r = random.uniform(0, total_weight)

        cumsum = 0
        for i in range(1, max_val + 1):
            cumsum += weights.get(i, 1)
            if cumsum >= r:
                return i
        return 1

    def get_history(self) -> List[Dict]:
        """获取预测历史"""
        return self.prediction_history


# =============================================================================
# 第四部分：辅助函数
# =============================================================================

def run_analysis(data_fetcher, show_report: bool = True):
    """运行分析流程"""
    # 加载数据
    data = data_fetcher.load()
    print(f"已加载 {len(data)} 条历史数据")

    # 分析频次
    analyzer = FrequencyAnalyzer(data)
    if show_report:
        analyzer.print_report()

    return analyzer.analyze()


def generate_prediction():
    """生成预测"""
    predictor = LotteryPredictor("智能预测器")
    result = predictor.predict()
    print(f"预测号码: 红球 {result['red_balls']} | 蓝球 {result['blue_ball']}")
    return result
