#Import Library
import sys
import cv2
import pytesseract
from PyQt5 import QtCore,QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi

#membuat class “ShowImage”
class ShowImage(QMainWindow):
    def __init__(self):
        super(ShowImage,self).__init__()
        loadUi('GUI_Project.ui',self)
        self.image=None
        self.LoadButton.clicked.connect(self.loadImage)
        self.ProsesButton.clicked.connect(self.proses)

    #membuat prosedur load image
    def loadImage(self):
        imagePath, _ = QFileDialog.getOpenFileName(self, 'Open File', 'c\\', 'Image files (*.jpg *.png *.jpeg)')
        if imagePath:
            self.Image = cv2.imread(imagePath)
            self.displayImage(1)

    def proses(self):
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

        # resize image
        scale_factor = 1
        resize_image = cv2.resize(self.Image,(int(self.Image.shape[1] * scale_factor), int(self.Image.shape[0] * scale_factor)))

        # grayscale
        gray = cv2.cvtColor(resize_image, cv2.COLOR_BGR2GRAY)
        self.Image = gray.copy()
        self.displayImage(4)

        # thresholding
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (20, 20))
        opening = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
        norm = gray - opening
        (thresh, normbw) = cv2.threshold(norm, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        self.Image = normbw.copy()
        self.displayImage(5)

        # dilasi
        kernel_dilasi = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        dilasi = cv2.dilate(normbw, kernel_dilasi, iterations=1)
        self.Image = dilasi.copy()
        self.displayImage(6)

        # contour
        contours, hierarchy = cv2.findContours(dilasi, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        index_plate_candidate = []
        index_counter_contour = 0

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h

            if w >= 200 and aspect_ratio <= 4:
                index_plate_candidate.append(index_counter_contour)
            index_counter_contour += 1

        img_show_plate = resize_image.copy()
        img_show_plate_bw = cv2.cvtColor(dilasi, cv2.COLOR_GRAY2RGB)

        if len(index_plate_candidate) == 0:

            print("Plat nomor tidak ditemukan")
            return

        elif len(index_plate_candidate) == 1:

            x_plate, y_plate, w_plate, h_plate = cv2.boundingRect(contours[index_plate_candidate[0]])

            cv2.rectangle(img_show_plate, (x_plate, y_plate),
                          (x_plate + w_plate, y_plate + h_plate), (0, 255, 0), 5)

            cv2.rectangle(img_show_plate_bw, (x_plate, y_plate),
                          (x_plate + w_plate, y_plate + h_plate), (0, 255, 0), 5)

            img_plate_gray = gray[y_plate:y_plate + h_plate, x_plate:x_plate + w_plate].copy()

        else:

            print('Dapat dua lokasi plat, pilih lokasi plat kedua')

            x_plate, y_plate, w_plate, h_plate = cv2.boundingRect(contours[index_plate_candidate[1]])

            cv2.rectangle(img_show_plate, (x_plate, y_plate),
                          (x_plate + w_plate, y_plate + h_plate), (0, 255, 0), 5)

            cv2.rectangle(img_show_plate_bw, (x_plate, y_plate),
                          (x_plate + w_plate, y_plate + h_plate), (0, 255, 0), 5)

            img_plate_gray = gray[y_plate:y_plate + h_plate, x_plate:x_plate + w_plate].copy()

        # OCR
        config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(img_plate_gray, config=config)
        print("Plat nomor:", text)
        self.textBrowser.setText(f"Plat Nomor : {text}\n")

        self.Image = img_show_plate
        self.displayImage(2)

        self.Image = img_plate_gray
        self.displayImage(3)

        self.Image = img_show_plate_bw.copy()
        self.displayImage(7)

        cv2.waitKey(0)
        cv2.destroyAllWindows()

    #membuat prosedur display image
    def displayImage(self, window = 1):
        qformat = QImage.Format_Indexed8

        if len(self.Image.shape) == 3:  # row[0],col[1],channel[2]
            if (self.Image.shape[2]) == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888

        img = QImage(self.Image, self.Image.shape[1], self.Image.shape[0],
                     self.Image.strides[0], qformat)

        # Scale the image to fit imgLabel
        img = img.scaled(self.imgLabel.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                         QtCore.Qt.TransformationMode.SmoothTransformation)

        img = img.rgbSwapped()
        if window == 1:
            self.imgLabel.setPixmap(QPixmap.fromImage(img))
            self.imgLabel.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        if window == 2:
            self.imgLabel_2.setPixmap(QPixmap.fromImage(img))
            self.imgLabel_2.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        if window == 3:
            self.imgLabel_3.setPixmap(QPixmap.fromImage(img))
            self.imgLabel_3.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        if window == 4:
            self.imgLabel_4.setPixmap(QPixmap.fromImage(img))
            self.imgLabel_4.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        if window == 5:
            self.imgLabel_5.setPixmap(QPixmap.fromImage(img))
            self.imgLabel_5.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        if window == 6:
            self.imgLabel_6.setPixmap(QPixmap.fromImage(img))
            self.imgLabel_6.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        if window == 7:
            self.imgLabel_7.setPixmap(QPixmap.fromImage(img))
            self.imgLabel_7.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        # memposisikan gambar di center


# Membuat window enable menampilkan user interface dan kelasnya
app=QtWidgets.QApplication(sys.argv)
window=ShowImage()
window.setWindowTitle('Show Image GUI')
window.show()
sys.exit(app.exec_())