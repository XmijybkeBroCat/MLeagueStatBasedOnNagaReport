### 简介：
用于从Naga报告中获取对局数据，并统计位次、PT、和牌率等信息。适合基于MLeague规则并使用Naga分析所有对局的立直麻将联赛。

### 运行环境：
Python 3.14，安装第三方库openpyxl, requests。没有在更低Python版本上尝试过。

### 使用方法：
完成对局并进行Naga分析后，使用`get_naga.py:fetch_naga_report_data(url: str, filename: str, origin: list[int], similarity: list[float])`从Naga报告中获取对局信息，并以json格式存储到本地。

需要获取统计信息时，使用`analyze.py:main(paipu_dir: str, filename: str)`统计指定路径中存储的所有对局信息，并将统计数据输出到Excel文件中。

### 更新日志
2026.6.25
 - 添加了队伍信息
 - 修改了触发除零错误的文本显示（-1 -> N / A）
 - 添加了常规赛前6场的数据(r1-r6)，及目前统计结果`Regular.xlsx`
