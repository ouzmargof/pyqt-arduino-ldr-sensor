import sys, serial, serial.tools.list_ports
from PyQt5 import QtWidgets, uic, QtCore

OPTIONS = {'update_time': 500, 'number_of_points': 10, 'threshold_value': 512}

class ApplicationWindow(QtWidgets.QDialog):
    def __init__(self, ):
        super().__init__()
        self.setupUi(self)
        self.initUI()

        self.btn_connexion.clicked.connect(self.on_btn_connexion_click)
        self.sld_thresh.valueChanged[int].connect(
            self.on_sld_thresh_valueChanged)

        self.com_list = []
        self.connexion_done = False
        self.com_found = False
        self.threshold_value = OPTIONS['threshold_value']

        self.check_com()
        self.populate_cbox()

        self.widgets = [
            self.lcd_reading, self.lbl_com, self.btn_connexion, 
            self.cbox_port, self.sld_thresh, self.lbl_thresh, self.lbl_reading]
        
        if not self.com_found:
            for widget in self.widgets:
                widget.setEnabled(False)


    def setupUi(self, Dialog):
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        
        self.hbox_port = QtWidgets.QHBoxLayout()
        self.lbl_com = QtWidgets.QLabel(Dialog)
        self.lbl_com.setText("Serial port")
        self.hbox_port.addWidget(self.lbl_com)
        self.cbox_port = QtWidgets.QComboBox(Dialog)
        self.hbox_port.addWidget(self.cbox_port)
        self.btn_connexion = QtWidgets.QPushButton(Dialog)
        self.btn_connexion.setText("Connect")
        self.hbox_port.addWidget(self.btn_connexion)
        self.verticalLayout.addLayout(self.hbox_port)
        
        self.hbox_min = QtWidgets.QHBoxLayout()
        self.lbl_thresh = QtWidgets.QLabel(Dialog)
        self.lbl_thresh.setText("Threshold")
        self.lbl_thresh.setMinimumSize(QtCore.QSize(95, 0))
        self.hbox_min.addWidget(self.lbl_thresh)
        self.sld_thresh = QtWidgets.QSlider(Dialog)
        self.sld_thresh.setMaximum(1023)
        self.sld_thresh.setProperty("value", OPTIONS['threshold_value'])
        self.sld_thresh.setOrientation(QtCore.Qt.Horizontal)
        self.hbox_min.addWidget(self.sld_thresh)
        self.lbl_reading = QtWidgets.QLabel(Dialog)
        self.lbl_reading.setText(str(OPTIONS['threshold_value']))
        self.lbl_reading.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_reading.setMinimumSize(QtCore.QSize(50, 0))
        self.hbox_min.addWidget(self.lbl_reading)
        self.verticalLayout.addLayout(self.hbox_min)

        self.lcd_reading = QtWidgets.QLCDNumber(Dialog)
        self.lcd_reading.setMinimumSize(QtCore.QSize(300, 100))
        self.verticalLayout.addWidget(self.lcd_reading)


    def initUI(self):
        self.setFixedSize(330, 220)
        self.setWindowTitle("PyQt Arduino light sensor")
        
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(
            (screen.width()-size.width())/2, 
            (screen.height()-size.height())/2)


    def check_com(self):
        ports = serial.tools.list_ports.comports()
        for port, desc, hwid in sorted(ports):
            if "Arduino" in desc:
                self.com_list.append({'port':port, 'desc':desc})

        if self.com_list:
            self.com_found = True


    def populate_cbox(self):
        if self.com_found:
            for port in self.com_list:
                self.cbox_port.addItem(port['port'])
        else:
            self.cbox_port.addItem("None found")


    def on_btn_connexion_click(self):
        if self.connexion_done:
            self.lcd_reading.display(0)
            self.arduino.close()
            self.timer.stop()
            self.lcd_reading.setEnabled(False)
            self.btn_connexion.setText("Connect")
            self.connexion_done = False
        else:
            port_name = self.com_list[self.cbox_port.currentIndex()]['port']
            self.arduino = Arduino(port_name)
            self.setup_timer()
            self.lcd_reading.setEnabled(True)
            self.btn_connexion.setText("Disconnect")
            self.connexion_done = True


    def on_sld_thresh_valueChanged(self, value):
        self.threshold_value = value
        self.lbl_reading.setNum(value)


    def setup_timer(self):
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(OPTIONS['update_time'])
        self.timer.timeout.connect(self.update_reading)
        self.timer.start()


    def get_value(self):
        return self.arduino.average_value()


    def update_reading(self):
        reading = self.get_value()
        self.lcd_reading.display(str(reading))
        
        if reading > self.threshold_value:
            self.arduino.turn_off()
        else:
            self.arduino.turn_on()


    def closeEvent(self, event):
        if self.connexion_done:
            self.timer.stop()
            self.arduino.turn_off()
            self.arduino.close()

class Arduino:
    port = ''
    
    def __init__(self, port):
        self.arduino = serial.Serial(port, 115200, timeout=1)


    def get_value(self):
        self.arduino.write(b'r')
        value = self.arduino.readline().decode("ascii").split("\r\n")[0]
        return value


    def average_value(self):
        data = [0] * OPTIONS['number_of_points']
        for i in range(0, OPTIONS['number_of_points']):
            while True:
                try:
                    value = self.get_value()
                    data[i] = int(value)
                except ValueError:
                    # Conversion failed 
                    continue
                break
        return int(sum(data)/OPTIONS['number_of_points'])


    def turn_on(self):
        self.arduino.write(b'1')


    def turn_off(self):
        self.arduino.write(b'0')


    def close(self):
        self.arduino.close()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = ApplicationWindow()
    main.show()
    sys.exit(app.exec_())