import os
import pandas as pd


# Get the absolute path to this script's directory
WORKING_DIR = os.path.dirname(__file__)


# Define functions for column casting in pd.read_csv()
def to_datetime_1(col):
    return pd.to_datetime(col, format="%Y-%m-%d")


def to_datetime_2(col):
    return pd.to_datetime(col, format="%m/%d/%Y %I:%M:%S.%f %p")


def to_datetime_3(col):
    return pd.to_datetime(col, format="%d-%b-%Y %H:%M:%S.%f")


users = pd.read_csv(
    WORKING_DIR + r"/data/users.csv",
    index_col="No",
    dtype={
        "UserID": "object",  "LicenseColor": "category",
        "Hight": "Int64"  # "Int64" is nullable version of "int64"
    },
    converters={
        "DateOfBirth": to_datetime_1,
        "UpdateTime": to_datetime_2
    },
    na_values={"LicenseColor": "Unknown"},
    skipinitialspace=True,
    encoding="utf-8"
)


orders = pd.read_csv(
    WORKING_DIR + r"/data/orders.csv",
    sep=";",
    names=[
        "OrderID", "OrderTime", "ProductID", "NumberOfOrders",
        "TotalAmount", "UnkDef", "UserID"
    ],
    dtype={
        "ProductID": "object", "NumberOfOrders": "Int64",
        "UserID": "object"
    },
    converters={"OrderTime": to_datetime_3},
    # Convert thousand-separated columns into ...
    # int64 if the column doesn't contain null, or
    # float64 if the column contains null.
    thousands=",",
    skipinitialspace=True,
    encoding="utf-8"
)


# Check if the csv files are read correctly.
def summarize(df):
    result = pd.DataFrame(df.dtypes.rename("Type"))
    result = result.merge(
        pd.DataFrame(df.isna().sum().rename("NAs")),
        left_index=True, right_index=True
    )
    result = result.merge(
        pd.DataFrame(df.iloc[0].rename("FirstElement")),
        left_index=True, right_index=True
    )
    result = result.merge(
        pd.DataFrame(df.iloc[-1].rename("LastElement")),
        left_index=True, right_index=True
    )
    return result


print("\n< Summary of users >")
rows, columns = users.shape
print(f"Number of rows = {rows:d}")
print(f"Number of columns = {columns:d}")
print(summarize(users))

print("\n< Summary of orders >")
rows, columns = orders.shape
print(f"Number of rows = {rows:d}")
print(f"Number of columns = {columns:d}")
print(summarize(orders))
