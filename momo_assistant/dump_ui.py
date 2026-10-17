"""
辅助脚本：导出当前陌陌聊天界面的 UI 层级结构，
用于在 config.py 中调整元素选择器（不同陌陌版本控件 ID 可能不同）。
用法：进入陌陌聊天界面后运行 python dump_ui.py
"""

import time
from device import MomoDevice


def main():
    device = MomoDevice()
    if not device.connect():
        return

    if not device.is_momo_foreground():
        print("[提示] 请先打开陌陌并进入聊天界面，按回车继续...")
        input()

    time.sleep(1)
    print("\n[导出] 当前界面 UI 层级（前 200 行）：")
    print("=" * 60)
    try:
        hierarchy = device.d.dump_hierarchy()
        lines = hierarchy.splitlines()
        for line in lines[:200]:
            print(line)
        if len(lines) > 200:
            print(f"... (共 {len(lines)} 行，已截断)")
    except Exception as e:
        print(f"[错误] 导出失败: {e}")

    # 同时列出所有可点击/文本元素，方便定位输入框和发送按钮
    print("\n" + "=" * 60)
    print("[列举] 主要可交互元素：")
    try:
        for el in device.d(className="android.widget.EditText"):
            print(f"  输入框: {el.info.get('resourceName')} text='{el.get_text()}'")
        for el in device.d(className="android.widget.Button"):
            txt = el.get_text()
            if txt:
                print(f"  按钮: {el.info.get('resourceName')} text='{txt}'")
    except Exception as e:
        print(f"[错误] {e}")


if __name__ == "__main__":
    main()
