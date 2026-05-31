"""优化器 — 最少用纸 / 最高利用率。"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from .boxes import (
    BoxSpec, UnfoldedBox, resolve_box_type,
    BOX_CALCULATORS,
)
from .paper import PaperSpec, resolve_paper, DEFAULT_PAPERS
from .layout import (
    LayoutResult, fit_single, fit_mixed, MixedOrder,
)


@dataclass
class OptimizationPlan:
    """优化结果"""
    paper: PaperSpec
    total_sheets: int          # 总用纸张数
    layouts: List[LayoutResult]
    total_boxes: int
    avg_utilization_pct: float
    multi_set: bool = False    # 是否多套混排


def optimize_single(box: BoxSpec,
                    box_type: str,
                    paper: PaperSpec,
                    quantity: int,
                    gap: float = 3.0) -> OptimizationPlan:
    """
    单盒型优化：给定数量，计算最少用纸张数。

    先计算单张能排多少个，然后 quantity ÷ 每张数量 = 张数。
    """
    calc = BOX_CALCULATORS[box_type]
    ubox = calc(box)
    single_result = fit_single(ubox, paper, gap)
    per_sheet = single_result.total_boxes

    if per_sheet == 0:
        return OptimizationPlan(
            paper=paper, total_sheets=0,
            layouts=[], total_boxes=0, avg_utilization_pct=0.0,
        )

    sheets = (quantity + per_sheet - 1) // per_sheet  # ceil division

    full_sheets = quantity // per_sheet
    remainder = quantity % per_sheet

    layouts = []
    for _ in range(full_sheets):
        layouts.append(fit_single(ubox, paper, gap))

    if remainder > 0:
        partial = fit_single(ubox, paper, gap)
        partial.total_boxes = remainder
        partial.total_positions = remainder
        partial.used_area_mm2 = remainder * ubox.area_mm2
        total_area = float(paper.area_mm2)
        partial.utilization_pct = round(
            (partial.used_area_mm2 / total_area * 100) if total_area > 0 else 0.0, 2
        )
        layouts.append(partial)

    total_used = sum(l.used_area_mm2 for l in layouts)
    total_paper = len(layouts) * float(paper.area_mm2)
    avg_util = (total_used / total_paper * 100) if total_paper > 0 else 0.0

    return OptimizationPlan(
        paper=paper,
        total_sheets=len(layouts),
        layouts=layouts,
        total_boxes=quantity,
        avg_utilization_pct=round(avg_util, 2),
    )


def try_all_papers(box: BoxSpec,
                   box_type: str,
                   quantity: int,
                   gap: float = 3.0,
                   min_width: int = 0) -> List[OptimizationPlan]:
    """
    尝试所有可用纸度，返回按用纸张数排序的结果。
    """
    results = []
    for ps in DEFAULT_PAPERS.values():
        if ps.width < min_width or ps.height < min_width:
            continue
        plan = optimize_single(box, box_type, ps, quantity, gap)
        if plan.total_sheets > 0:
            results.append(plan)

    results.sort(key=lambda p: (p.total_sheets, -p.avg_utilization_pct))
    return results
