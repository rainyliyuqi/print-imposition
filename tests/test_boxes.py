"""盒型计算单元测试。"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from imposition.boxes import (
    BoxSpec, calc_double_insert, calc_lock_bottom,
    calc_airplane_box, resolve_box_type, list_box_types,
)


def test_double_insert():
    """双插盒展开尺寸"""
    box = BoxSpec(name="test", length=300, width=200, height=100)
    ubox = calc_double_insert(box)

    assert ubox.box_type == "double-insert"
    # L + 2*H + tuck(0.5*W=100 → cap60) = 300 + 200 + 60 = 560
    assert abs(ubox.unfolded_width - 560.0) < 1
    # W + 2*H + glue(15) = 200 + 200 + 15 = 415
    assert abs(ubox.unfolded_length - 415.0) < 1


def test_lock_bottom():
    """扣底盒展开尺寸"""
    box = BoxSpec(name="test", length=200, width=150, height=80)
    ubox = calc_lock_bottom(box)

    assert ubox.box_type == "lock-bottom"
    # L + 2*H + tuck(0.5*W=75→cap60) = 200 + 160 + 60 = 420
    assert abs(ubox.unfolded_width - 420.0) < 1
    # W + 2*H + lock_bottom(0.6*W=90→cap70) = 150 + 160 + 70 = 380
    assert abs(ubox.unfolded_length - 380.0) < 1


def test_airplane_box():
    """飞机盒展开尺寸"""
    box = BoxSpec(name="test", length=250, width=180, height=60)
    ubox = calc_airplane_box(box)

    assert ubox.box_type == "airplane-box"
    # L + 2*H + 2*tab(0.3*H=18, min15) = 250 + 120 + 36 = 406
    assert abs(ubox.unfolded_width - 406.0) < 1
    # W + 2*H + 2*tab = 180 + 120 + 36 = 336
    assert abs(ubox.unfolded_length - 336.0) < 1


def test_resolve_box_type():
    """中英文盒型解析"""
    assert resolve_box_type("double-insert") == "double-insert"
    assert resolve_box_type("双插盒") == "double-insert"
    assert resolve_box_type("扣底盒") == "lock-bottom"
    assert resolve_box_type("飞机盒") == "airplane-box"

    try:
        resolve_box_type("不存在的盒型")
        assert False, "应该抛出异常"
    except ValueError:
        pass


def test_list_box_types():
    """列盒型"""
    result = list_box_types()
    assert "双插盒" in result
    assert "扣底盒" in result
    assert "飞机盒" in result


if __name__ == "__main__":
    test_double_insert()
    test_lock_bottom()
    test_airplane_box()
    test_resolve_box_type()
    test_list_box_types()
    print("ALL TESTS PASSED")
