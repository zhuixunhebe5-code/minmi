"""
设备控制模块 - 基于 uiautomator2 控制 Android 设备
职责：连接设备、读取陌陌聊天消息、填充输入框
注意：不负责点击发送按钮（发送由用户手动完成）。
"""

import time
from typing import List, Optional

import uiautomator2 as u2

from config import (
    DEVICE_SERIAL,
    MOMO_PACKAGE,
    MESSAGE_LIST_SELECTORS,
    MESSAGE_TEXT_SELECTORS,
    INPUT_BOX_SELECTORS,
)


class ChatMessage:
    """单条聊天消息"""

    def __init__(self, text: str, is_from_other: bool, bounds: tuple):
        self.text = text.strip()
        self.is_from_other = is_from_other  # True=对方发来的, False=自己发的
        self.bounds = bounds  # (left, top, right, bottom)

    def __repr__(self):
        sender = "对方" if self.is_from_other else "我"
        return f"[{sender}] {self.text}"


class MomoDevice:
    def __init__(self):
        self.d: Optional[u2.Device] = None
        self.screen_width = 0
        self.screen_height = 0

    # ---------- 连接 ----------
    def connect(self) -> bool:
        try:
            if DEVICE_SERIAL:
                self.d = u2.connect(DEVICE_SERIAL)
            else:
                self.d = u2.connect()
            info = self.d.info
            self.screen_width = info["displayWidth"]
            self.screen_height = info["displayHeight"]
            print(f"[设备] 已连接: {info.get('productName', 'unknown')} "
                  f"分辨率 {self.screen_width}x{self.screen_height}")
            return True
        except Exception as e:
            print(f"[设备] 连接失败: {e}")
            return False

    # ---------- 前台应用检测 ----------
    def is_momo_foreground(self) -> bool:
        try:
            pkg = self.d.app_current().get("package", "")
            return pkg == MOMO_PACKAGE
        except Exception:
            return False

    def open_momo(self):
        """启动陌陌（如未在前台）"""
        try:
            self.d.app_start(MOMO_PACKAGE)
            time.sleep(2)
        except Exception as e:
            print(f"[设备] 启动陌陌失败: {e}")

    # ---------- 元素查找工具 ----------
    def _find_element(self, selectors: list):
        """按候选选择器列表依次尝试，返回第一个找到的元素"""
        if not self.d:
            return None
        for sel in selectors:
            try:
                el = self.d(**sel)
                if el.exists:
                    return el
            except Exception:
                continue
        return None

    # ---------- 读取聊天消息 ----------
    def get_chat_messages(self) -> List[ChatMessage]:
        """
        读取当前聊天界面的所有可见消息。
        通过控件在屏幕左/右半区判断是对方还是自己发的。
        """
        if not self.d:
            return []

        messages = []
        try:
            # 先定位消息列表容器，再在其中找文本
            container = self._find_element(MESSAGE_LIST_SELECTORS)

            if container and container.exists:
                text_views = container.child(**{"className": "android.widget.TextView"})
                # 兼容写法：直接在容器下找所有 TextView
                elems = self.d(className="android.widget.TextView")
            else:
                # 兜底：全局查找所有 TextView（可能混入标题栏等，需靠位置过滤）
                elems = self.d(className="android.widget.TextView")

            count = elems.count
            for i in range(count):
                try:
                    el = elems[i]
                    text = el.get_text()
                    if not text or not text.strip():
                        continue
                    bounds = el.bounds()  # (left, top, right, bottom)
                    # 通过水平位置判断：左半屏=对方，右半屏=自己
                    center_x = (bounds[0] + bounds[2]) / 2
                    is_other = center_x < self.screen_width / 2
                    messages.append(ChatMessage(text, is_other, bounds))
                except Exception:
                    continue
        except Exception as e:
            print(f"[设备] 读取消息异常: {e}")

        # 按垂直位置排序（从上到下）
        messages.sort(key=lambda m: m.bounds[1])
        return messages

    def get_latest_other_message(self) -> Optional[ChatMessage]:
        """获取最新一条对方发来的消息"""
        msgs = self.get_chat_messages()
        for m in reversed(msgs):
            if m.is_from_other:
                return m
        return None

    # ---------- 填充输入框（不发送）----------
    def fill_input_box(self, text: str) -> bool:
        """
        将文本填入陌陌输入框，但不点击发送。
        返回是否成功。
        """
        if not self.d:
            return False
        try:
            input_el = self._find_element(INPUT_BOX_SELECTORS)
            if not input_el or not input_el.exists:
                print("[设备] 未找到输入框")
                return False
            # 先点击聚焦，再清空，再输入
            input_el.click()
            time.sleep(0.3)
            # 清空已有内容
            try:
                input_el.clear_text()
            except Exception:
                pass
            input_el.set_text(text)
            print(f"[设备] 已填入输入框: {text[:40]}{'...' if len(text) > 40 else ''}")
            return True
        except Exception as e:
            print(f"[设备] 填充输入框失败: {e}")
            return False

    # ---------- 辅助：截图 ----------
    def screenshot(self, path: str = "momo_screen.png"):
        if self.d:
            self.d.screenshot(path)
