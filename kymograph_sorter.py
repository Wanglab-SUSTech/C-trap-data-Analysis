import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
# 移除导致报错的库引用
# from ttkbootstrap.scrolled import ScrolledFrame 
import numpy as np
from PIL import Image 
import threading
from collections import OrderedDict
import pandas as pd
import traceback
from pathlib import Path
import re

# --- Matplotlib ---
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg 
import matplotlib.ticker as ticker
from matplotlib.ticker import FixedLocator, FuncFormatter, MaxNLocator, AutoLocator, MultipleLocator
from matplotlib.widgets import MultiCursor

# --- 全局设置 ---
matplotlib.rcParams['keymap.save'].remove('s')
matplotlib.rcParams['keymap.fullscreen'].remove('f')
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False
matplotlib.rcParams['font.size'] = 12       
matplotlib.rcParams['axes.titlesize'] = 14  
matplotlib.rcParams['axes.labelsize'] = 12  
matplotlib.rcParams['xtick.labelsize'] = 10 
matplotlib.rcParams['ytick.labelsize'] = 10

# --- H5 支持 ---
try:
    import lumicks.pylake as lk
    H5_SUPPORT = True
except ImportError:
    H5_SUPPORT = False
    print("警告: 未安装 lumicks.pylake")

IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.tif', '.tiff', '.bmp', '.gif'}
H5_EXTENSIONS = {'.h5'}

# ============================================================
#  I18N  (Internationalization)
# ============================================================
I18N = {
    # --- StitcherWindow ---
    'stitch_ready':       {'zh': '就绪，请添加 2 个或更多 H5 文件后点击开始拼接', 'en': 'Ready, add 2+ H5 files then click Start Stitch'},
    'stitch_hint':        {'zh': '按顺序添加要拼接的 Kymograph 文件（从左到右 = 从早到晚）', 'en': 'Add Kymograph files in order (Left=Early, Right=Late)'},
    'file_list':          {'zh': '文件列表', 'en': 'File List'},
    'add_file':           {'zh': '添加文件', 'en': 'Add File'},
    'remove_last':        {'zh': '移除末行', 'en': 'Remove Last'},
    'start_stitch':       {'zh': '开始拼接', 'en': 'Start Stitch'},
    'log_label':          {'zh': '日志:', 'en': 'Log:'},
    'stitch_warn_min':    {'zh': '至少需要保留 2 个文件条目', 'en': 'At least 2 file entries must remain'},
    'stitch_err_min_h5':  {'zh': '请至少选择 2 个 H5 文件。', 'en': 'Please select at least 2 H5 files.'},
    'stitch_done':        {'zh': '拼接成功！', 'en': 'Stitching successful!'},

    # --- Main UI: Input source ---
    'input_source':       {'zh': '1. 输入源管理', 'en': '1. Input Source'},
    'add_single':         {'zh': '添加单个', 'en': 'Add Single'},
    'batch_import':       {'zh': '批量导入', 'en': 'Batch Import'},
    'remove_selected':    {'zh': '移除选中', 'en': 'Remove Sel.'},
    'clear_all':          {'zh': '清空所有', 'en': 'Clear All'},
    'filter_label':       {'zh': '过滤:', 'en': 'Filter:'},
    'filter_image':       {'zh': '图片', 'en': 'Image'},
    'waiting_data':       {'zh': '等待添加数据...', 'en': 'Waiting for data...'},

    # --- Force export ---
    'force_export':       {'zh': '2. 力数据导出', 'en': '2. Force Export'},
    'downsample_hz':      {'zh': '降采样频率 (Hz):', 'en': 'Downsample (Hz):'},
    'export_force_csv':   {'zh': '导出力与距离数据 (.csv)', 'en': 'Export Force & Distance (.csv)'},
    'force_win_title':    {'zh': '选择导出的数据', 'en': 'Select Data to Export'},
    'force_ds_label':     {'zh': 'Downsampled (降采样):', 'en': 'Downsampled:'},
    'confirm_export':     {'zh': '确认导出', 'en': 'Confirm Export'},

    # --- File list ---
    'file_list_3':        {'zh': '3. 文件列表', 'en': '3. File List'},
    'col_filename':       {'zh': '文件名', 'en': 'Filename'},
    'col_folder':         {'zh': '位置', 'en': 'Location'},

    # --- Mode ---
    'mode_copy':          {'zh': '复制', 'en': 'Copy'},
    'mode_move':          {'zh': '移动', 'en': 'Move'},

    # --- Top bar buttons ---
    'scan_output':        {'zh': '输出', 'en': 'Output'},
    'link_folder':        {'zh': '关联', 'en': 'Link'},
    'kymo_stitch':        {'zh': '拼接', 'en': 'Stitch'},
    'new_category':       {'zh': '新建', 'en': 'New'},
    'annotate_tool':      {'zh': '标注', 'en': 'Annot'},
    'save_image':         {'zh': '保存', 'en': 'Save'},
    'lang_toggle':        {'zh': 'EN', 'en': '中文'},

    # --- Top bar tooltips ---
    'tt_scan_output':     {'zh': '选择扫描输出目录', 'en': 'Select scan output directory'},
    'tt_link_folder':     {'zh': '关联已有文件夹', 'en': 'Link existing folder'},
    'tt_kymo_stitch':     {'zh': 'Kymograph 拼接工具', 'en': 'Kymograph stitch tool'},
    'tt_new_category':    {'zh': '创建新分类文件夹', 'en': 'Create new category folder'},
    'tt_annotate':        {'zh': '打开标注工具', 'en': 'Open annotation tools'},
    'tt_save_image':      {'zh': '保存当前图像', 'en': 'Save current image'},
    'tt_lang_toggle':     {'zh': '切换为英文', 'en': 'Switch to Chinese'},
    'tt_mode_copy':       {'zh': '复制文件到分类文件夹', 'en': 'Copy files to category folders'},
    'tt_mode_move':       {'zh': '移动文件到分类文件夹', 'en': 'Move files to category folders'},

    # --- Image display ---
    'image_display':      {'zh': '图像显示 (Gain & Offset)', 'en': 'Image Display (Gain & Offset)'},
    'aspect_equal':       {'zh': '等比', 'en': '1:1'},

    # --- Crop & Ticks ---
    'crop_ticks':         {'zh': '裁剪与刻度 (Crop, Ticks & Output)', 'en': 'Crop, Ticks & Output'},
    'two_point_roi':      {'zh': '两点定界', 'en': '2-Point ROI'},
    'cancel_roi':         {'zh': '取消定界', 'en': 'Cancel'},
    'enable_crop':        {'zh': '启用裁剪', 'en': 'Enable Crop'},

    # --- Scan mode ---
    'scan_mode':          {'zh': 'Scan 模式', 'en': 'Scan Mode'},
    'scan_hint':          {'zh': 'X: Position (x) um   Y: Position (y) um   背景扣除建议用 ROI 框选', 'en': 'X: Position (x) um   Y: Position (y) um   ROI recommended for BG subtraction'},
    'prev_frame':         {'zh': '上一帧', 'en': 'Prev'},
    'next_frame':         {'zh': '下一帧', 'en': 'Next'},
    'frame_info':         {'zh': '帧 1 / 1', 'en': 'Frame 1 / 1'},

    # --- Background subtraction ---
    'bg_subtract':        {'zh': '背景扣除', 'en': 'BG Subtract'},
    'bg_timezero':        {'zh': '零点帧', 'en': 'Zero Frame'},
    'bg_temporal':        {'zh': '时间%', 'en': 'Time %'},
    'bg_spatial':         {'zh': '空间侧', 'en': 'Sides'},
    'bg_roi':             {'zh': 'ROI框选', 'en': 'ROI Select'},
    'bg_init_frames':     {'zh': '初始帧数:', 'en': 'Init Frames:'},
    'bg_percentile':      {'zh': '百分位(%):', 'en': 'Percentile(%):'},
    'bg_side_width':      {'zh': '侧宽(列):', 'en': 'Side Width:'},
    'bg_smooth':          {'zh': '平滑(行):', 'en': 'Smooth(rows):'},
    'bg_no_smooth':       {'zh': '(0=不平滑)', 'en': '(0=off)'},
    'bg_stat':            {'zh': '统计量:', 'en': 'Statistic:'},
    'bg_median':          {'zh': '中位数（推荐）', 'en': 'Median (Rec.)'},
    'bg_mean':            {'zh': '均值', 'en': 'Mean'},
    'bg_roi_drag':        {'zh': '拖拽选取BG区域', 'en': 'Drag to Select BG'},
    'bg_roi_clear':       {'zh': '清除ROI', 'en': 'Clear ROI'},
    'bg_not_selected':    {'zh': '未选取', 'en': 'Not Selected'},
    'bg_roi_mode_label':  {'zh': '（ROI模式）', 'en': '(ROI Mode)'},
    'bg_roi_coords':      {'zh': '列', 'en': 'Col'},
    'bg_roi_rows':        {'zh': '行', 'en': 'Row'},

    # --- Categories ---
    'category_ops':       {'zh': '分类操作', 'en': 'Category Ops'},
    'remove_btn':         {'zh': '移除按钮', 'en': 'Remove'},

    # --- Status bar ---
    'ready':              {'zh': '就绪', 'en': 'Ready'},
    'bg_roi_drag_hint':   {'zh': '拖拽选取背景 ROI 区域，释放鼠标完成选取，右键取消', 'en': 'Drag to select BG ROI, right-click to cancel'},
    'bg_roi_too_small':   {'zh': 'ROI 太小，请重新拖拽', 'en': 'ROI too small, try again'},
    'step1_hint':         {'zh': '【步骤1/2】请点击左上角(或任意一角)确定起始点...', 'en': '[Step 1/2] Click a corner to set start point...'},
    'step2_hint':         {'zh': '【步骤2/2】请点击对角线位置确定结束点...', 'en': '[Step 2/2] Click diagonal corner to set end point...'},
    'roi_locked':         {'zh': '区域已锁定', 'en': 'ROI locked'},
    'bg_processing':      {'zh': '后台处理:', 'en': 'Processing:'},
    'mode_copy_short':    {'zh': '复制', 'en': 'copied'},
    'mode_move_short':    {'zh': '移动', 'en': 'moved'},
    'save_image_suffix':  {'zh': ' (+图)', 'en': ' (+img)'},
    'file_saved_status':  {'zh': '已保存:', 'en': 'Saved:'},
    'annot_mode_status':  {'zh': '标注模式:', 'en': 'Annotate:'},
    'annot_cancel_hint':  {'zh': '右键取消当前操作', 'en': 'Right-click to cancel'},
    'scan_frame_status':  {'zh': 'Scan 帧', 'en': 'Scan Frame'},

    # --- Annotation panel ---
    'annot_win_title':    {'zh': '标注工具', 'en': 'Annotate'},
    'draw_tools':         {'zh': '绘制工具', 'en': 'Drawing Tools'},
    'tool_hline':         {'zh': '水平线', 'en': 'H-Line'},
    'tool_vline':         {'zh': '垂直线', 'en': 'V-Line'},
    'tool_line':          {'zh': '自由直线', 'en': 'Line'},
    'tool_arrow':         {'zh': '箭头', 'en': 'Arrow'},
    'tool_text':          {'zh': '文字标注', 'en': 'Text'},
    'tool_point':         {'zh': '圆点标记', 'en': 'Point'},
    'style_settings':     {'zh': '样式设置', 'en': 'Style Settings'},
    'color_label':        {'zh': '颜色:', 'en': 'Color:'},
    'custom_color':       {'zh': '自定义…', 'en': 'Custom…'},
    'pick_color_title':   {'zh': '选择颜色', 'en': 'Pick Color'},
    'linewidth_label':    {'zh': '线宽:', 'en': 'Width:'},
    'linestyle_label':    {'zh': '线型:', 'en': 'Style:'},
    'ls_solid':           {'zh': '实线', 'en': 'Solid'},
    'ls_dashed':          {'zh': '虚线', 'en': 'Dashed'},
    'ls_dotted':          {'zh': '点线', 'en': 'Dotted'},
    'ls_dashdot':         {'zh': '点划', 'en': 'DashDot'},
    'alpha_label':        {'zh': '透明度:', 'en': 'Alpha:'},
    'text_edit_title':    {'zh': '文字标注编辑', 'en': 'Text Annotation Editor'},
    'content_label':      {'zh': '内容:', 'en': 'Content:'},
    'fontsize_label':     {'zh': '字体大小:', 'en': 'Font Size:'},
    'text_place_hint':    {'zh': '点击图上放置文字；放置后可拖动位置', 'en': 'Click on image to place text; drag to move'},
    'apply_text_btn':     {'zh': '应用字体/内容到选中文字', 'en': 'Apply to Selected'},
    'dblclick_hint':      {'zh': '（双击文字可选中）', 'en': '(Double-click text to select)'},
    'undo_btn':           {'zh': '撤销上一条', 'en': 'Undo'},
    'clear_annot_btn':    {'zh': '清空所有', 'en': 'Clear All'},
    'exit_annot_btn':     {'zh': '退出标注', 'en': 'Exit'},
    'annot_status_init':  {'zh': '请选择工具后在图像上点击', 'en': 'Select a tool, then click on image'},
    'annot_tip_hline':    {'zh': '单击图上任意位置，添加水平线（线型由左侧线型决定）', 'en': 'Click anywhere, add horizontal line'},
    'annot_tip_vline':    {'zh': '单击图上任意位置，添加垂直线（线型由左侧线型决定）', 'en': 'Click anywhere, add vertical line'},
    'annot_tip_line':     {'zh': '单击起点，再单击终点，绘制直线（右键取消）', 'en': 'Click start, then end, draw line (Right-click cancel)'},
    'annot_tip_arrow':    {'zh': '单击起点，再单击终点，绘制箭头（右键取消）', 'en': 'Click start, then end, draw arrow (Right-click cancel)'},
    'annot_tip_text':     {'zh': '左键单击空白处，放置新文字；右键点击已有文字，实时编辑', 'en': 'Left-click empty, place text; Right-click text, edit'},
    'annot_tip_point':    {'zh': '单击图上任意位置，放置圆点标记', 'en': 'Click anywhere, place point marker'},
    'annot_start_picked': {'zh': '已选起点，请点击终点（右键取消）', 'en': 'Start point set, click end point (Right-click cancel)'},
    'annot_tip_line_2':   {'zh': '点击起点，再点击终点，绘制直线', 'en': 'Click start, then end to draw line'},
    'annot_tip_arrow_2':  {'zh': '点击起点，再点击终点，绘制箭头', 'en': 'Click start, then end to draw arrow'},
    'text_annot_title':   {'zh': '文字标注', 'en': 'Text Annotation'},
    'text_annot_prompt':  {'zh': '请输入要标注的文字\n（也可在面板框中预先填写）:', 'en': 'Enter annotation text\n(or pre-fill in panel):'},

    # --- Messageboxes ---
    'msg_warn':           {'zh': '警告', 'en': 'Warning'},
    'msg_hint':           {'zh': '提示', 'en': 'Hint'},
    'msg_error':          {'zh': '错误', 'en': 'Error'},
    'msg_input_error':    {'zh': '输入错误', 'en': 'Input Error'},
    'msg_success':        {'zh': '成功', 'en': 'Success'},
    'msg_done':           {'zh': '完成', 'en': 'Done'},
    'msg_removed':        {'zh': '已移除', 'en': 'Removed'},
    'msg_export_fail':    {'zh': '导出失败', 'en': 'Export Failed'},
    'msg_save_fail':      {'zh': '保存失败', 'en': 'Save Failed'},
    'msg_bg_error':       {'zh': '后台错误', 'en': 'Background Error'},
    'msg_h5_error':       {'zh': 'H5错误', 'en': 'H5 Error'},
    'msg_import_ok':      {'zh': '导入成功', 'en': 'Import Success'},

    'msg_no_h5':          {'zh': '请先选择一个有效的 H5 文件。', 'en': 'Please select a valid H5 file first.'},
    'msg_no_pylake':      {'zh': '未安装 lumicks.pylake，无法导出。', 'en': 'lumicks.pylake not installed, cannot export.'},
    'msg_no_force':       {'zh': "文件中未找到 'Force HF' 数据", 'en': "'Force HF' data not found in file"},
    'msg_no_channel':     {'zh': '未选择任何通道', 'en': 'No channel selected'},
    'msg_export_ok':      {'zh': '导出完成！', 'en': 'Export complete!'},
    'msg_crop_h5_only':   {'zh': '仅 H5 文件支持裁剪', 'en': 'Only H5 files support cropping'},
    'msg_removed_cat':    {'zh': '分类按钮已移除。', 'en': 'Category button removed.'},
    'msg_load_first':     {'zh': '请先加载文件', 'en': 'Please load a file first'},
    'msg_no_kymo_scan':   {'zh': '文件中未找到 Kymograph 或 Scan 数据', 'en': 'No Kymograph or Scan data found in file'},
    'msg_empty_scan':     {'zh': 'Scan 数据为空', 'en': 'Scan data is empty'},
    'msg_imported_paths': {'zh': '已添加', 'en': 'Added'},
    'msg_paths_suffix':   {'zh': '个路径', 'en': 'paths'},
    'msg_save_ok':        {'zh': '已保存至:', 'en': 'Saved to:'},
    'msg_bg_err_detail':  {'zh': '文件:', 'en': 'File:'},
    'msg_bg_err_label':   {'zh': '错误:', 'en': 'Error:'},

    # --- File dialogs ---
    'fd_select_dir':      {'zh': '选择单个文件夹', 'en': 'Select Folder'},
    'fd_select_parent':   {'zh': '选择父目录', 'en': 'Select Parent Directory'},

    # --- Tree tooltip ---
    'tt_file':            {'zh': '文件:', 'en': 'File:'},
    'tt_location':        {'zh': '位置:', 'en': 'Location:'},

    # --- Text edit dialog (双击编辑文字) ---
    'te_fontsize':        {'zh': '字号:', 'en': 'Size:'},
    'te_custom':          {'zh': '自定义', 'en': 'Custom'},
    'te_pick_color':      {'zh': '选择文字颜色', 'en': 'Pick Text Color'},
    'te_delete':          {'zh': '删除此标注', 'en': 'Delete'},
    'te_confirm':         {'zh': '确定', 'en': 'OK'},

    # --- Stitcher extras ---
    'stitch_loading':     {'zh': '载入主界面…', 'en': 'Loading main UI…'},
    'stitch_segments':    {'zh': '拼接段数:', 'en': 'Segments:'},
}


def _tr(lang, key):
    """Return translated text for *key* in *lang* ('zh' or 'en')."""
    entry = I18N.get(key)
    if entry is None:
        return key
    return entry.get(lang, entry.get('zh', key))


