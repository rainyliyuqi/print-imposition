"""输出格式化 — 表格 / JSON / SVG 示意图。"""

import json
from typing import List, Dict, Any
from .layout import LayoutResult, LayoutSet
from .optimizer import OptimizationPlan


def format_layout_table(result: LayoutResult) -> str:
    """以表格形式输出拼版结果。"""
    lines = []
    lines.append(f"纸度: {result.paper}")
    lines.append(f"总版位: {result.total_boxes}")
    lines.append(f"利用率: {result.utilization_pct}%")
    lines.append(f"使用面积: {result.used_area_mm2:.0f} mm²")
    lines.append("")

    for s in result.sets:
        lines.append(f"  ── 第{s.set_index + 1}套: {s.box_type} ──")
        lines.append(f"  排布: {s.rows}行 × {s.cols}列"
                      f"{' (旋转90°)' if s.rotated else ''}")
        lines.append(f"  展开尺寸: {s.unfolded_w:.0f}×{s.unfolded_l:.0f} mm")
        lines.append(f"  版位数: {len(s.positions)}")
        lines.append("")

    if result.warnings:
        lines.append("⚠️  注意事项:")
        for w in result.warnings:
            lines.append(f"  - {w}")

    return "\n".join(lines)


def format_optimization_table(plans: List[OptimizationPlan],
                              top_n: int = 5) -> str:
    """以表格输出多个纸度优化方案的对比。"""
    if not plans:
        return "无可用方案。"

    lines = []
    lines.append(f"{'纸度':^20s} {'张数':^8s} {'版位/张':^10s} {'利用率':^10s}")
    lines.append("-" * 50)

    for plan in plans[:top_n]:
        per_sheet = plan.layouts[0].total_boxes if plan.layouts else 0
        lines.append(
            f"{str(plan.paper):20s} {plan.total_sheets:^8d}"
            f" {per_sheet:^10d} {plan.avg_utilization_pct:^9.2f}%"
        )

    lines.append("")
    lines.append(f"共 {len(plans)} 个可用纸度方案。")
    return "\n".join(lines)


def result_to_json(result: LayoutResult) -> str:
    """拼版结果转 JSON。"""
    data = {
        "paper": {
            "name": result.paper.name,
            "width": result.paper.width,
            "height": result.paper.height,
        },
        "total_positions": result.total_boxes,
        "utilization_pct": result.utilization_pct,
        "used_area_mm2": round(result.used_area_mm2, 1),
        "sets": [],
        "warnings": result.warnings,
    }
    for s in result.sets:
        set_data = {
            "set_index": s.set_index + 1,
            "box_type": s.box_type,
            "unfolded_w_mm": round(s.unfolded_w, 1),
            "unfolded_l_mm": round(s.unfolded_l, 1),
            "cols": s.cols,
            "rows": s.rows,
            "rotated": s.rotated,
            "positions": len(s.positions),
        }
        data["sets"].append(set_data)
    return json.dumps(data, ensure_ascii=False, indent=2)


def result_to_svg(result: LayoutResult, scale: float = 1.0) -> str:
    """
    拼版结果转 SVG 示意图。

    scale: 缩放比例，1.0 = 1px/mm。
    """
    pw = int(result.paper.width * scale)
    ph = int(result.paper.height * scale)

    # 颜色方案（每套不同颜色）
    colors = ["#4A90D9", "#E67E22", "#2ECC71"]
    strokes = ["#2C5F8A", "#C0392B", "#1E8449"]

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg"'
        f' width="{pw}" height="{ph}"'
        f' viewBox="0 0 {pw} {ph}">',
        f'  <rect width="{pw}" height="{ph}" fill="#f5f5f5"'
        f' stroke="#333" stroke-width="2"/>',
    ]

    for s_idx, s in enumerate(result.sets):
        color = colors[s_idx % len(colors)]
        stroke = strokes[s_idx % len(strokes)]
        for pos in s.positions:
            x = int(pos.col * (s.unfolded_w + 3) * scale)
            y = int(pos.row * (s.unfolded_l + 3) * scale)
            w = int(s.unfolded_w * scale)
            h = int(s.unfolded_l * scale)

            svg_parts.append(
                f'  <rect x="{x}" y="{y}" width="{w}" height="{h}"'
                f' fill="{color}" fill-opacity="0.25"'
                f' stroke="{stroke}" stroke-width="1.5" rx="1"/>'
            )
            svg_parts.append(
                f'  <text x="{x + w//2}" y="{y + h//2 + 3}"'
                f' font-size="9" text-anchor="middle"'
                f' fill="#333">{s.box_type[:8]}</text>'
            )

    svg_parts.append('</svg>')
    return "\n".join(svg_parts)
