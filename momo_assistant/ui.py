"""
交互 UI 模块 - 终端界面展示回复建议并获取用户选择
采用终端交互，无需 GUI 依赖。用户选择后只填充输入框，不自动发送。
"""

import sys
from typing import List


def clear_screen():
    """清屏"""
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def show_suggestions(latest_msg: str, suggestions: List[str]) -> int:
    """
    展示对方消息和回复建议，返回用户选择的索引（0-based）。
    返回 -1 表示跳过。
    """
    print("\n" + "=" * 60)
    print(f"📩 对方新消息: {latest_msg}")
    print("-" * 60)
    print("AI 回复建议:")
    for i, s in enumerate(suggestions, 1):
        print(f"  {i}. {s}")
    print("-" * 60)
    print("操作: 输入数字选择并填入输入框 | 输入 e 手动编辑 | 输入 s 跳过")
    print("⚠️  填入后请在手机上手动点击发送")
    print("=" * 60)

    while True:
        try:
            choice = input("请选择 > ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return -1

        if choice == "s":
            return -1
        if choice == "e":
            return -2  # 手动编辑标记
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(suggestions):
                return idx
        print("无效输入，请重新选择。")


def manual_edit(default: str) -> str:
    """让用户手动编辑建议文本"""
    print(f"\n当前文本: {default}")
    try:
        new_text = input("编辑后回车（直接回车保留原文）> ").strip()
        return new_text if new_text else default
    except (EOFError, KeyboardInterrupt):
        return default
