"""盒型几何计算 — 展开尺寸与基本参数。"""

from dataclasses import dataclass
from typing import Dict, Tuple, Optional


@dataclass
class BoxSpec:
    """盒型规格"""
    name: str              # 盒型名称
    length: int            # 长 (mm)
    width: int             # 宽 (mm)
    height: int            # 高 (mm)
    paper_thickness: float = 0.5  # 纸厚 (mm)

    @property
    def volume_cc(self) -> float:
        """估算容积 (cm³)"""
        return (self.length * self.width * self.height) / 1000


@dataclass
class UnfoldedBox:
    """展开后尺寸"""
    box: BoxSpec
    unfolded_width: float   # 开料宽度 (mm)
    unfolded_length: float  # 开料长度 (mm)
    area_mm2: float         # 展开面积 (mm²)
    box_type: str           # 盒型标识


# ── 双插盒 ──────────────────────────────────────────────

def calc_double_insert(box: BoxSpec,
                       tuck_flap: Optional[float] = None,
                       glue_flap: float = 15.0) -> UnfoldedBox:
    """
    双插盒（双插口盒）展开尺寸。

    开料宽度 = L + 2*H + 插口位
    开料长度 = W + 2*H + 糊口位

    插口位默认取 0.5 * W（上下各一个插口），
    最小 20mm，最大 60mm。
    """
    if tuck_flap is None:
        tuck_flap = max(20.0, min(60.0, box.width * 0.5))

    uw = box.length + 2 * box.height + tuck_flap
    ul = box.width + 2 * box.height + glue_flap

    return UnfoldedBox(
        box=box,
        unfolded_width=uw,
        unfolded_length=ul,
        area_mm2=uw * ul,
        box_type="double-insert",
    )


# ── 扣底盒 ──────────────────────────────────────────────

def calc_lock_bottom(box: BoxSpec,
                     tuck_flap: Optional[float] = None,
                     glue_flap: float = 20.0) -> UnfoldedBox:
    """
    扣底盒展开尺寸。

    扣底结构在底部多消耗材料，
    开料宽度 = L + 2*H + 插口位
    开料长度 = W + 2*H + 扣底余量

    扣底余量默认取 0.6 * W，最小25mm，最大70mm。
    """
    lock_bottom_extra = max(25.0, min(70.0, box.width * 0.6))

    if tuck_flap is None:
        tuck_flap = max(20.0, min(60.0, box.width * 0.5))

    uw = box.length + 2 * box.height + tuck_flap
    ul = box.width + 2 * box.height + lock_bottom_extra

    return UnfoldedBox(
        box=box,
        unfolded_width=uw,
        unfolded_length=ul,
        area_mm2=uw * ul,
        box_type="lock-bottom",
    )


# ── 飞机盒 ──────────────────────────────────────────────

def calc_airplane_box(box: BoxSpec,
                      tab: Optional[float] = None) -> UnfoldedBox:
    """
    飞机盒（蝴蝶盒）展开尺寸。

    飞机盒展开呈"十"字形对称结构。
    开料宽度 = L + 2*H + 2*插舌
    开料长度 = W + 2*H + 2*插舌

    插舌默认取 max(15, min(40, 0.3 * H))。
    """
    if tab is None:
        tab = max(15.0, min(40.0, box.height * 0.3))

    uw = box.length + 2 * box.height + 2 * tab
    ul = box.width + 2 * box.height + 2 * tab

    return UnfoldedBox(
        box=box,
        unfolded_width=uw,
        unfolded_length=ul,
        area_mm2=uw * ul,
        box_type="airplane-box",
    )


# ── 盒型注册 ────────────────────────────────────────────

BOX_CALCULATORS: Dict[str, callable] = {
    "double-insert": calc_double_insert,
    "lock-bottom":   calc_lock_bottom,
    "airplane-box":  calc_airplane_box,
}

BOX_ALIASES: Dict[str, str] = {
    "双插盒": "double-insert",
    "扣底盒": "lock-bottom",
    "飞机盒": "airplane-box",
}

BOX_LABELS: Dict[str, str] = {
    "double-insert": "双插盒",
    "lock-bottom":   "扣底盒",
    "airplane-box":  "飞机盒",
}


def resolve_box_type(name: str) -> str:
    """支持中英文盒型名，返回标准 key。"""
    name = name.strip().lower()
    if name in BOX_CALCULATORS:
        return name
    if name in BOX_ALIASES:
        return BOX_ALIASES[name]
    raise ValueError(f"不支持的盒型: {name}，可选: {', '.join(BOX_LABELS.values())}")


def list_box_types() -> str:
    """列出所有支持的盒型。"""
    lines = ["支持的盒型:"]
    for key, label in BOX_LABELS.items():
        lines.append(f"  {key:20s} {label}")
    return "\n".join(lines)
