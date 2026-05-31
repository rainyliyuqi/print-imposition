"""拼版排布 — 单盒型排满、多尺码混合排、版位约束。"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from .boxes import UnfoldedBox
from .paper import PaperSpec


@dataclass
class Position:
    """单个版位"""
    row: int
    col: int
    box_type: str
    unfolded_w: float   # 该盒型展开宽度 (mm)
    unfolded_l: float   # 该盒型展开长度 (mm)
    rotated: bool = False  # 是否旋转 90°


@dataclass
class LayoutSet:
    """一套版（同一盒型在一个纸度上的排布）"""
    set_index: int          # 第几套版 (0,1,2)
    box_type: str           # 盒型标识
    unfolded_w: float       # 展开宽度
    unfolded_l: float       # 展开长度
    positions: List[Position] = field(default_factory=list)
    cols: int = 0
    rows: int = 0
    rotated: bool = False   # 整版是否旋转


@dataclass
class LayoutResult:
    """一次拼版排布的结果"""
    paper: PaperSpec
    sets: List[LayoutSet]
    total_positions: int
    used_area_mm2: float
    utilization_pct: float  # 利用率 (%)
    total_boxes: int        # 总版位数
    warnings: List[str] = field(default_factory=list)


# ── 单盒型排满 ──────────────────────────────────────────

def fit_single(ubox: UnfoldedBox,
               paper: PaperSpec,
               gap: float = 3.0) -> LayoutResult:
    """
    将同一盒型排满一张纸。

    尝试两种方向，选版位数量多的。
    gap: 版位间间距 (mm)
    """
    uw = ubox.unfolded_width + gap
    ul = ubox.unfolded_length + gap
    pw, ph = float(paper.width), float(paper.height)

    # 方案 A: uw 沿 pw 方向
    cols_a = int(pw // uw)
    rows_a = int(ph // ul)
    count_a = cols_a * rows_a

    # 方案 B: 旋转，uw 沿 ph 方向
    cols_b = int(pw // ul)
    rows_b = int(ph // uw)
    count_b = cols_b * rows_b

    if count_a >= count_b:
        cols, rows, rotated = cols_a, rows_a, False
        item_w, item_l = uw, ul
    else:
        cols, rows, rotated = cols_b, rows_b, True
        item_w, item_l = ul, uw

    positions = []
    for r in range(rows):
        for c in range(cols):
            positions.append(Position(
                row=r, col=c,
                box_type=ubox.box_type,
                unfolded_w=ubox.unfolded_width,
                unfolded_l=ubox.unfolded_length,
                rotated=rotated,
            ))

    layout_set = LayoutSet(
        set_index=0,
        box_type=ubox.box_type,
        unfolded_w=ubox.unfolded_width,
        unfolded_l=ubox.unfolded_length,
        positions=positions,
        cols=cols,
        rows=rows,
        rotated=rotated,
    )

    count = len(positions)
    used = count * ubox.area_mm2
    total = float(paper.area_mm2)
    utilization = (used / total * 100) if total > 0 else 0.0

    return LayoutResult(
        paper=paper,
        sets=[layout_set],
        total_positions=count,
        used_area_mm2=used,
        utilization_pct=round(utilization, 2),
        total_boxes=count,
    )


# ── 多尺码混合拼版 ──────────────────────────────────────

@dataclass
class MixedOrder:
    """混合拼版中的一种盒型与数量。"""
    box_type: str
    unfolded_w: float
    unfolded_l: float
    qty: int                    # 需要多少个


def fit_mixed(orders: List[MixedOrder],
              paper: PaperSpec,
              gap: float = 3.0,
              max_sets: int = 3,
              max_positions_per_set: int = 16) -> LayoutResult:
    """
    多尺码混合拼版。

    规则:
    - 最多 max_sets 套版
    - 每套最多 max_positions_per_set 个版位
    - 版位不能空
    - 按盒型面积从大到小分配套数

    使用贪心策略:
    1. 按面积降序排列订单
    2. 每个订单计算适用纸度排布
    3. 大盒型先占纸，再用小盒型填充剩余空间
    """
    if not orders:
        return LayoutResult(
            paper=paper, sets=[], total_positions=0,
            used_area_mm2=0, utilization_pct=0.0, total_boxes=0,
            warnings=["订单为空"],
        )

    # 按面积降序
    sorted_orders = sorted(orders, key=lambda o: o.unfolded_w * o.unfolded_l, reverse=True)
    sets: List[LayoutSet] = []
    total_boxes = 0
    used_area = 0.0
    warnings = []

    pw, ph = float(paper.width), float(paper.height)

    for idx, order in enumerate(sorted_orders):
        if idx >= max_sets:
            break

        uw = order.unfolded_w + gap
        ul = order.unfolded_l + gap
        needed = order.qty

        # 两种方向
        cols_a = int(pw // uw)
        rows_a = int(ph // ul)

        cols_b = int(pw // ul)
        rows_b = int(ph // uw)

        # 选版位多的方向
        if cols_a * rows_a >= cols_b * rows_b:
            cols, rows, rotated = cols_a, rows_a, False
            item_w, item_l = uw, ul
        else:
            cols, rows, rotated = cols_b, rows_b, True
            item_w, item_l = ul, uw

        positions_count = cols * rows

        if positions_count == 0:
            warnings.append(f"盒型 {order.box_type} 无法排入纸度")
            continue

        # 不能超过每套上限
        actual_count = min(positions_count, max_positions_per_set, needed)

        if actual_count == 0:
            continue

        positions = []
        count = 0
        for r in range(rows):
            for c in range(cols):
                if count >= actual_count:
                    break
                positions.append(Position(
                    row=r, col=c,
                    box_type=order.box_type,
                    unfolded_w=order.unfolded_w,
                    unfolded_l=order.unfolded_l,
                    rotated=rotated,
                ))
                count += 1
            if count >= actual_count:
                break

        layout_set = LayoutSet(
            set_index=idx,
            box_type=order.box_type,
            unfolded_w=order.unfolded_w,
            unfolded_l=order.unfolded_l,
            positions=positions,
            cols=cols,
            rows=rows,
            rotated=rotated,
        )
        sets.append(layout_set)
        total_boxes += actual_count
        used_area += actual_count * order.unfolded_w * order.unfolded_l
        needed -= actual_count

        if needed > 0:
            warnings.append(
                f"盒型 {order.box_type} 还需要 {needed} 个（本版只排 {actual_count} 个）"
            )

    total_paper_area = float(paper.area_mm2)
    utilization = (used_area / total_paper_area * 100) if total_paper_area > 0 else 0.0

    return LayoutResult(
        paper=paper,
        sets=sets,
        total_positions=total_boxes,
        used_area_mm2=used_area,
        utilization_pct=round(utilization, 2),
        total_boxes=total_boxes,
        warnings=warnings,
    )
