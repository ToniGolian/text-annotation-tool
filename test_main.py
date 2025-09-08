from view.duplicates_dialog import DuplicatesDialog
import tkinter as tk


duplicates = {
    'PLACE': [
        {'name': 'PLACE', 'path': 'app_data\\projects\\test_project\\config/tags/place.json', 'display_name': 'PLACE (test_project)', 'project': 'test_project'}, {
            'name': 'PLACE', 'path': 'app_data\\projects\\time_ml\\config/tags/place.json', 'display_name': 'PLACE (time_ml)', 'project': 'time_ml'}
    ],
    'TIMEX3': [
        {'name': 'TIMEX3', 'path': 'app_data\\projects\\test_project\\config/tags/timex3.json', 'display_name': 'TIMEX3 (test_project)', 'project': 'test_project'}, {
            'name': 'TIMEX3', 'path': 'app_data\\projects\\time_ml\\config/tags/timex3.json', 'display_name': 'TIMEX3 (time_ml)', 'project': 'time_ml'}
    ]
}

root = tk.Tk()
root.withdraw()

dialog = DuplicatesDialog(duplicates, master=root)
result = dialog.show()
print("Dialog result:", result)

root.destroy()
