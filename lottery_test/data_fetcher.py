#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""数据获取层 - 从网站 API 获取彩票数据并保存"""

import random
import urllib.request
import json
from datetime import datetime
from typing import List, Dict, Optional
import os


class DataFetcher:
    """数据获取器 - 负责从网站获取数据并保存"""

    def __init__(self, csv_path: str = "lottery_data.csv"):
        self.csv_path = csv_path

    def init_data_file(self):
        """初始化数据文件"""
        if os.path.exists(self.csv_path):
            return
        with open(self.csv_path, 'w', encoding='utf-8-sig') as f:
            f.write("期号,红球1,红球2,红球3,红球4,红球5,红球6,蓝球,开奖日期\n")
        print(f"已创建数据文件: {self.csv_path}")

    def fetch_latest(self, page_size: int = 50) -> List[Dict]:
        """从 API 接口获取最新开奖数据"""
        import time

        ts = str(int(time.time() * 1000))
        tt = str(time.time() + random.random())

        url = (f"https://jc.zhcw.com/port/client_json.php?"
               f"callback=jQuery112201817299721784883_{ts}"
               f"&transactionType=10001001&lotteryId=1"
               f"&issueCount={page_size}&startIssue=&endIssue="
               f"&startDate=&endDate=&type=0&pageNum=1"
               f"&pageSize={page_size}&tt={tt}&_={ts}")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.zhcw.com/'
        }

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                content = response.read().decode('utf-8')
                return self._parse_response(content)
        except Exception as e:
            print(f"API 请求失败: {e}")
            return []

    def fetch_all(self) -> List[Dict]:
        """获取所有历史数据"""
        import time

        print("正在获取所有历史数据...")

        ts = str(int(time.time() * 1000))
        tt = str(time.time() + random.random())

        url = (f"https://jc.zhcw.com/port/client_json.php?"
               f"callback=jQuery112201817299721784883_{ts}"
               f"&transactionType=10001001&lotteryId=1"
               f"&issueCount=10000&startIssue=&endIssue="
               f"&startDate=&endDate=&type=0&pageNum=1"
               f"&pageSize=10000&tt={tt}&_={ts}")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.zhcw.com/'
        }

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=60) as response:
                content = response.read().decode('utf-8')
                all_data = self._parse_response(content)

                if all_data:
                    first_issue = all_data[-1]['issue']
                    last_issue = all_data[0]['issue']
                    print(f"获取成功! 共 {len(all_data)} 条数据, 期号范围: {first_issue} - {last_issue}")

                return all_data
        except Exception as e:
            print(f"获取失败: {e}")
            return []

    def _parse_response(self, content: str) -> List[Dict]:
        """解析 API 响应"""
        try:
            if content.startswith('jQuery'):
                start = content.find('(') + 1
                end = content.rfind(')')
                content = content[start:end]

            data = json.loads(content)
            items = data.get('data', [])

            result = []
            for item in items:
                red_nums = item.get('frontWinningNum', '').split()
                blue_num = item.get('backWinningNum', '')

                result.append({
                    'issue': item.get('issue', ''),
                    'red_balls': [int(x) for x in red_nums],
                    'blue_ball': int(blue_num) if blue_num else 0,
                    'date': item.get('openTime', '')
                })

            print(f"API 返回 {len(result)} 条数据")
            return result
        except Exception as e:
            print(f"解析失败: {e}")
            return []

    def update(self) -> int:
        """更新数据到本地文件，返回新增条数"""
        self.init_data_file()

        # 获取本地已有的所有期号
        local_issues = set()
        try:
            with open(self.csv_path, 'r', encoding='utf-8-sig') as f:
                for line in f.readlines()[1:]:
                    parts = line.strip().split(',')
                    if parts[0]:
                        local_issues.add(parts[0])
        except FileNotFoundError:
            pass

        print(f"本地已有 {len(local_issues)} 条数据")

        web_data = self.fetch_latest(page_size=50)

        if not web_data:
            print("API 获取失败")
            return 0

        # 过滤：只保留本地没有的期号
        new_data = [item for item in web_data if item['issue'] not in local_issues]

        if new_data:
            print(f"发现 {len(new_data)} 条新数据")
            self.save(new_data)
        else:
            print("数据已是最新")

        return len(new_data)

    def fetch_and_save_all(self) -> int:
        """获取并保存所有历史数据"""
        self.init_data_file()

        # 清空旧数据
        with open(self.csv_path, 'w', encoding='utf-8-sig') as f:
            f.write("期号,红球1,红球2,红球3,红球4,红球5,红球6,蓝球,开奖日期\n")

        all_data = self.fetch_all()

        if all_data:
            self.save(all_data)
            print(f"已保存 {len(all_data)} 条数据")
        else:
            print("未获取到任何数据")

        return len(all_data)

    def save(self, data: List[Dict]):
        """保存数据到 CSV"""
        with open(self.csv_path, 'a', encoding='utf-8-sig') as f:
            for item in data:
                red = ','.join(map(str, item['red_balls']))
                line = f"{item['issue']},{red},{item['blue_ball']},{item['date']}\n"
                f.write(line)

    def load(self) -> List[Dict]:
        """从 CSV 加载数据"""
        data = []
        try:
            with open(self.csv_path, 'r', encoding='utf-8-sig') as f:
                for line in f.readlines()[1:]:  # 跳过表头
                    parts = line.strip().split(',')
                    if len(parts) >= 9:
                        data.append({
                            'issue': parts[0],
                            'red_balls': [int(parts[1]), int(parts[2]), int(parts[3]),
                                         int(parts[4]), int(parts[5]), int(parts[6])],
                            'blue_ball': int(parts[7]),
                            'date': parts[8]
                        })
        except FileNotFoundError:
            print(f"数据文件不存在: {self.csv_path}")
        return data

    def get_local_latest_issue(self) -> Optional[str]:
        """获取本地最新期号"""
        try:
            with open(self.csv_path, 'r', encoding='utf-8-sig') as f:
                lines = f.readlines()
                if len(lines) > 1:
                    return lines[-1].strip().split(',')[0]
        except FileNotFoundError:
            pass
        return None

    def generate_mock_data(self, count: int = 3) -> List[Dict]:
        """生成模拟数据（用于测试）"""
        mock_data = []
        base_issue = 2026001
        for i in range(count):
            issue = str(base_issue + i)
            red_balls = sorted(random.sample(range(1, 34), 6))
            blue_ball = random.randint(1, 16)
            date = datetime.now().strftime("%Y-%m-%d")

            mock_data.append({
                'issue': issue,
                'red_balls': red_balls,
                'blue_ball': blue_ball,
                'date': date
            })
        return mock_data
