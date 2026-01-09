import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import RectangleSelector
from scipy.signal import find_peaks
import os
import pandas as pd

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 全局变量
original_xlim = None
original_ylim = None
canvas = None
fig = None
ax = None
selector = None
export_data = {}

# 加载数据函数
def load_data(input_data=None, file_path=None):
    if input_data:
        lines = input_data.strip().split('\n')
    elif file_path and os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    else:
        raise ValueError("请提供数据字符串或有效文件路径")

    data = []
    for line in lines:
        parts = line.strip().split(',')
        if len(parts) >= 2:
            try:
                x = float(parts[0].strip())
                y = float(parts[1].strip())
                data.append([x, y])
            except ValueError:
                continue
    return np.array(data)

# 放大选择区域回调函数
def on_select(eclick, erelease):
    x1, y1 = eclick.xdata, eclick.ydata
    x2, y2 = erelease.xdata, erelease.ydata
    if x1 is not None and x2 is not None and y1 is not None and y2 is not None:
        ax.set_xlim(min(x1, x2), max(x1, x2))
        ax.set_ylim(min(y1, y2), max(y1, y2))
        canvas.draw()

# 重置视图函数
def reset_view():
    if original_xlim and original_ylim:
        ax.set_xlim(original_xlim)
        ax.set_ylim(original_ylim)
        canvas.draw()
    else:
        messagebox.showinfo("提示", "尚未绘制图表")

# 绘图函数
def plot_data(x_values, y_values, peaks, troughs):
    global fig, ax, canvas, original_xlim, original_ylim, selector

    try:
        peak_min = float(peak_min_entry.get()) if peak_min_entry.get() else -np.inf
        trough_max = float(trough_max_entry.get()) if trough_max_entry.get() else np.inf
    except ValueError:
        messagebox.showerror("错误", "请输入合法的数值作为极大值下限和极小值上限")
        return

    filtered_peaks = [i for i in peaks if y_values[i] >= peak_min]
    filtered_troughs = [i for i in troughs if y_values[i] <= trough_max]

    # 清除旧图
    for widget in plot_frame.winfo_children():
        widget.destroy()

    # 创建新图表
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.scatter(x_values, y_values, color='blue', label='原始数据', zorder=1)
    if len(filtered_peaks) > 0:
        ax.scatter(x_values[filtered_peaks], y_values[filtered_peaks], color='red', label='极大值', zorder=5)
    if len(filtered_troughs) > 0:
        ax.scatter(x_values[filtered_troughs], y_values[filtered_troughs], color='green', label='极小值', zorder=5)
    ax.set_title('数据散点图与极大值/极小值点')
    ax.set_xlabel('x 值')
    ax.set_ylabel('y 值')
    ax.legend()
    ax.grid(True)
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.3), ncol=3)
    fig.tight_layout()

    original_xlim = ax.get_xlim()
    original_ylim = ax.get_ylim()

    # 移除旧的 RectangleSelector
    if selector:
        selector.disconnect_events()
        selector = None

    # 添加放大选择功能
    selector = RectangleSelector(ax, on_select, useblit=True,
                                 button=[1], minspanx=5, minspany=5,
                                 spancoords='pixels', interactive=False)

    # 嵌入图表
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # 保存数据供导出使用
    global export_data
    export_data = {
        'peaks_x': x_values[filtered_peaks],
        'peaks_y': y_values[filtered_peaks],
        'troughs_x': x_values[filtered_troughs],
        'troughs_y': y_values[filtered_troughs],
    }

# 按钮点击事件
def on_plot_click():
    global original_xlim, original_ylim
    original_xlim = None
    original_ylim = None

    input_text = data_input.get("1.0", tk.END)
    file_path = path_entry.get()

    try:
        if input_text.strip():
            data = load_data(input_data=input_text)
        elif file_path and os.path.exists(file_path):
            data = load_data(file_path=file_path)
        else:
            messagebox.showerror("错误", "请输入数据或选择文件")
            return

        x_values = data[:, 0]
        y_values = data[:, 1]
        peaks, _ = find_peaks(y_values)
        troughs, _ = find_peaks(-y_values)

        plot_data(x_values, y_values, peaks, troughs)

    except Exception as e:
        messagebox.showerror("错误", str(e))

