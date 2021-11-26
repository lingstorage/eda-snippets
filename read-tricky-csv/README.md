# Advanced usage of read_csv method to read tricky csv files

*advanced_read.py* uses the *read_csv* method in an advanced manner to read two tricky csv files: *user.csv* and *order.csv* in *data* directory.

### Tricky requirements for *user.csv*
- Use the first column "No" as the index of the table.
- Read "UserID" (001, 002 ,...) as string type instead of integers in order to keep the padded zero.
- Read "DateOfBirth" (e.g. 1989-2-19) and "UpdateTime" (e.g. 01/01/2000 11:52:40.312 PM) as datetime instead of string type.
- Read "Hight", which contains null values, as integers instead of floating-point numbers (⚠️ *int64* is not nullable so pandas read it as *float64* by default)
- Read "LicenseColor" (Green/Blue/Gold/Unknown) as category type and treat *Unknown* as NA.

### Tricky requirements for *order.csv*
- Use ";" as the delimiter instead of ",".
- Give column names to the table (⚠️ The file doesn't contain a header row) 
- Read "OrderTime" (e.g. 01-Jan-2004 21:32:55.5768) as datetime instead of string type.
- Read "TotalAmount" and "UnkDef", which contain "," as the thousand separator, as numeric type.