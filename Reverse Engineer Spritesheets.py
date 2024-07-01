import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QFileDialog, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import xml.etree.ElementTree as ET
from PIL import Image
from threading import Thread

class SpriteSheetProcessor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sprite Sheet Processor")
        self.resize(400, 300)

        self.xml_file_path = ""
        self.image_path = ""
        self.output_folder = ""
        self.processing = False

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()


        self.image_label = QLabel("Image file: No file selected")
        self.layout.addWidget(self.image_label)

        self.image_button = QPushButton("Select Image File")
        self.image_button.clicked.connect(self.select_image)
        self.layout.addWidget(self.image_button)
        
        self.xml_label = QLabel("XML file: No file selected")
        self.layout.addWidget(self.xml_label)

        self.xml_button = QPushButton("Select XML File")
        self.xml_button.clicked.connect(self.select_xml)
        self.layout.addWidget(self.xml_button)

        self.output_label = QLabel("Output folder: No folder selected")
        self.layout.addWidget(self.output_label)

        self.output_button = QPushButton("Select Output Folder")
        self.output_button.clicked.connect(self.select_output)
        self.layout.addWidget(self.output_button)

        self.process_button = QPushButton("Process Sprite Sheet")
        self.process_button.clicked.connect(self.start_processing)
        self.layout.addWidget(self.process_button)

        self.loading_label = QLabel()
        self.layout.addWidget(self.loading_label)

        self.central_widget.setLayout(self.layout)

    def select_xml(self):
        self.xml_file_path, _ = QFileDialog.getOpenFileName(self, "Select XML File", "", "XML files (*.xml)")
        if self.xml_file_path:
            self.xml_label.setText(f"XML file: {self.xml_file_path}")
        else:
            self.xml_label.setText("XML file: No file selected")

    def select_image(self):
        self.image_path, _ = QFileDialog.getOpenFileName(self, "Select Image File", "", "Image files (*.png)")
        if self.image_path:
            self.image_label.setText(f"Image file: {self.image_path}")
        else:
            self.image_label.setText("Image file: No file selected")

    def select_output(self):
        self.output_folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if self.output_folder:
            self.output_label.setText(f"Output folder: {self.output_folder}")
        else:
            self.output_label.setText("Output folder: No folder selected")

    def start_processing(self):
        if not self.processing and all([self.xml_file_path, self.image_path, self.output_folder]):
            self.processing = True
            self.loading_label.setText("Processing...")
            self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.layout.addWidget(self.loading_label)
            self.update()

            # Update UI just before starting processing
            QApplication.processEvents()

            # Run processing in a separate thread
            processing_thread = Thread(target=self.process_sprite_sheet)
            processing_thread.start()
        elif self.processing:
            print("Processing already in progress.")
        else:
            print("Please select XML file, image file, and output folder.")


    def process_sprite_sheet(self):
        try:
            tree = ET.parse(self.xml_file_path)
            root = tree.getroot()

            for sub_texture in root.findall('.//SubTexture'):
                name = sub_texture.attrib['name']
                x = int(sub_texture.attrib['x'])
                y = int(sub_texture.attrib['y'])
                width = int(sub_texture.attrib['width'])
                height = int(sub_texture.attrib['height'])
                frame_x = int(sub_texture.attrib.get('frameX', 0))
                frame_y = int(sub_texture.attrib.get('frameY', 0))
                frame_width = int(sub_texture.attrib.get('frameWidth', width))
                frame_height = int(sub_texture.attrib.get('frameHeight', height))
                rotated = sub_texture.attrib.get('rotated', 'false') == 'true'

                image = Image.open(self.image_path)
                sprite = image.crop((x, y, x + width, y + height))

                if rotated:
                    sprite = sprite.rotate(90, expand=True)
                    width, height = sprite.size  # Swap width and height for rotated sprite

                canvas_width = max(width + abs(frame_x), frame_width)
                canvas_height = max(height + abs(frame_y), frame_height)

                canvas = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 0))
                canvas.paste(sprite, (abs(frame_x), abs(frame_y)))

                output_path = f"{self.output_folder}/{name}.png"
                canvas.save(output_path)

            self.loading_label.setText("Sprite sheet processed successfully.")
        except Exception as e:
            self.loading_label.setText(f"Error processing sprite sheet: {e}")
        finally:
            self.processing = False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('fusion')
    window = SpriteSheetProcessor()
    window.show()
    sys.exit(app.exec())
