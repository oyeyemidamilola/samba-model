# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 09:10:23 2019

@author: Oyeyemi Damilola
"""


import os
import numpy as np
#from models.model import Model       # this the first version of model designed
from PyQt5 import QtCore, QtGui, QtWidgets
from models.model_v2 import SambaModel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from models.exceptions import IncompleteInitialParameters,InvalidExtensionError,InvalidInputs,InvalidModelFile


class Figure_Canvas(FigureCanvas):    
    def __init__(self,parent=None, width= 6 , height = 5 ,dpi= 100):        
        fig = Figure(figsize=(width,height),dpi = 100 )        
        FigureCanvas.__init__(self,fig)
        self.setParent(parent)
        self.axes = fig.add_subplot(111)
        
        
    def display_plot(self,data):
        
        """
        Generates the plots/visualizations        
        @params        
        
            params : a dict that contains the variables to plotted
        """
        
        
        if data['visualization_type'] == 'Evapotranspiration':
            
            self.axes.plot(data['julian_days'],data['eto'],label='ETo')
            self.axes.plot(data['julian_days'],data['pe'],label='PE')
            self.axes.plot(data['julian_days'],data['ae'],label='AE')
            self.axes.set_xlabel('Julian Days')
            self.axes.set_ylabel('ETo, PE, AE (mm/day)')
            self.axes.grid(b=True,which='major')
            self.axes.legend()
            
            #self.self.axesaxes.plot(x, y)
         
        elif data['visualization_type'] == 'SMD':
            
            self.axes.plot(data['julian_days'],data['runoff'],label='Runoff')
            self.axes.plot(data['julian_days'],data['taw'],label='TAW')
            self.axes.plot(data['julian_days'],data['smd'],label='SMD')
            self.axes.plot(data['julian_days'],data['rainfall'],label='Rainfall')
            self.axes.grid(which='both')            
            self.axes.set_xlabel('Julian Days')
            self.axes.set_ylabel('Rain, Runoff, SMD, TAW (mm)')
            self.axes.legend()
            
        elif data['visualization_type'] == 'Monthly precipitation':
            
            self.axes.bar(data['y_pos'],data['monthly_precipitation'].values(),align='center',alpha=0.5)
            self.axes.set_xticks(data['y_pos'])
            self.axes.set_xticklabels(data['months'])
            self.axes.set_ylabel('Monthly Precipitation')
            self.axes.grid() 
            
        elif data['visualization_type'] == 'Recharge/Runoff':
            
            total_runoff = round( sum(data['runoff']) , 3)
            total_recharge = round( sum(data['recharge']) , 3 )
            self.axes.plot(data['julian_days'],data['runoff'],label='Runoff,Total:'+str(total_runoff))
            self.axes.plot(data['julian_days'],data['recharge'],label='Recharge,Total:'+ str(total_recharge))
            self.axes.grid(which='both')            
            self.axes.set_xlabel('Julian Days')
            self.axes.set_ylabel('Runoff, Recharge')
            self.axes.legend()
        

class Ui_SambaMainWindow(object):
    
    model = None
    
    def get_model(self):
        if self.model is not None:
            return self.model
        else:
            self.error_dialog.showMessage('No Model Generated')  
            
    def setupUi(self, SambaMainWindow):
        SambaMainWindow.setObjectName("SambaMainWindow")
        SambaMainWindow.resize(950, 700)
        SambaMainWindow.setMinimumSize(QtCore.QSize(950, 700))
        SambaMainWindow.setMaximumSize(QtCore.QSize(1000, 700))
        self.centralwidget = QtWidgets.QWidget(SambaMainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.soilBox = QtWidgets.QGroupBox(self.centralwidget)
        self.soilBox.setGeometry(QtCore.QRect(10, 10, 261, 51))
        self.soilBox.setObjectName("soilBox")
        self.layoutWidget = QtWidgets.QWidget(self.soilBox)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 20, 221, 22))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.layoutWidget)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.fpInput = QtWidgets.QLineEdit(self.layoutWidget)
        self.fpInput.setObjectName("fpInput")
        self.horizontalLayout.addWidget(self.fpInput)
        self.label_2 = QtWidgets.QLabel(self.layoutWidget)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.wpInput = QtWidgets.QLineEdit(self.layoutWidget)
        self.wpInput.setObjectName("wpInput")
        self.horizontalLayout.addWidget(self.wpInput)
        self.cropCoeffBox = QtWidgets.QGroupBox(self.centralwidget)
        self.cropCoeffBox.setGeometry(QtCore.QRect(10, 70, 261, 139))
        self.cropCoeffBox.setObjectName("cropCoeffBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.cropCoeffBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_4 = QtWidgets.QLabel(self.cropCoeffBox)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_2.addWidget(self.label_4)
        self.cropCoeff_Initial = QtWidgets.QLineEdit(self.cropCoeffBox)
        self.cropCoeff_Initial.setObjectName("cropCoeff_Initial")
        self.horizontalLayout_2.addWidget(self.cropCoeff_Initial)
        self.label_19 = QtWidgets.QLabel(self.cropCoeffBox)
        self.label_19.setObjectName("label_19")
        self.horizontalLayout_2.addWidget(self.label_19)
        self.cropDuration_Init = QtWidgets.QLineEdit(self.cropCoeffBox)
        self.cropDuration_Init.setObjectName("cropDuration_Init")
        self.horizontalLayout_2.addWidget(self.cropDuration_Init)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_5 = QtWidgets.QLabel(self.cropCoeffBox)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_3.addWidget(self.label_5)
        self.cropCoeff_Middle = QtWidgets.QLineEdit(self.cropCoeffBox)
        self.cropCoeff_Middle.setObjectName("cropCoeff_Middle")
        self.horizontalLayout_3.addWidget(self.cropCoeff_Middle)
        self.label_21 = QtWidgets.QLabel(self.cropCoeffBox)
        self.label_21.setObjectName("label_21")
        self.horizontalLayout_3.addWidget(self.label_21)
        self.cropDuration_Dev = QtWidgets.QLineEdit(self.cropCoeffBox)
        self.cropDuration_Dev.setObjectName("cropDuration_Dev")
        self.horizontalLayout_3.addWidget(self.cropDuration_Dev)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_6 = QtWidgets.QLabel(self.cropCoeffBox)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_4.addWidget(self.label_6)
        self.cropCoeff_End = QtWidgets.QLineEdit(self.cropCoeffBox)
        self.cropCoeff_End.setObjectName("cropCoeff_End")
        self.horizontalLayout_4.addWidget(self.cropCoeff_End)
        self.label_22 = QtWidgets.QLabel(self.cropCoeffBox)
        self.label_22.setObjectName("label_22")
        self.horizontalLayout_4.addWidget(self.label_22)
        self.cropDuration_Mid = QtWidgets.QLineEdit(self.cropCoeffBox)
        self.cropDuration_Mid.setObjectName("cropDuration_Mid")
        self.horizontalLayout_4.addWidget(self.cropDuration_Mid)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_7 = QtWidgets.QLabel(self.cropCoeffBox)
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_5.addWidget(self.label_7)
        self.cropCoeff_bs = QtWidgets.QLineEdit(self.cropCoeffBox)
        self.cropCoeff_bs.setObjectName("cropCoeff_bs")
        self.horizontalLayout_5.addWidget(self.cropCoeff_bs)
        self.label_23 = QtWidgets.QLabel(self.cropCoeffBox)
        self.label_23.setObjectName("label_23")
        self.horizontalLayout_5.addWidget(self.label_23)
        self.cropDuration_Late = QtWidgets.QLineEdit(self.cropCoeffBox)
        self.cropDuration_Late.setObjectName("cropDuration_Late")
        self.horizontalLayout_5.addWidget(self.cropDuration_Late)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.cropStagesBox = QtWidgets.QGroupBox(self.centralwidget)
        self.cropStagesBox.setGeometry(QtCore.QRect(10, 210, 261, 161))
        self.cropStagesBox.setObjectName("cropStagesBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.cropStagesBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_8 = QtWidgets.QLabel(self.cropStagesBox)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_6.addWidget(self.label_8)
        self.cropStages_Planting = QtWidgets.QLineEdit(self.cropStagesBox)
        self.cropStages_Planting.setObjectName("cropStages_Planting")
        self.horizontalLayout_6.addWidget(self.cropStages_Planting)
        self.verticalLayout_2.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.label_9 = QtWidgets.QLabel(self.cropStagesBox)
        self.label_9.setObjectName("label_9")
        self.horizontalLayout_7.addWidget(self.label_9)
        self.cropStages_Development = QtWidgets.QLineEdit(self.cropStagesBox)
        self.cropStages_Development.setObjectName("cropStages_Development")
        self.horizontalLayout_7.addWidget(self.cropStages_Development)
        self.verticalLayout_2.addLayout(self.horizontalLayout_7)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.label_10 = QtWidgets.QLabel(self.cropStagesBox)
        self.label_10.setInputMethodHints(QtCore.Qt.ImhDigitsOnly)
        self.label_10.setObjectName("label_10")
        self.horizontalLayout_8.addWidget(self.label_10)
        self.cropStages_Middle = QtWidgets.QLineEdit(self.cropStagesBox)
        self.cropStages_Middle.setObjectName("cropStages_Middle")
        self.horizontalLayout_8.addWidget(self.cropStages_Middle)
        self.verticalLayout_2.addLayout(self.horizontalLayout_8)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.label_11 = QtWidgets.QLabel(self.cropStagesBox)
        self.label_11.setObjectName("label_11")
        self.horizontalLayout_9.addWidget(self.label_11)
        self.cropStages_Late = QtWidgets.QLineEdit(self.cropStagesBox)
        self.cropStages_Late.setObjectName("cropStages_Late")
        self.horizontalLayout_9.addWidget(self.cropStages_Late)
        self.verticalLayout_2.addLayout(self.horizontalLayout_9)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.label_18 = QtWidgets.QLabel(self.cropStagesBox)
        self.label_18.setObjectName("label_18")
        self.horizontalLayout_10.addWidget(self.label_18)
        self.cropStages_Harvest = QtWidgets.QLineEdit(self.cropStagesBox)
        self.cropStages_Harvest.setObjectName("cropStages_Harvest")
        self.horizontalLayout_10.addWidget(self.cropStages_Harvest)
        self.verticalLayout_2.addLayout(self.horizontalLayout_10)
        self.runOffMatrix = QtWidgets.QGroupBox(self.centralwidget)
        self.runOffMatrix.setEnabled(True)
        self.runOffMatrix.setGeometry(QtCore.QRect(10, 380, 261, 201))
        self.runOffMatrix.setObjectName("runOffMatrix")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.runOffMatrix)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.gridLayout.setContentsMargins(9, 11, 20, 19)
        self.gridLayout.setHorizontalSpacing(31)
        self.gridLayout.setVerticalSpacing(24)
        self.gridLayout.setObjectName("gridLayout")
        self.lineEdit_3 = QtWidgets.QLineEdit(self.runOffMatrix)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.gridLayout.addWidget(self.lineEdit_3, 1, 3, 1, 1)
        self.lineEdit_12 = QtWidgets.QLineEdit(self.runOffMatrix)
        self.lineEdit_12.setObjectName("lineEdit_12")
        self.gridLayout.addWidget(self.lineEdit_12, 1, 2, 1, 1)
        self.lineEdit_17 = QtWidgets.QLineEdit(self.runOffMatrix)
        self.lineEdit_17.setObjectName("lineEdit_17")
        self.gridLayout.addWidget(self.lineEdit_17, 3, 1, 1, 1)
        self.lineEdit_13 = QtWidgets.QLineEdit(self.runOffMatrix)
        self.lineEdit_13.setObjectName("lineEdit_13")
        self.gridLayout.addWidget(self.lineEdit_13, 1, 1, 1, 1)
        self.lineEdit_16 = QtWidgets.QLineEdit(self.runOffMatrix)
        self.lineEdit_16.setObjectName("lineEdit_16")
        self.gridLayout.addWidget(self.lineEdit_16, 2, 3, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.runOffMatrix)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.lineEdit_18 = QtWidgets.QLineEdit(self.runOffMatrix)
        self.lineEdit_18.setObjectName("lineEdit_18")
        self.gridLayout.addWidget(self.lineEdit_18, 3, 2, 1, 1)
        self.lineEdit_14 = QtWidgets.QLineEdit(self.runOffMatrix)
        self.lineEdit_14.setObjectName("lineEdit_14")
        self.gridLayout.addWidget(self.lineEdit_14, 2, 1, 1, 1)
        self.label_16 = QtWidgets.QLabel(self.runOffMatrix)
        self.label_16.setObjectName("label_16")
        self.gridLayout.addWidget(self.label_16, 2, 0, 1, 1)
        self.lineEdit_15 = QtWidgets.QLineEdit(self.runOffMatrix)
        self.lineEdit_15.setObjectName("lineEdit_15")
        self.gridLayout.addWidget(self.lineEdit_15, 2, 2, 1, 1)
        self.lineEdit_19 = QtWidgets.QLineEdit(self.runOffMatrix)
        self.lineEdit_19.setObjectName("lineEdit_19")
        self.gridLayout.addWidget(self.lineEdit_19, 3, 3, 1, 1)
        self.label_17 = QtWidgets.QLabel(self.runOffMatrix)
        self.label_17.setObjectName("label_17")
        self.gridLayout.addWidget(self.label_17, 3, 0, 1, 1)
        self.label_15 = QtWidgets.QLabel(self.runOffMatrix)
        self.label_15.setInputMethodHints(QtCore.Qt.ImhMultiLine)
        self.label_15.setObjectName("label_15")
        self.gridLayout.addWidget(self.label_15, 0, 0, 1, 1)
        self.label_14 = QtWidgets.QLabel(self.runOffMatrix)
        self.label_14.setObjectName("label_14")
        self.gridLayout.addWidget(self.label_14, 0, 3, 1, 1)
        self.label_13 = QtWidgets.QLabel(self.runOffMatrix)
        self.label_13.setObjectName("label_13")
        self.gridLayout.addWidget(self.label_13, 0, 2, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.runOffMatrix)
        self.label_12.setObjectName("label_12")
        self.gridLayout.addWidget(self.label_12, 0, 1, 1, 1)
        self.verticalLayout_3.addLayout(self.gridLayout)
        self.layoutWidget_5 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget_5.setGeometry(QtCore.QRect(20, 590, 251, 22))
        self.layoutWidget_5.setObjectName("layoutWidget_5")
        self.horizontalLayout_19 = QtWidgets.QHBoxLayout(self.layoutWidget_5)
        self.horizontalLayout_19.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_19.setObjectName("horizontalLayout_19")
        self.label_35 = QtWidgets.QLabel(self.layoutWidget_5)
        self.label_35.setObjectName("label_35")
        self.horizontalLayout_19.addWidget(self.label_35)
        self.ze = QtWidgets.QLineEdit(self.layoutWidget_5)
        self.ze.setObjectName("ze")
        self.horizontalLayout_19.addWidget(self.ze)
        
        self.initial_smd_label = QtWidgets.QLabel(self.layoutWidget_5)
        self.initial_smd_label.setObjectName("Initial SMD")
        self.initial_smd_label.setText('Initial SMD')
        self.horizontalLayout_19.addWidget(self.initial_smd_label)
        
        self.initial_smd = QtWidgets.QLineEdit(self.layoutWidget_5)
        self.initial_smd.setObjectName("intial_smd")
        self.horizontalLayout_19.addWidget(self.initial_smd)      
        self.layoutWidget_6 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget_6.setGeometry(QtCore.QRect(20, 620, 251, 22))
        self.layoutWidget_6.setObjectName("layoutWidget_6")
        self.horizontalLayout_20 = QtWidgets.QHBoxLayout(self.layoutWidget_6)
        self.horizontalLayout_20.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_20.setObjectName("horizontalLayout_20")
        self.label_36 = QtWidgets.QLabel(self.layoutWidget_6)
        self.label_36.setObjectName("label_36")
        self.horizontalLayout_20.addWidget(self.label_36)
        self.depletionFactor = QtWidgets.QLineEdit(self.layoutWidget_6)
        self.depletionFactor.setObjectName("depletionFactor")
        self.horizontalLayout_20.addWidget(self.depletionFactor)
        self.nss_fraction_label = QtWidgets.QLabel(self.layoutWidget_6)
        self.nss_fraction_label.setObjectName("NSS Fraction")
        self.nss_fraction_label.setText('NSS Fraction')
        self.horizontalLayout_20.addWidget(self.nss_fraction_label)
        self.nss_fraction = QtWidgets.QLineEdit(self.layoutWidget_6)
        self.nss_fraction.setObjectName("nss_fraction")        
        self.horizontalLayout_20.addWidget(self.nss_fraction)
        self.layoutWidget_7 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget_7.setGeometry(QtCore.QRect(20, 650, 251, 22))
        self.layoutWidget_7.setObjectName("layoutWidget_7")
        self.horizontalLayout_21 = QtWidgets.QHBoxLayout(self.layoutWidget_7)
        self.horizontalLayout_21.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_21.setObjectName("horizontalLayout_21")
        self.label_37 = QtWidgets.QLabel(self.layoutWidget_7)
        self.label_37.setObjectName("label_37")
        self.horizontalLayout_21.addWidget(self.label_37)
        self.maxRootDepth = QtWidgets.QLineEdit(self.layoutWidget_7)
        self.maxRootDepth.setObjectName("maxRootDepth")
        self.horizontalLayout_21.addWidget(self.maxRootDepth)
        self.visualizationBox = QtWidgets.QGroupBox(self.centralwidget)
        self.visualizationBox.setGeometry(QtCore.QRect(280, 50, 651, 591))
        self.visualizationBox.setObjectName("visualizationBox")
        self.visualizationGraphicsView = QtWidgets.QGraphicsView(self.visualizationBox)
        self.visualizationGraphicsView.setGeometry(QtCore.QRect(10, 20, 631, 561))
        self.visualizationGraphicsView.setObjectName("visualizationGraphicsView")        
        self.graphicScene = QtWidgets.QGraphicsScene()        
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(280, 10, 651, 31))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout_34 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout_34.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_34.setObjectName("horizontalLayout_34")
        self.searchInput = QtWidgets.QLineEdit(self.horizontalLayoutWidget)
        self.searchInput.setReadOnly(True)
        self.searchInput.setObjectName("searchInput")
        self.horizontalLayout_34.addWidget(self.searchInput)
        self.selectModel = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.selectModel.setObjectName("selectModel")
        self.horizontalLayout_34.addWidget(self.selectModel)
        self.generateModel = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.generateModel.setObjectName("generateModel")
        self.horizontalLayout_34.addWidget(self.generateModel)
        self.horizontalLayoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(280, 650, 651, 25))
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")
        self.horizontalLayout_35 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout_35.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_35.setObjectName("horizontalLayout_35")
        self.selectPlot = QtWidgets.QComboBox(self.horizontalLayoutWidget_2)
        self.selectPlot.setObjectName("selectPlot")
        self.selectPlot.addItems(['                       --Select plot --                ',
                                  'SMD',
                                  'Monthly precipitation',
                                  'Evapotranspiration',
                                  'Recharge/Runoff'])
        self.horizontalLayout_35.addWidget(self.selectPlot)
        self.displayPlot = QtWidgets.QPushButton(self.horizontalLayoutWidget_2)
        self.displayPlot.setObjectName("displayPlot")
        self.horizontalLayout_35.addWidget(self.displayPlot)
        
        
        self.horizontalLayout_35.addWidget(self.displayPlot)
        
        self.label_20 = QtWidgets.QLabel(self.centralwidget)
        self.label_20.setGeometry(QtCore.QRect(740, 630, 47, 20))
        self.label_20.setObjectName("label_20")
        SambaMainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(SambaMainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 950, 21))
        self.menubar.setObjectName("menubar")
        SambaMainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(SambaMainWindow)
        self.statusbar.setObjectName("statusbar")
        SambaMainWindow.setStatusBar(self.statusbar)
        self.error_dialog = QtWidgets.QErrorMessage()
        self.msg_dialog = QtWidgets.QMessageBox()
        self.msg_dialog.setIcon(self.msg_dialog.Information)

        self.retranslateUi(SambaMainWindow)
        QtCore.QMetaObject.connectSlotsByName(SambaMainWindow)
        
         
        """
        Controllers
        """
        
        self.selectModel.clicked.connect(self.get_model_file)
        self.generateModel.setEnabled(False)        
        self.generateModel.clicked.connect(self.load_model)
        self.displayPlot.clicked.connect(self.show)

    def retranslateUi(self, SambaMainWindow):
        _translate = QtCore.QCoreApplication.translate
        SambaMainWindow.setWindowTitle(_translate("SambaMainWindow", "MainWindow"))
        self.soilBox.setTitle(_translate("SambaMainWindow", "SOIL"))
        self.label.setText(_translate("SambaMainWindow", "FC"))
        self.label_2.setText(_translate("SambaMainWindow", "WP"))
        self.cropCoeffBox.setTitle(_translate("SambaMainWindow", "CROP COEFFICIENT/ CROP DURATION"))
        self.label_4.setText(_translate("SambaMainWindow", "Initial  "))
        self.label_19.setText(_translate("SambaMainWindow", "Init"))
        self.label_5.setText(_translate("SambaMainWindow", "Middle "))
        self.label_21.setText(_translate("SambaMainWindow", "Dev"))
        self.label_6.setText(_translate("SambaMainWindow", "  End   "))
        self.label_22.setText(_translate("SambaMainWindow", "Mid"))
        self.label_7.setText(_translate("SambaMainWindow", "  BS     "))
        self.label_23.setText(_translate("SambaMainWindow", "Late"))
        self.cropStagesBox.setTitle(_translate("SambaMainWindow", "CROP STAGES"))
        self.label_8.setText(_translate("SambaMainWindow", "Planting"))
        self.label_9.setText(_translate("SambaMainWindow", "Development"))
        self.label_10.setText(_translate("SambaMainWindow", "Middle"))
        self.label_11.setText(_translate("SambaMainWindow", " Late   "))
        self.label_18.setText(_translate("SambaMainWindow", "Harvest"))
        self.runOffMatrix.setTitle(_translate("SambaMainWindow", "RUN-OFF MATRIX"))
        self.label_3.setText(_translate("SambaMainWindow", "   0-20"))
        self.label_16.setText(_translate("SambaMainWindow", "20-50"))
        self.label_17.setText(_translate("SambaMainWindow", "  >50"))
        self.label_15.setText(_translate("SambaMainWindow", "R.I/SMD"))
        self.label_14.setText(_translate("SambaMainWindow", "  >50"))
        self.label_13.setText(_translate("SambaMainWindow", "20-50"))
        self.label_12.setText(_translate("SambaMainWindow", "  0-20"))
        self.label_35.setText(_translate("SambaMainWindow", "Z E"))
        self.label_36.setText(_translate("SambaMainWindow", "Depletion Factor"))
        self.label_37.setText(_translate("SambaMainWindow", "Maximum Root Depth"))
        self.visualizationBox.setTitle(_translate("SambaMainWindow", "VISUALIZATION"))
        self.selectModel.setText(_translate("SambaMainWindow", "Select Model File"))
        self.generateModel.setText(_translate("SambaMainWindow", "Generate Model"))
        self.displayPlot.setText(_translate("SambaMainWindow", "Display Plot"))
        
        """
        Controller functions
        """
        
        
    def get_model_file(self):
        
        '''
        to retrieve the model file from the local drive
        '''
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(None,'Select Model File',os.getcwd())
        self.searchInput.setText(filename)
        self.generateModel.setEnabled(True)
        self.graphicScene.clear()
        return filename

    def show(self):
        
        '''
        to display the figure selected on the canvas / graphic scene
        '''
        model = self.get_model()
        dr = Figure_Canvas()
        dr.display_plot(model.load_visualization(self.selectPlot.currentText()))
        
       # graphicscene = QtWidgets.QGraphicsScene()
       # graphicscene.addWidget(dr)
        self.graphicScene.addWidget(dr)
        
        self.visualizationGraphicsView.setScene(self.graphicScene)
        self.visualizationGraphicsView.show() 
        
     
    def get_crop_duration(self):
        
        '''
        
        to retrieve the user's defined input for the duration of crops
        '''
        
        crop_duration = {}
        try:
            crop_duration['initial'] = float(self.cropDuration_Init.text())
            crop_duration['development'] = float(self.cropDuration_Dev.text())
            crop_duration['middle'] = float(self.cropDuration_Mid.text())
            crop_duration['late'] = float(self.cropDuration_Late.text())
        except Exception:
            raise InvalidInputs('Invalid Inputs')
        else:
            return crop_duration
        
            
    def get_run_off_matrix(self):
        
        '''
        
        to retrieve the user's defined input for the runoff matrix
        '''
        
        run_off_matrix = np.empty((3,3))
        
        try:
            # first row
            run_off_matrix[0,0] = float(self.lineEdit_13.text())
            run_off_matrix[0,1] = float(self.lineEdit_12.text())
            run_off_matrix[0,2] = float(self.lineEdit_3.text())
            
            #second row
            run_off_matrix[1,0] = float(self.lineEdit_14.text())
            run_off_matrix[1,1] = float(self.lineEdit_15.text())
            run_off_matrix[1,2] = float(self.lineEdit_16.text())
            
            #third row
            run_off_matrix[2,0] = float(self.lineEdit_17.text())
            run_off_matrix[2,1] = float(self.lineEdit_18.text())
            run_off_matrix[2,2] = float(self.lineEdit_19.text())
            
        except Exception:
            raise InvalidInputs('Invalid Inputs')
        else:
            return run_off_matrix
            
    def get_soil_parameters(self):
        
        '''
        
        to retrieve the user's defined input for the soil parameters
        '''      
                
        soil_params = {}
        try:
            soil_params['FC'] = float(self.fpInput.text())
            soil_params['WP'] = float(self.wpInput.text())
        except Exception:
            raise InvalidInputs('Invalid Inputs')
        else:
            return soil_params
           
    def get_crop_coefficient(self):
        
        '''
        
        to retrieve the user's defined input for the crop coefficient
        '''
            
        crop_coefficient = {}
        try:
            crop_coefficient['initial'] = float(self.cropCoeff_Initial.text())
            crop_coefficient['middle'] = float(self.cropCoeff_Middle.text())
            crop_coefficient['end'] = float(self.cropCoeff_End.text())
            crop_coefficient['bs'] = float(self.cropCoeff_bs.text())
        except Exception:
            raise InvalidInputs('Invalid Inputs')
        else:
            return crop_coefficient
    
    def get_crop_stages(self):
        
        '''
        
        to retrieve the user's defined input for the crop stages
        '''
        
        crop_stages = {}
        try:
            crop_stages['planting'] = float(self.cropStages_Planting.text())
            crop_stages['development'] = float(self.cropStages_Development.text())
            crop_stages['middle'] = float(self.cropStages_Middle.text())
            crop_stages['late'] = float(self.cropStages_Late.text())
            crop_stages['harvest'] = float(self.cropStages_Harvest.text())
        except Exception:
            raise InvalidInputs('Invalid Inputs')
        else:
            return crop_stages
    def get_model_constant_params(self):
        
        '''
        
        to retrieve the user's defined input for the constant parameters
        '''
         
        model_constant_params = {}
        try:
             model_constant_params['Ze'] = float(self.ze.text())
             model_constant_params['depletion_factor'] = float(self.depletionFactor.text())
             model_constant_params['initial_smd'] = float(self.initial_smd.text())
             model_constant_params['nss_fraction'] = float(self.nss_fraction.text())
        except Exception:
             raise InvalidInputs('Invalid Inputs')
        else:
             return model_constant_params
    def get_max_root_depth(self):
        
        '''
        
        to retrieve the user's defined input for the maximum root depth
        '''
        
        try:
            max_root_depth = float(self.maxRootDepth.text())
        except Exception:
            raise InvalidInputs('Invalid Inputs')
        else:
            return max_root_depth
    def load_model(self):
        
        # clear plot on the graphic scene
        self.graphicScene.clear()
        
        try:            
            RUN_OFF_MATRIX = self.get_run_off_matrix()
            SOIL = self.get_soil_parameters()
            MODEL_CONSTANT_PARAMS = self.get_model_constant_params()
            CROP_COEFF = self.get_crop_coefficient()
            CROP_STAGES = self.get_crop_stages()
            MAX_ROOT_DEPTH = self.get_max_root_depth()
            MODEL_FILE = self.searchInput.text() 
            CROP_DURATION = self.get_crop_duration()
            model = SambaModel(model_path = MODEL_FILE,
                          crop_stages = CROP_STAGES,
                          soil = SOIL,
                          crop_coefficient = CROP_COEFF,
                          run_off_matrix = RUN_OFF_MATRIX,
                          model_constant_params = MODEL_CONSTANT_PARAMS,
                          max_root_depth = MAX_ROOT_DEPTH,
                          crop_duration =  CROP_DURATION)
            self.model = model
            self.model.generate_model()
        except (InvalidExtensionError,InvalidInputs,IncompleteInitialParameters,InvalidModelFile) as e:
                self.error_dialog.showMessage(str(e))
        else:
             self.msg_dialog.setInformativeText('Model\nGenerated')
             self.msg_dialog.exec_()



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    SambaMainWindow = QtWidgets.QMainWindow()
    ui = Ui_SambaMainWindow()
    ui.setupUi(SambaMainWindow)
    SambaMainWindow.show()
    sys.exit(app.exec_())

