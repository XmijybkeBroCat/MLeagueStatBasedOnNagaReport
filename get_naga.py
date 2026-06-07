import re
import sys

import requests
import json

def fetch_naga_report_data(naga_url: str, filename: str) -> None:
    """
    从 NAGA 报告链接中获取对局数据（JSON格式）并输出。
    示例链接: https://naga.dmv.nico/htmls/report_viewer.html?report_id=a97fd874793c780ecda0efd80df9f4a151e92ca750351705f698779afeb633d4v2_2&tw=0
    """
    # 1. 从 URL 中提取 report_id
    match = re.search(r'report_id=([^&]+)', naga_url)
    if not match:
        print("错误：无法提取 report_id")
        return
    report_id = match.group(1)
    print(f"提取到 report_id: {report_id}")

    # 2. 构造数据接口 URL（经过测试，这是 NAGA 实际使用的接口）
    report_url = f"https://naga.dmv.nico/reports/{report_id}.json.gz"
    print(f"数据接口: {report_url}")

    # 3. 发送请求（模拟浏览器头）
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": naga_url,  # 重要：有些接口会检查 Referer
    }
    try:
        resp = requests.get(report_url, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        output = {'Players': data['player_info']['name'], 'Frames': data['custom_haihu']}
        # 输出 JSON 数据（格式化）
        json.dump(output, open(f'test/{filename}.json', 'w', encoding='UTF-8'), ensure_ascii=False, indent=2)
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
    except json.JSONDecodeError:
        print("返回内容不是合法 JSON，可能是接口变动。")
        print("原始响应:", resp.text[:500])

# 使用示例
if __name__ == "__main__":
    test_url = "https://naga.dmv.nico/htmls/report_viewer.html?report_id=568c9a2ccf26eb2a1f0bd73344ccfad91162c160a914c13f016f700cbe2a5914v2_2&tw=0"
    fetch_naga_report_data(test_url, 'e3')