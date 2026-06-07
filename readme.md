### 简介：
用于从Naga报告中获取对局数据，并统计位次、PT、和牌率等信息。适合基于MLeague规则并使用Naga分析所有对局的立直麻将联赛。

### 运行环境：
Python 3.14，安装第三方库openpyxl, requests。没有在更低Python版本上尝试过。

### 使用方法：
完成对局并进行Naga分析后，使用`get_naga.py:fetch_naga_report_data(url: str, filename: str')`从Naga报告中获取对局信息，并以json格式存储到本地。

需要获取统计信息时，使用`analyze.py:main(paipu_dir: str, filename: str)`统计指定路径中存储的所有对局信息，并将统计数据输出到Excel文件中。

提供了包含两份对局信息的路径`./test`以供测试，它的统计结果见`test.xlsx`。

### 已知bug：
程序统计的素点、PT均不正确，根本原因在于Naga报告中的持点不正确（引擎不接受负数持点，会强行修正为1000并调整其他家的点数），程序统计的素点是自行计算的，但不知道立直是否放铳燕返，因此为每一个立直都扣了立直棒。流局完场多余的立直棒也没有回收，最终点数总和低于十万点。