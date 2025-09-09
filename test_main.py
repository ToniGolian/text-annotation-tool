from view.duplicates_dialog import DuplicatesDialog
import tkinter as tk


test_data = {'project_name': 'e', 'tag_group_file_name': 'ee', 'tag_groups': {'e': ['CONFIDENCE (test_project_copy)', 'PLACE (test_project_copy)', 'TIMEX3 (test_project)'], 'ee': ['EVENT (time_ml)', 'PLACE (time_ml)']}, 'selected_tags': [{'name': 'TIMEX3', 'path': 'app_data\\projects\\test_project\\config/tags/timex3.json', 'display_name': 'TIMEX3 (test_project)', 'project': 'test_project'}, {'name': 'CONFIDENCE', 'path': 'app_data\\projects\\test_project_copy\\config/tags/confidence.json', 'display_name': 'CONFIDENCE (test_project_copy)', 'project': 'test_project_copy'}, {
    'name': 'PLACE', 'path': 'app_data\\projects\\test_project_copy\\config/tags/place.json', 'display_name': 'PLACE (test_project_copy)', 'project': 'test_project_copy'}, {'name': 'EVENT', 'path': 'app_data\\projects\\time_ml\\config/tags/event.json', 'display_name': 'EVENT (time_ml)', 'project': 'time_ml'}, {'name': 'PLACE', 'path': 'app_data\\projects\\time_ml\\config/tags/place.json', 'display_name': 'PLACE (time_ml)', 'project': 'time_ml'}]}

# root = tk.Tk()
# root.withdraw()

# dialog = DuplicatesDialog(duplicates, master=root)
# result = dialog.show()
# print("Dialog result:", result)

# root.destroy()