# --- 自定义稳定版滚动框架 (替代 ttkbootstrap 版) ---
class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        
        # 定义 Canvas 和 滚动条
        self.canvas = tk.Canvas(self, highlightthickness=0, borderwidth=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        
        # 内部容器 Frame
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # 监听内部 Frame 大小变化，更新滚动区域
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        # 在 Canvas 中创建窗口
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # 监听 Canvas 大小变化，强制内部 Frame 宽度自适应 (实现类似 sticky='ew' 效果)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # 绑定鼠标滚轮
        self.bind_mouse_scroll()
        
        # 尝试匹配主题背景色 (获取 TFrame 的背景色)
        try:
            style = ttk.Style()
            bg = style.lookup('TFrame', 'background')
            if bg:
                self.canvas.configure(bg=bg)
        except:
            pass

    def _on_canvas_configure(self, event):
        # 设置内部窗口宽度等于 Canvas 宽度
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def bind_mouse_scroll(self):
        # 绑定滚轮事件
        # 注意：这里使用 bind_all 可能会影响全局，但在这种简单布局中通常是安全的
        # 或者可以使用 bind("<Enter>") / unbind("<Leave>") 策略
        self.canvas.bind("<Enter>", self._bound_to_mousewheel)
        self.canvas.bind("<Leave>", self._unbound_to_mousewheel)
        self.scrollable_frame.bind("<Enter>", self._bound_to_mousewheel)
        self.scrollable_frame.bind("<Leave>", self._unbound_to_mousewheel)

    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        try:
            # Windows 下 event.delta 通常是 120 的倍数
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        except:
            pass
            
    # 为了兼容旧代码，提供 container 属性指向内部 Frame
    @property
    def container(self):
        return self.scrollable_frame


# --- Tooltip ---
class ToolTip(object):
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        self.text = text
        if self.tipwindow or not self.text: return
        try:
            x = self.widget.winfo_pointerx() + 10
            y = self.widget.winfo_pointery() + 10
            self.tipwindow = tw = tk.Toplevel(self.widget)
            tw.wm_overrideredirect(1)
            tw.wm_geometry("+%d+%d" % (x, y))
            label = tk.Label(tw, text=self.text, justify=LEFT, background="#FFFFFF",
                             relief=SOLID, borderwidth=1,
                             font=("Segoe UI", 10), foreground="#333333")
            label.pack(ipadx=2)
        except: pass

    def hidetip(self):
        tw = self.tipwindow; self.tipwindow = None
        if tw: tw.destroy()

class StitcherWindow(ttk.Toplevel):
    """
    Multi-Kymograph Stitcher
    ─────────────────────────
     支持任意数量的 H5 文件按顺序拼接（沿时间轴）
     每个文件独立设置亮度增益
     大文件优化：分块写入临时 memmap，避免全量 hstack 撑爆内存
     拼接在后台线程执行，进度实时回报到日志
    """

    def __init__(self, master_app):
        super().__init__()
        self.master_app = master_app
        self.title("Kymograph Stitcher  Multi-File (Time Axis)")
        self.geometry("780x660")
        self.minsize(620, 500)
        self.resizable(True, True)

        # 文件条目列表  [{'path_var': StringVar, 'gain_var': DoubleVar, 'frame': Frame}, ...]
        self._entries = []

        self._build_ui()
        self._add_file_entry()   # 默认先加一行
        self._add_file_entry()   # 第二行

        self.log(self.tr('stitch_ready'))

    # ───────────────────── UI ─────────────────────

    def tr(self, key):
        lang = getattr(self.master_app, 'lang', 'zh') if self.master_app else 'zh'
        return _tr(lang, key)


    def _build_ui(self):
        pad = {'padx': 10, 'pady': 4}

        # 顶部标题
        ttk.Label(self, text=self.tr('stitch_hint'),
                  font=('Segoe UI', 10, 'bold'), bootstyle="primary").pack(anchor='w', **pad)

        # ── 文件列表区（可滚动）──
        list_outer = ttk.Labelframe(self, text=self.tr('file_list'), padding=6, bootstyle="primary")
        list_outer.pack(fill='both', expand=True, padx=10, pady=4)

        self._scroll_frame = ScrollableFrame(list_outer)
        self._scroll_frame.pack(fill='both', expand=True)
        self._entries_container = self._scroll_frame.container  # 实际的内框

        # ── 操作按钮行 ──
        btn_row = ttk.Frame(self)
        btn_row.pack(fill='x', padx=10, pady=(4, 0))
        ttk.Button(btn_row, text=self.tr('add_file'), command=self._add_file_entry,
                   bootstyle="", width=14).pack(side='left', padx=(0, 6))
        ttk.Button(btn_row, text=self.tr('remove_last'), command=self._remove_last_entry,
                   bootstyle="", width=14).pack(side='left')

        ttk.Button(btn_row, text=self.tr('start_stitch'), command=self.start_thread,
                   bootstyle="", width=18).pack(side='right')

        # ── 日志区 ──
        ttk.Label(self, text=self.tr('log_label'), font=('Segoe UI', 10, 'bold')).pack(anchor='w', padx=10, pady=(6, 0))
        self.log_text = tk.Text(self, height=10, state='disabled', font=("Consolas", 9))
        self.log_text.pack(fill='both', expand=False, padx=10, pady=(2, 8))

    def _add_file_entry(self):
        """在列表底部追加一行文件条目"""
        idx = len(self._entries)
        path_var = tk.StringVar()
        gain_var = tk.DoubleVar(value=1.0)

        row = ttk.Frame(self._entries_container)
        row.pack(fill='x', pady=2)

        # 序号标签
        lbl = ttk.Label(row, text=f"#{idx+1}", width=3,
                        font=('Segoe UI', 10, 'bold'), bootstyle="primary")
        lbl.pack(side='left', padx=(2, 4))

        # 路径输入框
        ent = ttk.Entry(row, textvariable=path_var)
        ent.pack(side='left', fill='x', expand=True)

        # 浏览按钮
        ttk.Button(row, text="…", width=3,
                   command=lambda v=path_var: self._browse(v)).pack(side='left', padx=3)

        # 增益输入
        ttk.Label(row, text="Gain:", font=('Segoe UI', 9)).pack(side='left', padx=(4, 1))
        ttk.Spinbox(row, textvariable=gain_var, from_=0.01, to=500.0,
                    increment=0.1, width=6, format='%.2f').pack(side='left')

        self._entries.append({'path_var': path_var, 'gain_var': gain_var, 'frame': row})

    def _remove_last_entry(self):
        if len(self._entries) <= 2:
            messagebox.showwarning(self.tr('msg_hint'), self.tr('stitch_warn_min'))
            return
        entry = self._entries.pop()
        entry['frame'].destroy()

    def _browse(self, var):
        path = filedialog.askopenfilename(
            filetypes=[("HDF5 Files", "*.h5"), ("All Files", "*.*")])
        if path:
            var.set(path)

    def log(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

    # ─────────────── Thread Entry ───────────────

    def start_thread(self):
        threading.Thread(target=self._run_stitch_safe, daemon=True).start()

    def _run_stitch_safe(self):
        try:
            self.run_stitch()
        except Exception as e:
            self.after(0, lambda: self.log(f" 未捕获异常: {e}"))
            traceback.print_exc()
            try:
                messagebox.showerror("Error", str(e))
            except Exception:
                pass

    # ──────────────── Helpers ───────────────────

    @staticmethod
    def get_kymo_pixels(kymo, channel="green"):
        attr_name = f"{channel}_image"
        if hasattr(kymo, attr_name):
            return getattr(kymo, attr_name)
        elif hasattr(kymo, "get_image"):
            try:
                return kymo.get_image(channel)
            except Exception:
                return None
        return None

    @staticmethod
    def load_kymo_from_h5(h5_path):
        f = lk.File(h5_path)
        keys = list(f.kymos.keys())
        if not keys:
            raise ValueError(f"No kymographs found in {h5_path}")
        return f.kymos[keys[0]]

    @staticmethod
    def _resample_cols(img, current_lt, target_lt):
        """沿列（时间）轴重采样，使不同 line_time 的 kymograph 对齐。
        大数组时使用分块操作，减少峰值内存。"""
        if img is None:
            return None
        if np.isclose(current_lt, target_lt, rtol=1e-5):
            return img
        if current_lt > target_lt:
            # 慢  快：重复列（像素内插最简单的近邻）
            ratio = current_lt / target_lt
            repeat = max(1, int(round(ratio)))
            out = np.repeat(img, repeat, axis=1)
            return (out / repeat).astype(img.dtype)
        else:
            # 快  慢：binning（求和后除以 bin_size）
            bin_size = max(1, int(round(target_lt / current_lt)))
            n_rows, n_cols = img.shape
            new_cols = n_cols // bin_size
            if new_cols == 0:
                return img
            trimmed = img[:, :new_cols * bin_size]
            # reshape + mean，分行处理以控制内存
            out = trimmed.reshape(n_rows, new_cols, bin_size).mean(axis=2)
            return out

    # ─────────────── Core Stitch ────────────────

    def run_stitch(self):
        import tempfile, os

        # ── 收集有效路径 ──
        paths  = []
        gains  = []
        for e in self._entries:
            p = e['path_var'].get().strip().strip('"').strip("'")
            if p:
                paths.append(p)
                gains.append(e['gain_var'].get())

        if len(paths) < 2:
            messagebox.showwarning(self.tr('msg_input_error'), self.tr('stitch_err_min_h5'))
            return

        self.after(0, lambda: self.log("=" * 40))
        self.after(0, lambda: self.log(f"共 {len(paths)} 个文件，开始拼接…"))

        # ── 智能命名 ──
        def parse_name(name):
            m = re.search(r'(\d{8})-(\d{6})\s*Kymograph\s*(\d+)', name, re.IGNORECASE)
            if m:
                return {'date': m.group(1), 'time': m.group(2),'id': m.group(3),'short': f"{m.group(2)}_K{m.group(3)}"}
            return {'date': None, 'short': name}

        names_raw = [os.path.splitext(os.path.basename(p))[0] for p in paths]
        infos     = [parse_name(n) for n in names_raw]
        dates     = [i['date'] for i in infos]
        shared_date = dates[0] if all(d == dates[0] and d for d in dates) else None

        if shared_date:
            parts_str = " + ".join(f"{i['time']} K{i['id']}" for i in infos)
            plot_title = f"Stitch: {parts_str} (Date: {shared_date})"
        else:
            plot_title = "Stitch: " + " + ".join(i['short'] for i in infos)

        safe_filename = re.sub(r'[\\/*?:"<>|\n\r]', '_', plot_title).replace('__', '_').strip()

        # ── 逐文件加载并确定公共参数 ──
        kymos = []
        line_times = []
        for i, p in enumerate(paths):
            msg = f"[{i+1}/{len(paths)}] 加载: {names_raw[i]}"
            self.after(0, lambda m=msg: self.log(m))
            k = self.load_kymo_from_h5(p)
            kymos.append(k)
            line_times.append(k.line_time_seconds)

        target_lt = min(line_times)
        self.after(0, lambda: self.log(f"目标 line_time = {target_lt:.6f} s"))

        # ── 获取公共高度（取最小值）──
        CHANNELS = ['red', 'green', 'blue']
        valid_h = None
        for k in kymos:
            for ch in CHANNELS:
                d = self.get_kymo_pixels(k, ch)
                if d is not None:
                    valid_h = d.shape[0] if valid_h is None else min(valid_h, d.shape[0])

        if valid_h is None:
            self.after(0, lambda: self.log(" 没有找到有效图像通道"))
            return

        # ── 预先计算每段重采样后的列数 & stitch 时间列表 ──
        col_counts = []   # 重采样后各段列数
        stitch_times = [] # 各分割线的绝对时间（秒）
        cumulative_cols = 0

        for i, (k, lt, gain) in enumerate(zip(kymos, line_times, gains)):
            # 取一个通道估算列数
            ref_ch = None
            for ch in CHANNELS:
                d = self.get_kymo_pixels(k, ch)
                if d is not None:
                    ref_ch = d
                    break
            if ref_ch is None:
                col_counts.append(0)
                continue
            resampled = self._resample_cols(ref_ch, lt, target_lt)
            n_cols = resampled.shape[1]
            col_counts.append(n_cols)
            if i > 0:
                stitch_times.append(cumulative_cols * target_lt)
            cumulative_cols += n_cols

        total_cols = sum(col_counts)
        self.after(0, lambda: self.log(
            f"拼接尺寸: {valid_h} 行 × {total_cols} 列  "
            f"({valid_h * total_cols * 4 / 1024**2:.1f} MB per channel)"))

        # ── 大文件阈值：超过 200 MB (单通道 float32) 使用 memmap 中转 ──
        USE_MEMMAP = (valid_h * total_cols * 4) > 200 * 1024 * 1024
        if USE_MEMMAP:
            self.after(0, lambda: self.log(" 大文件模式：使用 memmap 分块写入，避免内存峰值"))

        # ── 分通道拼接 ──
        final_arrays = {}
        tmp_files = []

        for ch in CHANNELS:
            self.after(0, lambda c=ch: self.log(f"   处理通道 {c}…"))

            if USE_MEMMAP:
                tmp_f = tempfile.NamedTemporaryFile(suffix='.dat', delete=False)
                tmp_f.close()
                tmp_files.append(tmp_f.name)
                out_arr = np.memmap(tmp_f.name, dtype='float32', mode='w+',
                                    shape=(valid_h, total_cols))
            else:
                out_arr = np.empty((valid_h, total_cols), dtype='float32')

            col_offset = 0
            has_data = False
            for i, (k, lt, gain, n_cols) in enumerate(zip(kymos, line_times, gains, col_counts)):
                if n_cols == 0:
                    continue
                d = self.get_kymo_pixels(k, ch)
                if d is None:
                    # 通道不存在，填零
                    out_arr[:, col_offset:col_offset + n_cols] = 0
                    col_offset += n_cols
                    continue
                has_data = True
                seg = self._resample_cols(d.astype('float32'), lt, target_lt)
                seg = seg[:valid_h, :n_cols] * float(gain)
                out_arr[:, col_offset:col_offset + seg.shape[1]] = seg
                col_offset += seg.shape[1]

                pct = int((i + 1) / len(kymos) * 100)
                self.after(0, lambda c=ch, p=pct: self.log(f"    通道 {c}: {p}%"))

            if has_data:
                final_arrays[ch] = np.array(out_arr)  # 拷贝到普通 ndarray

            # 删临时文件
            if USE_MEMMAP:
                del out_arr
                try:
                    os.unlink(tmp_files[-1])
                    tmp_files.pop()
                except Exception:
                    pass

        if not final_arrays:
            self.after(0, lambda: self.log(" 所有通道均无有效数据"))
            return

        # ── 保存 NPZ ──
        save_dir = os.path.dirname(paths[0])
        save_path = os.path.join(save_dir, f"{safe_filename}.npz")

        self.after(0, lambda: self.log(" 正在写入 NPZ（压缩存储）…"))
        np.savez_compressed(
            save_path,
            line_time=target_lt,
            pixel_size=0.1,
            stitch_times=np.array(stitch_times, dtype='float64'),
            **final_arrays
        )
        self.after(0, lambda: self.log(f" 已保存: {os.path.basename(save_path)}"))

        # ── 自动载入主界面 ──
        self.after(0, lambda: self.log(self.tr('stitch_loading')))
        self.master_app.after(0, lambda: self.master_app.load_stitched_data(save_path))

        try:
            messagebox.showinfo(self.tr('msg_done'), self.tr('stitch_done') + f"\n\n{self.tr('tt_file')} {os.path.basename(save_path)}\n{self.tr('stitch_segments')} {len(paths)}")
        except Exception:
            pass
class ModernKymographSorter(ttk.Window):
    def __init__(self):
        super().__init__(themename="morph")
        self.title("Kymograph & Scan Sorter Pro v43.0 (ROI BG + Multi-Frame Scan + i18n)")
        self.geometry("1900x1200") 
        self.minsize(1200, 900)




        # --- 统一配色：#F8F8F8 主背景 + #FFFFFF 面板/卡片 + 浅灰过渡 ---
        self._BG = '#F8F8F8'    # 全局主背景（浅灰）
        self._FG = '#333333'    # 文字颜色
        self._CARD = '#FFFFFF'  # 卡片/面板背景（纯白）
        self._BD = '#EEEEEE'    # 边框色（极浅灰，接近白）
        self._ACCENT = '#888888'# 强调色（中性灰，替代蓝）

        _BG = self._BG
        _FG = self._FG
        _CARD = self._CARD
        _BD = self._BD
        _ACCENT = self._ACCENT

        self.configure(background=_BG)

        # ===== 全局覆盖：将 morph 主题默认的 #D9E3F1 全部替换为白色 =====
        _ALL_BG_STATES = [
            ('active', _BG), ('pressed', _BG), ('hover', _BG),
            ('focus', _BG), ('disabled', _BG), ('!disabled', _BG),
            ('selected', _BG), ('alternate', _BG),
        ]
        _CARD_BG_STATES = [
            ('active', _CARD), ('pressed', _CARD), ('hover', _CARD),
            ('focus', _CARD), ('disabled', _CARD), ('!disabled', _CARD),
        ]

        # --- 批量覆盖所有 ttkbootstrap bootstyle 变体的背景 ---
        _BOOTSTYLE_SUFFIXES = [
            '', '.primary', '.secondary', '.info', '.success',
            '.warning', '.danger',
            '.outline-primary', '.outline-secondary', '.outline-info',
            '.outline-success', '.outline-warning', '.outline-danger',
            '.link', '.light', '.dark',
            '-outline', '-primary-outline', '-secondary-outline',
            '-info-outline', '-success-outline', '-warning-outline',
            '-danger-outline',
            '-round-toggle', '-square-toggle',
            '-round-toggle.primary', '-round-toggle.success',
            '-round-toggle.info', '-round-toggle.warning', '-round-toggle.danger',
        ]
        _BASE_WIDGETS = [
            'TButton', 'TLabelframe', 'TCheckbutton', 'TRadiobutton',
            'TLabel', 'TFrame', 'TEntry', 'TSpinbox', 'TScale', 'TProgressbar',
        ]

        import re as _re
        _d9e3f1_pat = _re.compile(r'^#D9[Ee]3[Ff]1$')
        for _wname in _BASE_WIDGETS:
            for _suf in _BOOTSTYLE_SUFFIXES:
                _full_name = _wname + _suf
                try:
                    if _d9e3f1_pat.match(self.style.lookup(_full_name, 'background') or ''):
                        self.style.map(_full_name, background=_ALL_BG_STATES)
                except Exception:
                    pass

        # Labelframe 系列统一为白色卡片
        for _suf in _BOOTSTYLE_SUFFIXES:
            try:
                self.style.map('TLabelframe' + _suf, background=_CARD_BG_STATES)
            except Exception:
                pass
        self.style.map('TLabelframe', background=_CARD_BG_STATES)

        # ===== 显式配置关键样式 =====

        # 全局默认
        self.style.configure('.', background=_BG, foreground=_FG)

        # TFrame / TLabel
        self.style.configure('TFrame', background=_BG)
        self.style.configure('TLabel', background=_BG, foreground=_FG)

        # ===== TButton 全系列：灰底 + 黑字（彻底消除蓝/白底） =====
        _BTN_SUFFIXES = [
            '', '.primary', '.secondary', '.info', '.success',
            '.warning', '.danger',
            '.outline-primary', '.outline-secondary', '.outline-info',
            '.outline-success', '.outline-warning', '.outline-danger',
            '.link', '.light', '.dark',
            '-outline', '-primary-outline', '-secondary-outline',
            '-info-outline', '-success-outline', '-warning-outline',
            '-danger-outline',
            '-round-toggle', '-square-toggle',
            '-round-toggle.primary', '-round-toggle.success',
            '-round-toggle.info', '-round-toggle.warning', '-round-toggle.danger',
            '-square-toggle.primary', '-square-toggle.success',
            '-square-toggle.info', '-square-toggle.warning', '-square-toggle.danger',
            '-toolbutton', '.striped',
        ]
        for _bs in _BTN_SUFFIXES:
            try:
                self.style.configure('TButton' + _bs,
                                     background=_BG, foreground='#000000',
                                     bordercolor=_BD, focuscolor=_BG,
                                     font=('Segoe UI', 11))
                # 清除 ttkbootstrap 内置的按钮背景图片（彻底去蓝）
                self.style.element_create('TButton' + _bs + '.background', 'from', 'clam')
                self.style.map('TButton' + _bs,
                               background=[('active', _BG), ('pressed', _BD),
                                           ('hover', _BG), ('disabled', _CARD)],
                               bordercolor=[('active', _BD), ('pressed', _BD),
                                            ('hover', _BD), ('disabled', _BD)])
            except Exception:
                pass
        # 基础 TButton 也覆盖
        self.style.configure('TButton', background=_BG, foreground='#000000',
                             bordercolor=_BD, focuscolor=_BG,
                             font=('Segoe UI', 11))
        try:
            self.style.element_create('TButton.background', 'from', 'clam')
        except Exception:
            pass
        self.style.map('TButton', background=[('active', _BG), ('pressed', _BD),
                                              ('hover', _BG), ('disabled', _CARD)],
                       bordercolor=[('active', _BD), ('pressed', _BD),
                                    ('hover', _BD), ('disabled', _BD)])

        # ===== TLabelframe 全系列：白底 + 纯灰边框（彻底消除蓝） =====
        _LF_SUFFIXES = [
            '', '.primary', '.secondary', '.info', '.success',
            '.warning', '.danger',
            '.outline-primary', '.outline-secondary', '.outline-info',
            '.outline-success', '.outline-warning', '.outline-danger',
            '-outline', '-primary-outline', '-secondary-outline',
            '-info-outline', '-success-outline', '-warning-outline',
            '-danger-outline',
        ]
        for _bs in _LF_SUFFIXES:
            try:
                self.style.configure('TLabelframe' + _bs,
                                     background=_CARD,
                                     bordercolor=_BD,
                                     lightcolor=_BD,
                                     darkcolor=_BD,
                                     relief='solid',
                                     borderwidth=1)
                self.style.configure('TLabelframe' + _bs + '.Label',
                                     background=_CARD, foreground=_FG,
                                     font=('Segoe UI', 12, 'bold'))
                self.style.map('TLabelframe' + _bs, background=_CARD_BG_STATES)
                self.style.map('TLabelframe' + _bs + '.Label', background=_CARD_BG_STATES)
            except Exception:
                pass
        # 基础 TLabelframe
        self.style.configure('TLabelframe',
                             background=_CARD,
                             bordercolor=_BD,
                             lightcolor=_BD,
                             darkcolor=_BD,
                             relief='solid',
                             borderwidth=1)
        self.style.configure('TLabelframe.Label', background=_CARD, foreground=_FG,
                             font=('Segoe UI', 12, 'bold'))
        self.style.map('TLabelframe', background=_CARD_BG_STATES)
        self.style.map('TLabelframe.Label', background=_CARD_BG_STATES)

        # ===== TFrame 也全系列覆盖（防止内部嵌套 frame 残留蓝底） =====
        _FRAME_SUFFIXES = [
            '', '.primary', '.secondary', '.info', '.success',
            '.warning', '.danger', '.card', '.border',
        ]
        for _bs in _FRAME_SUFFIXES:
            try:
                self.style.configure('TFrame' + _bs, background=_BG)
            except Exception:
                pass

        # Treeview (文件列表) — 白底
        self.style.configure('Treeview', background=_CARD, fieldbackground=_CARD,
                             foreground=_FG, font=('Segoe UI', 11), rowheight=30)
        self.style.configure('Treeview.Heading', background=_BG, foreground=_FG,
                             font=('Segoe UI', 12, 'bold'))
        self.style.map('Treeview.Heading', background=_ALL_BG_STATES)
        # Treeview 选中行也用浅灰而非蓝色
        self.style.map('Treeview', background=[('selected', '#F0F0F0')])

        # Panedwindow / Scrollbar / Separator
        self.style.configure('TPanedwindow', background=_BD)
        self.style.configure('TScrollbar', background=_BG, troughcolor=_BD)
        self.style.configure('TSeparator', background=_BD)

        # Checkbutton / Radiobutton — 全系列去蓝
        _CB_SUFFIXES = [
            '', '.primary', '.secondary', '.info', '.success',
            '.warning', '.danger', '.outline-primary', '.outline-secondary',
            '.outline-info', '.outline-success', '.outline-warning', '.outline-danger',
            '-round-toggle', '-square-toggle', '-round-toggle.primary',
            '-round-toggle.success', '-round-toggle.info', '-round-toggle.warning',
            '-round-toggle.danger', '-square-toggle.primary', '-square-toggle.success',
            '-square-toggle.info', '-square-toggle.warning', '-square-toggle.danger',
            '-toolbutton', '.round-toggle', '.square-toggle',
        ]
        for _bs in _CB_SUFFIXES:
            try:
                self.style.configure('TCheckbutton' + _bs, background=_BG, foreground=_FG)
                self.style.configure('TRadiobutton' + _bs, background=_BG, foreground=_FG)
            except Exception:
                pass
        self.style.configure('TCheckbutton', background=_BG, foreground=_FG)
        self.style.configure('TRadiobutton', background=_BG, foreground=_FG)

        # TSpinbox / TEntry 边框也统一
        self.style.configure('TSpinbox', fieldbackground=_CARD, foreground=_FG,
                             arrowsbackground=_BG, bordercolor=_BD)
        self.style.configure('TEntry', fieldbackground=_CARD, insertcolor=_FG)

        # Scale / Progressbar
        self.style.configure('TScale', background=_BG, troughcolor=_BD)
        self.style.configure('TProgressbar', background='#AAAAAA', troughcolor=_BD)

        # Notebook（标签页）
        self.style.configure('TNotebook', background=_BG)
        self.style.configure('TNotebook.Tab', background=_BG, foreground=_FG)
        self.style.map('TNotebook.Tab', background=[
            ('selected', _CARD), ('active', _BG),
        ])


        # 数据存储
        self.input_dirs = []
        self.all_images_data = [] 
        self.current_index = -1
        self.categories = {} 
        self.category_buttons = {}
        self.file_status_map = {} 
        self.operation_mode = tk.StringVar(value="copy")
        
        # 开关
        self.save_kymo_var = tk.BooleanVar(value=False)
        
        # H5 数据
        self.h5_data = {'red': None, 'green': None, 'blue': None,'max_r': 1, 'max_g': 1, 'max_b': 1,'force_t': None, 'force_v': None} 
        # metadata 新增 is_scan 字段
        self.h5_metadata = {'duration': 0, 'width': 0, 'is_scan': False}
        self.is_h5_mode = False
        self.current_file_path = None
        self.current_extent = None

        # Scan 多帧导航
        self._scan_frames = []          # [{red, green, blue, max_r, max_g, max_b}, ...]
        self._scan_frame_idx = tk.IntVar(value=1)    # 当前帧 (1-based, 给 Spinbox 用)
        self._scan_frame_count = 0      # 总帧数
        
        # LRU 缓存
        self.data_cache = OrderedDict()
        self.CACHE_SIZE = 20
        
        # UI 变量
        self.channel_vars = {}
        self.contrast_vars = {}
        self.control_panel = None 
        self.filter_img_var = tk.BooleanVar(value=False)
        self.filter_h5_var = tk.BooleanVar(value=True)
        
        # Force Plot selection
        self.force_channel_var = tk.StringVar(value="None")
        
        # 坐标轴裁剪变量
        self.crop_enable_var = tk.BooleanVar(value=False)
        self.axis_vars = {'xmin': tk.DoubleVar(value=0),'xmax': tk.DoubleVar(value=0),'ymin': tk.DoubleVar(value=0),'ymax': tk.DoubleVar(value=0)
        }

        # 刻度设置 (Step)
        self.tick_vars = {'x_step': tk.DoubleVar(value=20.0),'y_step': tk.DoubleVar(value=1.0)
        }
        self.flip_y_var = tk.BooleanVar(value=False)
        self.aspect_equal_var = tk.BooleanVar(value=False)  # 等比锁定：scan 加载时自动 True，kymo 为 False

        # Unit Conversion
        self.y_unit_var = tk.StringVar(value="um") 
        self.dna_rise_var = tk.DoubleVar(value=0.34) 
        
        # Output Size
        self.fig_w_var = tk.DoubleVar(value=5.0)
        self.fig_h_var = tk.DoubleVar(value=4.0)

        # ---- 背景扣除 (Background Subtraction) ----
        self.bg_sub_enable_var  = tk.BooleanVar(value=False)
        # 'timezero' = 初始帧归一化, 'temporal' = 时间低百分位, 'spatial' = 空间两侧
        self.bg_mode_var        = tk.StringVar(value='timezero')
        self.bg_t0_frames_var   = tk.IntVar(value=10)           # 零点模式：取前 N 帧均值作背景
        self.bg_percentile_var  = tk.IntVar(value=10)           # 时间百分位模式：取每行最低 N% 作为背景
        self.bg_width_var       = tk.IntVar(value=10)           # 空间模式：两侧各取多少列
        self.bg_smooth_var      = tk.IntVar(value=5)            # 平滑窗口（行），0=不平滑
        # ROI 模式专用
        self.bg_roi_coords      = None          # (x1_col, y1_row, x2_col, y2_row) 像素索引，None=未选取
        self.bg_roi_stat_var    = tk.StringVar(value='median')  # 'median' | 'mean' self._bg_roi_rect_patch = None          # 图上显示的蓝色矩形 patch
        self._bg_roi_select_mode = False        # 是否处于拖拽选取状态
        self._bg_roi_press_pos   = None         # 鼠标按下时的 display 坐标
        self._bg_roi_cid_press   = None
        self._bg_roi_cid_release = None
        self._bg_roi_cid_motion  = None
        self._bg_roi_preview_patch = None       # 拖拽过程中的预览矩形

        # Force Export
        self.downsample_hz_var = tk.DoubleVar(value=100.0)

        # 点击交互变量
        self.click_mode_active = False 
        self.cid_click = None          
        self.click_points = []         
        self.temp_markers = []
        self.cursor = None 

        # ---- 标注系统 ----
        # 标注工具模式: None | 'hline' | 'vline' | 'line' | 'arrow' | 'text' | 'point' self.annot_mode = None
        self.annot_pending_points = []   # 等待第二点的临时点
        self.annotations = []            # 存储所有标注信息(dict)
        self.annot_artists = []          # 存储 matplotlib artist 对象
        self.annot_cid = None            # canvas 事件连接 id
        self.annot_preview_artist = None # 预览线条
        self.annot_move_cid = None       # 鼠标移动事件 id

        # 文字标注拖动相关
        self._dragging_text_idx = None   # 正在拖动的标注索引
        self._drag_offset = (0.0, 0.0)   # 拖动起始偏移
        self._drag_cid_press = None
        self._drag_cid_release = None
        self._drag_cid_motion = None
        self._selected_text_idx = None   # 当前选中的文字标注索引
        self._text_edit_idx = None        # 正在编辑面板中编辑的文字索引
        self._dragging_text_idx = None    # 当前正在拖动的文字索引
        self._drag_offset = (0, 0)        # 拖动偏移量

        # 标注样式变量
        self.annot_color_var = tk.StringVar(value='white')
        self.annot_linewidth_var = tk.DoubleVar(value=1.5)
        self.annot_linestyle_var = tk.StringVar(value='--')
        self.annot_fontsize_var = tk.DoubleVar(value=10.0)
        self.annot_alpha_var = tk.DoubleVar(value=0.9)

        self.tooltip = None

        # ---- I18N ----
        self.lang = "zh"

        self.create_ui()

    def reset_output_size(self):
        self.fig_w_var.set(5.0)
        self.fig_h_var.set(4.0)

    def _on_canvas_resize(self, event):
        """让 matplotlib figure 随可视化区大小自适应。"""
        if getattr(self, '_resizing_canvas', False):
            return
        try:
            self._resizing_canvas = True
            # 留出底部 toolbar 约 36 像素
            toolbar_h = 36
            w = max(event.width, 200)
            h = max(event.height - toolbar_h, 120)
            new_w = w / self.fig.dpi
            new_h = h / self.fig.dpi
            if (abs(new_w - self.fig.get_figwidth()) > 0.05 or
                    abs(new_h - self.fig.get_figheight()) > 0.05):
                self.fig.set_size_inches(new_w, new_h)
                self.canvas.draw_idle()
        finally:
            self._resizing_canvas = False

    def create_ui(self):
        main_container = ttk.Panedwindow(self, orient=HORIZONTAL)
        main_container.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # ================= 左侧栏 =================
        sidebar_frame = ttk.Frame(main_container, width=500) 
        main_container.add(sidebar_frame, weight=0)
        sidebar = ttk.Frame(sidebar_frame, padding=(0, 0, 10, 0))
        sidebar.pack(fill=BOTH, expand=True)

        # 1. 输入源
        input_frame = ttk.Labelframe(sidebar, text=self.tr('input_source'), padding=15, bootstyle="primary")
        input_frame.pack(fill=X, pady=(0, 15))
        
        btn_row = ttk.Frame(input_frame)
        btn_row.pack(fill=X, pady=(0, 10))
        ttk.Button(btn_row, text=self.tr('add_single'), command=self.add_input_dir, bootstyle="").pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        ttk.Button(btn_row, text=self.tr('batch_import'), command=self.add_batch_input_dir, bootstyle="").pack(side=LEFT, fill=X, expand=True, padx=(5, 0))
        
        dir_list_frame = ttk.Frame(input_frame)
        dir_list_frame.pack(fill=X, pady=5)
        self.input_dir_listbox = tk.Listbox(dir_list_frame, height=4, font=('Segoe UI', 10), selectmode=tk.EXTENDED)
        sb = ttk.Scrollbar(dir_list_frame, orient=VERTICAL, command=self.input_dir_listbox.yview)
        self.input_dir_listbox.configure(yscrollcommand=sb.set)
        self.input_dir_listbox.pack(side=LEFT, fill=X, expand=True)
        sb.pack(side=RIGHT, fill=Y)

        btn_row2 = ttk.Frame(input_frame)
        btn_row2.pack(fill=X, pady=(10, 5))
        ttk.Button(btn_row2, text=self.tr('remove_selected'), command=self.remove_selected_input_dir, bootstyle="").pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        ttk.Button(btn_row2, text=self.tr('clear_all'), command=self.clear_input_dirs, bootstyle="").pack(side=LEFT, fill=X, expand=True, padx=(5, 0))
        
        filter_row = ttk.Frame(input_frame)
        filter_row.pack(fill=X, pady=(5,0))
        ttk.Label(filter_row, text=self.tr('filter_label'), font=('Segoe UI', 10)).pack(side=LEFT)
        ttk.Checkbutton(filter_row, text=self.tr('filter_image'), variable=self.filter_img_var, bootstyle="round-toggle", command=self.load_all_files).pack(side=LEFT, padx=10)
        ttk.Checkbutton(filter_row, text="H5", variable=self.filter_h5_var, bootstyle="round-toggle", command=self.load_all_files).pack(side=LEFT, padx=10)

        self.lbl_stats = ttk.Label(input_frame, text=self.tr('waiting_data'), font=("Segoe UI", 10), foreground="#999999")
        self.lbl_stats.pack(anchor=W, pady=(5, 0))

        # 2. 力数据导出板块
        force_frame = ttk.Labelframe(sidebar, text=self.tr('force_export'), padding=15, bootstyle="info")
        force_frame.pack(fill=X, pady=(0, 15))
        
        f_row1 = ttk.Frame(force_frame)
        f_row1.pack(fill=X, pady=5)
        ttk.Label(f_row1, text=self.tr('downsample_hz')).pack(side=LEFT, padx=(0,10))
        ttk.Entry(f_row1, textvariable=self.downsample_hz_var, width=12).pack(side=LEFT)
        
        ttk.Button(force_frame, text=self.tr('export_force_csv'), command=self.open_force_export_window, bootstyle="").pack(fill=X, pady=(10,0))

        # 3. 文件列表
        list_frame = ttk.Labelframe(sidebar, text=self.tr('file_list_3'), padding=5, bootstyle="secondary")
        list_frame.pack(fill=BOTH, expand=True) 
        
        columns = ("filename", "folder")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.column("filename", width=300, minwidth=200, anchor="w")
        self.tree.heading("filename", text=self.tr('col_filename'))
        self.tree.column("folder", width=120, minwidth=80, anchor="center", stretch=False)
        self.tree.heading("folder", text=self.tr('col_folder'))
        
        v_scroll = ttk.Scrollbar(list_frame, orient=VERTICAL, command=self.tree.yview)
        h_scroll = ttk.Scrollbar(list_frame, orient=HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)
        
        self.tree.bind("<<TreeviewSelect>>", self.on_file_select)
        self.bind('<Up>', lambda e: self.navigate(-1))
        self.bind('<Down>', lambda e: self.navigate(1))
        
        self.tooltip = ToolTip(self.tree)
        self.tree.bind("<Motion>", self.on_tree_motion)
        self.tree.bind("<Leave>", lambda e: self.tooltip.hidetip())
        
        self.tree.tag_configure("done", foreground='#555555')
        self.tree.tag_configure("h5", foreground='#777777')
        self.tree.tag_configure("normal", foreground="#333333")

        # ================= 右侧栏 (工作区) =================
        workspace_frame = ttk.Frame(main_container)
        main_container.add(workspace_frame, weight=4)
        workspace = ttk.Frame(workspace_frame, padding=(10, 0, 0, 0))
        workspace.pack(fill=BOTH, expand=True)

        # 顶部工具栏 (单行布局，纯文字按钮，WorkBuddy 风格配色)
        top_bar = ttk.Frame(workspace)
        top_bar.pack(fill=X, pady=(0, 15))
        
        mode_frame = ttk.Frame(top_bar) 
        mode_frame.pack(side=LEFT, padx=(0, 10))
        ttk.Label(mode_frame, text="Mode:", font=("Segoe UI", 12, "bold"), foreground=self._FG).pack(side=LEFT, padx=(0, 8))
        rb_copy = ttk.Radiobutton(mode_frame, text=self.tr('mode_copy'), variable=self.operation_mode, value="copy", bootstyle="")
        rb_copy.pack(side=LEFT, padx=4)
        self._add_tooltip(rb_copy, 'tt_mode_copy')
        rb_move = ttk.Radiobutton(mode_frame, text=self.tr('mode_move'), variable=self.operation_mode, value="move", bootstyle="")
        rb_move.pack(side=LEFT, padx=4)
        self._add_tooltip(rb_move, 'tt_mode_move')

        ttk.Separator(top_bar, orient=VERTICAL).pack(side=LEFT, fill=Y, padx=8)

        btn_scan_out = ttk.Button(top_bar, text=self.tr('scan_output'), command=self.select_output_root, bootstyle="")
        btn_scan_out.pack(side=LEFT, padx=2)
        self._add_tooltip(btn_scan_out, 'tt_scan_output')
        btn_link = ttk.Button(top_bar, text=self.tr('link_folder'), command=self.link_existing_folder, bootstyle="")
        btn_link.pack(side=LEFT, padx=2)
        self._add_tooltip(btn_link, 'tt_link_folder')
        btn_stitch = ttk.Button(top_bar, text=self.tr('kymo_stitch'), command=self.open_stitcher_window, bootstyle="")
        btn_stitch.pack(side=LEFT, padx=2)
        self._add_tooltip(btn_stitch, 'tt_kymo_stitch')
        
        btn_annot = ttk.Button(top_bar, text=self.tr('annotate_tool'), command=self.open_annotation_panel, bootstyle="")
        btn_annot.pack(side=RIGHT, padx=2)
        self._add_tooltip(btn_annot, 'tt_annotate')
        btn_new_cat = ttk.Button(top_bar, text=self.tr('new_category'), command=self.create_new_category_folder, bootstyle="")
        btn_new_cat.pack(side=RIGHT, padx=2)
        self._add_tooltip(btn_new_cat, 'tt_new_category')
        btn_save = ttk.Button(top_bar, text=self.tr('save_image'), command=self.save_current_plot, bootstyle="")
        btn_save.pack(side=RIGHT, padx=2)
        self._add_tooltip(btn_save, 'tt_save_image')
        btn_lang = ttk.Button(top_bar, text=self.tr('lang_toggle'), command=self._toggle_language, bootstyle="", width=5)
        btn_lang.pack(side=RIGHT, padx=2)
        self._add_tooltip(btn_lang, 'tt_lang_toggle')


        # 底部控制区
        bottom_container = ttk.Frame(workspace)
        bottom_container.pack(side=BOTTOM, fill=X, pady=(15, 0))
        bottom_container.columnconfigure(0, weight=3)
        bottom_container.columnconfigure(1, weight=1)
        
        # [左侧区域] 控制面板
        left_control_col = ttk.Frame(bottom_container)
        left_control_col.grid(row=0, column=0, sticky="nsew", padx=(0, 15))

        # [左侧-上] 图像控制
        ctrl_frame = ttk.Labelframe(left_control_col, text=self.tr('image_display'), padding=5, bootstyle="info")
        ctrl_frame.pack(fill=X, pady=(0, 10))

        # --- 数据存储初始化 ---
        self.brightness_vars = {} 

        # --- 紧凑的 RGB 控制区 ---
        rgb_container = ttk.Frame(ctrl_frame)
        rgb_container.pack(fill=X, expand=True)

        channels_config = [
            ('Red', 'red', 'danger', 25.0), 
            ('Green', 'green', 'success', 25.0), 
            ('Blue', 'blue', 'primary', 25.0)
        ]

        for label, key, color_style, default_gain in channels_config:
            if key not in self.channel_vars:
                self.channel_vars[key] = tk.BooleanVar(value=True)
            if key not in self.contrast_vars:
                self.contrast_vars[key] = tk.DoubleVar(value=default_gain)
            if key not in self.brightness_vars:
                self.brightness_vars[key] = tk.DoubleVar(value=0.0)

            chan_frame = ttk.Labelframe(rgb_container, bootstyle=color_style, padding=5)
            chan_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=3)

            cb = ttk.Checkbutton(
                chan_frame, 
                text=label, 
                variable=self.channel_vars[key], 
                bootstyle=f"{color_style}-round-toggle",
                command=self.update_plot_content
            )
            cb.pack(side=TOP, anchor="w", pady=(0, 5))

            gain_row = ttk.Frame(chan_frame)
            gain_row.pack(fill=X)
            ttk.Label(gain_row, text="G", font=("Arial", 9, "bold"), width=2).pack(side=LEFT)
            ttk.Scale(
                gain_row, 
                from_=0.1, to=500.0, 
                variable=self.contrast_vars[key], 
                orient=HORIZONTAL, 
                command=lambda v: self.update_plot_content(),
                bootstyle=color_style
            ).pack(side=LEFT, fill=X, expand=True)

            offset_row = ttk.Frame(chan_frame)
            offset_row.pack(fill=X, pady=(5, 0))
            ttk.Label(offset_row, text="O", font=("Arial", 9, "bold"), width=2).pack(side=LEFT)
            ttk.Scale(
                offset_row, 
                from_=-5.0, to=5.0, 
                variable=self.brightness_vars[key], 
                orient=HORIZONTAL, 
                command=lambda v: self.update_plot_content(),
                bootstyle=color_style
            ).pack(side=LEFT, fill=X, expand=True)

        # --- 底部工具栏 ---
        tools_row = ttk.Frame(ctrl_frame)
        tools_row.pack(fill=X, pady=(10, 0))
        
        ttk.Button(tools_row, text=" Reset", command=self.reset_contrast, bootstyle="", width=6).pack(side=LEFT)
        ttk.Checkbutton(tools_row, text="Flip Y", variable=self.flip_y_var, bootstyle="round-toggle", command=self.update_plot_content).pack(side=LEFT, padx=(15, 5))
        ttk.Checkbutton(tools_row, text=self.tr('aspect_equal'), variable=self.aspect_equal_var, bootstyle="round-toggle", command=self.update_plot_content).pack(side=LEFT, padx=(0, 15))
        
        f_frame = ttk.Frame(tools_row)
        f_frame.pack(side=RIGHT)
        ttk.Label(f_frame, text="Force:").pack(side=LEFT)
        self.force_cb = ttk.Combobox(f_frame, textvariable=self.force_channel_var, values=['Force 1x', 'Force 1y', 'Force 2x', 'Force 2y', 'None'], width=10, state="readonly")
        self.force_cb.pack(side=LEFT, padx=(5,0))
        self.force_cb.bind("<<ComboboxSelected>>", lambda e: self.reload_and_update())

        # [左侧-下] 裁剪与刻度
        crop_frame = ttk.Labelframe(left_control_col, text=self.tr('crop_ticks'), padding=10, bootstyle="warning")
        crop_frame.pack(fill=X)
        
        c_row1 = ttk.Frame(crop_frame)
        c_row1.pack(fill=X)
        
        self.btn_select_roi = ttk.Button(c_row1, text=self.tr('two_point_roi'), command=self.toggle_click_mode, bootstyle="", width=16)
        self.btn_select_roi.pack(side=LEFT, padx=(0,15))
        self.chk_apply_crop = ttk.Checkbutton(c_row1, text=self.tr('enable_crop'), variable=self.crop_enable_var, bootstyle="round-toggle", command=self.update_plot_content)
        self.chk_apply_crop.pack(side=LEFT, padx=15)
        
        ttk.Separator(c_row1, orient=VERTICAL).pack(side=LEFT, fill=Y, padx=15)

        ttk.Label(c_row1, text="Unit:").pack(side=LEFT, padx=5)
        ttk.Radiobutton(c_row1, text="μm", variable=self.y_unit_var, value="um", command=self.update_plot_content).pack(side=LEFT, padx=2)
        self._rb_kbp = ttk.Radiobutton(c_row1, text="kbp", variable=self.y_unit_var, value="kbp", command=self.update_plot_content)
        self._rb_kbp.pack(side=LEFT, padx=2)
        self._lbl_nmbp = ttk.Label(c_row1, text="(nm/bp):")
        self._lbl_nmbp.pack(side=LEFT, padx=(10, 2))
        self._en_dna_rise = ttk.Entry(c_row1, textvariable=self.dna_rise_var, width=5)
        self._en_dna_rise.pack(side=LEFT)

        # Scan 专属提示行（加载 kymo 时隐藏）
        self._scan_info_row = ttk.Frame(crop_frame)
        ttk.Label(self._scan_info_row, text=self.tr('scan_mode'),
                  font=('Segoe UI', 9, 'bold'), foreground=self._FG).pack(side=LEFT, padx=(4, 12))
        ttk.Label(self._scan_info_row, text=self.tr('scan_hint'),
                  font=('Segoe UI', 9), foreground='#999999').pack(side=LEFT)

        # Scan 多帧导航行（仅 scan 模式 + 多帧时显示）
        self._scan_nav_row = ttk.Frame(crop_frame)
        ttk.Button(self._scan_nav_row, text=self.tr('prev_frame'),
                   bootstyle="primary-outline", width=10,
                   command=self._scan_prev_frame).pack(side=LEFT, padx=(4, 6))
        self._spn_scan_frame = ttk.Spinbox(
            self._scan_nav_row, textvariable=self._scan_frame_idx,
            from_=1, to=9999, increment=1, width=6, format='%1.0f',
            command=lambda: self._switch_scan_frame())
        self._spn_scan_frame.pack(side=LEFT, padx=(0, 4))
        self._spn_scan_frame.bind('<Return>', lambda e: self._switch_scan_frame())
        ttk.Button(self._scan_nav_row, text=self.tr('next_frame'),
                   bootstyle="primary-outline", width=10,
                   command=self._scan_next_frame).pack(side=LEFT, padx=(0, 10))
        self._lbl_scan_frame = ttk.Label(self._scan_nav_row, text=self.tr('frame_info'),
                                          font=('Segoe UI', 9, 'bold'), foreground=self._FG)
        self._lbl_scan_frame.pack(side=LEFT)


        
        c_row2 = ttk.Frame(crop_frame)
        c_row2.pack(fill=X, pady=(10,0))
        
        ttk.Label(c_row2, text="X Step:").pack(side=LEFT, padx=5)
        self.en_xstep = ttk.Entry(c_row2, textvariable=self.tick_vars['x_step'], width=6, font=('Segoe UI', 10))
        self.en_xstep.pack(side=LEFT, padx=5)
        self.en_xstep.bind('<Return>', lambda e: self.update_plot_content())
        
        ttk.Label(c_row2, text="Y Step:").pack(side=LEFT, padx=5)
        self.en_ystep = ttk.Entry(c_row2, textvariable=self.tick_vars['y_step'], width=6, font=('Segoe UI', 10))
        self.en_ystep.pack(side=LEFT, padx=5)
        self.en_ystep.bind('<Return>', lambda e: self.update_plot_content())

        ttk.Separator(c_row2, orient=VERTICAL).pack(side=LEFT, fill=Y, padx=15)
        
        ttk.Label(c_row2, text="W(in):").pack(side=LEFT, padx=2)
        ttk.Entry(c_row2, textvariable=self.fig_w_var, width=4).pack(side=LEFT, padx=2)
        
        ttk.Label(c_row2, text="H(in):").pack(side=LEFT, padx=2)
        ttk.Entry(c_row2, textvariable=self.fig_h_var, width=4).pack(side=LEFT, padx=2)
        
        ttk.Button(c_row2, text="", command=self.reset_output_size, bootstyle="", width=3, padding=0).pack(side=LEFT, padx=5)

        # ── 背景扣除控件行 ──
        c_row3 = ttk.Frame(crop_frame)
        c_row3.pack(fill=X, pady=(8, 0))

        ttk.Checkbutton(c_row3, text=self.tr('bg_subtract'),
                        variable=self.bg_sub_enable_var,
                        bootstyle="round-toggle",
                        command=self.update_plot_content).pack(side=LEFT)

        ttk.Separator(c_row3, orient=VERTICAL).pack(side=LEFT, fill=Y, padx=8)

        # 模式选择（第一行：radio 按钮组）
        ttk.Radiobutton(c_row3, text=self.tr('bg_timezero'), variable=self.bg_mode_var,
                        value='timezero', command=self.update_plot_content).pack(side=LEFT)
        ttk.Radiobutton(c_row3, text=self.tr('bg_temporal'), variable=self.bg_mode_var,
                        value='temporal', command=self.update_plot_content).pack(side=LEFT)
        ttk.Radiobutton(c_row3, text=self.tr('bg_spatial'), variable=self.bg_mode_var,
                        value='spatial', command=self.update_plot_content).pack(side=LEFT)
        ttk.Radiobutton(c_row3, text=self.tr('bg_roi'), variable=self.bg_mode_var,
                        value='roi', command=self.update_plot_content).pack(side=LEFT, padx=(0, 8))

        # 参数：根据模式动态切换标签 + 绑定变量
        self._lbl_bg_param = ttk.Label(c_row3, text=self.tr('bg_init_frames'))
        self._lbl_bg_param.pack(side=LEFT, padx=(0, 3))
        self._spn_bg_param = ttk.Spinbox(c_row3, textvariable=self.bg_t0_frames_var,
                                          from_=1, to=9999, increment=1, width=5)
        self._spn_bg_param.pack(side=LEFT)
        self._spn_bg_param.bind('<Return>', lambda e: self.update_plot_content())

        ttk.Separator(c_row3, orient=VERTICAL).pack(side=LEFT, fill=Y, padx=8)

        ttk.Label(c_row3, text=self.tr('bg_smooth')).pack(side=LEFT, padx=(0, 3))
        en_bgs = ttk.Spinbox(c_row3, textvariable=self.bg_smooth_var,
                             from_=0, to=200, increment=1, width=5)
        en_bgs.pack(side=LEFT)
        en_bgs.bind('<Return>', lambda e: self.update_plot_content())

        ttk.Label(c_row3, text=self.tr('bg_no_smooth'),
                  font=('Segoe UI', 9), foreground='#999999').pack(side=LEFT, padx=6)

        # ROI 模式：第二行控件（平时隐藏，选 ROI 模式时显示）
        self._roi_ctrl_frame = ttk.Frame(crop_frame)
        # 统计量选择
        ttk.Label(self._roi_ctrl_frame, text=self.tr('bg_stat')).pack(side=LEFT, padx=(0, 3))
        ttk.Radiobutton(self._roi_ctrl_frame, text=self.tr('bg_median'),
                        variable=self.bg_roi_stat_var, value='median',
                        command=self.update_plot_content).pack(side=LEFT)
        ttk.Radiobutton(self._roi_ctrl_frame, text=self.tr('bg_mean'),
                        variable=self.bg_roi_stat_var, value='mean',
                        command=self.update_plot_content).pack(side=LEFT, padx=(0, 10))
        ttk.Separator(self._roi_ctrl_frame, orient=VERTICAL).pack(side=LEFT, fill=Y, padx=6)
        # 选取按钮
        self._btn_bg_roi = ttk.Button(self._roi_ctrl_frame, text=self.tr('bg_roi_drag'),
                                       bootstyle="info-outline",
                                       command=self._start_bg_roi_select)
        self._btn_bg_roi.pack(side=LEFT, padx=(0, 6))
        # 清除按钮
        ttk.Button(self._roi_ctrl_frame, text=self.tr('bg_roi_clear'),
                   bootstyle="secondary-outline",
                   command=self._clear_bg_roi).pack(side=LEFT, padx=(0, 10))
        # 当前 ROI 坐标显示
        self._lbl_roi_coords = ttk.Label(self._roi_ctrl_frame, text=self.tr('bg_not_selected'),
                                          font=('Segoe UI', 9), foreground='#999999')
        self._lbl_roi_coords.pack(side=LEFT)

        # 模式切换时更新标签 + 参数绑定 + ROI 子面板显隐
        def _on_bg_mode_changed(*_):
            m = self.bg_mode_var.get()
            if m == 'timezero':
                self._lbl_bg_param.config(text=self.tr('bg_init_frames'))
                self._spn_bg_param.config(textvariable=self.bg_t0_frames_var,
                                          from_=1, to=9999)
                self._roi_ctrl_frame.pack_forget()
            elif m == 'temporal':
                self._lbl_bg_param.config(text=self.tr('bg_percentile'))
                self._spn_bg_param.config(textvariable=self.bg_percentile_var,
                                          from_=1, to=99)
                self._roi_ctrl_frame.pack_forget()
            elif m == 'spatial':
                self._lbl_bg_param.config(text=self.tr('bg_side_width'))
                self._spn_bg_param.config(textvariable=self.bg_width_var,
                                          from_=1, to=200)
                self._roi_ctrl_frame.pack_forget()
            else:  # roi
                self._lbl_bg_param.config(text=self.tr('bg_roi_mode_label'))
                self._spn_bg_param.config(textvariable=self.bg_t0_frames_var,
                                          from_=1, to=9999)
                self._roi_ctrl_frame.pack(fill=X, pady=(4, 0))
        self.bg_mode_var.trace_add('write', _on_bg_mode_changed)

        # [右侧区域] 分类操作
        action_container = ttk.Frame(bottom_container) 
        action_container.grid(row=0, column=1, sticky="nsew")
        
        header_frame = ttk.Frame(action_container, padding=(5, 5))
        header_frame.pack(fill=X)
        ttk.Label(header_frame, text=self.tr('category_ops'), font=("Segoe UI", 12, "bold")).pack(side=LEFT, padx=5)
        ttk.Checkbutton(header_frame, text="Auto Save", variable=self.save_kymo_var, bootstyle="round-toggle").pack(side=RIGHT)
        ttk.Separator(action_container, orient=HORIZONTAL).pack(fill=X, padx=5)

        # --- 使用自定义的 ScrollableFrame 替代 ttkbootstrap.ScrolledFrame ---
        self.scrolled_btn = ScrollableFrame(action_container) 
        self.scrolled_btn.pack(fill=BOTH, expand=True, pady=(5, 0))
        self.btn_inner = self.scrolled_btn.container # 使用 container 属性

        # 5. 可视化区
        viz_frame = ttk.Frame(workspace)
        viz_frame.pack(side=TOP, fill=BOTH, expand=True)

        # [Init]
        self.fig = Figure(figsize=(8, 5), dpi=110, facecolor='#FFFFFF')
        self.ax = self.fig.add_subplot(111)
        self.ax_force = None
        self.ax.axis('off')

        self.canvas = FigureCanvasTkAgg(self.fig, master=viz_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)

        toolbar_frame = ttk.Frame(viz_frame)
        toolbar_frame.pack(side=BOTTOM, fill=X)
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        self.toolbar.update()

        # 绑定容器尺寸变化，让 figure 自适应（用 after 防递归）
        viz_frame.bind('<Configure>', lambda e: self.after(30, lambda: self._on_canvas_resize(e)))

        self.status_bar = ttk.Label(self, text=self.tr('ready'), bootstyle="inverse-secondary", anchor=W, font=("Segoe UI", 10))
        self.status_bar.pack(side=BOTTOM, fill=X)

    # --- I18N ---
    def tr(self, key):
        return _tr(self.lang, key)

    def _add_tooltip(self, widget, key):
        tip = ToolTip(widget)
        widget.bind("<Enter>", lambda e: tip.showtip(self.tr(key)))
        widget.bind("<Leave>", lambda e: tip.hidetip())

    def _toggle_language(self):
        """Switch UI language (zh <-> en) by recreating the interface."""
        self.lang = "en" if self.lang == "zh" else "zh"
        if hasattr(self, '_annot_win') and self._annot_win.winfo_exists():
            self._annot_win.destroy()
        for child in self.winfo_children():
            child.destroy()
        self.create_ui()
        self.refresh_input_listbox()
        self.load_all_files()
        self.refresh_category_buttons()
        self.refresh_tree_visuals()
        if 0 <= self.current_index < len(self.all_images_data):
            self.select_index(self.current_index)
        self.status_bar.config(text=self.tr('ready'))

    # --- Button Refresh Logic ---
    def refresh_category_buttons(self):
        """
        清空按钮区域，并按 2 列网格重新排列。
        """
        # 1. 清除当前显示的所有按钮
        for widget in self.btn_inner.winfo_children():
            widget.destroy()
        self.category_buttons.clear() 

        # 2. 配置列宽权重
        self.btn_inner.columnconfigure(0, weight=1)
        self.btn_inner.columnconfigure(1, weight=1)

        # 3. 获取所有分类名称并排序
        cat_names = sorted(list(self.categories.keys()))

        # 4. 重新生成并排列按钮
        for i, name in enumerate(cat_names):
            row = i // 2 
            col = i % 2   
            
            btn = ttk.Button(
                self.btn_inner, 
                text=f" {name}", 
                command=lambda n=name: self.do_classify(n), 
                bootstyle="primary-outline"
            )
            
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            
            btn.bind("<Button-3>", lambda event, n=name: self.show_context_menu(event, n))
            
            self.category_buttons[name] = btn

    # --- Unit Logic ---
    def _get_y_scale_factor(self):
        if self.y_unit_var.get() == "kbp":
            try:
                return self.dna_rise_var.get() 
            except:
                return 0.34
        return 1.0

    def _get_y_label(self):
        if self.h5_metadata.get('is_scan', False):
            return "Position (y) (μm)"
        return "Position (kbp)" if self.y_unit_var.get() == "kbp" else "Position (μm)"

    def _apply_scan_ui_mode(self, is_scan: bool):
        """加载文件后同步 UI：scan 模式隐藏 kbp、显示提示行；kymo 模式还原。"""
        try:
            if is_scan:
                # 隐藏 kbp 控件（scan 两轴都是 μm，kbp 无意义）
                self._rb_kbp.pack_forget()
                self._lbl_nmbp.pack_forget()
                self._en_dna_rise.pack_forget()
                # 强制切回 μm
                self.y_unit_var.set("um")
                # 显示 scan 提示行
                self._scan_info_row.pack(fill=X, pady=(4, 0))
                # BG 扣除：timezero/temporal 对 scan 无意义，自动切到 roi（仅当前两者之一时）
                if self.bg_mode_var.get() in ('timezero', 'temporal'):
                    self.bg_mode_var.set('roi')
                # 多帧导航行：仅 scan 模式 + 多帧时显示
                if self._scan_frame_count > 1:
                    self._scan_nav_row.pack(fill=X, pady=(4, 0))
                    self._spn_scan_frame.config(to=self._scan_frame_count)
                    self._lbl_scan_frame.config(text=f"帧 {self._scan_frame_idx.get()} / {self._scan_frame_count}")
                else:
                    self._scan_nav_row.pack_forget()
            else:
                # 还原 kbp 控件（重新 pack 到 _en_dna_rise 之前的位置）
                self._rb_kbp.pack(side=LEFT, padx=2)
                self._lbl_nmbp.pack(side=LEFT, padx=(10, 2))
                self._en_dna_rise.pack(side=LEFT)
                # 隐藏 scan 提示行和帧导航行
                self._scan_info_row.pack_forget()
                self._scan_nav_row.pack_forget()
        except Exception:
            pass

    # --- Helper ---
    def reload_and_update(self):
        if self.current_file_path:
            if self.current_file_path.endswith('.npz'):
                self.load_stitched_data(self.current_file_path)
            else:
                self.load_h5_kymo(self.current_file_path)

    # --- Scan 多帧导航 ---
    def _switch_scan_frame(self, frame_idx=None):
        """切换到指定 scan 帧（1-based），不传则读 _scan_frame_idx"""
        if not self._scan_frames:
            return
        if frame_idx is None:
            frame_idx = self._scan_frame_idx.get()
        frame_idx = max(1, min(frame_idx, self._scan_frame_count))
        self._scan_frame_idx.set(frame_idx)

        frame = self._scan_frames[frame_idx - 1]   # 转为 0-based 访问数组
        for col in ('red', 'green', 'blue'):
            self.h5_data[col] = frame.get(col)
            self.h5_data[f'max_{col[0]}'] = frame.get(f'max_{col[0]}', 1)

        # 更新帧标签
        if hasattr(self, '_lbl_scan_frame'):
            self._lbl_scan_frame.config(text=f"帧 {frame_idx} / {self._scan_frame_count}")

        self.update_plot_content()
        self.status_bar.config(
            text=self.tr('scan_frame_status') + f" {frame_idx}/{self._scan_frame_count}: {os.path.basename(self.current_file_path or '')}")

    def _scan_prev_frame(self):
        if self._scan_frame_count <= 1: return
        idx = self._scan_frame_idx.get()
        if idx > 1:
            self._switch_scan_frame(idx - 1)

    def _scan_next_frame(self):
        if self._scan_frame_count <= 1: return
        idx = self._scan_frame_idx.get()
        if idx < self._scan_frame_count:
            self._switch_scan_frame(idx + 1)



    # --- Force Export Logic ---
    def open_force_export_window(self):
        if not self.current_file_path or not os.path.exists(self.current_file_path):
            messagebox.showwarning(self.tr('msg_warn'), self.tr('msg_no_h5'))
            return
        
        if not H5_SUPPORT:
            messagebox.showerror(self.tr('msg_error'), self.tr('msg_no_pylake'))
            return

        forceRoot = tk.Toplevel(self)
        forceRoot.wm_title(self.tr('force_win_title'))
        forceRoot.geometry("350x450")
        
        ttk.Label(forceRoot, text="High Frequency (原始):", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=15, pady=(15,5))
        
        vars_map = {}
        hf_channels = ['Force 1x', 'Force 1y', 'Force 2x', 'Force 2y']
        for ch in hf_channels:
            var = tk.BooleanVar(value=False)
            vars_map[f"{ch} HF"] = var
            ttk.Checkbutton(forceRoot, text=f"{ch} HF", variable=var).pack(anchor="w", padx=25)
            
        ttk.Label(forceRoot, text=self.tr('force_ds_label'), font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=15, pady=(15,5))
        ds_channels = ['Force 1x', 'Force 1y', 'Force 2x', 'Force 2y']
        for ch in ds_channels:
            var = tk.BooleanVar(value=(ch == 'Force 1x')) 
            vars_map[f"{ch} DS"] = var
            ttk.Checkbutton(forceRoot, text=f"{ch} Downsampled", variable=var).pack(anchor="w", padx=25)
            
        def perform_export():
            try:
                h5 = lk.File(self.current_file_path)
                filename_no_ext = os.path.splitext(os.path.basename(self.current_file_path))[0]
                save_dir = os.path.dirname(self.current_file_path)
                
                try:
                    f1x = h5['Force HF']['Force 1x']
                    sample_rate = f1x.sample_rate
                except:
                    messagebox.showerror(self.tr('msg_error'), self.tr('msg_no_force'))
                    return

                target_hz = self.downsample_hz_var.get()
                downsample_factor = int(sample_rate / target_hz)
                
                force_data_map = {'Force 1x': h5['Force HF']['Force 1x'],'Force 1y': h5['Force HF']['Force 1y'],'Force 2x': h5['Force HF']['Force 2x'],'Force 2y': h5['Force HF']['Force 2y']
                }
                
                time_hf = (f1x.timestamps - f1x.timestamps[0]) / 1e9
                f1x_ds = f1x.downsampled_by(downsample_factor)
                time_ds = (f1x_ds.timestamps - f1x_ds.timestamps[0]) / 1e9
                
                export_data = {}
                
                dist_label = "Distance (μm)"
                if 'Distance' in h5 and 'Distance 1' in h5['Distance']:
                    dist_label = "Distance 1 (μm)"
                
                has_hf = any(vars_map[f"{ch} HF"].get() for ch in hf_channels)
                if has_hf:
                    export_data['Time (s)'] = time_hf
                    for ch in hf_channels:
                        if vars_map[f"{ch} HF"].get():
                            export_data[f"{ch} HF (pN)"] = force_data_map[ch].data
                    
                    if 'Distance' in h5 and 'Distance 1' in h5['Distance']:
                         dist_raw = h5['Distance']['Distance 1']
                         dist_interp = np.interp(f1x.timestamps, dist_raw.timestamps, dist_raw.data)
                         export_data[dist_label] = dist_interp

                has_ds = any(vars_map[f"{ch} DS"].get() for ch in ds_channels)
                if has_ds:
                    export_data['Time Downsampled (s)'] = pd.Series(time_ds) 
                    for ch in ds_channels:
                        if vars_map[f"{ch} DS"].get():
                            ds_data = force_data_map[ch].downsampled_by(downsample_factor).data
                            export_data[f"{ch} DS {target_hz}Hz (pN)"] = pd.Series(ds_data)
                    
                    if 'Distance' in h5 and 'Distance 1' in h5['Distance']:
                         dist_raw = h5['Distance']['Distance 1']
                         dist_interp_ds = np.interp(f1x_ds.timestamps, dist_raw.timestamps, dist_raw.data)
                         export_data[f"{dist_label} (DS)"] = pd.Series(dist_interp_ds)

                if not export_data:
                    messagebox.showinfo(self.tr('msg_hint'), self.tr('msg_no_channel'))
                    return

                df = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in export_data.items() ]))
                
                save_path = os.path.join(save_dir, f"{filename_no_ext}_force_export.csv")
                df.to_csv(save_path, index=False)
                
                meta_path = os.path.join(save_dir, f"{filename_no_ext}_desc.txt")
                with open(meta_path, "w") as f:
                    f.write(h5.description)
                    
                messagebox.showinfo(self.tr('msg_success'), self.tr('msg_export_ok') + f"\nCSV: {os.path.basename(save_path)}")
                forceRoot.destroy()
                
            except Exception as e:
                messagebox.showerror(self.tr('msg_export_fail'), str(e))

        ttk.Separator(forceRoot).pack(fill=X, pady=15)
        ttk.Button(forceRoot, text=self.tr('confirm_export'), command=perform_export, bootstyle="").pack(pady=10, fill=X, padx=20)

    # --- Two Point Selection Logic ---
    def toggle_click_mode(self):
        if not self.is_h5_mode: 
            messagebox.showwarning(self.tr('msg_hint'), self.tr('msg_crop_h5_only'))
            return
        if self.click_mode_active:
            self._disable_click_mode()
        else:
            self.click_mode_active = True
            self.click_points = [] 
            self._clear_temp_markers() 
            self.btn_select_roi.config(text=self.tr('cancel_roi'))
            self.status_bar.config(text=self.tr('step1_hint'))
            if self.cid_click is None:
                self.cid_click = self.canvas.mpl_connect('button_press_event', self.on_canvas_click)
            
            targets = [self.ax]
            if self.ax_force: targets.append(self.ax_force)
            self.cursor = MultiCursor(self.canvas, targets, color='red', lw=1, linestyle='--', horizOn=True, vertOn=True)
            
            self.crop_enable_var.set(False)
            self.update_plot_content()

    def _disable_click_mode(self):
        self.click_mode_active = False
        self.click_points = []
        
        if self.cid_click is not None:
            self.canvas.mpl_disconnect(self.cid_click)
            self.cid_click = None
        
        if self.cursor:
            try: self.cursor.disconnect() 
            except: pass
            lines_to_remove = []
            if hasattr(self.cursor, 'vlines'): 
                lines_to_remove.extend(self.cursor.vlines)
            if hasattr(self.cursor, 'hlines'): 
                lines_to_remove.extend(self.cursor.hlines)
            for line in lines_to_remove:
                try: line.remove() 
                except Exception: pass
            self.cursor = None 
        
        self.btn_select_roi.config(text=self.tr('two_point_roi'))
        self.status_bar.config(text=self.tr('ready'))
        self._clear_temp_markers()
        self.canvas.draw_idle()

    def _clear_temp_markers(self):
        if self.temp_markers:
            for artist in self.temp_markers:
                try: artist.remove()
                except: pass
            self.temp_markers = []

    # ── BG ROI 拖拽选取 ─────────────────────────────────────────────────────

    def _start_bg_roi_select(self):
        """进入 BG ROI 拖拽选取模式"""
        if self.h5_data.get('green') is None and self.h5_data.get('red') is None:
            return
        # 取消其他交互模式
        if self.click_mode_active:
            self._disable_click_mode()

        self._bg_roi_select_mode = True
        self._bg_roi_press_pos   = None
        self._btn_bg_roi.config(text=" 取消选取")
        self.status_bar.config(text=self.tr('bg_roi_drag_hint'))

        self._bg_roi_cid_press   = self.canvas.mpl_connect('button_press_event',   self._on_bg_roi_press)
        self._bg_roi_cid_release = self.canvas.mpl_connect('button_release_event', self._on_bg_roi_release)
        self._bg_roi_cid_motion  = self.canvas.mpl_connect('motion_notify_event',  self._on_bg_roi_motion)

    def _cancel_bg_roi_select(self):
        """退出 BG ROI 选取模式（不清除已有 ROI）"""
        self._bg_roi_select_mode = False
        self._bg_roi_press_pos   = None
        for cid_attr in ('_bg_roi_cid_press', '_bg_roi_cid_release', '_bg_roi_cid_motion'):
            cid = getattr(self, cid_attr, None)
            if cid is not None:
                self.canvas.mpl_disconnect(cid)
                setattr(self, cid_attr, None)
        # 移除预览矩形
        if self._bg_roi_preview_patch is not None:
            try: self._bg_roi_preview_patch.remove()
            except: pass
            self._bg_roi_preview_patch = None
        self.canvas.draw_idle()
        self._btn_bg_roi.config(text=self.tr('bg_roi_drag'))
        self.status_bar.config(text=self.tr('ready'))

    def _clear_bg_roi(self):
        """清除 BG ROI，重置背景扣除"""
        self._cancel_bg_roi_select()
        self.bg_roi_coords = None
        if self._bg_roi_rect_patch is not None:
            try: self._bg_roi_rect_patch.remove()
            except: pass
            self._bg_roi_rect_patch = None
        self._lbl_roi_coords.config(text=self.tr('bg_not_selected'))
        self.canvas.draw_idle()
        self.update_plot_content()

    def _on_bg_roi_press(self, event):
        if event.inaxes != self.ax:
            return
        if event.button == 3:          # 右键取消
            self._cancel_bg_roi_select()
            return
        if event.button != 1:
            return
        self._bg_roi_press_pos = (event.x, event.y, event.xdata, event.ydata)

    def _on_bg_roi_motion(self, event):
        if not self._bg_roi_select_mode or self._bg_roi_press_pos is None:
            return
        if event.inaxes != self.ax or event.xdata is None:
            return
        x0d, y0d = self._bg_roi_press_pos[2], self._bg_roi_press_pos[3]
        x1d, y1d = event.xdata, event.ydata
        # 预览矩形（数据坐标）
        import matplotlib.patches as mpatches
        if self._bg_roi_preview_patch is not None:
            try: self._bg_roi_preview_patch.remove()
            except: pass
        rx = min(x0d, x1d); ry = min(y0d, y1d)
        rw = abs(x1d - x0d);  rh = abs(y1d - y0d)
        self._bg_roi_preview_patch = mpatches.Rectangle(
            (rx, ry), rw, rh,
            linewidth=1.5, edgecolor='cyan', facecolor='cyan', alpha=0.25,
            transform=self.ax.transData)
        self.ax.add_patch(self._bg_roi_preview_patch)
        self.canvas.draw_idle()

    def _on_bg_roi_release(self, event):
        if not self._bg_roi_select_mode or self._bg_roi_press_pos is None:
            return
        if event.button != 1:
            return
        x0d, y0d = self._bg_roi_press_pos[2], self._bg_roi_press_pos[3]
        x1d = event.xdata if event.xdata is not None else x0d
        y1d = event.ydata if event.ydata is not None else y0d

        # 转换为像素（列/行）索引
        try:
            # 从实际通道数据获取形状
            ch_data = next((self.h5_data[c] for c in ('green', 'red', 'blue')
                            if self.h5_data.get(c) is not None), None)
            if ch_data is None:
                self._cancel_bg_roi_select()
                return
            n_rows, n_cols = ch_data.shape[:2]

            x_max = self.h5_metadata['duration']   # 时间轴最大值（s 或 µm）
            y_scale = self._get_y_scale_factor()
            y_max = self.h5_metadata['width'] / y_scale  # 位置轴最大值

            col0 = int(round(max(min(x0d, x1d), 0) / x_max * n_cols)) if x_max > 0 else 0
            col1 = int(round(min(max(x0d, x1d), x_max) / x_max * n_cols)) if x_max > 0 else n_cols
            row0 = int(round(max(min(y0d, y1d), 0) / y_max * n_rows)) if y_max > 0 else 0
            row1 = int(round(min(max(y0d, y1d), y_max) / y_max * n_rows)) if y_max > 0 else n_rows

            col0 = max(0, min(col0, n_cols - 1))
            col1 = max(0, min(col1, n_cols))
            row0 = max(0, min(row0, n_rows - 1))
            row1 = max(0, min(row1, n_rows))

            if col1 <= col0 or row1 <= row0:
                self._cancel_bg_roi_select()
                self.status_bar.config(text=self.tr('bg_roi_too_small'))
                return

            self.bg_roi_coords = (col0, row0, col1, row1)
            self._lbl_roi_coords.config(
                text=f"{self.tr('bg_roi_coords')} {col0}{col1}  {self.tr('bg_roi_rows')} {row0}{row1}  ({col1-col0}×{row1-row0}px)")
        except Exception as e:
            self._cancel_bg_roi_select()
            return

        self._cancel_bg_roi_select()   # 退出选取模式、恢复按钮

        # 在图上画持久矩形
        import matplotlib.patches as mpatches
        if self._bg_roi_rect_patch is not None:
            try: self._bg_roi_rect_patch.remove()
            except: pass
        xd0, xd1 = min(x0d, x1d), max(x0d, x1d)
        yd0, yd1 = min(y0d, y1d), max(y0d, y1d)
        self._bg_roi_rect_patch = mpatches.Rectangle(
            (xd0, yd0), xd1 - xd0, yd1 - yd0,
            linewidth=1.5, edgecolor='cyan', facecolor='none', linestyle='--',
            transform=self.ax.transData)
        self.ax.add_patch(self._bg_roi_rect_patch)
        self.canvas.draw_idle()

        # 立即应用背景扣除
        self.update_plot_content()

    def on_canvas_click(self, event):
        if self.toolbar.mode: return
        if event.button != 1: return 
        
        inv = self.ax.transData.inverted()
        try:
            data_x, data_y = inv.transform((event.x, event.y))
        except:
            return 

        # Snap Logic
        max_time_or_width = self.h5_metadata['duration']
        if max_time_or_width <= 0: return

        if data_x < 0: data_x = 0
        elif data_x > max_time_or_width: data_x = max_time_or_width
        
        y_scale = self._get_y_scale_factor()
        max_height_disp = self.h5_metadata['width'] / y_scale
        
        if data_y < 0: data_y = 0
        elif data_y > max_height_disp: data_y = max_height_disp

        self.click_points.append((data_x, data_y))

        if len(self.click_points) == 1:
            line, = self.ax.plot(data_x, data_y, 'r+', markersize=12, markeredgewidth=2)
            self.temp_markers.append(line)
            self.canvas.draw_idle()
            self.status_bar.config(text=self.tr('step2_hint'))

        elif len(self.click_points) == 2:
            x1, y1_disp = self.click_points[0]
            x2, y2_disp = self.click_points[1]
            
            y1 = y1_disp * y_scale
            y2 = y2_disp * y_scale

            xmin, xmax = sorted([x1, x2])
            ymin, ymax = sorted([y1, y2])
            
            self.axis_vars['xmin'].set(round(xmin, 2))
            self.axis_vars['xmax'].set(round(xmax, 2))
            self.axis_vars['ymin'].set(round(ymin, 2))
            self.axis_vars['ymax'].set(round(ymax, 2))
            
            self.crop_enable_var.set(True)
            self.update_plot_content() 
            self._disable_click_mode()
            self.status_bar.config(text=self.tr('roi_locked') + f" ({xmin:.2f}-{xmax:.2f}, {ymin:.2f}-{ymax:.2f})")

    # --- Classification Logic ---

    def do_classify(self, tag):
        if self.current_index < 0: return
        item_index = self.current_index
        item_data = self.all_images_data[item_index]
        fname = item_data['filename']
        src = item_data['full_path']
        if tag not in self.categories: return
        dest_dir = self.categories[tag]
        dest = os.path.join(dest_dir, fname)
        mode = self.operation_mode.get()
        old_dir = self.file_status_map.get(fname)
        old_path = os.path.join(old_dir, fname) if old_dir else None
        save_image = self.save_kymo_var.get()

        is_scan = self.h5_metadata.get('is_scan', False)

        crop_settings = {'enabled': self.crop_enable_var.get(),'xlim': (self.axis_vars['xmin'].get(), self.axis_vars['xmax'].get()),'ylim': (self.axis_vars['ymin'].get(), self.axis_vars['ymax'].get()),'flip_y': self.flip_y_var.get(),'x_step': self.tick_vars['x_step'].get(),'y_step': self.tick_vars['y_step'].get(),'y_scale': self._get_y_scale_factor(),'y_label': self._get_y_label(),'is_scan': is_scan,'aspect_equal': self.aspect_equal_var.get()
        }
        
        # Determine X Label
        if is_scan:
            crop_settings['x_label'] = "Position (x) (μm)"
        else:
            crop_settings['x_label'] = "Time (s)"

        snapshot_rgb = None
        snapshot_metadata = self.h5_metadata.copy() if self.h5_metadata else None
        if self.is_h5_mode:
            snapshot_rgb = self._get_current_rgb_composite()
            if snapshot_rgb is not None and crop_settings['flip_y']:
                snapshot_rgb = np.flipud(snapshot_rgb)

        self.navigate(1)
        self.status_bar.config(text=self.tr('bg_processing') + f" {fname}...")

        def worker_task():
            try:
                if old_path and old_dir != dest_dir:
                    if os.path.exists(old_path) and os.path.abspath(old_path) != os.path.abspath(src):
                        try: os.remove(old_path)
                        except: pass
                if mode == 'move':
                    shutil.move(src, dest)
                    self.after(0, lambda: self._update_item_path(item_index, dest))
                else:
                    shutil.copy2(src, dest)
                
                if save_image:
                    if not os.path.exists(dest_dir): os.makedirs(dest_dir, exist_ok=True)
                    name_no_ext = os.path.splitext(fname)[0]
                    img_path = os.path.join(dest_dir, f"{name_no_ext}.png")
                    
                    has_force = (self.force_channel_var.get() != "None") and (not is_scan)
                    
                    custom_w = self.fig_w_var.get()
                    custom_h = self.fig_h_var.get()
                    
                    fig_bg = Figure(figsize=(custom_w, custom_h), dpi=300)
                    
                    if has_force:
                        gs = fig_bg.add_gridspec(2, 1, height_ratios=[3, 1], hspace=0.15)
                        ax_bg = fig_bg.add_subplot(gs[0])
                        ax_force = fig_bg.add_subplot(gs[1], sharex=ax_bg)
                        
                        # --- Force Plot logic on save ---
                        if self.h5_data['force_t'] is not None and self.h5_data['force_v'] is not None:
                            f_time = self.h5_data['force_t']
                            f_val = self.h5_data['force_v']
                            ax_force.plot(f_time, f_val, linewidth=0.5, color='black')
                            ax_force.set_ylabel(self.force_channel_var.get() + " (pN)", fontsize=9, fontname='Arial')
                            ax_force.set_xlabel("Time (s)", fontsize=9, fontname='Arial')
                            ax_force.grid(True, linestyle='--', alpha=0.5)
                            
                            if crop_settings['enabled']:
                                x_min, x_max = crop_settings['xlim']
                                mask = (f_time >= x_min) & (f_time <= x_max)
                                if np.any(mask):
                                    vvals = f_val[mask]
                                    ymin, ymax = np.min(vvals), np.max(vvals)
                                    span = ymax - ymin if ymax != ymin else 1.0
                                    ax_force.set_ylim(ymin - span*0.1, ymax + span*0.1)
                            ax_force.yaxis.set_major_locator(MaxNLocator(nbins=5, integer=True))
                    else:
                        fig_bg.subplots_adjust(left=0.15, right=0.95, top=0.90, bottom=0.15)
                        ax_bg = fig_bg.add_subplot(111)
                    
                    if snapshot_rgb is not None and snapshot_metadata is not None:
                        y_scale = crop_settings['y_scale']
                        extent = [0, snapshot_metadata['duration'], 0, snapshot_metadata['width'] / y_scale]
                        
                        ax_bg.imshow(snapshot_rgb, aspect='auto', extent=extent, origin='lower')
                        
                        # Apply Aspect Ratio
                        if crop_settings.get('aspect_equal', False):
                            ax_bg.set_aspect('equal')
                        else:
                            ax_bg.set_aspect('auto')

                        ax_bg.set_title(fname, fontsize=10, fontname='Arial')
                        ax_bg.set_ylabel(crop_settings['y_label'], fontsize=9, fontname='Arial')
                        
                        x_step = crop_settings['x_step']
                        y_step = crop_settings['y_step']
                        
                        if crop_settings['enabled']:
                            x_min, x_max = crop_settings['xlim']
                            y_min_um, y_max_um = crop_settings['ylim']
                            y_min_disp = y_min_um / y_scale
                            y_max_disp = y_max_um / y_scale
                            
                            ax_bg.set_xlim(x_min, x_max)
                            ax_bg.set_ylim(y_min_disp, y_max_disp)
                            
                            if x_step > 0:
                                ax_bg.xaxis.set_major_locator(MultipleLocator(x_step))
                                ax_bg.xaxis.set_major_formatter(FuncFormatter(lambda x, p: f"{int(round(x - x_min))}"))
                                if has_force:
                                    ax_force.xaxis.set_major_locator(MultipleLocator(x_step))
                                    ax_force.xaxis.set_major_formatter(FuncFormatter(lambda x, p: f"{int(round(x - x_min))}"))
                            if y_step > 0:
                                ax_bg.yaxis.set_major_locator(MultipleLocator(y_step))
                                ax_bg.yaxis.set_major_formatter(FuncFormatter(lambda y, p: f"{int(round(y - y_min_disp))}"))
                        else:
                            ax_bg.set_xlim(0, snapshot_metadata['duration'])
                            ax_bg.set_ylim(0, snapshot_metadata['width'] / y_scale)
                            if x_step > 0: 
                                ax_bg.xaxis.set_major_locator(MultipleLocator(x_step))
                                if has_force: ax_force.xaxis.set_major_locator(MultipleLocator(x_step))
                            if y_step > 0: 
                                ax_bg.yaxis.set_major_locator(MultipleLocator(y_step))
                    
                    if has_force: ax_bg.tick_params(labelbottom=False)
                    else: ax_bg.set_xlabel(crop_settings['x_label'], fontsize=9, fontname='Arial')

                    # --- 将标注绘制到导出图上 ---
                    for ann_info in self.annotations:
                        c = ann_info.get('color', 'white')
                        lw = ann_info.get('linewidth', 1.5)
                        ls = ann_info.get('linestyle', '--')
                        al = ann_info.get('alpha', 0.9)
                        fs = ann_info.get('fontsize', 10)
                        at = ann_info.get('type')
                        if at == 'hline':
                            ax_bg.axhline(y=ann_info['y'], color=c, linewidth=lw, linestyle=ls, alpha=al)
                        elif at == 'vline':
                            ax_bg.axvline(x=ann_info['x'], color=c, linewidth=lw, linestyle=ls, alpha=al)
                        elif at == 'line':
                            ax_bg.plot([ann_info['x0'], ann_info['x1']], [ann_info['y0'], ann_info['y1']],
                                       color=c, linewidth=lw, linestyle=ls, alpha=al)
                        elif at == 'arrow':
                            ax_bg.annotate('', xy=(ann_info['x1'], ann_info['y1']),
                                           xytext=(ann_info['x0'], ann_info['y0']),
                                           arrowprops=dict(arrowstyle='->', color=c, lw=lw), alpha=al)
                        elif at == 'text':
                            ax_bg.text(ann_info['x'], ann_info['y'], ann_info.get('text', ''),
                                       color=c, fontsize=fs, alpha=al, fontname='Arial',
                                       bbox=dict(boxstyle='round,pad=0.2', fc='none', ec=c, lw=0.5))
                        elif at == 'point':
                            ax_bg.plot(ann_info['x'], ann_info['y'], 'o', color=c,
                                       markersize=6, alpha=al, markeredgewidth=0)

                    FigureCanvasAgg(fig_bg).print_png(img_path)

                self.after(0, lambda: self._on_classify_success(fname, dest_dir, mode, tag))
                
            except Exception as e:
                err_msg = str(e)
                self.after(0, lambda: messagebox.showerror(self.tr('msg_bg_error'), f"{self.tr('msg_bg_err_detail')} {fname}\n{self.tr('msg_bg_err_label')}\n{err_msg}"))

        threading.Thread(target=worker_task, daemon=True).start()

    def _get_current_rgb_composite(self):
        if not self.is_h5_mode: return None
        shape = None
        for c in ['red', 'green', 'blue']:
            if self.h5_data[c] is not None: shape = self.h5_data[c].shape; break
        if not shape: return None
        rgb = np.zeros((shape[0], shape[1], 3), dtype=np.float32)
        for col, idx in {'red': 0, 'green': 1, 'blue': 2}.items():
            if self.channel_vars[col].get() and self.h5_data[col] is not None:
                rgb[:, :, idx] = (self.h5_data[col] / self.h5_data[f'max_{col[0]}']) * self.contrast_vars[col].get()
        return np.clip(rgb, 0, 1)

    def _update_item_path(self, index, new_path):
        if 0 <= index < len(self.all_images_data):
            self.all_images_data[index]['full_path'] = new_path

    def _on_classify_success(self, fname, dest_dir, mode, tag):
        self.file_status_map[fname] = dest_dir
        self.refresh_tree_visuals()
        mode_text = self.tr('mode_move_short') if mode == 'move' else self.tr('mode_copy_short')
        save_text = self.tr('save_image_suffix') if self.save_kymo_var.get() else ""
        self.status_bar.config(text=f" {mode_text}{save_text}: {fname} -> {tag}")

    # --- Helpers ---
    def refresh_input_listbox(self):
        self.input_dir_listbox.delete(0, tk.END)
        for p in self.input_dirs: self.input_dir_listbox.insert(tk.END, p)
    
    def add_input_dir(self):
        path = filedialog.askdirectory(title=self.tr('fd_select_dir'))
        if path and path not in self.input_dirs: self.input_dirs.append(path); self.refresh_input_listbox(); self.load_all_files()
    
    def add_batch_input_dir(self):
        parent_path = filedialog.askdirectory(title=self.tr('fd_select_parent'))
        if not parent_path: return
        added_count = 0
        if parent_path not in self.input_dirs: self.input_dirs.append(parent_path); added_count += 1
        try:
            subdirs = [os.path.join(parent_path, d) for d in os.listdir(parent_path) if os.path.isdir(os.path.join(parent_path, d))]
            for d in subdirs: 
                if d not in self.input_dirs: self.input_dirs.append(d); added_count += 1
        except: pass
        if added_count > 0: self.refresh_input_listbox(); self.load_all_files(); messagebox.showinfo(self.tr('msg_import_ok'), f"{self.tr('msg_imported_paths')} {added_count} {self.tr('msg_paths_suffix')}")
    
    def remove_selected_input_dir(self):
        sel_idx = self.input_dir_listbox.curselection()
        if not sel_idx: return
        for i in reversed(sel_idx): del self.input_dirs[i]; self.input_dir_listbox.delete(i)
        self.load_all_files()
    
    def clear_input_dirs(self): self.input_dirs = []; self.refresh_input_listbox(); self.load_all_files()
    
    def load_all_files(self):
        self.tree.delete(*self.tree.get_children())
        self.all_images_data = []
        self.ax.clear(); 
        if self.ax_force: self.ax_force.clear()
        self.canvas.draw()
        show_img = self.filter_img_var.get(); show_h5 = self.filter_h5_var.get(); count_total = 0
        for d in self.input_dirs:
            try:
                folder_name = os.path.basename(d)
                for f in sorted(os.listdir(d)):
                    ext = os.path.splitext(f)[1].lower()
                    is_h5 = ext in {'.h5'}; is_img = ext in IMAGE_EXTENSIONS
                    if is_h5: 
                        if not show_h5: continue # 移除 Kymograph 命名限制
                    elif is_img:
                        if not show_img: continue
                    else: continue
                    self.all_images_data.append({'display_text': f"{f}", 'full_path': os.path.join(d, f), 'filename': f, 'type': 'H5' if is_h5 else 'IMG', 'folder': folder_name})
                    count_total += 1
            except: pass
        for i, item in enumerate(self.all_images_data):
            tag = "h5" if item['type']=='H5' else "normal"
            self.tree.insert("", END, iid=str(i), values=(item['filename'], item['folder']), tags=(tag,))
        self.lbl_stats.config(text=f"已加载 {count_total} 个文件")
        self.scan_all_categories_status()
        if self.all_images_data: self.select_index(0)
    
    def scan_all_categories_status(self):
        self.file_status_map = {}
        fs = set(x['filename'] for x in self.all_images_data)
        for p in self.categories.values():
            try: 
                for f in os.listdir(p): 
                    if f in fs: self.file_status_map[f] = p
            except: pass
        self.refresh_tree_visuals()
    
    def refresh_tree_visuals(self):
        for i, x in enumerate(self.all_images_data):
            f = x['filename']; is_done = f in self.file_status_map
            display_name = f" {f}" if is_done else f; folder = x['folder']
            if is_done: tag = "done"
            elif x['type'] == "H5": tag = "h5"
            else: tag = "normal"
            self.tree.item(str(i), values=(display_name, folder), tags=(tag,))
    
    def register_category(self, n, p):
        # 1. 存入数据
        self.categories[n] = p
        
        # 2. 刷新界面布局 (解决布局问题的关键)
        self.refresh_category_buttons()
        
    def show_context_menu(self, event, name):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label=self.tr('remove_btn') + f" [{name}]", command=lambda: self.remove_category(name))
        menu.post(event.x_root, event.y_root)
    
    def remove_category(self, name):
        # 1. 删除数据
        if name in self.categories: 
            del self.categories[name]
        
        # 2. 刷新界面布局 (此时会自动移除对应的按钮并重新对齐剩下的)
        self.refresh_category_buttons()
        
        # 3. 更新文件状态标记
        self.scan_all_categories_status()
        messagebox.showinfo(self.tr('msg_removed'), f"[{name}] {self.tr('msg_removed_cat')}")
    
    def on_tree_motion(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id: self.tooltip.hidetip(); return
        try:
            index = int(item_id)
            if 0 <= index < len(self.all_images_data):
                data = self.all_images_data[index]; text = f"{self.tr('tt_file')} {data['filename']}\n{self.tr('tt_location')} {data['folder']}"
                self.tooltip.showtip(text)
            else: self.tooltip.hidetip()
        except: self.tooltip.hidetip()
    
    def reset_contrast(self):
        for key in ['red', 'green', 'blue']: 
            self.contrast_vars[key].set(25.0) 
            self.brightness_vars[key].set(0.0) 
        self.update_plot_content()
    
    def save_current_plot(self):
        if not self.current_file_path: 
            messagebox.showwarning(self.tr('msg_hint'), self.tr('msg_load_first'))
            return
        
        folder = os.path.dirname(self.current_file_path)
        name = os.path.splitext(os.path.basename(self.current_file_path))[0]
        save_path = os.path.join(folder, f"{name}.png")

        try:
            target_w = self.fig_w_var.get()
            target_h = self.fig_h_var.get()
        except:
            target_w, target_h = 5.0, 4.0

        original_size = self.fig.get_size_inches()
        cursor_was_visible = False
        hidden_markers = []

        try:
            if self.cursor:
                cursor_was_visible = self.cursor.visible
                self.cursor.visible = False 
            
            for marker in self.temp_markers:
                if marker.get_visible():
                    marker.set_visible(False)
                    hidden_markers.append(marker)

            self.fig.set_size_inches(target_w, target_h)
            
            try: self.fig.tight_layout()
            except: pass 

            self.fig.savefig(save_path, dpi=300, bbox_inches='tight')
            
            messagebox.showinfo(self.tr('msg_success'), self.tr('msg_save_ok') + f"\n{save_path}\n{target_w} x {target_h} inches")
            self.status_bar.config(text=self.tr('file_saved_status') + f" {os.path.basename(save_path)}")

        except Exception as e: 
            messagebox.showerror(self.tr('msg_save_fail'), str(e))
        
        finally:
            self.fig.set_size_inches(original_size)
            try: self.fig.tight_layout() 
            except: pass
            if self.cursor and cursor_was_visible: self.cursor.visible = True
            for marker in hidden_markers: marker.set_visible(True)
            self.canvas.draw_idle()
    
    def load_h5_kymo(self, path):
        if not H5_SUPPORT: return
        self._disable_click_mode() 
        
        try:
            h5 = lk.File(path)
            
            new_h5 = {'red': None, 'green': None, 'blue': None, 'max_r': 1, 'max_g': 1, 'max_b': 1, 'force_t': None, 'force_v': None}
            valid_shape = None
            
            # --- 检测数据类型: Kymo vs Scan ---
            data_source = None
            is_scan_mode = False

            if h5.kymos:
                data_source = h5.kymos[list(h5.kymos.keys())[0]]
                is_scan_mode = False
            elif h5.scans:
                is_scan_mode = True
            else:
                messagebox.showwarning(self.tr('msg_warn'), self.tr('msg_no_kymo_scan'))
                return

            # --- 读取图像 ---
            if is_scan_mode:
                # Scan 多帧：遍历所有 scan，拆分 3D 数据，存入 _scan_frames
                self._scan_frames = []
                for sk in list(h5.scans.keys()):
                    scan_obj = h5.scans[sk]
                    ch_data = {}
                    for col, attr in [('red', 'red_image'), ('green', 'green_image'), ('blue', 'blue_image')]:
                        try:
                            data = getattr(scan_obj, attr)
                            if isinstance(data, np.ndarray) and data.size > 0:
                                ch_data[col] = data.astype(float)
                        except: pass
                    if not ch_data:
                        continue

                    sample = next(iter(ch_data.values()))
                    if sample.ndim == 3:
                        # 3D (h, w, frames): 拆分为独立帧
                        for f in range(sample.shape[2]):
                            frame = {'red': None, 'green': None, 'blue': None,'max_r': 1, 'max_g': 1, 'max_b': 1}
                            for col in ('red', 'green', 'blue'):
                                if col in ch_data:
                                    frame[col] = ch_data[col][:, :, f]
                                    vmax = np.percentile(frame[col], 99.5)
                                    frame[f'max_{col[0]}'] = vmax if vmax > 0 else 1
                            self._scan_frames.append(frame)
                    else:
                        # 2D (h, w): 单帧
                        frame = {'red': None, 'green': None, 'blue': None,'max_r': 1, 'max_g': 1, 'max_b': 1}
                        for col in ('red', 'green', 'blue'):
                            if col in ch_data:
                                frame[col] = ch_data[col]
                                vmax = np.percentile(frame[col], 99.5)
                                frame[f'max_{col[0]}'] = vmax if vmax > 0 else 1
                        self._scan_frames.append(frame)

                self._scan_frame_count = len(self._scan_frames)
                self._scan_frame_idx.set(1)
                if self._scan_frame_count == 0:
                    messagebox.showwarning(self.tr('msg_warn'), self.tr('msg_empty_scan'))
                    return

                # 使用第一帧
                new_h5.update(self._scan_frames[0])
                data_source = h5.scans[list(h5.scans.keys())[0]]
                for col in ('red', 'green', 'blue'):
                    if new_h5[col] is not None:
                        valid_shape = new_h5[col].shape
                        break
            else:
                # Kymo: 单帧读取（原逻辑）
                for col, attr in [('red', 'red_image'), ('green', 'green_image'), ('blue', 'blue_image')]:
                    try:
                        data = getattr(data_source, attr)
                        if isinstance(data, np.ndarray) and data.size > 0:
                            new_h5[col] = data.astype(float)
                            vmax = np.percentile(data, 99.5)
                            new_h5[f'max_{col[0]}'] = vmax if vmax > 0 else 1
                            if valid_shape is None: valid_shape = data.shape
                    except: pass
                self._scan_frames = []
                self._scan_frame_count = 0
            
            # --- 读取力数据 (仅限 Kymo 模式) ---
            selected_force = self.force_channel_var.get()
            if not is_scan_mode and selected_force != "None":
                try:
                    if 'Force HF' in h5:
                        hf_group = h5['Force HF']
                        if selected_force in hf_group:
                            force_trace = hf_group[selected_force]
                            f_slice = force_trace[data_source.start:data_source.stop]
                            f_ds = f_slice.downsampled_by(int(force_trace.sample_rate/100))
                            new_h5['force_t'] = (f_ds.timestamps - data_source.start) / 1e9
                            new_h5['force_v'] = f_ds.data
                except Exception as e:
                    print(f"Force load error: {e}")

            if valid_shape is None: return

            # --- 物理尺寸计算 (单位换算 Unit Conversion) ---
            x_max = 0
            y_max_um = 0
            
            def safe(v): return float(v[0]) if isinstance(v, (list, tuple, np.ndarray)) else float(v)

            if is_scan_mode:
                # Scan: X轴 = 宽度(μm)
                try:
                    if hasattr(data_source, 'scan_width_um'):
                        x_max = safe(data_source.scan_width_um) 
                    else:
                        # 换算公式: 宽度像素 * 像素大小
                        x_max = valid_shape[1] * safe(data_source.pixel_size_um)
                except: x_max = 10.0 

                # Scan: Y轴 = 高度(μm)
                try:
                    if hasattr(data_source, 'scan_height_um'):
                         y_max_um = safe(data_source.scan_height_um)
                    elif hasattr(data_source, 'scan_width_um'):
                         # 假设矩形扫描，按像素比例换算
                         pixel_size = x_max / valid_shape[1]
                         y_max_um = valid_shape[0] * pixel_size
                    else:
                        y_max_um = 10.0
                except: y_max_um = 10.0
                
                x_label = "Position (x) (μm)"
                
            else:
                # Kymo: X轴 = 时间(s)
                try: x_max = safe(getattr(data_source, 'line_time_seconds', 0)) * valid_shape[1]
                except: pass
                
                # ==================== 修改开始 ====================
                # Kymo: Y轴 = 位置(μm) - 修正版
                # 强制使用 (像素行数 * 像素大小) 计算，这才是图像的真实物理高度。
                # 不要读取 scan_width_um，那个是设定的扫描范围，往往比实际图像大，会导致拉伸。
                try:
                    # valid_shape[0] 是图像的高度（像素行数）
                    if hasattr(data_source, 'pixel_size_um') and valid_shape is not None:
                        y_max_um = valid_shape[0] * safe(data_source.pixel_size_um)
                    
                    # 如果获取失败，才作为备选尝试读取 metadata
                    elif hasattr(data_source, 'scan_width_um'): 
                        y_max_um = safe(data_source.scan_width_um)
                    elif hasattr(data_source, 'pixels_per_line'): 
                        y_max_um = safe(data_source.pixels_per_line) * safe(data_source.pixel_size_um)
                    else: 
                        y_max_um = 10.0
                except: 
                    y_max_um = 10.0
                # ==================== 修改结束 ====================
                
                x_label = "Time (s)"

            self.h5_data = new_h5
            self.h5_metadata = {'duration': x_max, 'width': y_max_um, 'is_scan': is_scan_mode,'scan_frame_count': self._scan_frame_count}

            # scan 模式自动锁定等比，kymo 模式自动解锁
            self.aspect_equal_var.set(is_scan_mode)
            # 联动 UI：scan 时隐藏 kbp、显示提示行；kymo 时还原
            self._apply_scan_ui_mode(is_scan_mode)

            self.init_matplotlib_plot(os.path.basename(path), [0, x_max, 0, y_max_um], x_label, "Position (μm)")
            self.update_plot_content()
            
            type_str = "Scan" if is_scan_mode else "Kymo"
            self.status_bar.config(text=f"{type_str}: {os.path.basename(path)}")
            
        except Exception as e: messagebox.showerror(self.tr('msg_h5_error'), str(e))

    def load_stitched_data(self, npz_path):
        """Loads a stitched NPZ file into the sorter workspace.
        兼容新版 stitch_times 数组（多段）和旧版 stitch_duration（单段）。
        """
        try:
            # Stitched data usually has no force, so reset this first to avoid plot errors
            self.force_channel_var.set("None")
            
            data = np.load(npz_path)
            
            new_h5 = {'red': None, 'green': None, 'blue': None,'max_r': 1, 'max_g': 1, 'max_b': 1,'force_t': None, 'force_v': None}
            valid_shape = None
            
            # Load channels
            for col in ['red', 'green', 'blue']:
                if col in data:
                    arr = data[col].astype(float)
                    new_h5[col] = arr
                    vmax = np.percentile(arr, 99.5)
                    new_h5[f'max_{col[0]}'] = vmax if vmax > 0 else 1
                    if valid_shape is None:
                        valid_shape = arr.shape
            
            # Support legacy 'kymo_data' key
            if new_h5['green'] is None and 'kymo_data' in data:
                arr = data['kymo_data'].astype(float)
                new_h5['green'] = arr
                vmax = np.percentile(arr, 99.5)
                new_h5['max_g'] = vmax if vmax > 0 else 1
                if valid_shape is None:
                    valid_shape = arr.shape

            if valid_shape is None:
                messagebox.showerror("Loading Error", "No image data found in NPZ.")
                return

            # Metadata
            try:
                line_time = float(data['line_time'])
            except Exception:
                line_time = 0.1

            try:
                pixel_size = float(data['pixel_size'])
            except Exception:
                pixel_size = 0.1

            # ── 拼接分割线时间列表（兼容新/旧格式）──
            stitch_times_list = []
            if 'stitch_times' in data:
                # 新格式：ndarray，可含多个时间点
                arr_st = np.asarray(data['stitch_times']).flatten()
                stitch_times_list = [float(v) for v in arr_st if np.isfinite(v)]
            elif 'stitch_duration' in data:
                # 旧格式：单个时间点（两段拼接）
                try:
                    stitch_times_list = [float(data['stitch_duration'])]
                except Exception:
                    pass

            duration  = valid_shape[1] * line_time
            width_um  = valid_shape[0] * pixel_size

            self.h5_data = new_h5
            self.h5_metadata = {'duration': duration, 'width': width_um, 'is_scan': False}
            self.is_h5_mode = True
            self.current_file_path = npz_path

            # 清理标题
            filename    = os.path.basename(npz_path)
            clean_name  = os.path.splitext(filename)[0]
            clean_title = clean_name.replace("Stitched", "").replace("Stitch_", "")

            self.init_matplotlib_plot(
                clean_title,
                [0, duration, 0, width_um],
                "Time (s)", "Position (μm)",
                stitch_times=stitch_times_list
            )
            self.update_plot_content()
            
            seg_info = f"({len(stitch_times_list)+1} 段)" if stitch_times_list else ""
            self.status_bar.config(
                text=f"Stitched Data Loaded {seg_info}: {os.path.basename(npz_path)}")
            
        except Exception as e:
            messagebox.showerror("Stitch Load Error", str(e))
            traceback.print_exc()

    def load_image_from_disk(self, path):
        try:
            img = Image.open(path); arr = np.array(img)
            self.ax.clear(); 
            if self.ax_force: self.ax_force.clear()
            self.image_artist = None; self.ax.axis('off'); 
            if self.ax_force: self.ax_force.axis('off')
            self.ax.set_title(os.path.basename(path), fontsize=10, fontname='Arial')
            self.ax.imshow(arr, aspect='auto'); self.canvas.draw()
        except: pass

    def init_matplotlib_plot(self, title, extent, xlabel, ylabel, stitch_times=None):
        # ── 清空旧标注（加载新文件时不保留上一张的标注）──
        self.annotations.clear()
        self.annot_artists.clear()
        self.annot_pending_points.clear()
        self.annot_preview_artist = None

        # ── 清除 BG ROI 选取状态（新文件不继承旧 ROI）──
        if self._bg_roi_select_mode:
            self._cancel_bg_roi_select()
        self.bg_roi_coords = None
        self._bg_roi_rect_patch = None
        self._bg_roi_preview_patch = None
        try:
            self._lbl_roi_coords.config(text=self.tr('bg_not_selected'))
        except Exception:
            pass



        self.fig.clear()
        
        is_scan = self.h5_metadata.get('is_scan', False)
        # Scan 模式下不显示 Force Plot
        has_force = (self.force_channel_var.get() != "None") and (not is_scan)
        
        if has_force:
            gs = self.fig.add_gridspec(2, 1, height_ratios=[3, 1], hspace=0.15)
            self.ax = self.fig.add_subplot(gs[0])
            self.ax_force = self.fig.add_subplot(gs[1], sharex=self.ax)
            self.ax_force.axis('on')
            self.ax_force.set_xlabel(xlabel, fontsize=9, fontname='Arial')
            self.ax_force.set_ylabel("Force (pN)", fontsize=9, fontname='Arial')
            self.ax.tick_params(labelbottom=False)
        else:
            self.ax = self.fig.add_subplot(111)
            self.ax_force = None 
            self.ax.set_xlabel(xlabel, fontsize=9, fontname='Arial')
        
        self.ax.axis('on')
        self.ax.set_title(title, fontsize=10, fontname='Arial')
        
        self.ax.set_ylabel(self._get_y_label(), fontsize=9, fontname='Arial')
        
        self.current_extent = extent
        
        # 绘制拼接分割线（支持单值/列表两种传入方式）
        if stitch_times is not None:
            # 兼容旧版单值写法
            if isinstance(stitch_times, (int, float)):
                stitch_times = [stitch_times]
            for st in stitch_times:
                self.ax.axvline(x=st, color='white', linestyle='--',
                                linewidth=1, alpha=0.8)

        # --- 核心：AspectRatio 控制 ---
        if self.aspect_equal_var.get():
            self.ax.set_aspect('equal')
        else:
            self.ax.set_aspect('auto')

        self.ax.set_xlim(extent[0], extent[1])
        self.ax.set_ylim(extent[2], extent[3])
        if self.ax_force: self.ax_force.set_xlim(extent[0], extent[1])
        
        self.image_artist = None

    def update_plot_content(self):
        if not self.is_h5_mode: return
        self._clear_temp_markers()

        # RGB 图像合成
        shape = None
        for c in ['red', 'green', 'blue']:
            if self.h5_data[c] is not None: shape = self.h5_data[c].shape; break
        if not shape: return

        rgb = np.zeros((shape[0], shape[1], 3), dtype=np.float32)
        for col, idx in {'red': 0, 'green': 1, 'blue': 2}.items():
            if self.channel_vars[col].get() and self.h5_data[col] is not None:
                raw_data = self.h5_data[col]
                gain = self.contrast_vars[col].get()
                offset = self.brightness_vars[col].get()
                channel_val = (raw_data + offset) * gain
                channel_val = channel_val / 255.0
                rgb[:, :, idx] = channel_val

        # ── 背景扣除 ──
        if self.bg_sub_enable_var.get():
            try:
                smooth = max(0, self.bg_smooth_var.get())
                mode   = self.bg_mode_var.get()   # 'timezero' | 'temporal' | 'spatial' n_rows, n_cols = rgb.shape[:2]

                for ch_idx in range(3):
                    ch = rgb[:, :, ch_idx]   # (rows, cols)

                    if mode == 'timezero':
                        # 模式0: 取前 N 帧逐行均值作为 t=0 背景，然后相减
                        # 对应文献 "intensities normalized to background at time zero"
                        n_t0 = max(1, min(self.bg_t0_frames_var.get(), n_cols))
                        bg_row = ch[:, :n_t0].mean(axis=1).astype('float32')  # (rows,)

                        if smooth > 1:
                            kernel = np.ones(smooth, dtype='float32') / smooth
                            bg_row = np.convolve(bg_row, kernel, mode='same')

                        rgb[:, :, ch_idx] = ch - bg_row[:, np.newaxis]

                    elif mode == 'temporal':
                        # 模式1: 每行取时间轴低百分位作为背景
                        pct = max(1, min(99, self.bg_percentile_var.get()))
                        bg_row = np.percentile(ch, pct, axis=1).astype('float32')

                        if smooth > 1:
                            kernel = np.ones(smooth, dtype='float32') / smooth
                            bg_row = np.convolve(bg_row, kernel, mode='same')

                        rgb[:, :, ch_idx] = ch - bg_row[:, np.newaxis]

                    elif mode == 'spatial':
                        # 模式2: 空间两侧均值背景
                        bw = max(1, self.bg_width_var.get())
                        left_w  = min(bw, n_cols // 4)
                        right_w = min(bw, n_cols // 4)

                        bg_left  = ch[:, :left_w].mean(axis=1)
                        bg_right = ch[:, n_cols - right_w:].mean(axis=1)
                        bg_row   = ((bg_left + bg_right) / 2.0).astype('float32')

                        if smooth > 1:
                            kernel = np.ones(smooth, dtype='float32') / smooth
                            bg_row = np.convolve(bg_row, kernel, mode='same')

                        rgb[:, :, ch_idx] = ch - bg_row[:, np.newaxis]

                    else:
                        # 模式3: ROI 框选背景
                        # 用拖拽选中矩形内的像素，逐行计算中位数或均值，然后减除
                        coords = self.bg_roi_coords
                        if coords is None:
                            continue   # 尚未选取 ROI，跳过
                        col0, row0, col1, row1 = coords
                        # 确保索引在范围内
                        col0 = max(0, min(col0, n_cols))
                        col1 = max(0, min(col1, n_cols))
                        row0 = max(0, min(row0, n_rows))
                        row1 = max(0, min(row1, n_rows))
                        if col1 <= col0 or row1 <= row0:
                            continue

                        roi_patch = ch[row0:row1, col0:col1]   # (roi_h, roi_w)
                        stat = self.bg_roi_stat_var.get()

                        if stat == 'median':
                            # 逐行中位数（高背景推荐，对热点/瞬间亮斑稳健）
                            roi_bg = np.median(roi_patch, axis=1).astype('float32')  # (roi_h,)
                        else:
                            roi_bg = roi_patch.mean(axis=1).astype('float32')

                        # roi_bg 只有 roi 区域的行数，需要扩展到全图行数
                        # 用 roi_bg 整体均值/中位数作为全图每行的背景估算值
                        # （因为 ROI 选在背景区，该区域的统计代表整个时间轴的背景水平）
                        bg_scalar = float(np.median(roi_bg) if stat == 'median' else roi_bg.mean())
                        bg_row = np.full(n_rows, bg_scalar, dtype='float32')

                        if smooth > 1:
                            # 平滑无效（scalar），跳过
                            pass

                        rgb[:, :, ch_idx] = ch - bg_row[:, np.newaxis]

            except Exception:
                pass

        rgb = np.clip(rgb, 0, 1)

        if self.flip_y_var.get(): rgb = np.flipud(rgb)
        
        y_scale = self._get_y_scale_factor()
        
        # Scan 模式下 metadata['duration'] 实际上存的是宽度
        x_max_val = self.h5_metadata['duration']
        y_max_val = self.h5_metadata['width'] / y_scale
        
        display_extent = [0, x_max_val, 0, y_max_val]
        
        if self.image_artist: 
            self.image_artist.set_data(rgb)
            self.image_artist.set_extent(display_extent) 
        else: 
            self.image_artist = self.ax.imshow(rgb, aspect='auto', extent=display_extent, origin='lower')
        
        # 再次强制 Aspect Ratio，防止被 imshow 重置
        if self.aspect_equal_var.get():
            self.ax.set_aspect('equal')
        else:
            self.ax.set_aspect('auto')
        
        # Force Plot 更新 (仅限 Kymo)
        if self.ax_force and self.force_channel_var.get() != "None" and not self.h5_metadata.get('is_scan', False):
            self.ax_force.clear()
            if self.h5_data['force_t'] is not None and self.h5_data['force_v'] is not None:
                f_time = self.h5_data['force_t']
                f_val = self.h5_data['force_v']
                
                if self.crop_enable_var.get():
                    x_start = self.axis_vars['xmin'].get()
                    x_end = self.axis_vars['xmax'].get()
                else:
                    x_start = display_extent[0]
                    x_end = display_extent[1]
                
                mask = (f_time >= x_start) & (f_time <= x_end)
                if np.any(mask):
                    visible_vals = f_val[mask]
                    y_min, y_max = np.min(visible_vals), np.max(visible_vals)
                    span = y_max - y_min if y_max != y_min else 1.0
                    self.ax_force.set_ylim(y_min - span*0.1, y_max + span*0.1)
                
                self.ax_force.plot(f_time, f_val, linewidth=0.5, color='black')
                self.ax_force.set_ylabel(self.force_channel_var.get() + " (pN)", fontsize=9, fontname='Arial')
                self.ax_force.grid(True, linestyle='--', alpha=0.5)
                self.ax_force.yaxis.set_major_locator(MaxNLocator(nbins=5, integer=True))
        
        # 坐标轴刻度更新
        try: x_step = self.tick_vars['x_step'].get()
        except: x_step = 0
        try: y_step = self.tick_vars['y_step'].get()
        except: y_step = 0

        target_ax = self.ax_force if (self.ax_force and self.force_channel_var.get() != "None" and not self.h5_metadata.get('is_scan', False)) else self.ax

        if self.crop_enable_var.get():
            try:
                x_min = self.axis_vars['xmin'].get(); x_max = self.axis_vars['xmax'].get()
                y_min_um = self.axis_vars['ymin'].get(); y_max_um = self.axis_vars['ymax'].get()
                y_min_disp = y_min_um / y_scale
                y_max_disp = y_max_um / y_scale
                
                self.ax.set_xlim(x_min, x_max)
                self.ax.set_ylim(y_min_disp, y_max_disp)
                
                if x_step > 0:
                    target_ax.xaxis.set_major_locator(MultipleLocator(x_step))
                    target_ax.xaxis.set_major_formatter(FuncFormatter(lambda x, p: f"{int(round(x - x_min))}"))
                else:
                    target_ax.xaxis.set_major_locator(AutoLocator())
                    target_ax.xaxis.set_major_formatter(ticker.ScalarFormatter())

                if y_step > 0:
                    self.ax.yaxis.set_major_locator(MultipleLocator(y_step))
                    self.ax.yaxis.set_major_formatter(FuncFormatter(lambda y, p: f"{int(round(y - y_min_disp))}"))
                else:
                    self.ax.yaxis.set_major_locator(AutoLocator())
                    self.ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
            except: pass
        else:
            self.ax.set_xlim(display_extent[0], display_extent[1])
            self.ax.set_ylim(0, display_extent[3])
            
            if x_step > 0: target_ax.xaxis.set_major_locator(MultipleLocator(x_step))
            else: target_ax.xaxis.set_major_locator(AutoLocator())
            target_ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
            
            if y_step > 0: self.ax.yaxis.set_major_locator(MultipleLocator(y_step))
            else: self.ax.yaxis.set_major_locator(AutoLocator())
            self.ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
        
        self.ax.set_ylabel(self._get_y_label(), fontsize=9, fontname='Arial')
        
        # 重绘标注（保证图像刷新后标注不消失）
        self._redraw_annotations()
        
        self.canvas.draw()

    def on_file_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        self.current_index = int(sel[0]); item = self.all_images_data[self.current_index]
        self.is_h5_mode = (item['type'] == 'H5'); self.current_file_path = item['full_path']
        if self.control_panel:
            state = '!disabled' if self.is_h5_mode else 'disabled'
            for child in self.control_panel.winfo_children():
                try: child.state([state])
                except: pass

        if self.is_h5_mode: self.load_h5_kymo(item['full_path'])
        else: self.load_image_from_disk(item['full_path'])
    def select_index(self, i): 
        if 0<=i<len(self.all_images_data): self.tree.selection_set(str(i)); self.tree.see(str(i))
    def navigate(self, d): self.select_index(self.current_index + d)
    def select_output_root(self): 
        d=filedialog.askdirectory()
        if d: 
            for x in os.listdir(d): 
                if os.path.isdir(os.path.join(d,x)): self.register_category(x,os.path.join(d,x))
            self.scan_all_categories_status()
    def link_existing_folder(self): d=filedialog.askdirectory(); (self.register_category(os.path.basename(d),d), self.scan_all_categories_status()) if d else None
    def create_new_category_folder(self): d=filedialog.askdirectory(); n=simpledialog.askstring("New","Name:"); (os.makedirs(os.path.join(d,n),exist_ok=True), self.register_category(n,os.path.join(d,n))) if d and n else None

    def open_stitcher_window(self):
        if not H5_SUPPORT:
            messagebox.showerror("Error", "lumicks.pylake is not installed.")
            return
        win = StitcherWindow(self)

    # =========================================================
    #  标注系统 (Annotation System)
    # =========================================================
    def open_annotation_panel(self):
        """打开标注工具面板（独立浮动窗口）"""
        if hasattr(self, '_annot_win') and self._annot_win.winfo_exists():
            self._annot_win.lift()
            return

        win = tk.Toplevel(self)
        win.title(self.tr('annot_win_title'))
        win.geometry("420x640")
        win.resizable(False, False)
        self._annot_win = win

        pad = {'padx': 10, 'pady': 4}

        # ------- 工具选择 -------
        ttk.Label(win, text=self.tr('draw_tools'), font=('Segoe UI', 11, 'bold')).pack(anchor='w', **pad)
        tool_frame = ttk.Frame(win)
        tool_frame.pack(fill=tk.X, **pad)

        self._annot_mode_btn_var = tk.StringVar(value='')

        tools = [
            (self.tr('tool_hline'), 'hline'),
            (self.tr('tool_vline'), 'vline'),
            (self.tr('tool_line'), 'line'),
            (self.tr('tool_arrow'), 'arrow'),
            (self.tr('tool_text'), 'text'),
            (self.tr('tool_point'), 'point'),
        ]
        for i, (label, mode) in enumerate(tools):
            rb = ttk.Radiobutton(
                tool_frame, text=label,
                variable=self._annot_mode_btn_var, value=mode,
                bootstyle='',
                command=lambda m=mode: self._set_annot_mode(m)
            )
            rb.grid(row=i//2, column=i%2, padx=8, pady=4, sticky='w')

        ttk.Separator(win, orient='horizontal').pack(fill=tk.X, padx=10, pady=6)

        # ------- 样式设置 -------
        ttk.Label(win, text=self.tr('style_settings'), font=('Segoe UI', 11, 'bold')).pack(anchor='w', **pad)
        style_frame = ttk.Frame(win)
        style_frame.pack(fill=tk.X, padx=10)

        # 颜色
        cr = ttk.Frame(style_frame); cr.pack(fill=tk.X, pady=3)
        ttk.Label(cr, text=self.tr('color_label'), width=10).pack(side=tk.LEFT)
        colors = ['white', 'yellow', 'cyan', 'red', 'lime', 'orange', 'black', '#aaaaaa']
        self._color_btns = {}
        color_box = ttk.Frame(cr)
        color_box.pack(side=tk.LEFT)
        for c in colors:
            btn = tk.Button(
                color_box, bg=c, width=2, height=1, relief='flat', bd=1,
                command=lambda col=c: self._select_annot_color(col)
            )
            btn.pack(side=tk.LEFT, padx=1)
            self._color_btns[c] = btn
        ttk.Button(cr, text=self.tr('custom_color'), command=self._pick_custom_color, width=8).pack(side=tk.LEFT, padx=5)
        self._cur_color_lbl = tk.Label(cr, bg=self.annot_color_var.get(), width=3, relief='sunken')
        self._cur_color_lbl.pack(side=tk.LEFT, padx=3)

        # 线宽
        lwr = ttk.Frame(style_frame); lwr.pack(fill=tk.X, pady=3)
        ttk.Label(lwr, text=self.tr('linewidth_label'), width=10).pack(side=tk.LEFT)
        ttk.Scale(lwr, from_=0.5, to=5.0, variable=self.annot_linewidth_var,
                  orient=tk.HORIZONTAL, length=160, bootstyle='').pack(side=tk.LEFT)
        ttk.Label(lwr, textvariable=self.annot_linewidth_var, width=4).pack(side=tk.LEFT, padx=3)

        # 线型
        lsr = ttk.Frame(style_frame); lsr.pack(fill=tk.X, pady=3)
        ttk.Label(lsr, text=self.tr('linestyle_label'), width=10).pack(side=tk.LEFT)
        for ls_label, ls_val in [(self.tr('ls_solid'), '-'), (self.tr('ls_dashed'), '--'), (self.tr('ls_dotted'), ':'), (self.tr('ls_dashdot'), '-.')]:
            ttk.Radiobutton(lsr, text=ls_label, variable=self.annot_linestyle_var,
                            value=ls_val, bootstyle='').pack(side=tk.LEFT, padx=4)

        # 透明度
        alr = ttk.Frame(style_frame); alr.pack(fill=tk.X, pady=3)
        ttk.Label(alr, text=self.tr('alpha_label'), width=10).pack(side=tk.LEFT)
        ttk.Scale(alr, from_=0.1, to=1.0, variable=self.annot_alpha_var,
                  orient=tk.HORIZONTAL, length=160, bootstyle='').pack(side=tk.LEFT)

        ttk.Separator(win, orient='horizontal').pack(fill=tk.X, padx=10, pady=6)

        # ------- 文字标注编辑区 -------
        ttk.Label(win, text=self.tr('text_edit_title'), font=('Segoe UI', 11, 'bold')).pack(anchor='w', **pad)
        text_frame = ttk.Labelframe(win, text="", padding=8, bootstyle='warning')
        text_frame.pack(fill=tk.X, padx=10, pady=2)

        # 文字内容输入框
        tc_row = ttk.Frame(text_frame); tc_row.pack(fill=tk.X, pady=2)
        ttk.Label(tc_row, text=self.tr('content_label'), width=8).pack(side=tk.LEFT)
        self._text_content_var = tk.StringVar(value='')
        ttk.Entry(tc_row, textvariable=self._text_content_var, width=24).pack(side=tk.LEFT, padx=5)

        # 字体大小
        fs_row = ttk.Frame(text_frame); fs_row.pack(fill=tk.X, pady=2)
        ttk.Label(fs_row, text=self.tr('fontsize_label'), width=8).pack(side=tk.LEFT)
        ttk.Spinbox(fs_row, from_=6, to=48, textvariable=self.annot_fontsize_var,
                    width=6).pack(side=tk.LEFT, padx=5)
        ttk.Label(fs_row, text="pt", foreground='#999999').pack(side=tk.LEFT)

        # 应用按钮
        apply_row = ttk.Frame(text_frame); apply_row.pack(fill=tk.X, pady=(6, 2))
        ttk.Label(apply_row, text=self.tr('text_place_hint'),
                  font=('Segoe UI', 9), foreground='#777777').pack(anchor='w')
        apply_btn_row = ttk.Frame(text_frame); apply_btn_row.pack(fill=tk.X, pady=2)
        ttk.Button(apply_btn_row, text=self.tr('apply_text_btn'),
                   command=self._apply_text_edit,
                   bootstyle='').pack(side=tk.LEFT, padx=0)
        ttk.Label(apply_btn_row, text=self.tr('dblclick_hint'),
                  font=('Segoe UI', 9), foreground='#999999').pack(side=tk.LEFT, padx=8)

        ttk.Separator(win, orient='horizontal').pack(fill=tk.X, padx=10, pady=6)

        # ------- 操作按钮 -------
        act_frame = ttk.Frame(win)
        act_frame.pack(fill=tk.X, padx=10, pady=4)

        ttk.Button(act_frame, text=self.tr('undo_btn'), command=self._undo_last_annotation,
                   bootstyle='secondary-outline').pack(side=tk.LEFT, padx=5)
        ttk.Button(act_frame, text=self.tr('clear_annot_btn'), command=self._clear_all_annotations,
                   bootstyle='danger-outline').pack(side=tk.LEFT, padx=5)
        ttk.Button(act_frame, text=self.tr('exit_annot_btn'), command=self._exit_annot_mode,
                   bootstyle='secondary').pack(side=tk.RIGHT, padx=5)

        # 状态提示
        self._annot_status_var = tk.StringVar(value=self.tr('annot_status_init'))
        ttk.Label(win, textvariable=self._annot_status_var,
                  font=('Segoe UI', 10), foreground='#999999').pack(anchor='w', padx=10, pady=4)

        win.protocol("WM_DELETE_WINDOW", self._exit_annot_mode)

    def _select_annot_color(self, color):
        self.annot_color_var.set(color)
        try:
            self._cur_color_lbl.config(bg=color)
        except:
            pass

    def _pick_custom_color(self):
        from tkinter.colorchooser import askcolor
        result = askcolor(color=self.annot_color_var.get(), title=self.tr('pick_color_title'))
        if result and result[1]:
            self._select_annot_color(result[1])

    def _set_annot_mode(self, mode):
        """激活某种标注模式"""
        # 先断开旧的事件
        self._disconnect_annot_events()
        self.annot_pending_points = []
        self._remove_annot_preview()
        self._selected_text_idx = None
        self._text_edit_idx = None

        self.annot_mode = mode
        tips = {'hline': self.tr('annot_tip_hline'),'vline': self.tr('annot_tip_vline'),'line':  self.tr('annot_tip_line'),'arrow': self.tr('annot_tip_arrow'),'text':  self.tr('annot_tip_text'),'point': self.tr('annot_tip_point'),
        }
        if hasattr(self, '_annot_status_var'):
            self._annot_status_var.set(tips.get(mode, ''))

        # 连接事件
        self.annot_cid = self.canvas.mpl_connect('button_press_event', self._on_annot_click)
        if mode in ('line', 'arrow'):
            self.annot_move_cid = self.canvas.mpl_connect('motion_notify_event', self._on_annot_move)
        if mode == 'text':
            # 注册文字拖动事件
            self._drag_cid_motion  = self.canvas.mpl_connect('motion_notify_event',   self._on_text_drag_motion)
            self._drag_cid_release = self.canvas.mpl_connect('button_release_event',   self._on_text_drag_release)

        self.status_bar.config(text=self.tr('annot_mode_status') + f" {mode} " + self.tr('annot_cancel_hint'))

    def _exit_annot_mode(self):
        self._disconnect_annot_events()
        self._remove_annot_preview()
        self.annot_mode = None
        self.annot_pending_points = []
        if hasattr(self, '_annot_mode_btn_var'):
            self._annot_mode_btn_var.set('')
        self.status_bar.config(text=self.tr('ready'))
        if hasattr(self, '_annot_win') and self._annot_win.winfo_exists():
            self._annot_win.destroy()
        if hasattr(self, '_text_edit_win') and self._text_edit_win is not None:
            try:
                self._text_edit_win.destroy()
            except:
                pass

    def _disconnect_annot_events(self):
        if self.annot_cid is not None:
            try: self.canvas.mpl_disconnect(self.annot_cid)
            except: pass
            self.annot_cid = None
        if self.annot_move_cid is not None:
            try: self.canvas.mpl_disconnect(self.annot_move_cid)
            except: pass
            self.annot_move_cid = None
        for attr in ('_drag_cid_press', '_drag_cid_motion', '_drag_cid_release'):
            cid = getattr(self, attr, None)
            if cid is not None:
                try: self.canvas.mpl_disconnect(cid)
                except: pass
                setattr(self, attr, None)

    def _remove_annot_preview(self):
        if self.annot_preview_artist is not None:
            try: self.annot_preview_artist.remove()
            except: pass
            self.annot_preview_artist = None
            self.canvas.draw_idle()

    def _get_annot_style(self):
        return {'color': self.annot_color_var.get(),'linewidth': self.annot_linewidth_var.get(),'linestyle': self.annot_linestyle_var.get(),'fontsize': self.annot_fontsize_var.get(),'alpha': self.annot_alpha_var.get(),
        }

    def _on_annot_click(self, event):
        """处理标注画布点击"""
        if event.inaxes != self.ax:
            return
        x, y = event.xdata, event.ydata
        if x is None or y is None:
            return

        mode = self.annot_mode
        style = self._get_annot_style()

        # 右键处理：text 模式打开编辑面板，其他模式取消当前操作
        if event.button == 3:
            if mode == 'text':
                idx = self._find_nearest_text_annotation(x, y)
                if idx is not None:
                    self._open_text_edit_panel(idx, event.x, event.y)
            else:
                self.annot_pending_points = []
                self._remove_annot_preview()
                if hasattr(self, '_annot_status_var'):
                    self._annot_status_var.set("已取消，请重新点击")
            return

        if event.button != 1:
            return

        if mode == 'hline':
            self._draw_annotation({'type': 'hline', 'y': y, **style})

        elif mode == 'vline':
            self._draw_annotation({'type': 'vline', 'x': x, **style})

        elif mode == 'point':
            self._draw_annotation({'type': 'point', 'x': x, 'y': y, **style})

        elif mode == 'text':
            # 查找点击位置最近的文字标注
            idx = self._find_nearest_text_annotation(x, y)
            if event.button == 3:  # 右键
                if idx is not None:
                    # 右键点击已有文字  打开编辑面板
                    self._open_text_edit_panel(idx, event.x, event.y)
                return
            # 左键
            if idx is not None:
                # 左键点击已有文字  开始拖动
                self._dragging_text_idx = idx
                self._drag_offset = (
                    self.annotations[idx]['x'] - x,
                    self.annotations[idx]['y'] - y,
                )
                return
            # 左键点击空白处  放置新文字
            content = ''
            if hasattr(self, '_text_content_var'):
                content = self._text_content_var.get().strip()

            if not content:
                content = simpledialog.askstring(self.tr('text_annot_title'), self.tr('text_annot_prompt'), parent=self)
                if content and hasattr(self, '_text_content_var'):
                    self._text_content_var.set(content)
            if content:
                self._draw_annotation({'type': 'text', 'x': x, 'y': y, 'text': content, **style})

        elif mode in ('line', 'arrow'):
            if len(self.annot_pending_points) == 0:
                self.annot_pending_points = [(x, y)]
                # 画起点标记
                marker, = self.ax.plot(x, y, '+', color=style['color'],
                                       markersize=10, markeredgewidth=1.5, alpha=style['alpha'])
                self.annot_preview_artist = marker
                self.canvas.draw_idle()
                if hasattr(self, '_annot_status_var'):
                    self._annot_status_var.set(self.tr('annot_start_picked'))
            else:
                x0, y0 = self.annot_pending_points[0]
                self._remove_annot_preview()
                self.annot_pending_points = []
                self._draw_annotation({'type': mode, 'x0': x0, 'y0': y0,'x1': x, 'y1': y, **style})
                if hasattr(self, '_annot_status_var'):
                    tips = {'line': self.tr('annot_tip_line_2'),'arrow': self.tr('annot_tip_arrow_2')}
                    self._annot_status_var.set(tips.get(mode, ''))

    def _on_annot_move(self, event):
        """在 line/arrow 模式下显示预览线"""
        if len(self.annot_pending_points) != 1:
            return
        if event.inaxes != self.ax:
            return
        x0, y0 = self.annot_pending_points[0]
        x1, y1 = event.xdata, event.ydata
        if x1 is None or y1 is None:
            return
        style = self._get_annot_style()

        # 移除旧预览
        if self.annot_preview_artist is not None:
            try: self.annot_preview_artist.remove()
            except: pass
            self.annot_preview_artist = None

        if self.annot_mode == 'arrow':
            art = self.ax.annotate('', xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(
                    arrowstyle='->', color=style['color'],
                    lw=style['linewidth']
                ),
                alpha=style['alpha']
            )
        else:
            art, = self.ax.plot([x0, x1], [y0, y1],
                                 color=style['color'],
                                 linewidth=style['linewidth'],
                                 linestyle=style['linestyle'],
                                 alpha=style['alpha'] * 0.5)
        self.annot_preview_artist = art
        self.canvas.draw_idle()

    def _draw_annotation(self, info):
        """根据 info 字典绘制标注，并记录到 self.annotations"""
        color = info.get('color', 'white')
        lw = info.get('linewidth', 1.5)
        ls = info.get('linestyle', '--')
        alpha = info.get('alpha', 0.9)
        fs = info.get('fontsize', 10)
        t = info.get('type')

        artist = None

        if t == 'hline':
            artist = self.ax.axhline(y=info['y'], color=color, linewidth=lw,
                                      linestyle=ls, alpha=alpha)
        elif t == 'vline':
            artist = self.ax.axvline(x=info['x'], color=color, linewidth=lw,
                                      linestyle=ls, alpha=alpha)
        elif t == 'line':
            artist, = self.ax.plot([info['x0'], info['x1']], [info['y0'], info['y1']],
                                    color=color, linewidth=lw, linestyle=ls, alpha=alpha)
        elif t == 'arrow':
            artist = self.ax.annotate('', xy=(info['x1'], info['y1']), xytext=(info['x0'], info['y0']),
                arrowprops=dict(
                    arrowstyle='->', color=color, lw=lw,
                    linestyle='solid' ),
                alpha=alpha
            )
        elif t == 'text':
            artist = self.ax.text(
                info['x'], info['y'], info['text'],
                color=color, fontsize=fs, alpha=alpha,
                fontname='Arial',
                bbox=dict(boxstyle='round,pad=0.2', fc='none', ec=color,
                          lw=0.5, alpha=alpha * 0.5)
            )
        elif t == 'point':
            artist, = self.ax.plot(info['x'], info['y'], 'o',
                                    color=color, markersize=6,
                                    alpha=alpha, markeredgewidth=0)

        if artist is not None:
            self.annotations.append(info)
            self.annot_artists.append(artist)
            self.canvas.draw_idle()

    def _undo_last_annotation(self):
        """撤销最后一条标注"""
        if not self.annot_artists:
            return
        artist = self.annot_artists.pop()
        try: artist.remove()
        except: pass
        if self.annotations:
            self.annotations.pop()
        self.canvas.draw_idle()

    def _clear_all_annotations(self):
        """清空所有标注"""
        for artist in self.annot_artists:
            try: artist.remove()
            except: pass
        self.annot_artists.clear()
        self.annotations.clear()
        self.canvas.draw_idle()

    def _redraw_annotations(self):
        """重绘所有已保存的标注（在 update_plot_content 后调用）"""
        self.annot_artists.clear()
        for info in list(self.annotations):
            self._draw_annotation_no_record(info)

    def _draw_annotation_no_record(self, info):
        """与 _draw_annotation 相同，但不记录到 self.annotations（用于重绘）"""
        color = info.get('color', 'white')
        lw = info.get('linewidth', 1.5)
        ls = info.get('linestyle', '--')
        alpha = info.get('alpha', 0.9)
        fs = info.get('fontsize', 10)
        t = info.get('type')
        artist = None

        if t == 'hline':
            artist = self.ax.axhline(y=info['y'], color=color, linewidth=lw, linestyle=ls, alpha=alpha)
        elif t == 'vline':
            artist = self.ax.axvline(x=info['x'], color=color, linewidth=lw, linestyle=ls, alpha=alpha)
        elif t == 'line':
            artist, = self.ax.plot([info['x0'], info['x1']], [info['y0'], info['y1']],
                                    color=color, linewidth=lw, linestyle=ls, alpha=alpha)
        elif t == 'arrow':
            artist = self.ax.annotate('', xy=(info['x1'], info['y1']), xytext=(info['x0'], info['y0']),
                arrowprops=dict(arrowstyle='->', color=color, lw=lw, linestyle='solid'),
                alpha=alpha
            )
        elif t == 'text':
            artist = self.ax.text(
                info['x'], info['y'], info['text'],
                color=color, fontsize=fs, alpha=alpha, fontname='Arial',
                bbox=dict(boxstyle='round,pad=0.2', fc='none', ec=color, lw=0.5, alpha=alpha*0.5)
            )
        elif t == 'point':
            artist, = self.ax.plot(info['x'], info['y'], 'o', color=color,
                                    markersize=6, alpha=alpha, markeredgewidth=0)

        if artist is not None:
            self.annot_artists.append(artist)

    # -------- 文字标注：拖动 --------
    def _on_text_drag_motion(self, event):
        """拖动过程中实时更新文字位置"""
        if self.annot_mode != 'text':
            return
        if self._dragging_text_idx is None:
            return
        if event.inaxes != self.ax:
            return
        x, y = event.xdata, event.ydata
        if x is None or y is None:
            return
        idx = self._dragging_text_idx
        new_x = x + self._drag_offset[0]
        new_y = y + self._drag_offset[1]
        # 更新数据
        self.annotations[idx]['x'] = new_x
        self.annotations[idx]['y'] = new_y
        # 直接更新 artist
        artist = self.annot_artists[idx]
        artist.set_position((new_x, new_y))
        self.canvas.draw_idle()

    def _on_text_drag_release(self, event):
        """松开鼠标结束拖动"""
        if self.annot_mode != 'text':
            return
        self._dragging_text_idx = None
        self._drag_offset = (0, 0)

    def _find_nearest_text_annotation(self, x, y, tol_frac=0.04):
        """返回距离 (x,y) 最近的文字标注索引，超过容差则返回 None"""
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        tol_x = (xlim[1] - xlim[0]) * tol_frac
        tol_y = (ylim[1] - ylim[0]) * tol_frac
        best_idx = None
        best_d = float('inf')
        for i, info in enumerate(self.annotations):
            if info.get('type') != 'text':
                continue
            dx = abs(info['x'] - x) / max(tol_x, 1e-12)
            dy = abs(info['y'] - y) / max(tol_y, 1e-12)
            d = (dx**2 + dy**2) ** 0.5
            if d < 1.0 and d < best_d:
                best_d = d
                best_idx = i
        return best_idx

    # -------- 文字标注：右键编辑面板 --------
    def _open_text_edit_panel(self, idx, screen_x, screen_y):
        """在文字标注位置弹出编辑面板，实时编辑内容/字号/颜色"""
        # 如果已有面板，先关闭
        if hasattr(self, '_text_edit_win') and self._text_edit_win is not None:
            try:
                self._text_edit_win.destroy()
            except:
                pass

        self._text_edit_idx = idx
        info = self.annotations[idx]

        win = tk.Toplevel(self)
        win.title("编辑文字标注")
        win.attributes('-topmost', True)
        win.resizable(False, False)

        # 偏移到鼠标位置附近
        try:
            win.geometry(f"+{screen_x+10}+{screen_y-80}")
        except Exception:
            win.geometry("+100+100")

        # ---- 实时更新函数：直接修改 artist，不重建 ----
        def _do_update():
            new_text = entry.get().strip()
            try:
                new_fs = float(fs_var.get())
            except Exception:
                new_fs = info.get('fontsize', 10)
            new_color = color_var.get()

            # 更新数据
            self.annotations[idx]['text'] = new_text
            self.annotations[idx]['fontsize'] = new_fs
            self.annotations[idx]['color'] = new_color

            # 直接修改 artist（比重建更可靠）
            artist = self.annot_artists[idx]
            artist.set_text(new_text)
            artist.set_fontsize(new_fs)
            artist.set_color(new_color)
            self.canvas.draw_idle()

        # ---- 内容输入 ----
        frm_content = ttk.Frame(win)
        frm_content.pack(fill=X, padx=10, pady=(10, 5))
        ttk.Label(frm_content, text=self.tr('content_label')).pack(side=LEFT)
        entry = ttk.Entry(frm_content, width=28)
        entry.insert(0, info.get('text', ''))
        entry.pack(side=LEFT, padx=(5, 0), fill=X, expand=True)
        # 打字即实时更新
        entry.bind('<KeyRelease>', lambda *a: _do_update())
        entry.bind('<FocusOut>', lambda *a: _do_update())

        # ---- 字号 ----
        frm_fs = ttk.Frame(win)
        frm_fs.pack(fill=X, padx=10, pady=5)
        ttk.Label(frm_fs, text=self.tr('te_fontsize')).pack(side=LEFT)
        fs_var = tk.StringVar(value=str(info.get('fontsize', 10)))
        fs_spin = ttk.Spinbox(frm_fs, from_=6, to=72, textvariable=fs_var, width=5)
        fs_spin.pack(side=LEFT, padx=(5, 10))
        ttk.Label(frm_fs, text="pt").pack(side=LEFT)
        # Spinbox 变化实时更新
        fs_var.trace_add('write', lambda *a: _do_update())

        # ---- 颜色 ----
        frm_color = ttk.Frame(win)
        frm_color.pack(fill=X, padx=10, pady=5)
        ttk.Label(frm_color, text=self.tr('color_label')).pack(side=LEFT)
        color_var = tk.StringVar(value=info.get('color', 'white'))

        def _set_color(col):
            color_var.set(col)
            _do_update()

        preset_colors = ['white', 'red', 'yellow', 'lime', 'cyan','#FF6B6B', '#FFD93D', '#6BCB77', '#4D96FF', '#FF6BFF',
        ]
        color_btns = []
        for col in preset_colors:
            # 用 Label 做颜色块，带边框
            lbl = tk.Label(frm_color, width=2, height=1, bg=col,
                           relief=SOLID, bd=1, cursor='hand2')
            lbl.pack(side=LEFT, padx=1)
            lbl.bind('<Button-1>', lambda e, c=col: _set_color(c))
            color_btns.append((col, lbl))

        def _on_custom_color():
            import tkinter.colorchooser as cc
            result = cc.askcolor(info.get('color', 'white'), parent=win, title=self.tr('te_pick_color'))
            if result[1]:
                _set_color(result[1])

        ttk.Button(frm_color, text=self.tr('te_custom'), command=_on_custom_color, width=6).pack(side=LEFT, padx=(5, 0))

        # 颜色按钮选中高亮
        def _update_color_preview(*args):
            cur = color_var.get()
            for col, lbl in color_btns:
                if col == cur:
                    lbl.config(highlightbackground='#888888', highlightthickness=2)
                else:
                    lbl.config(highlightbackground=None, highlightthickness=0)

        color_var.trace_add('write', _update_color_preview)
        _update_color_preview()

        # ---- 按钮行 ----
        frm_btn = ttk.Frame(win)
        frm_btn.pack(fill=X, padx=10, pady=(5, 10))

        def _on_delete():
            _do_update()  # 先保存当前值
            self._delete_annotation(idx)
            win.destroy()

        def _on_confirm():
            _do_update()  # 确保最新值已保存
            win.destroy()

        ttk.Button(frm_btn, text=self.tr('te_delete'), command=_on_delete, bootstyle='').pack(side=LEFT)
        ttk.Button(frm_btn, text=self.tr('te_confirm'), command=_on_confirm, bootstyle='').pack(side=RIGHT)

        self._text_edit_win = win
        win.bind('<Destroy>', lambda e: setattr(self, '_text_edit_win', None))
        entry.focus_set()
        # 初次显示时也应用一次当前值（确保初始样式正确）
        _do_update()

    def _delete_annotation(self, idx):
        """删除指定索引的标注"""
        if idx < 0 or idx >= len(self.annotations):
            return
        # 从画布上移除 artist
        if idx < len(self.annot_artists):
            try:
                self.annot_artists[idx].remove()
            except Exception:
                pass
        # 同步删除 annotations 和 artists
        self.annotations.pop(idx)
        self.annot_artists.pop(idx)
        self.canvas.draw_idle()

    # -------- 文字标注：旧版应用编辑（保留兼容） --------
    def _apply_text_edit(self):
        """将面板中的内容和字体大小应用到选中的文字标注"""
        idx = self._selected_text_idx
        if idx is None or idx >= len(self.annotations):
            if hasattr(self, '_annot_status_var'):
                self._annot_status_var.set(" 请先右键点击图上的文字来选中它")
            return
        new_text = ''
        if hasattr(self, '_text_content_var'):
            new_text = self._text_content_var.get().strip()

        new_fs = self.annot_fontsize_var.get()

        # 更新数据记录
        if new_text:
            self.annotations[idx]['text'] = new_text
        self.annotations[idx]['fontsize'] = new_fs

        # 更新 artist
        artist = self.annot_artists[idx]
        try:
            if new_text:
                artist.set_text(new_text)
            artist.set_fontsize(new_fs)
            self.canvas.draw_idle()
            if hasattr(self, '_annot_status_var'):
                self._annot_status_var.set(f" 已更新：'{self.annotations[idx]['text']}' {new_fs}pt")
        except Exception as e:
            if hasattr(self, '_annot_status_var'):
                self._annot_status_var.set(f"更新失败: {e}")

if __name__ == "__main__":
    app = ModernKymographSorter()
    app.mainloop()
