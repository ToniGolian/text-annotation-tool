# config.json – Configuration Format for CSVConverter

## Structure

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
  }
}
```

## Explanation

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
