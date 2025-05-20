import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QCheckBox, QPushButton, QTextEdit, QToolBar, QAction, QLabel, QFileDialog
from PyQt5.QtCore import Qt

class FileBrowserApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Browser with LLM-Friendly Text Generator")
        self.setGeometry(100, 100, 600, 400)

        # Main widget and layout
        self.main_widget = QWidget()
        self.layout = QVBoxLayout()

        self.choose_dir_button = QPushButton("Choose Directory")
        self.choose_dir_button.clicked.connect(self.choose_directory)
        self.layout.addWidget(self.choose_dir_button)

        self.selected_directory = os.getcwd()  # Start with the current working directory

        # Add toolbar
        toolbar = QToolBar("Main Toolbar")
        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(self.refresh_file_list)
        toolbar.addAction(refresh_action)
        self.addToolBar(Qt.LeftToolBarArea, toolbar)

        # Text area to display generated LLM-friendly paths or file contents
        self.text_area = QTextEdit()
        self.layout.addWidget(self.text_area)

        # Generate buttons
        self.generate_button = QPushButton("Generate Paths")
        self.generate_button.clicked.connect(self.generate_paths)
        self.layout.addWidget(self.generate_button)

        self.generate_content_button = QPushButton("Generate File Contents")
        self.generate_content_button.clicked.connect(self.generate_file_contents)
        self.layout.addWidget(self.generate_content_button)

        # Set layout
        self.main_widget.setLayout(self.layout)
        self.setCentralWidget(self.main_widget)

        # Store checkboxes and file paths
        self.checkboxes = []
        self.file_paths = []

        # Populate file list initially
        self.refresh_file_list()

    def refresh_file_list(self):
        # Clear current checkboxes and paths
        for checkbox in self.checkboxes:
            self.layout.removeWidget(checkbox)
            checkbox.deleteLater()
        self.checkboxes.clear()
        self.file_paths.clear()

        files_and_folders = os.listdir(self.selected_directory)

        # Create checkboxes for each file/folder
        for item in files_and_folders:
            item_path = os.path.join(self.selected_directory, item)
            if os.path.isdir(item_path) and not self.has_files(item_path):
                # Skip empty folders
                continue
            checkbox = QCheckBox(item)
            self.layout.insertWidget(0, checkbox)  # Add to layout at the top
            self.checkboxes.append(checkbox)
            self.file_paths.append(item_path)

    def has_files(self, directory):
        # Check if the folder contains any files or non-empty subdirectories
        for root, dirs, files in os.walk(directory):
            if files or dirs:  # Non-empty folder
                return True
        return False

    def generate_paths(self):
        selected_paths = []

        # Gather selected file and folder paths
        for checkbox, path in zip(self.checkboxes, self.file_paths):
            if checkbox.isChecked():
                relative_path = os.path.relpath(path, self.selected_directory)
                if os.path.isdir(path):
                    selected_paths.append(f"{relative_path}/")
                    # Recursively add subfolder files and folders, skip empty folders
                    for subdir, dirs, files in os.walk(path):
                        if files or dirs:  # Only include non-empty directories
                            relative_subdir = os.path.relpath(subdir, self.selected_directory)
                            selected_paths.append(f"{relative_subdir}/")
                            for file in files:
                                selected_paths.append(f"{relative_subdir}/{file}")
                else:
                    selected_paths.append(relative_path)

        # Display generated text in text area
        self.text_area.setText("\n".join(selected_paths))

    def generate_file_contents(self):
        selected_contents = []

        # Gather text contents of selected files and subfolders
        for checkbox, path in zip(self.checkboxes, self.file_paths):
            if checkbox.isChecked():
                if os.path.isdir(path):
                    # Recursively process subfolders and files
                    for subdir, _, files in os.walk(path):
                        for file in files:
                            file_path = os.path.join(subdir, file)
                            try:
                                with open(file_path, 'r') as f:
                                    file_content = f.read()
                                    relative_path = os.path.relpath(file_path, self.selected_directory)
                                    # Add file path label and file content to the display
                                    selected_contents.append(f"File: {relative_path}\n\n{file_content}\n{'-'*80}\n")
                            except Exception as e:
                                selected_contents.append(f"File: {relative_path} could not be read.\n{'-'*80}\n")
                elif os.path.isfile(path):
                    # Process the selected file
                    try:
                        with open(path, 'r') as file:
                            file_content = file.read()
                            relative_path = os.path.relpath(path, self.selected_directory)
                            # Add file path label and file content to the display
                            selected_contents.append(f"File: {relative_path}\n\n{file_content}\n{'-'*80}\n")
                    except Exception as e:
                        selected_contents.append(f"File: {relative_path} could not be read.\n{'-'*80}\n")

        # Display file contents in text area
        self.text_area.setText("\n".join(selected_contents))

    def choose_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory", self.selected_directory)
        if directory:
            self.selected_directory = directory
            self.refresh_file_list()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileBrowserApp()
    window.show()
    sys.exit(app.exec_())
