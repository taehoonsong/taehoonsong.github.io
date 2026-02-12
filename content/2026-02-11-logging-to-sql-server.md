---
title: Log Python apps to SQL Server
date: 2026-02-11
summary: When deploying a Python function app on Azure or AWS, collecting logs on your database may be better than relying on third-party solutions.
---

# Why log to a database?
If you already have a database set up, having a dedicated table for logging seems like a no-brainer. You don't have to rely on external tools for logging nor do you need to pay extra for those tools. There are a few things you may want to consider before proceeding with this method, however.
  1. What if your database is down. Do you have the necessary redundancy measures in place so that logs are not lost?
  2. How sensitive are the log messages? Do you have proper read/write policies for all tables/schemas? If you think your log messages are sensitive, you may want to implement a custom logger anyway, but you should make sure all security measures are in place.
  3. How many log messages are you expecting to send? For extremely high throughput operations, SQL could become a bottleneck. You could look for faster databases such as Redis, or simply opt for another logging service.

# Create a custom logger
With the caveats aside, how do you actually set up the Python to send logs to the SQL database instead of to `stdout` or to a log file? We need to write a custom `Handler` class, but it's pretty simple. First, we need to set up some classes for SQLAlchemy.

```Python
# database.py
from enum import StrEnum

from sqlalchemy import Column, DateTime, Enum, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base

DB_ENGINE = create_engine("sqlite:///example.db")


class LogLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


Base = declarative_base()


class Record(Base):
    __tablename__ = "python_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    file_name = Column(String(50), nullable=False)
    function_name = Column(String(100), nullable=False)
    log_level = Column(Enum(LogLevel), nullable=False)
    log_message = Column(String(1000), nullable=False)
    timestamp = Column(DateTime, nullable=False)


Base.metadata.create_all(DB_ENGINE)

```

Here, we're using a local SQLite database. In reality, you will need to edit the connection string to your database with the proper authentication methods. The `LogLevel` enum is just a helper class that ensures that we only accept Python's log level names. Now we can set up the custom log handler:

```Python
# logger.py
import datetime as dt
from logging import Handler, Logger, LogRecord, getLevelName, getLogger

from sqlalchemy.orm import Session

from database import DB_ENGINE, Record


class SQLHandler(Handler):
    def __init__(self, level: int | str = 0) -> None:
        self._sesh = Session(DB_ENGINE)
        super().__init__(level)

    def emit(self, record: LogRecord) -> None:
        """
        Custom emit function to send log record to SQL database.

        Assumes the target SQL table has the following schema:
            file_name: name of .py file that triggered the log record.
            function_name: function that emitted the log record.
            log_level: one of DEBUG, INFO, WARNING, ERROR, CRITICAL.
            message: log message.
            timestamp: timestamp of log message
        """
        new_record = Record(
            file_name=record.filename,
            function_name=record.funcName,
            log_level=getLevelName(record.levelno),
            log_message=record.getMessage(),
            timestamp=dt.datetime.now(),
        )

        self._sesh.add(new_record)
        self._sesh.commit()


def get_sql_logger(logger_name: str, log_level: str | int) -> Logger:
    logger = getLogger(logger_name)
    logger.setLevel(log_level)
    handler = SQLHandler(log_level)
    logger.addHandler(handler)

    return logger
```

You can see that we're connecting to the database when we initialize the handler. Another way is to inject the depedency into the class instead of creating one at initialization. The most important part of this exercise is the custom `emit` function. As you can see, all we're doing is creating a new record in the database when we receive a new log record. It's really that simple. The `get_sql_logger` function is just for convenience. So, in the rest of the code, we can use our custom logger like so:

```Python
# main.py

import logging

from sqlalchemy.orm import Session

from database import DB_ENGINE, Record
from logger import get_sql_logger


def main() -> None:
    sql_logger = get_sql_logger("custom_logger", logging.INFO)

    sql_logger.debug("This will not be sent to SQL.")
    sql_logger.info("This will be sent to SQL.")
    sql_logger.critical("Big mistake, huge!")

    # Print all logs
    session = Session(bind=DB_ENGINE)
    records = session.query(Record).all()

    for record in records:
        print(f"{record.timestamp}: ({record.log_level}) {record.log_message}")  # noqa: T201


if __name__ == "__main__":
    main()
```

If everything is set up properly, you'll see the following outputs:
```
>>> 2026-02-11 14:48:51.326668: (INFO) This will be sent to SQL.
>>> 2026-02-11 14:48:51.328932: (CRITICAL) Big mistake, huge!
```

The code for this blog post can be found in my [blog-example repo](https://github.com/taehoonsong/blog-examples/tree/log-to-sql).

# Next steps
As I've shown in this example, setting up a logging system on SQL can be extremely easy and flexible. You can set up the table schema to only include the columns you care about. You can send the record to multiple tables across multiple databases, if you so choose. For your next Python app, I hope this encourages you to save your logs to a database for your next project. I can't count the number of times my log table saved me when diagnosing a long-running Python app on Azure. Good luck!
