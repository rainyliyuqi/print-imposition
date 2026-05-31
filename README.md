# print-imposition

印刷包装拼版 CLI 工具 — 盒型计算、拼版排布、用纸优化。

## 安装

```bash
pip install print-imposition
```

或从源码安装：

```bash
git clone https://github.com/seanyli/print-imposition.git
cd print-imposition
pip install -e .
```

## 用法

```bash
# 查看支持的盒型
pi boxes --list

# 单盒型拼版计算
pi calc --box double-insert --length 300 --width 200 --height 100 --paper 1092

# 多尺码混合拼版优化
pi optimize --orders orders.json --paper 1092x787
```

## 支持盒型

- 双插盒 (double-insert)
- 扣底盒 (lock-bottom)
- 飞机盒 (airplane-box)
- 更多开发中…

## 协议

MIT
