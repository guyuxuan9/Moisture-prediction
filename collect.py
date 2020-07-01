import sys
import os
import time
import threading
import multiprocessing
import cv2
import serial
import serial.tools.list_ports
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class MainWindow(QMainWindow):

    autoCapturing = False  # 是否处于自动采集状态
    interval = 10          # 自动采集的间隔秒数

    def __init__(self, app):
        super(MainWindow, self).__init__()

        self.initWindow(self)

        self.webcam = cv2.VideoCapture(0)

        self.refresh_label_time_Thread = threading.Thread(
            target=self.refresh_label_time)
        self.refresh_label_time_Thread.setDaemon(True)
        self.refresh_label_time_Thread.start()

        self.refresh_camView_Thread = threading.Thread(
            target=self.refresh_camView)
        self.refresh_camView_Thread.setDaemon(True)
        self.refresh_camView_Thread.start()

        self.com = serial.Serial()

        return

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'exit?',
                                     "exit?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def __del__(self):
        self.webcam.release()
        self.com.release()
        return

    def initWindow(self, Form):
        # 主窗口
        Form.setObjectName("MainWindow")
        Form.resize(900, 500)
        Form.setMinimumSize(QtCore.QSize(900, 500))
        Form.setMaximumSize(QtCore.QSize(900, 500))
        Form.setWindowTitle("Soil Data Collector")

        # 画面预览
        self.camView = QtWidgets.QLabel(Form)
        self.camView.setGeometry(QtCore.QRect(10, 10, 640, 480))
        self.camView.setObjectName("camView")
        self.camView.setText("摄像头初始化中......")

        # 提示行
        self.label_prompt = QtWidgets.QLabel(Form)
        self.label_prompt.setGeometry(QtCore.QRect(660, 0, 230, 30))
        self.label_prompt.setTextFormat(QtCore.Qt.AutoText)
        self.label_prompt.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.label_prompt.setObjectName("label_prompt")
        self.label_prompt.setText("Prompt")
        self.textEdit_prompt = QtWidgets.QTextEdit(Form)
        self.textEdit_prompt.setGeometry(QtCore.QRect(660, 30, 230, 230))
        self.textEdit_prompt.setObjectName("Prompt View Box")
        self.textEdit_prompt.setReadOnly(True)

        # 显示时间和湿度
        self.label_time = QtWidgets.QLabel(Form)
        self.label_time.setGeometry(QtCore.QRect(660, 255, 230, 30))
        self.label_time.setTextFormat(QtCore.Qt.AutoText)
        self.label_time.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.label_time.setObjectName("label_time")
        self.label_time.setText("<h3>Initializing...</h3>")
        self.label_moisture = QtWidgets.QLabel(Form)
        self.label_moisture.setGeometry(QtCore.QRect(660, 280, 230, 30))
        self.label_moisture.setTextFormat(QtCore.Qt.AutoText)
        self.label_moisture.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.label_moisture.setObjectName("label_moisture")
        self.label_moisture.setText("<h2>Moisture: NO DATA</h2>")

        # 自动采集的时间间隔设定
        self.label_interval = QtWidgets.QLabel(Form)
        self.label_interval.setGeometry(QtCore.QRect(660, 310, 230, 30))
        self.label_interval.setTextFormat(QtCore.Qt.AutoText)
        self.label_interval.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.label_interval.setObjectName("label_interval")
        self.label_interval.setText("Capture Interval (s)")
        self.lineEdit_interval = QtWidgets.QLineEdit(Form)
        self.lineEdit_interval.setGeometry(QtCore.QRect(660, 340, 230, 30))
        self.lineEdit_interval.setObjectName("lineEdit_interval")
        self.lineEdit_interval.setText(str(self.interval))
        self.lineEdit_interval.textChanged.connect(self.interval_set)

        # 采集状态和按钮
        self.label_capture = QtWidgets.QLabel(Form)
        self.label_capture.setGeometry(QtCore.QRect(660, 375, 230, 30))
        self.label_capture.setTextFormat(QtCore.Qt.AutoText)
        self.label_capture.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.label_capture.setObjectName("label_capture")
        self.label_capture.setText(
            "<h3><font color=\"#FF0000\">Idling...</font></h3>")
        self.button_capture_auto = QtWidgets.QPushButton(Form)
        self.button_capture_auto.setGeometry(QtCore.QRect(660, 410, 150, 80))
        self.button_capture_auto.setObjectName("button_capture_auto")
        self.button_capture_auto.setText("Start\nCapture")
        self.button_capture_auto.clicked.connect(self.capture_auto_switch)
        self.button_capture_single = QtWidgets.QPushButton(Form)
        self.button_capture_single.setGeometry(QtCore.QRect(820, 410, 70, 80))
        self.button_capture_single.setObjectName("button_capture_single")
        self.button_capture_single.setText("Single\nCapture")
        self.button_capture_single.clicked.connect(self.capture_single)

        self.show()
        return

    def prompt_print(self, content, color="#0000FF"):
        self.textEdit_prompt.append(time.strftime(
            '<font color="' + color + '">%Y-%m-%d %H:%M:%S</font>',
            time.localtime(time.time())))
        self.textEdit_prompt.append(content)

    def prompt_clear(self):
        self.textEdit_prompt.clear()
        return

    def capture_single(self):
        # TODO: 单次采集
        self.prompt_print("点了下右边按钮")
        return

    def capture_auto_switch(self):
        # TODO: 切换自动采集的开/关
        self.prompt_print("点了下左边按钮，当前设定的时间间隔是%.f" % (self.interval))
        if self.autoCapturing == False:
            self.label_capture.setText(
                "<h3><font color=\"#00FF00\">Running...</font></h3>")
            self.button_capture_auto.setText("Finish\nCapture")
            self.autoCapturing = True
        else:
            self.label_capture.setText(
                "<h3><font color=\"#FF0000\">Idling...</font></h3>")
            self.button_capture_auto.setText("Start\nCapture")
            self.autoCapturing = False

        return

    def refresh_label_time(self):
        """刷新时间显示的死循环"""
        while True:
            nowtime = time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            self.label_time.setText('<h3>' + nowtime + '</h3>')
            time.sleep(0.1)
        return

    def refresh_label_moisture(self):
        """刷新湿度显示的死循环"""
        while True:
            # TODO: 从串口读来湿度数据
            self.label_moisture.setText("<h2>Moisture: NO DATA</h2>")
            time.sleep(0.1)
        return
    
    def refresh_camView(self): 
        """刷新摄像头画面预览的死循环"""
        while True:
            try:
                ret, self.lastFrame = self.webcam.read() 
                qtframeView = self.lastFrame
                qtframeView = cv2.cvtColor(qtframeView, cv2.COLOR_BGR2RGB)
                qtframeView = cv2.resize(qtframeView, (640, 480))
                qtframeView = QtGui.QImage(
                    qtframeView.data, qtframeView.shape[1], qtframeView.shape[0], QtGui.QImage.Format_RGB888)
                self.camView.setPixmap(QtGui.QPixmap.fromImage(qtframeView))
            except Exception as e:
                self.prompt_print("Detect Error，" + str(e), color="#FF0000")
        return

    def interval_set(self):
        """时间间隔设定框被修改后自动改变interval变量的值"""
        try:
            self.interval = float(self.lineEdit_interval.text())
        except:
            self.prompt_print("Interval Setting ERROR!", color="#FF0000")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow(app)
    sys.exit(app.exec_())
