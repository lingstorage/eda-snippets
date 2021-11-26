import os
import re
import numpy as np
import pandas as pd

# Get the absolute path to this script's directory.
WORKING_DIR = os.path.dirname(__file__)

# Define the absolute path where this script's outputs will be stored.
OUTPUT_DIR = WORKING_DIR + "/outputs"


#### Read datasets #####################################################
def to_datetime_1(col):
    return pd.to_datetime(col, format="%d/%m/%Y %H:%M:%S")


def to_datetime_2(col):
    return pd.to_datetime(col, format="%d.%m.%Y %H:%M:%S")


def read_csv_(filename):
    return pd.read_csv(
        r"~/datasets/it-salary-survey-eu/" + filename,
        converters={
            "Timestamp": to_datetime_1,
            "Zeitstempel": to_datetime_2
        },
        skipinitialspace=True,
        encoding="utf-8"
    )


DATASETS = [
    "IT Salary Survey EU 2018",
    "IT Salary Survey EU 2019",
    "IT Salary Survey EU 2020"
]

df_dict = {
    DATASETS[0]: read_csv_("IT Salary Survey EU 2018.csv"),
    DATASETS[1]: read_csv_("T Salary Survey EU 2019.csv"),
    DATASETS[2]: read_csv_("IT Salary Survey EU  2020.csv"),
}


#### Get number of rows and columns of each dataset ####################
shape = pd.DataFrame(columns=["dataset", "# of rows", "# of columns"])


def append_shape(df_dict_, key_):
    shape.loc[len(shape)] = [
        key_,
        len(df_dict_[key_]),
        len(df_dict_[key_].columns)
    ]


for key in DATASETS:
    append_shape(df_dict, key)


#### Get descriptive statistics of each column #########################
def pretty_format(str_):
    rjust_length = 19  # length for right-justification

    # Compile regex to capture datetime in "yyyy-mm-dd hh-mm-ss.f" format
    datetime_regex = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(\.\d+)?")

    # Compile regex to capture integer or decimal numbers
    number_regex = re.compile(r"^-?\d+(\.\d+)?$")

    if str_ == "nan":
        return "-".rjust(rjust_length)

    if datetime_regex.search(str_) != None:
        # Remove milliseconds
        return str_.split(".")[0].rjust(rjust_length)

    if number_regex.search(str_) != None:
        return f"{float(str_):,.3f}".rjust(rjust_length)

    if len(str_) > rjust_length:
        return str_[:rjust_length - 3] + "..."

    return str_.rjust(rjust_length)


def get_desc_as_series(df_dict_, key_):
    """This returns a column of "Colmun summary" table in _summary.html."""
    # Create descriptive statistics of all columns
    desc = df_dict_[key_].describe(include="all", datetime_is_numeric=True)
    desc.loc["nas"] = df_dict_[key_].isnull().sum()
    desc.loc["nas(%)"] = df_dict_[key_].isnull().mean() * 100
    desc.loc["type"] = df_dict_[key_].dtypes

    desc_series = pd.Series(name=key_, dtype="object")

    for col in desc.columns:
        # Convert the descriptive statistics of each column into a
        # string object in readable format.
        desc_one = (
            desc.index.str.ljust(6) + ": "
            + desc[col].astype("str").map(pretty_format)
        )
        desc_series.loc[col] = desc_one.to_string(index=False)

    return desc_series


cols_summary = pd.DataFrame()

for key in DATASETS:
    cols_summary = cols_summary.merge(
        right=get_desc_as_series(df_dict, key),
        left_index=True, right_index=True, how="outer"
    )


#### Create summary report #############################################
shape_html = shape.to_html(
    index=False,
    formatters={
        "# of rows": lambda x: format(x, ",d"),
        "# of columns": lambda x: format(x, ",d")
    },
    justify="center",  # This justifies only column labels
    col_space=100
)

# Compile regex to capture a number in any format surrounded by <td> tags.
# For example, the following strings are to be captured.
#     <td>1000</td>      # Integer
#     <td>-1000</td>     # Negative integer
#     <td>1,000</td>     # Thousand separeted
#     <td>1000.00</td>   # Decimal
#     <td>1,000.00</td>  # Thousand separated decimal
#     <td>-1,000.00</td> # Negative thousand separated decimal
#     <td>00001</td>     # Zero padded
number_regex = re.compile(
    r"<td>(-?\d+(\.\d+)?|-?\d{1,3}(,\d{3})*(\.\d+)?)</td>")

# Left-justify text for numeric cells.
pretty_shape_html = ""
for line in shape_html.splitlines():
    mo = number_regex.search(line)
    if mo == None:
        pretty_shape_html += line + "\n"
    else:
        pretty_shape_html += line.replace(
            mo.group(),
            '<td style="text-align:right">' + mo.group(1) + "</td>\n"
        )


cols_summary_html = cols_summary \
    .to_html(justify="center") \
    .replace(r"\n", "<br>") \
    .replace("<th></th>", '<th>Column Name</th>') \
    .replace("<th>", '<th width="200">') \
    .replace("<td>", '<td style="text-align:Center"><pre>') \
    .replace("</td>", "</pre></td>")


# Create html file
html_file = open(OUTPUT_DIR + "/_summary.html", "w")
html_file.write(pretty_shape_html)
html_file.write("<br>\n")
html_file.write("""
<body>
    <h1>Column summary</h1>
    <p>"NaN" means the dataset doesn't contain the column.</p>
</body>
""")
html_file.write(cols_summary_html)
html_file.close()


#### Compare levels of each categorical column. ########################
# Create a list of categorical columns.
cat_col_list = []

for key in DATASETS:
    dtypes = df_dict[key].dtypes
    dtypes = dtypes[(dtypes == "object") | (dtypes == "category")]
    cat_col_list.extend(dtypes.index.to_list())

# Remove duplications.
cat_col_list = pd.Series(cat_col_list).drop_duplicates().to_list()


def rowcount_by_level(target_col):
    """This counts # of rows by level of target_col in each dataset and
    save the result in target_col.html."""

    rows_by_level = pd.DataFrame()

    for key in DATASETS:
        if target_col in df_dict[key]:
            rows_by_level = rows_by_level.merge(
                right=df_dict[key]
                .groupby(target_col).size()
                .rename(key)
                .astype("str"),
                left_index=True, right_index=True, how="outer"
            )
        else:
            rows_by_level[key] = np.nan

    # Create HTML file only if # of levels is less than 1000.
    if len(rows_by_level) - 1 < 1000:
        rows_by_level_html = rows_by_level \
            .reset_index() \
            .to_html(justify="center") \
            .replace("NaN", "-") \
            .replace("<td>", '<td style="text-align:right">')

        target_col = target_col.replace(" ", "-")
        target_col = target_col.replace("/", "|")
        html_file = open(f"{OUTPUT_DIR}/{target_col}.html", "w")
        html_file.write(rows_by_level_html)
        html_file.close()


for col in cat_col_list:
    rowcount_by_level(col)