# 保存图片功能
def save_plot():
    if 'canvas' not in globals() or canvas is None:
        messagebox.showerror("错误", "请先绘制图表")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[
            ("PNG 图像", "*.png"),
            ("JPG 图像", "*.jpg"),
            ("SVG 矢量图", "*.svg"),
            ("PDF 文件", "*.pdf"),
            ("所有文件", "*.*")
        ]
    )

    if file_path:
        try:
            fig = canvas.figure
            fig.savefig(file_path, dpi=300, bbox_inches='tight')
            messagebox.showinfo("成功", f"图表已保存至：{file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败：{str(e)}")

# 文件选择对话框
def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("文本文件", "*.txt"), ("CSV文件", "*.csv")])
    if file_path:
        path_entry.delete(0, tk.END)
        path_entry.insert(tk.END, file_path)

# 导出Excel功能
def export_to_excel():
    if 'export_data' not in globals():
        messagebox.showerror("错误", "请先绘制图表并筛选数据")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel 文件", "*.xlsx"), ("所有文件", "*.*")]
    )

    if not file_path:
        return

    max_len = max(len(export_data['peaks_x']), len(export_data['troughs_x']))
    peaks_x = np.pad(export_data['peaks_x'], (0, max_len - len(export_data['peaks_x'])), 'constant', constant_values=np.nan)
    peaks_y = np.pad(export_data['peaks_y'], (0, max_len - len(export_data['peaks_y'])), 'constant', constant_values=np.nan)
    troughs_x = np.pad(export_data['troughs_x'], (0, max_len - len(export_data['troughs_x'])), 'constant', constant_values=np.nan)
    troughs_y = np.pad(export_data['troughs_y'], (0, max_len - len(export_data['troughs_y'])), 'constant', constant_values=np.nan)

    df = pd.DataFrame({
        '极大值_x': peaks_x,
        '极大值_y': peaks_y,
        '极小值_x': troughs_x,
        '极小值_y': troughs_y
    })

    try:
        df.to_excel(file_path, index=False)
        messagebox.showinfo("成功", f"数据已导出至：{file_path}")
    except Exception as e:
        messagebox.showerror("错误", f"导出失败：{str(e)}")

# 创建主窗口
root = tk.Tk()
root.title("极大值极小值识别工具")
root.geometry("1000x600")

# 输入区域
input_frame = tk.Frame(root)
input_frame.pack(pady=10, fill=tk.X)

# 数据输入框
tk.Label(input_frame, text="手动输入数据 (每行 x,y):", font=("微软雅黑", 10)).grid(row=0, column=0, sticky="w")
data_input = scrolledtext.ScrolledText(input_frame, width=40, height=6, font=("Courier New", 10))
data_input.grid(row=1, column=0, padx=5, sticky="nsew")

# 文件路径输入
tk.Label(input_frame, text="或选择文件:", font=("微软雅黑", 10)).grid(row=0, column=1, sticky="w")
path_entry = tk.Entry(input_frame, width=40, font=("微软雅黑", 10))
path_entry.grid(row=1, column=1, padx=5, sticky="w")
tk.Button(input_frame, text="选择文件", command=select_file).grid(row=1, column=2, padx=5, sticky="w")

# 极大值下限 & 极小值上限 输入框
tk.Label(input_frame, text="极大值下限:", font=("微软雅黑", 10)).grid(row=2, column=0, sticky="w", padx=5, pady=5)
peak_min_entry = tk.Entry(input_frame, width=10, font=("微软雅黑", 10))
peak_min_entry.grid(row=2, column=0, sticky="w", padx=(90, 0), pady=5)

tk.Label(input_frame, text="极小值上限:", font=("微软雅黑", 10)).grid(row=2, column=1, sticky="w", padx=5, pady=5)
trough_max_entry = tk.Entry(input_frame, width=10, font=("微软雅黑", 10))
trough_max_entry.grid(row=2, column=1, sticky="w", padx=(90, 0), pady=5)

# 按钮区域
btn_frame = tk.Frame(input_frame)
btn_frame.grid(row=3, column=0, columnspan=3, pady=10)

tk.Button(btn_frame, text="绘图", command=on_plot_click, width=10, bg="lightblue").pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="保存图片", command=save_plot, width=10, bg="lightgreen").pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="重置视图", command=reset_view, width=10, bg="lightyellow").pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="导出Excel", command=export_to_excel, width=10, bg="lightpink").pack(side=tk.LEFT, padx=5)

# 图表显示区域
plot_frame = tk.Frame(root)
plot_frame.pack(fill=tk.BOTH, expand=True)

# 启动主循环
root.mainloop()