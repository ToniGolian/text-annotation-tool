# Database Embedding 
This document explains how to define the database configuration for tags that are linked to a database for value selection. It also describes where to place the configuration file so it can be integrated into the application.

The database can be linked to tags in existing projects as well as to new tags defined independently of a project. The latter is useful if you want to create a new project with the project wizard and want to use that tag type linked to a database.

# Link a database to tag type independently of a project
## Needed files
To enable database embedding for a tag type, you need to create three files:
1. A tag definition file in JSON format that defines the tag type and its properties. How to create this file is described in the [Tag Definition documentation](README_tag_definition.md).
2. A database configuration file in JSON format that specifies how to read and interpret the source database. How to create this file is described below. 
3. A source database file in CSV format that contains the data to be used for tagging.

## Placement of the files
### Placement of the tag definition file
The tag definition file should be placed in the `app_data/projects/<project_name>/config/tags` directory.
### Placement of the database config file
The database configuration file should be placed in the `app_data/app/databases/config` directory.
### Placement of the source database file
The source database file should be placed in the `app_data/app/databases/sources` directory. It must be a CSV file.

# Link a database to tag type in an existing project
## Needed files
To enable database embedding for a tag type, you need to create two files:
1. A database configuration file in JSON format that specifies how to read and interpret the source database.
2. A registry lock file in JSON format that manages the association between the tag type and its database.
How to create these files is described below.
We also need the tag definition file for the corresponding tag type, which we want to link to the database.
Finally we need the source database file itself, which should be a CSV file. In an existing project, these last two files should already be present.

## Placement of the files
### Placement of the database config file
The database configuration file should be placed in the `app_data/projects/<project_name>/config/database` directory.
### Placement of the registry lock file
The registry lock file should be placed in the `app_data/projects/<project_name>/database_registry_locks` directory.
### Placement of the tag definition file
The tag definition file should be placed in the `app_data/projects/<project_name>/config/tags` directory.
### Placement of the source database file
The source database file should be placed in the `app_data/app/databases/sources` directory. It must be a CSV file.

## Settings to enable database embedding for a tag type
The corresponding tag definition file must have the `has_database` field set to `true`.
Also make sure that the `type` field in the tag definition file matches the type of the tag (case sensitive).

Finally change the `current_config_file` field in the `app_data/projects/<project_name>/config/settings/project.json` for the corresponding tag type to the file name and add the extension `.json`. Also put this file name (with extension) in the `config_files` list in the same settings file.


# Structure of the config file.

```json
{
  "options": {
    "delimiter": "...",
    "dict_delimiters": [...],
    "prefixes": { "<column_index>": [ ... ] },
    "postfixes": { "<column_index>": [ ... ] },
    "infixes": { "<column_index>": [ ... ] }
  },
  "columns": {
    "key_column": <int>,
    "output_columns": [<int>, ...],
    "display_columns": [<int>, ...]
  },
  "source": "<source_file>.csv",
  "source_registry": "<source_registry>"
}
```

### columns
- `key_column`: (int) Index (0-based) of the column containing the main word used as the dictionary key. On this the search is based.
- `output_columns`: (list of int) Column indices used to build the output string for tagging which will be part of the tag in the end.
- `display_columns`: (list of int) Column indices used to build a display string for menu choices for the user.

### options
- `delimiter`: (string) String for how to separate  multiple columns in output/display values.
- `dict_delimiters`: (list of strings) Delimiters that define nested dictionary structure. A new sub-dictionary is created if a word starts with the current word plus one of these elimiters.
- `prefixes`: (dict) Maps column indices (as strings) to lists of prefixes to strip from the values. If one of the column indices from the output/display_columns is preset as a
 key in this dictionary, then in the output/display values, are stripped from the prefix that is provided as a value here.
- `postfixes`: (dict) Maps column indices to lists of suffixes to strip. Similar to prefixes.
- `infixes`: (dict) Maps column indices to substrings (infixes) to remove from inside the values. Similar to prefixes.

**Note:** Column indices in `prefixes`, `postfixes`, and `infixes` must be strings due to JSON limitations. Also see Notes at the bottom.

### source
- `source`: (string) The name of the source CSV file placed in the `app_data/app/databases/sources` directory.
### source_registry
- `source_registry`: (string) The name of the directory containing the csv source database files.

## Example
```json
{
  "options": {
    "delimiter": " | ",
    "dict_delimiters": ["|", "-", "/", ",", ";", ":", "_", " "],
    "prefixes": { "2": ["AX_", "Gem"] },
    "postfixes": { "2": ["DE"] },
    "infixes": { "2": ["-"] }
  },
  "columns": {
    "key_column": 4,
    "output_columns": [0],
    "display_columns": [2, 0]
  }
}
```

## Notes
- Use valid 0-based indices matching your CSV file columns.
- If you don’t need to strip any prefix/postfix/infix, provide an empty dict.
- Infixes are all removed if found, but without overlap: e.g. if you provide ```"infixes": { "2": ["a", "foo"] }``` and the word is ```bbbfoaobbb``` then only ```a``` is removed (yields ```bbbfoobbbb```). If the word is ```bbbfooabbb```, then ```a``` and ```foo``` are removed (yields ```bbbbbb```). 
- Infixes are removed if at any position in the word, also at the start or end.
- Post- and Prefixes are only removed such that the first occurence of one of the values provided is removed: e.g. if the word is ```AX_Gemeinde``` and ```"prefixes": { "2": ["AX_", "Gem"] }```, then ```Gemeinde``` is returned because only the first match is removed.
- The order of removal for the three types is: First prefixes, then postfixes and last infixes.

# Structure of the registry lock 
{
    "name": <TAG_TYPE>,
    "database_registry": <database_name>,
    "source_registry": <tag_type>,
    "source": <source_file>,
    "current_db": "",
    "dbs": [],
    "current_config_file": "<database_config_file>",
    "config_files": [
        "<database_config_file>"
    ],
    "count": 0
}

- `name`: (string) The tag type this registry lock is for. Must match the `type` field in the tag definition file.
- `database_registry`: (string) The name of the database registry. This is used to identify the database in the application.
- `source_registry`: (string) The source registry name. This is typically the same as the tag type.
- `source`: (string) The source file name. This is the name of the CSV file placed in the `app_data/app/databases/sources` directory.
- `current_db`: (string) The current database file in use. This is typically empty initially.
- `dbs`: (list) A list of database files associated with this tag type. This is typically empty initially.
- `current_config_file`: (string) The current configuration file in use. This should match the name of the database config file placed in the `app_data/projects/<PROJECT_NAME>/config/database` directory.
- `config_files`: (list) A list of configuration files associated with this tag type. This should include the name of the database config file. 
- `count`: (int) A counter for tracking purposes. This is typically initialized to 0.

Considerations:
- This is case sensitive. Use the case as provided in the placeholders.