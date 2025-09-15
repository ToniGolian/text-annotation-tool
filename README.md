# text-annotation-tool
A lightweight text annotation tool for annotating spans of text with custom tags and attributes.
Author: Toni Golian

## Features
- Text extraction from PDF files
- Easy-to-use interface for text annotation
- Support for custom tags and attributes
- Export and import annotations in various formats
- Collaborative annotation support

## Installation
### Linux / MacOS
1. Clone the repository:
   ```bash
   git clone git@github.com:ToniGolian/text-annotation-tool.git
   ```
2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Navigate to the project directory:
    ```bash
   cd text-annotation-tool
   ```
4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the application:
   ```bash
   python3 main.py
   ```
   
### Windows
1. Clone the repository:
   ```bash
   git clone https://github.com/ToniGolian/text-annotation-tool.git
   ```
2. Navigate to the project directory:
    ```bash
   cd text-annotation-tool
   ```      
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python main.py
   ```
# Usage
## Extraction Mode
Select the notebook tab `PDF Extraction` at the top.
### Steps to extract text from a PDF:  
1. Open a pdf document using the `Open File` menu.
2. Click on `Extract Pages` to extract text from the pdf.
3. Correct any extraction errors using the text editor.
4. Click on `Adopt Text` to save the extracted text. The text will now be displayed in the annotation view.

## Annotation Mode
Select the notebook tab `Text Annotation` at the top.
### Add Tags
1. Select the text you want to annotate.
2. Choose an annotation type from the sidebar.
3. Add any additional tag information in the corresponding widgets on the right-hand side.
4. Click `Add Tag` to store your changes.

### Edit Tags
1. Select an existing tag from the list `ID to edit`. 
2. Make your changes in the text fields provided.
3. Click `Edit Tag` to update the tag.

### Delete Tags
1. Select an existing tag from the list `ID to Delete`.
2. Click `Delete Tag` to remove the tag.

### Database usage
1. Click on `Start <TAG_NAME> Annotation` to search the text for words that have corresponding entries in the database associated with the tag type.
2. Select a suggestion from the list.
3. Add any additional tag information in the corresponding widgets on the right-hand side.
4. Click `Add Tag` to store your changes.

You can navigate through the suggestions using the `Previous` and `Next` buttons.
You can end the search mode by clicking on `End <TAG_NAME> Annotation`.

## Comparison Mode
Select the notebook tab `Text Comparison` at the top.
### Steps to compare annotated texts:
1. Open two or more annotated text documents using the `Open File` menu. Alternatively you can open a comparison document, which is obtained by saving a comparison project.
2. You can now choose one annotation with the radio buttons on the top. Alternatively you can make a new annotation of the sentence in the first text display and adopt this annotation. This works the same way as in the annotation mode.
3. Click on `Adopt` to adopt the chosen or newly created annotation to your merged document.

### Save Comparison projects
You can save your comparison project by clicking on `Save` or `Save As` in the `File` menu. This will save a comparison file and allow you to reopen the comparison project later and continue your work.

### Export Comparison Results
You can export the results of your comparison project by clicking on `Export Merged Document` on the bottom left. This will save a new annotated text document containing all the annotations you have adopted during your comparison to the merged document directory of your project.

## Project Management
### Create New Project
Start the new project wizard by clicking on `New Project` in the `Project` menu.
1. Enter a name for your project. Click `Next`.
2. Choose tags you want to use in your project. (How to create and manage tags is described in the README_tags.md) Click `Next`.
3. Order the tags in tag groups. Click `Finish`.

### Load Existing Project
1. Load an existing project by clicking on `Open Project` in the `Project` menu.
2. Choose an existing project from the list.
3. Click on `Load Project`.

# License
This project is licensed under the MIT License. See the `LICENSE` file for details.