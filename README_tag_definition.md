# Tag Definition Format

This document describes how to define tags for annotation in the tool. Tag definitions are specified in JSON files and control which attributes are available for annotation, their types, and constraints.

## Placement of the tag definition file
<!-- todo continue -->

## Structure

A tag definition JSON file has the following structure:

```json
{
  "type": "<TAG_TYPE>",
  "id_prefix": "<ID_PREFIX>",
  "has_database": <bool>,
  "attributes": {
    "<attribute_name>": {
      "type": "<TYPE>",
      "allowedValues": [ ... ] // optional
    },
    // ...more attributes...
  }
}
```

### Top-Level Fields

- **type**: (string) The name of the tag type (e.g., `"TIMEX3"`, `"PLACE"`).
- **id_prefix**: (string) Prefix for automatically generated tag IDs (e.g., `"t"` for `"t1"`, `"t2"`).
- **has_database**: (boolean) If true, the tag is linked to a database for value selection.
- **attributes**: (object) Defines the attributes available for this tag.

### Attribute Definition

Each attribute is defined as an object with:

- **type**: (string) The data type of the attribute. Common types:
  - `"ID"`: Unique identifier.
  - `"IDREF"`: Reference to another tag's ID.
  - `"string"`: Free text or restricted string.
  - `"boolean"`: `"true"` or `"false"`.
  - `"union"`: Value must match one of several types.
  - `"CDATA"`: Arbitrary text.
  - Custom types (e.g., `"Duration"`, `"Date"`) may be supported.
- **allowedValues**: (array, optional) Restricts the attribute value to the listed options.

### Notes

- All attribute names must be unique within a tag definition.
- If `allowedValues` is omitted, any value matching the attribute's type is accepted.
- Custom types must be supported by the annotation tool.
- Tag definitions are used to validate and guide annotation.

## Example: TIMEX3 Tag Definition

Below is an example tag definition for the TIMEX3 tag, which annotates temporal expressions:

```json
{
  "type": "TIMEX3",
  "id_prefix": "t",
  "has_database": false,
  "attributes": {
    "tid": { "type": "ID" },
    "type": { "type": "string", "allowedValues": ["DATE", "TIME", "DURATION", "SET"] },
    "functionInDocument": { "type": "string", "allowedValues": ["CREATION_TIME", "EXPIRATION_TIME", "MODIFICATION_TIME", "PUBLICATION_TIME", "RELEASE_TIME", "RECEPTION_TIME", "NONE"] },
    "beginPoint": { "type": "IDREF" },
    "endPoint": { "type": "IDREF" },
    "quant": { "type": "CDATA" },
    "freq": { "type": "Duration" },
    "temporalFunction": { "type": "boolean", "allowedValues": ["true", "false"] },
    "value": { "type": "union", "allowedValues": ["Duration", "Date", "Time", "WeekDate", "WeekTime", "Season", "PartOfYear", "PaPrFu"] },
    "valueFromFunction": { "type": "IDREF" },
    "mod": { "type": "string", "allowedValues": ["BEFORE", "AFTER", "ON_OR_BEFORE", "ON_OR_AFTER", "LESS_THAN", "MORE_THAN", "EQUAL_OR_LESS", "EQUAL_OR_MORE", "START", "MID", "END", "APPROX"] },
    "anchorTimeID": { "type": "IDREF" },
    "comment": { "type": "CDATA" }
  }
}
```

### Example Tag Instances

```xml
<TIMEX3 tid="t1" type="DURATION" value="P60D" mod="EQUAL_OR_LESS">no more than 60 days</TIMEX3>
<TIMEX3 tid="t2" type="DATE" value="2000" mod="START">the dawn of 2000</TIMEX3>
<TIMEX3 tid="t3" type="SET" value="P1M" freq="2X">twice a month</TIMEX3>
<TIMEX3 tid="t4" type="SET" value="P1M" quant="EVERY" freq="3D">three days every month</TIMEX3>
<TIMEX3 tid="t5" type="SET" value="P1D" quant="EVERY">daily</TIMEX3>
<TIMEX3 tid="t6" type="DURATION" value="P2W" beginPoint="t61" endPoint="t62">two weeks</TIMEX3>
<TIMEX3 tid="t61" type="DATE" value="2003-06-07">June 7, 2003</TIMEX3>
<TIMEX3 tid="t62" type="DATE" value="2003-06-21" temporalFunction="true" anchorTimeID="t6"/>
<TIMEX3 tid="t71" type="DATE" value="1992">1992</TIMEX3>
<TIMEX3 tid="t72" type="DATE" value="1995">1995</TIMEX3>
<TIMEX3 tid="t7" type="DURATION" value="P4Y" beginPoint="t71" endPoint="t72" temporalFunction="true"/>
```

## References

- [TimeML Schema](https://timeml.github.io/site/publications/timeMLdocs/timeml_1.2.1.html#timex3)
