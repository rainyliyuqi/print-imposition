"""拼版排布单元测试。"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from imposition.boxes import BoxSpec, calc_double_insert
from imposition.paper import resolve_paper
from imposition.layout import fit_single, fit_mixed, MixedOrder


def test_fit_single_simple():
    """单盒型排满"""
    box = BoxSpec("test", 300, 200, 100)
    ubox = calc_double_insert(box)
    paper = resolve_paper("1092x787")

    result = fit_single(ubox, paper)

    assert result.total_boxes > 0
    assert result.utilization_pct > 0
    assert len(result.sets) == 1
    for pos in result.sets[0].positions:
        assert pos.box_type == "double-insert"


def test_fit_mixed_simple():
    """多尺码混合拼版"""
    orders = [
        MixedOrder("double-insert", 200, 150, 8),
        MixedOrder("lock-bottom", 150, 120, 4),
    ]
    paper = resolve_paper("1092x787")

    result = fit_mixed(orders, paper)

    assert result.total_boxes > 0
    assert len(result.sets) <= 3
    for s in result.sets:
        assert len(s.positions) <= 16


def test_fit_mixed_empty():
    """空订单"""
    result = fit_mixed([], resolve_paper("a3"))
    assert result.total_boxes == 0
    assert len(result.warnings) > 0


if __name__ == "__main__":
    test_fit_single_simple()
    test_fit_mixed_simple()
    test_fit_mixed_empty()
    print("ALL LAYOUT TESTS PASSED")
