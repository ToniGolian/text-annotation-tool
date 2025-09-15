# text-annotation-tool
A lightweight and flexible application for creating, editing, and managing text annotations.  
It is designed for projects where spans of text need to be tagged with custom categories and enriched with additional attributes.  
The annotations are intended to make texts machine-readable — for example, as training data for language models or other natural language processing tasks.  
The tool is also suitable for any use case where text needs to be enriched with structured, automatically processable tags.

Author: Toni Golian

## Features
- **PDF text extraction**: Import text directly from PDF files and correct extraction errors before annotation.  
- **Interactive annotation interface**: Select text spans and assign custom tags with user-defined attributes.  
- **Custom tag management**: Define, group, and reuse tag types tailored to your project needs.  
- **Database integration**: Link tags to external databases for assisted annotation with automatic suggestions.  
- **Annotation comparison and merging**: Open multiple annotated documents side by side, compare annotations, and consolidate them into a single merged document.  
- **Flexible project management**: Create, load, and manage annotation projects with structured tag groups.  
- **Import and export**: Save annotations and comparison results in multiple formats for interoperability.  
- **Collaboration-ready**: Supports workflows where annotations are created, reviewed, and combined by multiple users.  



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