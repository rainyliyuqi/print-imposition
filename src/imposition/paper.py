"""纸张规格 — 常用印刷用纸尺寸与自定义纸度。"""

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional


@dataclass
class PaperSpec:
    """纸张规格"""
    name: str          # 名称，如 "1092×787"
    width: int         # 纸度宽度 (mm)
    height: int        # 纸度长度 (mm)

    @property
    def area_mm2(self) -> int:
        return self.width * self.height

    def __str__(self) -> str:
        return f"{self.name} ({self.width}×{self.height}mm)"


# ── 常用正度 / 大度 / 特殊纸度 ──────────────────────

DEFAULT_PAPERS: Dict[str, PaperSpec] = {
    # 正度
    "787x1092":  PaperSpec("正度 787×1092",   787,  1092),
    "889x1194":  PaperSpec("大度 889×1194",   889,  1194),
    # 常用大幅面
    "1092x787":  PaperSpec("正度 1092×787",   1092, 787),
    "1194x889":  PaperSpec("大度 1194×889",   1194, 889),
    # 国际 A 系列
    "a0":        PaperSpec("A0",               841,  1189),
    "a1":        PaperSpec("A1",               594,  841),
    "a2":        PaperSpec("A2",               420,  594),
    "a3":        PaperSpec("A3",               297,  420),
    "a4":        PaperSpec("A4",               210,  297),
    # 特种/常用
    "1200x900":  PaperSpec("1200×900",         1200, 900),
    "1450x1000": PaperSpec("1450×1000",        1450, 1000),
    "1500x1100": PaperSpec("1500×1100",        1500, 1100),
}


def resolve_paper(spec: str) -> PaperSpec:
    """
    解析纸张规格。

    支持:
    - 预定义名称: '1092x787', 'a3', 'a4' 等
    - 自定义尺寸: '1200x900', '1000*700'
    - 单数（自动补宽高）: '1092' → 1092×1092
    """
    spec = spec.strip().lower()

    # 预定义
    if spec in DEFAULT_PAPERS:
        return DEFAULT_PAPERS[spec]

    # 自定义: 1200x900 或 1200*900
    for sep in ("x", "*", "×"):
        if sep in spec:
            parts = spec.split(sep)
            if len(parts) == 2:
                try:
                    w, h = int(parts[0]), int(parts[1])
                    return PaperSpec(f"{w}×{h}", w, h)
                except ValueError:
                    pass

    # 单数
    try:
        s = int(spec)
        return PaperSpec(f"{s}×{s}", s, s)
    except ValueError:
        pass

    raise ValueError(
        f"无法解析纸张规格: '{spec}'。"
        f"可用预定义: {', '.join(DEFAULT_PAPERS)}"
    )


def list_papers() -> str:
    """列出常用纸度。"""
    lines = ["常用纸度:"]
    for key, ps in DEFAULT_PAPERS.items():
        lines.append(f"  {key:15s} {ps}")
    return "\n".join(lines)
