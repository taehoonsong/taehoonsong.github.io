---
title: bcp now has a Python package
date: 2026-04-14
summary: There is now a Python package from Microsoft that lets you use bcp without having to install the binary. But it's not all sunshine and rainbows just yet.
---
# What's the problem with bcp?
Check out my [previous post about bcp](./2025-12-29-sql-dataload-bcp.md), if you're curious about the details. For this post, what's important is that bcp is a CLI tool from Microsoft that massively speeds up bulk copying data to and from a SQL database. In the past, this tool had to be installed separately and invoked from Python using `subprocess`. I wrote a custom class that would help me use bcp in a more Pythonic way in the past; however, this also meant I had to make sure my users also had bcp installed on their machines. It wasn't the end of the world, but it was less ideal.

# Python package?
Well, it turns out, Microsoft has been working on a native Python solution for bcp! Starting v1.4.0 of [mssql-python](https://pypi.org/project/mssql-python/), you can use the `bulkcopy` API. This library is meant to be Microsoft's official Python driver for SQL Server. Let's look at an example.

```Python
import mssql_python as mssql

connection_string = "SERVER=<server address>;DATABASE=<database name>;Authentication=ActiveDirectoryDefault;Encrypt=yes;"
conn = mssql.connect(connection_string)

# Data to load
# Assume the target table named TestTable has two columns: col_a [int], col_b [varchar](5)
data = [
  (1, 'ABC'),
  (2, 'DEF'),
  (3, None)
]

cursor = conn.cursor()
cursor.bulkcopy(table_name="TestTable", data=data)

# Close connection
conn.commit()
conn.close()

# Your table should now contain:
# col_a | col_b
# 1     | 'ABC'
# 2     | 'DEF'
# 3     | NULL
```

As you can see, this library follows Python's DBAPI (see [PEP 249](https://peps.python.org/pep-0249/)), so it should look familiar if you've ever connected to a database using Python. There are a lot of options that this Python API exposes to the user. You can check out the documentation [here](https://github.com/microsoft/mssql-python/wiki/Bulk-Copy-(BCP)-API-Reference). Some of my favorites are `table_lock` and `column_mappings`. I generally like to lock the entire table for inserts for less overhead, but you should check if you can afford to do this, because all other reads will be waiting until `bulkcopy` is finished. You can, of course, bypass this by using a `(NOLOCK)` hint, but I'm talking about general reads here.

The `column_mappings` option is super helpful because it was a bit annoying to set up table schemas for the bcp CLI tool. With this Python implementation, you can either pass a list of column names (in order), or the a list of tuples containing the column index of your `data` and the target column in the database. For instance, if you wanted to only insert data to `col_b` in the above example, you would use the following syntax:

```Python
...
cursor.bulkcopy(table_name="TestTable", data=data, column_mappings=[(1, "col_b")])
...

```

# What's the catch?
## Bugs
Because this API was made public only a couple of months ago (February 2026) as of writing this post, there are certain issues that need to be ironed out. One issue I encountered is that the driver doesn't gracefully handle timeouts. I already reported [this](https://github.com/microsoft/mssql-python/issues/513) and they're working on a fix. The gist is that the connection can panic instead of raising a `TimeoutException`, as you would expect, when the timeout is reached. You could get around this by setting the `timeout` parameter to a high value, but this is still unexpected so Microsoft will be implementing a fix. For now, make sure to set a high enough `timeout` value. The default is 30 seconds, which might not be long enough if your data is particularly large or if you have a lot of columns. Based on some testing, I found that the number of columns have a noticeable impact on throughput. Here's what I found (this is also in the bug report I filed):

| Test Data Size | rows_copied | batch_count | elapsed_time | rows_per_second |
| --------------- | -------------- | -------------- | -------------- | ------------------- |
| 1m rows, 1 col | 1,000,000 | 1 | 6.2116232 | 160,988.515852024 |
| 5m rows, 1 col | 5,000,000 | 1 | 30.1131109 | 166,040.63315158847 |
| 1m rows, 10 cols | 1,000,000 | 1 | 6.290492 | 158,970.07738027486 |
| 5m rows, 10 cols | 5,000,000 | 1 | 37.8730692 | 132,019.93146095483 |
| 1m rows, 20 cols | 1,000,000 | 1 | 9.2570929 | 108,025.27432775359 |
| 5m rows, 20 cols | 5,000,000 | 1 | 45.5451105 | 109,781.26839762524 |
| 1m rows, 30 cols | 1,000,000 | 1 | 13.6634428 | 73,187.99622010347 |
| 5m rows, 30 cols | 5,000,000 | 1 | 68.4133351 | 73,085.16669581279 |
| 1m rows, 50 cols | 1,000,000 | 1 | 22.805045 | 43,849.94636055311 |
| 5m rows, 50 cols | 5,000,000 | 1 | 113.1195291 | 44,201.03265794094 |
| 1m rows, 100 cols | 1,000,000 | 1 | 45.144546 | 22,151.070031804065 |
| 5m rows, 100 cols | 5,000,000 | 1 | 225.6622574 | 22,157.006039061278 |
| 1m rows, 200 cols | 1,000,000 | 1 | 90.6763206  | 11,028.23750879014  |
| 5m rows, 200 cols | 5,000,000 | 1 | 453.4855953 | 11,025.70853808992  |

Another bug I saw is that `DATETIME` is rounded inconsistently. See [issue 516](https://github.com/microsoft/mssql-python/issues/516). This is not relevant for my workflow, but it might be for yours. And who knows what other bugs are waiting to be discovered?

## No SQLAlchemy support yet
Another issue is that [SQLAlchemy](https://pypi.org/project/SQLAlchemy/) does not support this new driver (`mssql-python`) at the moment. I know that the team is working on adding support for the 2.1 release. If you're using SQLAlchemy or relying on it, you should probably wait. [Pandas](https://pypi.org/project/pandas/) and [Polars](https://pypi.org/project/polars/) rely on SQLAlchemy for writing to the database as well. I'm not sure when 2.1 will be released, but it's not difficult to write a custom wrapper around `bulkcopy` to easily load data frames. Here's an example involving a Polars data frame:

```Python
import polars as pl
import mssql_python as mssql

# Same data as previous example, but as a polars dataframe.
df = pl.DataFrame({"col_a": [1, 2, 3], "col_b": ["ABC", "DEF", None]})

# Create connection
connection_string = "SERVER=<server address>;DATABASE=<database name>;Authentication=ActiveDirectoryDefault;Encrypt=yes;"
conn = mssql.connect(connection_string)
cursor = conn.cursor()

# Load data using bulkcopy
# Make sure the dataframe column names match the column names in the database!
cursor.bulkcopy(table_name="TestTable", data=df.iterrows(), column_mappings=df.columns)

# Close connection
conn.commit()
conn.close()
```

As long as your data frame column names match the database column names, you can easily provide the column mappings without worrying about column order! This is a huge usability win compared to bcp where we had to make sure the column order was identical or fiddle with the convoluted table schema option in the CLI.

## Authentication
I mentioned this in my [previous post about bcp](./2025-12-29-sql-dataload-bcp.md), but bcp does not support token based authentication on Windows. I don't know if Microsoft will eventually support it (the CLI tool supports tokens for MacOS/Linux), but I hope they eventually do. The list of supported methods can be found [here](https://github.com/microsoft/mssql-python/wiki/Microsoft-Entra-ID-support#authentication-methods).

# So what should I do?
If you have a relatively simple tech stack or you can afford to swap out existing APIs, I would say the speed benefit of `bulkcopy` is worth the hassle. In my current role, I have a monthly ETL process that used to take a little over an hour to finish. With this new `bulkcopy` API, the entire load took only 15 minutes. A 4x speed improvement is nothing to scoff at! However, for the majority of codebases, I think waiting for the SQLAlchemy support is the safer bet, especially if you have a lot of SQLAlchemy code already.

