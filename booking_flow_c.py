import tkinter as tk
from tkinter import messagebox, ttk
import re


# 沿用 Part B 定义的颜色，保持风格统一
BG_COLOR = "#F5F5F5"
FONT_TITLE = ("Arial", 18, "bold")
FONT_LABEL = ("Arial", 12)
FONT_BUTTON = ("Arial", 12, "bold")
PRIMARY_BG = "#2F80ED"
PRIMARY_FG = "white"
SECONDARY_BG = "#E0E0E0"
SECONDARY_FG = "#333333"

class Tooltip:
    """
    Tooltip类，在鼠标悬停或触发时，在目标控件旁边弹出一个小窗口
    """
    def __init__(self, widget, text, timeout=2000):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.timeout = timeout
        self._after_id = None

    def show(self):
        self.hide()
        if not self.text:
            return
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 25
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, background="#ffffe0",
                         relief="solid", borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=5, ipady=2)
        self._after_id = tw.after(self.timeout, self.hide)

    def hide(self):
        if self._after_id and self.tipwindow:
            self.tipwindow.after_cancel(self._after_id)
            self._after_id = None
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None


class GuestInfoPage(tk.Frame):
    """
    Part C - F3 & F6: 填写住客信息
    设计意图: 接收用户输入，进行校验，然后存入 controller。
    """

    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller

        # 1. 标题区
        tk.Label(self, text="Enter Guest Details", font=FONT_TITLE, bg=BG_COLOR).pack(pady=20)

        # 2. 表单容器
        form_frame = tk.Frame(self, bg=BG_COLOR)
        form_frame.pack(pady=10)

        # --- F3: 人数选择 (Spinbox) ---
        tk.Label(form_frame, text="Adults (>12):", font=FONT_LABEL, bg=BG_COLOR).grid(row=0, column=0, padx=10, pady=10,
                                                                                      sticky="e")
        self.spin_adults = tk.Spinbox(form_frame, from_=1, to=6, justify="center", width=5, font=FONT_LABEL,
                                      command=self.check_children)
        self.spin_adults.grid(row=0, column=1, sticky="w")

        tk.Label(form_frame, text="Children (<=12):", font=FONT_LABEL, bg=BG_COLOR).grid(row=0, column=2, padx=10,
                                                                                         pady=10, sticky="e")
        self.spin_children = tk.Spinbox(form_frame, from_=0, to=6, justify="center", width=5, font=FONT_LABEL,
                                        command=self.check_children)
        self.spin_children.grid(row=0, column=3, sticky="w")

        # --- F6: 个人信息 (Entry) ---
        # Entering First Name
        tk.Label(form_frame, text="First Name:", font=FONT_LABEL, bg=BG_COLOR).grid(row=1, column=0, padx=10, pady=10,
                                                                                   sticky="e")
        self.entry_first_name = tk.Entry(form_frame, width=10, font=FONT_LABEL)
        self.entry_first_name.grid(row=1, column=1, columnspan=1, sticky="w")
        # Entering Last Name
        tk.Label(form_frame, text="Last Name:", font=FONT_LABEL, bg=BG_COLOR).grid(row=1, column=2, padx=10, pady=10,
                                                                                    sticky="e")
        self.entry_last_name = tk.Entry(form_frame, width=10, font=FONT_LABEL)
        self.entry_last_name.grid(row=1, column=3, columnspan=1, sticky="w")

        # 邮箱
        tk.Label(form_frame, text="Email:", font=FONT_LABEL, bg=BG_COLOR).grid(row=2, column=0, padx=10, pady=10,
                                                                               sticky="e")
        self.entry_email = tk.Entry(form_frame, width=30, font=FONT_LABEL)
        self.entry_email.grid(row=2, column=1, columnspan=4, sticky="w")

        # 电话
        tk.Label(form_frame, text="Phone:", font=FONT_LABEL, bg=BG_COLOR).grid(row=3, column=0, padx=10, pady=10,
                                                                               sticky="e")
        self.entry_phone = tk.Entry(form_frame, width=30, font=FONT_LABEL)
        self.entry_phone.grid(row=3, column=1, columnspan=4, sticky="w")

        # 3. 底部按钮区
        btn_frame = tk.Frame(self, bg=BG_COLOR)
        btn_frame.pack(pady=30)

        # 返回按钮 (回到搜索结果页)
        tk.Button(btn_frame, text="Back", font=FONT_BUTTON, bg=SECONDARY_BG, fg=SECONDARY_FG, width=12,
                  command=lambda: controller.show_frame("SearchResultsPage")).pack(side="left", padx=20)

        # 继续按钮 (触发校验和跳转)
        tk.Button(btn_frame, text="Continue to Review Booking", font=FONT_BUTTON, bg=PRIMARY_BG, fg=PRIMARY_FG, width=15,
                  command=self.validate_and_proceed).pack(side="left", padx=20)

    def check_children(self):
        """Ensure children < adults and total ≤ 6."""
        try:
            adults = int(self.spin_adults.get())
            children = int(self.spin_children.get())
        except ValueError:
            self.spin_children.delete(0, "end")
            self.spin_children.insert(0, "0")
            return

        tooltip = Tooltip(self.spin_children, "Children must be less than adults and no more than 6 people in total")

        # Rule 1：children counts < adults count
        if children >= adults:
            new_value = max(adults - 1, 0)
            self.spin_children.delete(0, "end")
            self.spin_children.insert(0, str(new_value))
            tooltip.show()
            return

        # Rule 2：total people counts <= 6
        if adults + children > 6:
            # automatically changes children number
            new_value = max(6 - adults, 0)
            self.spin_children.delete(0, "end")
            self.spin_children.insert(0, str(new_value))
            tooltip.show()

    def validate_and_proceed(self):
        """逻辑处理：数据校验与保存"""
        first_name = self.entry_first_name.get().strip()
        last_name = self.entry_last_name.get().strip()
        email = self.entry_email.get().strip()
        phone = self.entry_phone.get().strip()

        # 简单的校验逻辑 (F6 要求)
        if not first_name or any(char.isdigit() for char in first_name):
            messagebox.showerror("Error", "Please enter a valid first name (no numbers).")
            return
        if not last_name or any(char.isdigit() for char in last_name):
            messagebox.showerror("Error", "Please enter a valid last name (no numbers).")
            return

        # ================== 修改开始 ==================
        # 使用 Regex 校验邮箱格式
        # 解释:
        # ^[a-zA-Z0-9._%+-]+  : 用户名部分 (允许字母、数字、点、下划线等)
        # @                   : 必须包含 @ 符号
        # [a-zA-Z0-9.-]+      : 域名部分 (例如 gmail, hotmail)
        # \.                  : 必须包含点
        # [a-zA-Z]{2,}$       : 顶级域名 (例如 com, org, cn)，至少2个字母
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if not re.match(email_pattern, email):
            messagebox.showerror("Error", "Please enter a valid email address (e.g., user@example.com).")
            return
        # ================== 修改结束 ==================

        if not phone.isdigit() or len(phone) < 8:
            messagebox.showerror("Error", "Please enter a valid phone number (digits only).")
            return

        # 保存数据到 Controller (共享数据)
        self.controller.guest_info = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "adults": int(self.spin_adults.get()),
            "children": int(self.spin_children.get())
        }

        # 跳转到订单汇总页面
        self.controller.show_frame("SummaryPage")


