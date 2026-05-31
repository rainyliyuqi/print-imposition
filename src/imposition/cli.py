"""CLI 入口 — click 命令。"""

import json
import click
from .boxes import (
    BoxSpec, list_box_types, resolve_box_type,
    BOX_CALCULATORS, BOX_LABELS,
)
from .paper import resolve_paper, list_papers
from .layout import fit_single
from .optimizer import optimize_single, try_all_papers
from .output import (
    format_layout_table, format_optimization_table,
    result_to_json, result_to_svg,
)


@click.group()
def cli():
    """print-imposition — 印刷包装拼版 CLI 工具"""


@cli.command("boxes")
@click.option("--list", "show_list", is_flag=True, help="列出所有支持的盒型")
def boxes_cmd(show_list):
    """查看盒型信息"""
    if show_list:
        click.echo(list_box_types())


@cli.command("papers")
@click.option("--list", "show_list", is_flag=True, help="列出常用纸度")
def papers_cmd(show_list):
    """查看纸张规格"""
    if show_list:
        click.echo(list_papers())


@cli.command("calc")
@click.option("--box", required=True, help="盒型: double-insert / lock-bottom / airplane-box")
@click.option("--length", type=int, required=True, help="盒长 (mm)")
@click.option("--width", type=int, required=True, help="盒宽 (mm)")
@click.option("--height", type=int, required=True, help="盒高 (mm)")
@click.option("--paper", default="1092x787", help="纸度, 如 1092x787 或 1200x900")
@click.option("--gap", type=float, default=3.0, help="版位间距 (mm)")
@click.option("--json-output", is_flag=True, help="输出 JSON")
@click.option("--svg", is_flag=True, help="输出 SVG 示意图")
def calc_cmd(box, length, width, height, paper, gap, json_output, svg):
    """计算单盒型拼版排布"""
    try:
        box_type = resolve_box_type(box)
    except ValueError as e:
        click.echo(f"❌ {e}", err=True)
        return

    try:
        paper_spec = resolve_paper(paper)
    except ValueError as e:
        click.echo(f"❌ {e}", err=True)
        return

    box_spec = BoxSpec(
        name=BOX_LABELS.get(box_type, box_type),
        length=length, width=width, height=height,
    )

    calc = BOX_CALCULATORS[box_type]
    ubox = calc(box_spec)
    result = fit_single(ubox, paper_spec, gap)

    if json_output:
        click.echo(result_to_json(result))
    elif svg:
        click.echo(result_to_svg(result))
    else:
        click.echo(format_layout_table(result))


@cli.command("optimize")
@click.option("--box", required=True, help="盒型")
@click.option("--length", type=int, required=True, help="盒长 (mm)")
@click.option("--width", type=int, required=True, help="盒宽 (mm)")
@click.option("--height", type=int, required=True, help="盒高 (mm)")
@click.option("--quantity", type=int, required=True, help="订单数量")
@click.option("--gap", type=float, default=3.0, help="版位间距 (mm)")
@click.option("--top", type=int, default=5, help="显示前 N 个方案")
def optimize_cmd(box, length, width, height, quantity, gap, top):
    """给定订单数量，试所有纸度找最优方案"""
    try:
        box_type = resolve_box_type(box)
    except ValueError as e:
        click.echo(f"❌ {e}", err=True)
        return

    box_spec = BoxSpec(
        name=BOX_LABELS.get(box_type, box_type),
        length=length, width=width, height=height,
    )

    plans = try_all_papers(box_spec, box_type, quantity, gap)
    click.echo(format_optimization_table(plans, top_n=top))


if __name__ == "__main__":
    cli()
