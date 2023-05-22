#THIS IS A PROGRAM WHICH HAS 2 BUTTONS AND A CANVAS 
#Where button 1 When clicked, a random geometric image from the open source repository
#(https://github.com/hfg-gmuend/openmoji/tree/master/src/symbols/geometric) should be
#downloaded and rendered at any random location on the canvas. It should be selectable
#and movable. An image from that repository should keep on appearing whenever this
#button is clicked, without removing/overwriting the previous images and
#Button 2 will be used for grouping multiple images as a single object.
#You need to select multiple images and click the button. Those images will move as a
#single object thereafter


#IMPORTING THE NECESSARY MODULES

import sys
import os
import requests
import random
from PyQt6.QtCore import QUrl, QByteArray, Qt, QPoint
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel,QMessageBox,QSizePolicy,QHBoxLayout
from PyQt6.QtGui import QDesktopServices, QPixmap, QMouseEvent, QCursor,QImage,QPainter,QPen,QRegion
from PyQt6.QtSvg import QSvgRenderer



class SvgResize(QLabel):
    def __init__(self, renderer=None,parent=None):
        super().__init__(parent)
        self.setPixmap(QPixmap.fromImage(renderer))
        self.setScaledContents(True)
        self.setMouseTracking(True)
        self.item_move_pos = QPoint()
        self.mouse_press_pos = QPoint()
        self.is_selected = False

#THIS FUNCTION DESCRIBES WHAT IS DONE WHEN THE MOUSE IS PRESSED BY THE USER

    def mousePressEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            self.mouse_press_pos = event.pos()
            self.global_mouse_press_pos = self.mapToGlobal(event.pos())
            self.item_move_pos = self.pos()

            # Toggle the item's selection status
            self.is_selected = not self.is_selected
            self.update()

        super().mousePressEvent(event)

#THIS FUNCTION DESCRIBES WHAT IS DONE WHEN THE MOUSE IS MOVED BY THE USER

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton:
            delta = self.mapToGlobal(event.pos()) - self.global_mouse_press_pos
            new_pos = self.item_move_pos + delta

            #MOVEMENT IS WITHIN THE CANVAS
            canvas_rect = self.parentWidget().contentsRect()
            if new_pos.x() >= 0 and new_pos.x() + self.width() <= canvas_rect.width():
                self.move(new_pos.x(), self.y())

            if new_pos.y() >= 0 and new_pos.y() + self.height() <= canvas_rect.height():
                self.move(self.x(), new_pos.y())

        super().mouseMoveEvent(event)

#THIS FUNCTION DESCRIBES WHAT IS DONE WHEN THE MOUSE IS RELEASED BY THE USER

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)

        #INDICATES THAT THE IMAGE IS SELECTED BY DRAWING A DOTTED LINE AROUND THE IMAGE 
        if self.is_selected:
            painter = QPainter(self)
            painter.setPen(QPen(Qt.GlobalColor.red, 4 ,Qt.PenStyle.DashDotDotLine))
            painter.drawRect(self.rect())

#THIS CLASS GROUPS THE SVG IMAGES
class GroupedSvgItem(QLabel):
    def __init__(self, grouped_image, parent=None):
        super().__init__(parent)
        self.setPixmap(grouped_image)
        self.setScaledContents(True)
        self.setMouseTracking(True)
        self.mouse_press_pos = QPoint()
        self.item_move_pos = QPoint()
        self.is_selected = False

#THE FOLLOWING FUNCTIONS MANAGES THE MOVEMENT OF THE MOUSE 
#THE FOLLOWING FUNCTIONS SAYS AT WHICH STAGE WHICH TYPE OF MOUSE SHOULD BE DISPLAYED

    def mousePressEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            self.mouse_press_pos = event.pos()
            self.global_mouse_press_pos = self.mapToGlobal(event.pos())
            self.item_move_pos = self.pos()

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton:
            delta = self.mapToGlobal(event.pos()) - self.global_mouse_press_pos
            new_pos = self.item_move_pos + delta

            # MOVEMENT IS ONLY WITHIN THE CANVAS
            canvas_rect = self.parentWidget().contentsRect()
            if new_pos.x() >= 0 and new_pos.x() + self.width() <= canvas_rect.width():
                self.move(new_pos.x(), self.y())

            if new_pos.y() >= 0 and new_pos.y() + self.height() <= canvas_rect.height():
                self.move(self.x(), new_pos.y())

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)

        if self.is_selected:
            painter = QPainter(self)
            outer_rect = self.rect().adjusted(5, 5, -5, -5)  # Adjust the rectangle size
            painter.setPen(QPen(Qt.GlobalColor.red, 4, Qt.PenStyle.DashDotDotLine))
            painter.drawRect(outer_rect)

