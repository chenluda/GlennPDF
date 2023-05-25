# GlennPDF
深渊巨坑：基于 pyqt 的简约 pdf 阅读器

* 2023-05-24 08:26:01 updata main.py：PDF 文件打开，显示，翻页，滚动条等基本功能
* 2023-05-24 15:48:36 updata main.py：搜索功能
* 2023-05-25 10:33:51 updata main.py：添加检测图片文本功能，将识别出的文本与矩形框坐标存储起来

todo：

- [ ] 当鼠标移至矩形框中时变为文本光标；
- [ ] 文本选中反显；
- [ ] 识别论文中的参考文献；
- [ ] 将参考文献显示在右侧弹出窗口中；
- [ ] 美化界面；

---
![59d5607c829e19f6c30b2bda68d9ab7](https://github.com/chenluda/GlennPDF/assets/45784833/c38961c8-2298-4035-8739-4c8e4a4a5d83)

> tesseract 安装：
1. tesseract 下载地址：[https://digi.bib.uni-mannheim.de/tesseract/](https://digi.bib.uni-mannheim.de/tesseract/?C=M;O=D)
2. 将 tesseract 安装路径加入环境变量，如：D:\software\tesseract
3. 安装 pytesseract：
```
pip install pytesseract
```
