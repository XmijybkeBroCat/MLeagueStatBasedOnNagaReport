from json import load, loads
from openpyxl import Workbook
from os import listdir
from re import search


class PlayerGameData:
    n1 = 4  # Number 1
    t1 = ['顺位', 'PT', '素点', 'Naga nishiki 类似度' ]  # Title 1
    n2 = 11
    t2 = ['总局数', '和牌局数', '放铳局数', '自摸局数', '默和局数', '立直局数', '副露局数', '和牌得点', '放铳失点', '流局局数', '流听局数']
    #      0        1         2          3         4         5         6          7         8         9          10

    def __init__(self, frame: int):
        self.point = 0
        self.d1 = []
        self.d2 = [0 for _ in range(self.n2)]
        self.d2[0] = frame


class PlayerData:
    n1 = 8
    t1 = ['总场数', '总PT', '总素点', '总Naga nishiki 类似度', '一位数', '二位数', '三位数', '四位数']
    #      0        1      2        3                       4       5        6        7
    n2 = 11
    t2 = ['总局数', '和牌局数', '放铳局数', '自摸局数', '默和局数', '立直局数', '副露局数', '和牌得点', '放铳失点', '流局局数', '流听局数']
    #      0        1         2          3         4         5         6          7         8         9          10

    def __init__(self, name: str):
        self.name = name
        self.max_point = -99999
        self.d1 = [0 for _ in range(self.n1)]
        self.d2 = [0 for _ in range(self.n2)]

    def add_game(self, game: PlayerGameData):
        self.max_point = max(self.max_point, game.point)
        self.d1[0] += 1
        for i in range(1, 4):
            self.d1[i] += game.d1[i]
        self.d1[game.d1[0] + 3] += 1
        self.d2 = [self.d2[i] + game.d2[i] for i in range(self.n2)]

    def dump(self) -> list[float]:
        return [self.name, self.d1[0], self.d1[1], self.d1[2], self.d1[3] / self.d1[0],
                self.d1[4], self.d1[5], self.d1[6], self.d1[7],
                self.d1[4] / self.d1[0], sum(self.d1[4:6]) / self.d1[0], sum(self.d1[4:7]) / self.d1[0], self.max_point,
                self.d2[0], self.d2[1] / self.d2[0], self.d2[2] / self.d2[0],
                self.d2[3] / self.d2[1] if self.d2[1] else -1, self.d2[4] / self.d2[1] if self.d2[1] else -1,
                self.d2[5] / self.d2[0], self.d2[6] / self.d2[0],
                self.d2[7] / self.d2[1] if self.d2[1] else -1, self.d2[8] / self.d2[2] if self.d2[2] else -1,
                self.d2[9] / self.d2[0], self.d2[10] / self.d2[9] if self.d2[9] else -1]


def split_hfp(title: str):
    """从 NAGA 报告的和牌信息字符串中提取总和牌点数。"""
    if m := search(r'(\d+)点∀$', title):  # 庄家自摸
        a = int(m.group(1))
        return 3 * a
    if m := search(r'(\d+)-(\d+)点$', title):  # 闲家自摸
        a = int(m.group(1))
        b = int(m.group(2))
        return 2 * a + b
    if m := search(r'(\d+)点$', title):  # 荣和
        return int(m.group(1))
    raise ValueError(f"无法识别的和牌点数格式: {title}")


def umaoka(game_point: list[int]) -> tuple[list[int], list[float], list[float], list[float]]:
    """应用MLeague规则将游戏内分数转换为(顺位, 素点, 马点, PT)"""
    srp = sorted(game_point, reverse=True)
    rp = [p / 1000 - 25 for p in game_point]
    rk = [srp.index(p) + 1 for p in game_point]
    if srp[0] == srp[3]:  # 暴力枚举可能的同分情况
        mp = [0, 0, 0, 0]
    elif srp[0] == srp[2]:
        mp = [35 / 3, 35 / 3, 35 / 3, -35]
    elif srp[1] == srp[3]:
        mp = [45, -15, -15, -15]
    elif srp[0] == srp[1] and srp[2] == srp[3]:
        mp = [25, 25, -25, -25]
    elif srp[0] == srp[1]:
        mp = [25, 25, -15, -35]
    elif srp[1] == srp[2]:
        mp = [45, -5, -5, -35]
    elif srp[2] == srp[3]:
        mp = [45, 5, -25, -25]
    else:
        mp = [45, 5, -15, -35]
    return rk, rp, [mp[rk[i] - 1] for i in range(4)], [rp[i] + mp[rk[i] - 1] for i in range(4)]


