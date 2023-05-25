'''
Description: 简约 pdf 阅读器
Version: 1.0
Author: Glenn
Email: chenluda01@outlook.com
Date: 2023-05-24 09:27:56
FilePath: \20-pdf\main.py
Copyright (c) 2023 by Kust-BME, All Rights Reserved. 
'''
import sys
import fitz
import cv2
import numpy as np
import pytesseract
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QScrollArea, QLineEdit, QAction, QWidget, QStatusBar, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QPixmap, QImage, QIcon
from PyQt5.QtCore import Qt, QPoint

# 定义PDF阅读器类
class PDFReader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pdf = None  # 存储当前打开的PDF文件
        self.page = None  # 存储当前显示的PDF页面
        self.page_num = 0  # 当前显示的页面号（从0开始）
        self.matches = []  # 存储搜索结果的位置
        self.current_match = -1  # 当前显示的搜索结果的索引
        self.manual_scroll = False  # 是否正在手动翻页
        self.initUI()  # 初始化用户界面
        self.page_text_boxes = {}  # 存储当前页面的文本框

    def initUI(self):
        # 设置窗口标题和初始位置、大小
        self.setWindowTitle('PDF Reader')
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon('./images/logo.png'))

        # 创建一个窗口小部件并设为主窗口小部件
        widget = QWidget()
        self.setCentralWidget(widget)

        # 创建一个垂直布局并设为主窗口小部件的布局
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # 创建工具栏，并添加打开PDF文件的操作
        toolbar = self.addToolBar('Toolbar')
        open_action = QAction(QIcon('./images/open_icon.png'), 'Open PDF', self)
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)

        # 创建搜索栏布局，并添加到主布局中
        search_layout = QHBoxLayout()
        layout.addLayout(search_layout)

        # 创建搜索栏，并连接其回车信号到搜索函数
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText('Search...')
        self.search_bar.returnPressed.connect(self.search_text)
        search_layout.addWidget(self.search_bar)

        # 创建搜索结果上一个和下一个的按钮，并连接其点击信号
        self.btn_prev_match = QPushButton(QIcon('./images/prev_icon.png'), '')
        self.btn_prev_match.clicked.connect(self.prev_match)
        search_layout.addWidget(self.btn_prev_match)
        self.btn_next_match = QPushButton(QIcon('./images/next_icon.png'), '')
        self.btn_next_match.clicked.connect(self.next_match)
        search_layout.addWidget(self.btn_next_match)

        # 创建一个用于显示PDF页面的标签，并放在一个滚动区域中
        self.page_label = QLabel()
        self.page_label.setAlignment(Qt.AlignCenter)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.page_label)
        # 连接滚动条的值变化信号到检查滚动位置的函数
        self.scroll_area.verticalScrollBar().valueChanged.connect(self.check_scroll_position)
        layout.addWidget(self.scroll_area)

        # 在状态栏显示页面导航和页面号
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.addPermanentWidget(QWidget(), 1)  # Add spacer on left
        self.btn_prev = QPushButton(QIcon('./images/prev_icon.png'), '')
        self.btn_prev.clicked.connect(self.prev_page)
        self.statusbar.addPermanentWidget(self.btn_prev)
        self.page_num_input = QLineEdit()
        self.page_num_input.setPlaceholderText('Page Num')
        self.page_num_input.returnPressed.connect(self.jump_to_page)
        self.statusbar.addPermanentWidget(self.page_num_input)
        self.page_num_label = QLabel()
        self.statusbar.addPermanentWidget(self.page_num_label)
        self.btn_next = QPushButton(QIcon('./images/next_icon.png'), '')
        self.btn_next.clicked.connect(self.next_page)
        self.statusbar.addPermanentWidget(self.btn_next)
        self.statusbar.addPermanentWidget(QWidget(), 1)  # Add spacer on right

    # 打开文件对话框让用户选择PDF文件，并加载它
    def open_file(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "PDF Files (*.pdf)", options=options)
        if filename:
            self.load_pdf(filename)

    # 加载指定的PDF文件
    def load_pdf(self, filename):
        self.pdf = fitz.open(filename)
        self.show_page(0)

    # 显示指定页面的函数
    def show_page(self, page_num):
        if self.pdf is not None and page_num >= 0 and page_num < len(self.pdf):
            self.page_num = page_num
            self.page = self.pdf.load_page(self.page_num)
            zoom_x = 2.0
            zoom_y = 2.0
            mat = fitz.Matrix(zoom_x, zoom_y)
            pix = self.page.get_pixmap(matrix=mat)

            # 检测当前页面是否已经检测过文本
            if self.page_num not in self.page_text_boxes:
                img = np.frombuffer(pix.samples, np.uint8).reshape(pix.h, pix.w, pix.n)
                # 检测文本，将检测出的文本和矩形框坐标保存到字典中
                self.page_text_boxes[self.page_num] = self.detect_text(img)

            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
            self.page_label.setPixmap(QPixmap.fromImage(img))
            self.page_num_label.setText(f'Page {self.page_num + 1} of {len(self.pdf)}')
    
    # 用于检测图片中的文本
    def detect_text(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, threshold = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        data = pytesseract.image_to_data(threshold, output_type=pytesseract.Output.DICT)
        text_boxes = {}
        for i in range(len(data["text"])):
            text = data["text"][i]
            x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
            if text.strip():  # 去除空格
                text_boxes[text] = (x, y, x + w, y + h)
        return text_boxes

    # 显示上一个和下一个页面的函数
    def prev_page(self):
        self.manual_scroll = True
        self.show_page(self.page_num - 1)
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())
        self.manual_scroll = False
    def next_page(self):
        self.manual_scroll = True
        self.show_page(self.page_num + 1)
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().minimum())
        self.manual_scroll = False

    # 在PDF中搜索指定的文本，并高亮显示
    def search_text(self):
        text = self.search_bar.text()
        zoom_x = 2.0
        zoom_y = 2.0
        mat = fitz.Matrix(zoom_x, zoom_y)
        # 清除之前的高亮
        for page_num in range(len(self.pdf)):
            page = self.pdf.load_page(page_num)
            for annot in page.annots():
                if annot.type[0] == 8:  # 检查是否为高亮
                    annot = page.delete_annot(annot)

        # 如果搜索框为空，停止执行并刷新页面
        if text.strip() == "":
            self.show_page(self.page_num)
            return
        
        # 清除之前的匹配项
        self.matches = []
        self.current_match = -1

        # 找到匹配项并添加高亮
        for page_num in range(len(self.pdf)):
            page = self.pdf.load_page(page_num)
            instances = page.search_for(text)
            for inst in instances:
                highlight = page.add_highlight_annot(inst)
                self.matches.append((page_num, highlight.rect))
            page.apply_redactions() # 确保注释已应用到页面
        
        if self.matches:
            self.next_match()

    # 显示上一个和下一个搜索结果的函数
    def next_match(self):
        if self.matches:
            self.current_match = (self.current_match + 1) % len(self.matches)
            self.show_match(self.current_match)
    def prev_match(self):
        if self.matches:
            self.current_match = (self.current_match - 1) % len(self.matches)
            self.show_match(self.current_match)

    # 显示指定的搜索结果的函数
    def show_match(self, match_index):
        page_num, rect = self.matches[match_index]
        self.show_page(page_num)
        self.scroll_area.verticalScrollBar().setValue(int(rect.y0))

    # 跳转到指定页面的函数
    def jump_to_page(self):
        page_num = int(self.page_num_input.text()) - 1
        if 0 <= page_num < len(self.pdf):
            self.show_page(page_num)

    # 检查滚动位置的函数，用于自动翻页
    def check_scroll_position(self):
        if self.manual_scroll:
            return
        if self.scroll_area.verticalScrollBar().value() == self.scroll_area.verticalScrollBar().minimum():
            if self.page_num > 0:
                self.prev_page()
        elif self.scroll_area.verticalScrollBar().value() == self.scroll_area.verticalScrollBar().maximum():
            if self.page_num < len(self.pdf) - 1:
                self.next_page()

# 主函数
if __name__ == '__main__':
    app = QApplication(sys.argv)  # 创建Qt应用
    ex = PDFReader()  # 创建PDF阅读器实例
    ex.show()  # 显示PDF阅读器
    sys.exit(app.exec_())  # 进入Qt应用的事件循环