class SummaryPage(tk.Frame):
    """
    Part C - F7: 订单汇总、计价与支付调用
    """

    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller

        tk.Label(self, text="Step 4 - Booking Summary", font=FONT_TITLE, bg=BG_COLOR).pack(pady=20)

        # 显示信息的区域 (使用 Label 列表展示)
        self.info_frame = tk.Frame(self, bg="white", bd=1, relief="solid", padx=20, pady=20)
        self.info_frame.pack(fill="both", expand=True, padx=50, pady=10)

        # 底部按钮
        btn_frame = tk.Frame(self, bg=BG_COLOR)
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Edit Details", font=FONT_BUTTON, bg=SECONDARY_BG, fg=SECONDARY_FG, width=12,
                  command=lambda: controller.show_frame("GuestInfoPage")).pack(side="left", padx=20)

        # 确认支付按钮 (调用 Part D)
        tk.Button(btn_frame, text="Confirm & Pay", font=FONT_BUTTON, bg="green", fg="white", width=15,
                  command=self.process_payment).pack(side="left", padx=20)

        # ★ 关键：每次显示页面时，触发数据刷新
        self.bind("<<ShowPage>>", self.refresh_data)

    def refresh_data(self, event=None):
        """动态读取 Controller 中的数据并计算价格"""
        # 1. 清空旧内容
        for widget in self.info_frame.winfo_children():
            widget.destroy()

        # 2. 安全地获取数据 (防止报错)
        stay = getattr(self.controller, "current_stay", {})
        room = getattr(self.controller, "selected_room", {})
        guest = getattr(self.controller, "guest_info", {})

        if not stay or not room:
            tk.Label(self.info_frame, text="Missing booking info.", bg="white").pack()
            return

        # 3. 提取变量
        check_in = stay.get("check_in")
        nights = stay.get("nights", 0)
        room_name = room.get("name", "Unknown")
        price_per_night = float(room.get("price", 0))
        adults = guest.get("adults", 1)

        # 4. 价格计算 (F7 核心逻辑)
        room_total = price_per_night * nights
        tax = room_total * 0.10  # 假设 10% 税费
        self.final_total = room_total + tax  # 存为实例变量，支付时要用

        # 【新增】把总价存到 controller，供 Part D 使用
        self.controller.booking_total = self.final_total

        # 5. UI 展示
        lines = [
            ("GUEST", f"{guest.get('first_name')}", 14, "bold"),
            ("Room Type", f"{room_name}", 12, "normal"),
            ("Dates", f"{check_in} ({nights} nights)", 12, "normal"),
            ("Guests", f"{adults} Adults, {guest.get('children')} Children", 12, "normal"),
            ("-" * 40, "", 10, "normal"),
            ("Room Charge", f"${room_total:.2f}", 12, "normal"),
            ("Tax (10%)", f"${tax:.2f}", 12, "normal"),
            ("TOTAL DUE", f"${self.final_total:.2f}", 16, "bold")
        ]

        for title, value, size, weight in lines:
            row = tk.Frame(self.info_frame, bg="white")
            row.pack(fill="x", pady=2)
            tk.Label(row, text=title, font=("Arial", size, weight), bg="white", fg="#555").pack(side="left")
            tk.Label(row, text=value, font=("Arial", size, weight), bg="white", fg="black").pack(side="right")

    def process_payment(self):
        """修复后：跳转到 Part D 的支付页面"""
        # 准备要保存的数据字典
        try:
            self.controller.show_frame("PaymentPage")
        except KeyError:
            messagebox.showerror("Error", "Payment Page not found!")