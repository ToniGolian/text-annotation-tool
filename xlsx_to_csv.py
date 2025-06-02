import pandas as pd

# Passe den Pfad an deine Datei an
xlsx_path = r"C:\Users\tonig\PythonProjects\text-annotation-tool\app_data\projects\time_ml\project_data\db_csv\place_csv_db.xlsx"
csv_path = r"C:\Users\tonig\PythonProjects\text-annotation-tool\app_data\projects\time_ml\project_data\db_csv\place_csv_db.csv"

df = pd.read_excel(xlsx_path)
df.to_csv(csv_path, index=False, encoding="utf-8")
