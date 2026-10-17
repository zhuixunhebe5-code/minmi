"""
陌陌聊天助手 - 主程序
流程：监听陌陌聊天界面 → 检测对方新消息 → AI 生成回复建议 → 用户选择 → 填入输入框
⚠️  发送动作由用户在手机上手动完成，本程序不自动发送任何消息。
"""

import sys
import time

from config import POLL_INTERVAL
from device import MomoDevice
from ai_client import AIClient
from ui import show_suggestions, manual_edit


def main():
    print("=" * 60)
    print("  陌陌聊天助手（AI 辅助回复 · 人工确认发送）")
    print("  ⚠️  本工具不会自动发送消息，发送由你手动点击")
    print("=" * 60)

    # 初始化设备
    device = MomoDevice()
    if not device.connect():
        print("[错误] 无法连接 Android 设备，请检查 USB 调试与 ADB 连接。")
        sys.exit(1)

    # 初始化 AI
    ai = AIClient()

    # 确保陌陌在前台
    if not device.is_momo_foreground():
        print("[提示] 陌陌未在前台，正在启动...")
        device.open_momo()
        time.sleep(2)
        if not device.is_momo_foreground():
            print("[警告] 请手动打开陌陌并进入一个聊天界面，然后按回车继续...")
            input()

    print("\n[运行] 开始监听新消息... (Ctrl+C 退出)")
    print("       请保持陌陌聊天界面在前台。\n")

    # 记录已处理的对方最新消息，避免重复提示
    last_processed_msg = ""

    try:
        while True:
            if not device.is_momo_foreground():
                # 陌陌不在前台，跳过本轮
                time.sleep(POLL_INTERVAL)
                continue

            latest = device.get_latest_other_message()
            if latest and latest.text and latest.text != last_processed_msg:
                print(f"\n[新消息] 对方: {latest.text}")
                last_processed_msg = latest.text

                # 获取上下文
                context = device.get_chat_messages()

                # 生成建议
                suggestions = ai.generate_suggestions(latest.text, context)
                if not suggestions:
                    print("[AI] 未生成建议，跳过。")
                    time.sleep(POLL_INTERVAL)
                    continue

                # 展示并让用户选择
                choice = show_suggestions(latest.text, suggestions)

                if choice == -1:
                    print("[操作] 已跳过。")
                elif choice == -2:
                    # 手动编辑
                    text = manual_edit(suggestions[0])
                    if text:
                        device.fill_input_box(text)
                else:
                    selected = suggestions[choice]
                    ok = device.fill_input_box(selected)
                    if ok:
                        print("[完成] 文本已填入输入框，请在手机上点击发送。")
                    else:
                        print("[失败] 填入输入框失败。")

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print("\n\n[退出] 程序已停止。")
    except Exception as e:
        print(f"\n[异常] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
