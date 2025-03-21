import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout, QVBoxLayout, QWidget, QFileDialog, QLabel, QMessageBox, QCheckBox, QRadioButton, QButtonGroup, QMessageBox, QProgressDialog, QSizePolicy
from PyQt5.QtCore import Qt, QMimeData, pyqtSignal, QThread, QSize
from PyQt5.QtGui import QPixmap, QClipboard, QMovie, QImage
import pytesseract
from PIL import Image
import docx
from easyocr import Reader
import cv2


# Neural Text Recognition - мое название технологии

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

# Реализация многопоточности

class TextRecognitionThread(QThread):
    recognition_completed = pyqtSignal(str)

    def __init__(self, file_path, selected_recognition_method, image_label):
        super().__init__()
        self.file_path = file_path
        self.selected_recognition_method = selected_recognition_method
        self.image_label = image_label

    def run(self):
# Выполняем распознавание текста
        pixmap = QPixmap(self.file_path)

        visual_img = cv2.imread(self.file_path)

        self.image_label.setPixmap(pixmap)
        self.image_label.setScaledContents(True)

        img = Image.open(self.file_path)
        if self.selected_recognition_method == "pytesseract":
            text_pytesseract = pytesseract.image_to_string(img, lang='eng+rus')
            boxes = pytesseract.image_to_boxes(img, lang='eng+rus')

            for box in boxes.splitlines():
                box = box.split(' ')
                x, y, w, h = int(box[1]), int(box[2]), int(box[3]), int(box[4])
                cv2.rectangle(visual_img, (x, y), (w, h), (0, 255, 0), 2)

            # Преобразуем visual_img в QPixmap и отображаем в self.image_label
            height, width, channel = visual_img.shape
            bytesPerLine = 3 * width
            qImg = QImage(visual_img.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
            pixmap_with_boxes = QPixmap.fromImage(qImg)
            self.image_label.setPixmap(pixmap_with_boxes)
            self.image_label.setScaledContents(True)
            self.recognition_completed.emit(text_pytesseract)
        elif self.selected_recognition_method == "easyocr":
            reader = Reader(['en', 'ru'])
            text_results = reader.readtext(self.file_path)

            for (coord, text, prob) in text_results:
                (topleft, topright, bottomright, bottomleft) = coord
                tx, ty = (int(topleft[0]), int(topleft[1]))
                bx, by = (int(bottomright[0]), int(bottomright[1]))
                cv2.rectangle(visual_img, (tx, ty), (bx, by), (0, 255, 0), 2)

            # Преобразуем visual_img в QPixmap и отображаем в self.image_label
            height, width, channel = visual_img.shape
            bytesPerLine = 3 * width
            qImg = QImage(visual_img.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
            pixmap_with_boxes = QPixmap.fromImage(qImg)
            self.image_label.setPixmap(pixmap_with_boxes)
            self.image_label.setScaledContents(True)
            text = ' '.join([result[1] for result in text_results])
            self.recognition_completed.emit(text)

class TextRecognitionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # Load and apply the CSS file
        with open('D:\YandexDisk\Visual Studio Code\Python\AITextVision\Style.css', 'r') as file:
            self.setStyleSheet(file.read())
        self.setWindowTitle("AITextVision")

        self.label = QLabel()
        self.label.setParent(None)
        self.label.resize(300, 300)
        self.label.setWindowFlag(Qt.FramelessWindowHint)
        self.label.setAlignment(Qt.AlignCenter)

        # layout_animate = QVBoxLayout()
        # layout_animate.addWidget(self.label)
        # layout_animate.setAlignment(self.label, Qt.AlignCenter)

        # self.setLayout(layout_animate)
        # layout_animate.setAlignment(Qt.AlignCenter)


        # Заменяем чекбоксы на радиокнопки
        self.pytesseract_radio = QRadioButton("Оптическое распознавание (OCR)")
        self.easyocr_radio = QRadioButton("ИИ распознавание (ATR)")

        # Устанавливаем группу для радиокнопок
        self.recognition_group = QButtonGroup()
        self.recognition_group.addButton(self.pytesseract_radio)
        self.recognition_group.addButton(self.easyocr_radio)

        # По умолчанию выбираем Pytesseract
        self.pytesseract_radio.setChecked(True)
        self.selected_recognition_method = "pytesseract"

        # Подключаем слот для обработки изменения состояния радиокнопок
        self.recognition_group.buttonClicked.connect(self.recognition_method_changed)

        self.open_button = QPushButton("Открыть изображение")
        self.open_button.clicked.connect(self.open_image)

        self.copy_button = QPushButton("Копировать текст")
        self.copy_button.clicked.connect(self.copy_text)

        self.save_txt_button = QPushButton("Сохранить в .txt")
        self.save_txt_button.clicked.connect(self.save_to_txt)

        self.save_docx_button = QPushButton("Сохранить в .docx")
        self.save_docx_button.clicked.connect(self.save_to_docx)

        self.clear_button = QPushButton("Очистить")
        self.clear_button.clicked.connect(self.clear_fields)

        self.text_box = QTextEdit()
        self.text_box.setAcceptDrops(False)  # Отключаем возможность перетаскивания текста в текстовое поле
        self.text_box.setReadOnly(True)  # Делаем текстовое поле доступным только для чтения
        self.text_box.setMinimumSize(900, 200)

        self.image_label = QLabel("Перетащите изображение сюда")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setAcceptDrops(True)  # Включаем возможность перетаскивания изображения
        self.image_label.setStyleSheet("border: 4px dashed #aaa")  # Добавляем пунктирную рамку для обозначения области перетаскивания
        self.image_label.setMinimumSize(900, 400)

        # Если нет текста, делаем кнопки невидимыми
        self.copy_button.setVisible(False)
        self.save_txt_button.setVisible(False)
        self.save_docx_button.setVisible(False)
        self.clear_button.setVisible(False)

        self.label.setVisible(False)

        # Подключаем слот для обновления видимости кнопок при изменении текста в текстовом поле
        self.text_box.textChanged.connect(self.update_button_visibility)

        # Создаем вертикальный макет
        layout = QVBoxLayout()
        # layout.addWidget(self.label)
        # layout.setAlignment(self.label, Qt.AlignCenter)
        # Создаем горизонтальный макет
        h_layout = QHBoxLayout()
        # Добавляем радиокнопки в layout
        h_layout.addWidget(self.pytesseract_radio)
        h_layout.addWidget(self.easyocr_radio)
        h_layout.addWidget(self.open_button)
        h_layout.addWidget(self.clear_button)

        # Добавляем горизонтальный макет в вертикальный макет
        layout.addLayout(h_layout)

        layout.addWidget(self.image_label)

        layout.addWidget(self.text_box)

        h_layout2 = QHBoxLayout()


        h_layout2.addWidget(self.copy_button)
        h_layout2.addWidget(self.save_txt_button)
        h_layout2.addWidget(self.save_docx_button)


         # Добавляем горизонтальный макет в вертикальный макет
        layout.addLayout(h_layout2)



        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.image_label.dragEnterEvent = self.drag_enter_event
        self.image_label.dropEvent = self.drop_event

    def update_button_visibility(self):
        # Проверяем, есть ли текст в текстовом поле
        if self.text_box.toPlainText():
            # Если есть текст, делаем кнопки видимыми
            self.copy_button.setVisible(True)
            self.save_txt_button.setVisible(True)
            self.save_docx_button.setVisible(True)
            self.clear_button.setVisible(True)
        else:
            # Если нет текста, делаем кнопки невидимыми
            self.copy_button.setVisible(False)
            self.save_txt_button.setVisible(False)
            self.save_docx_button.setVisible(False)
            self.clear_button.setVisible(False)

    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "", "Изображения (*.png *.jpg *.jpeg)")
        if file_path:
            self.display_image(file_path)

    def drag_enter_event(self, e):
        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.ignore()

    def drop_event(self, e):
        for url in e.mimeData().urls():
            file_path = str(url.toLocalFile())
            if file_path.endswith(('.png', '.jpg', '.jpeg')):
                self.display_image(file_path)
                break
            
    # Изменяем функцию recognition_method_changed
    def recognition_method_changed(self, button):
        if button == self.pytesseract_radio:
            self.selected_recognition_method = "pytesseract"
        elif button == self.easyocr_radio:
            self.selected_recognition_method = "easyocr"
            
    def display_image(self, file_path):
        self.recognition_thread = TextRecognitionThread(file_path, self.selected_recognition_method, self.image_label)
        self.recognition_thread.recognition_completed.connect(self.display_recognition_results)
        self.recognition_thread.start()

        # Show the spinner animation
        spinner_movie = QMovie("D:\\YandexDisk\\Visual Studio Code\\Python\\AITextVision\\animations\\updatess.gif")
        self.label.setVisible(True)
        self.label.setMovie(spinner_movie)
        spinner_movie.start()

    def display_recognition_results(self, text):
        # Stop the spinner animation
        self.label.clear()
        self.label.setVisible(False)
        self.text_box.setPlainText(text)

    def copy_text(self):
        text = self.text_box.toPlainText()
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        QMessageBox.information(self, "Скопировано", "Распознанный текст скопирован в буфер обмена.")

    def save_to_txt(self):
        text = self.text_box.toPlainText()
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить в .txt", "", "Текстовые файлы (*.txt)")
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(text)
            QMessageBox.information(self, "Сохранено", "Распознанный текст сохранен в файл .txt.")

    def save_to_docx(self):
        text = self.text_box.toPlainText()
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить в .docx", "", "Документы Word (*.docx)")
        if file_path:
            doc = docx.Document()
            doc.add_paragraph(text)
            doc.save(file_path)
            QMessageBox.information(self, "Сохранено", "Распознанный текст сохранен в файл .docx.")

    def clear_fields(self):
        self.text_box.clear()
        self.image_label.clear()
        self.image_label.setText("Перетащите изображение сюда")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TextRecognitionApp()
    window.show()
    sys.exit(app.exec_())