#THIS IS THE MAIN CLASS WHICH CONTROLS THE OVERALL OPERATIONS OF THESE BUTTONS

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mainFunc()
        self.svg_items = [] #EMPTY LIST IS FOR STORING ALL THE IMAGES
        self.grouped_item = None #THIS LIST IS FOR GROUPING ITEMS TOGETHER 
        self.is_selected = False

#THIS IS THE MAIN FUNCTION WHICH CONTROLS THE CANVAS AND BUTTONS

    def mainFunc(self):
        self.setWindowTitle("Desktop App")

        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)

        self.canvas = QWidget()
        
        self.canvas.setStyleSheet("background-color: yellow")#CANVAS BACKGROUND
        layout.addWidget(self.canvas)

        #BUTTONS 

        #FIRST BUTTON IS TO OPEN A RANDOM IMAGE

        button = QPushButton("Click me to Open Random Image!!!")#PUSHBUTTON IS A DEFAULT BUTTON
        button.clicked.connect(self.open_random_image)#CONNECTS TO THE OPEN_RANDOM_IMAGE FUNCTION
        layout.addWidget(button)

        group_button = QPushButton("Click me to Group Selected Images!!!")
        group_button.clicked.connect(self.group_selected_images)#CONNECTS TO THE GROUP_SELECTED_IMAGES FUNCTION
        layout.addWidget(group_button)

        self.setCentralWidget(central_widget)
        self.resize(500, 400)

        self.is_resize_move_enabled = False

    #THIS FUNCTION GETS THE URLS OF THE RESPECTIVE IMAGES

    def fetch_image_urls(self):
        github_api_url = "https://api.github.com/repos/hfg-gmuend/openmoji/contents/src/symbols/geometric"
        username = "hfg-gmuend"
        repository = "openmoji"

        api_url = github_api_url.replace("hfg-gmuend", username).replace("openmoji", repository)
        response = requests.get(api_url)
        data = response.json()

        image_urls = []#EMPTY LIST TO STORE URLS
        for item in data:
            if isinstance(item, dict):
                if item.get("type") == "file" and item.get("name", "").endswith(".svg"):
                    image_urls.append(item.get("download_url"))
        return image_urls

    #FIRST BUTTON FUNCTIONALITY:

    def open_random_image(self):
        image_urls = self.fetch_image_urls()

        if len(image_urls) == 0:
            return

        random_url = random.choice(image_urls)
        response = requests.get(random_url)
        svg_data = response.content

        svg_item = SvgResize(QImage.fromData(svg_data), parent=self.canvas)
        svg_item.move(random.randint(0, self.canvas.width() - svg_item.width()),
                      random.randint(0, self.canvas.height() - svg_item.height()))
        svg_item.show()

        self.svg_items.append(svg_item)

        # EXTRACT IMG NAME FROM URL AS SAVED IN THE GITHUB REPOSITORY
        image_name = os.path.basename(random_url)

        #DOWNLOAD IMAGE
        #DOWNLOAD LINK TO DOWNLOAD IMAGE TO THE LOCAL MACHINE
        download_url = self.generate_download_url(svg_data)

        self.download_image(svg_data, download_url, image_name)

    def toggle_resize_move(self):
        self.is_resize_move_enabled = not self.is_resize_move_enabled
        for svg_item in self.svg_items:
            svg_item.setMouseTracking(self.is_resize_move_enabled)

    def generate_download_url(self, data):
        return f"data:image/svg+xml;base64,{data.decode()}"

    def download_image(self, data, url, filename):

        # SAVE TO FILE
        with open(f"{filename}.svg", "wb") as file:
            file.write(data)



    def group_selected_images(self):
        selected_items = [item for item in self.svg_items if item.is_selected]

        if len(selected_items) < 2:
            QMessageBox.warning(self, "Warning", "Please select at least 2 images.")
            return

        # Create a single QPixmap by combining the selected images
        grouped_image = QPixmap(self.canvas.size())
        grouped_image.fill(Qt.GlobalColor.transparent)

        painter = QPainter(grouped_image)
        for item in selected_items:
            painter.drawPixmap(item.pos(), item.pixmap())

        painter.end()

        # Remove from canvas and add to the grouped list
        for item in selected_items:
            item.setParent(None)
            item.deleteLater()
            self.svg_items.remove(item)

        self.grouped_item = GroupedSvgItem(grouped_image, parent=self.canvas)
        self.grouped_item.move(random.randint(0, self.canvas.width() - self.grouped_item.width()),
                               random.randint(0, self.canvas.height() - self.grouped_item.height()))
        self.grouped_item.show()

        self.svg_items.append(self.grouped_item)



#MAIN FUNCTION

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

#END