'''
data = [[
    (0): [局编号, 本场编号, 场供数量],
    (1): 调整后的各家持点（没用）,
    (2): 表宝指列表,
    (3): 里宝指列表,
    (4): 0号玩家配牌,
    (5): 0号玩家摸牌,
    (6): 0号玩家打牌,
    (7-9): 1号玩家,
    (10-12): 2号玩家,
    (13-15): 3号玩家,
    (16): [
        (0): "和了",
        (1): 点数变动列表,
        (2): [
            (0): 和牌家,
            (1): 放铳家（若也为和牌家则是自摸）,
            (2): 和0一样，不知道为啥
            (3+): 番种列表
        ]
    ]
    (16'): [
        (0): "流局",
        (1): 点数变动列表
]]
'''


def read_naga_frame_data(data: list[str]):
    players = [PlayerGameData(len(data)) for _ in range(4)]
    points = [25000 for _ in range(4)]
    dama = [True for _ in range(4)]
    for d in data:
        dama = [True for _ in range(4)]
        js_obj = loads(d)[0]
        for i in range(4):
            for c in js_obj[5 + 3 * i]:  # 摸牌列表
                if isinstance(c, str):  # 副露了
                    dama[i] = False
                    players[i].d2[6] += 1
                    break
            for c in js_obj[6 + 3 * i]:  # 出牌列表
                if isinstance(c, str):   # 立直了
                    points[i] -= 1000  # 怎么还得手动交棒子，呕吐
                    # todo: 燕返会扣棒子，并且南四流局完场的棒子没有回收。主要是不知道燕返怎么识别。
                    dama[i] = False
                    players[i].d2[5] += 1
        fd = js_obj[16]
        points = [points[i] + fd[1][i] for i in range(4)]
        if fd[0] == "和了":
            players[fd[2][0]].d2[1] += 1  # 和牌家的和牌局数
            pt = split_hfp(fd[2][3])
            players[fd[2][0]].d2[7] += pt  # 和牌家的和牌得点
            if dama[fd[2][0]]:  # 和牌家在默听
                players[fd[2][0]].d2[4] += 1
            if fd[2][1] == fd[2][0]:  # 和牌家自摸
                players[fd[2][0]].d2[3] += 1
            else:  # 有人放铳
                players[fd[2][1]].d2[2] += 1
                players[fd[2][1]].d2[8] += pt
        elif fd[0] == '流局':
            for i in range(4):
                players[i].d2[9] += 1  # 流局局数
                if fd[1][i] > 0:
                    players[i].d2[10] += 1  # 流听局数
        else:
            print(fd[0], "What??!")
    rk, rp, mp, pt = umaoka(points)
    for i in range(4):
        players[i].d1 = [rk[i], pt[i], rp[i], -1]
        players[i].point = points[i]
    return players


def main(paipu_dir: str, filename: str):
    players = {}
    for fn in listdir(paipu_dir):
        game_data = load(open(f'{paipu_dir}/{fn}', 'r', encoding='UTF-8'))
        frame_data = read_naga_frame_data(game_data['Frames'])
        for i in range(4):
            if (name := game_data['Players'][i]) not in players:
                players[name] = PlayerData(name)
            players[game_data['Players'][i]].add_game(frame_data[i])
    wb = Workbook()
    sheet = wb['Sheet']
    sheet.append(['雀魂ID', '半庄数', '总PT', '总素点', '平均Naga nishiki 类似度',
                  '一位数', '二位数', '三位数', '四位数', 'TOP率', '连对率', '避四率', '半庄最高打点',
                  '小局数', '和牌率', '放铳率', '自摸率', '默和率', '立直率', '副露率',
                  '平均打点', '平均铳点', '流局率', '流听率'])
    for p in players:
        sheet.append(players[p].dump())
    wb.save(filename)


if __name__ == '__main__':
    main('test', 'test.xlsx')
