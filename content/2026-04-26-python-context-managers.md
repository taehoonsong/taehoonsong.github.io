---
title: Context managers in Python
date: 2026-04-26
summary: What are context managers and when should you use them? Let's explore.
---
# What is a context manager?
You've probably seen this pattern before:

```python
with open("data.txt", "r") as f:
    content = f.read()
```

The `with` statement here is using a **context manager**. A context manager is any object that implements two dunder methods: `__enter__` and `__exit__`. When Python hits the `with` block, it calls `__enter__` to set things up and `__exit__` to tear things down, even if an exception is raised inside the block.

So in the example above, `open()` returns a file object that acts as a context manager. After the `with` block exits (normally or due to an error), the file is automatically closed. No need to call `f.close()` yourself.

# When should you use one?
Context managers shine whenever you have a **setup and teardown** pattern. The classic examples are:

- Opening and closing files
- Acquiring and releasing database connections
- Locking and unlocking threads
- Starting and stopping a timer

The key insight is that the teardown **must** happen regardless of whether the code inside succeeds or fails. Without a context manager, you'd need a `try/finally` block:

```python
f = open("data.txt", "r")
try:
    content = f.read()
finally:
    f.close()
```

This works, but it's verbose and easy to forget. A context manager handles this for you automatically and keeps your code clean.

# Is there a downside?
For simple one-off operations, a context manager can feel like overkill. If you're just reading a small file and you know it won't fail, the mental overhead of thinking about resource management may not be worth it.

Writing a *custom* context manager also requires a bit of boilerplate. You either need to implement a class with `__enter__` and `__exit__`, or use the `contextlib.contextmanager` decorator. Neither is difficult, but it's more code than doing things manually. If you only need the setup/teardown logic in one place, it might not be worth extracting into a context manager.

That said, in most real-world code, the benefits far outweigh the costs. Resource leaks, especially for unclosed database connections, are notoriously hard to debug. Context managers make them nearly impossible to introduce accidentally.

# Examples
## Using contextlib to wrap a function
In my [previous post on mssql-python](./2026-04-14-mssql-python.md), I was manually commiting and closing the connection. In reality, here's how you would do it:

```python
from collections.abc import Generator
from contextlib import contextmanager

import mssql_python as mssql

connection_string = "SERVER=<server>;DATABASE=<db>;Authentication=ActiveDirectoryDefault;Encrypt=yes;"

@contextmanager
def sql_connection(connection_string: str, **kwargs) -> Generator[mssql.Connection]:
  conn = mssql.connect(connection_string, **kwargs)

  try:
    yield conn
  except mssql.exceptions.Exception as e:
    # Handle specific exceptions and use better logging in production code
    print(e)
    c.rollback()
  finally:
    conn.commit()
    conn.close()

with sql_connection(connection_string) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
```

When the `with` block exits, the connection is automatically committed and closed. If an exception occurs, the transaction is rolled back.

## Writing a custom context manager class
Let's say you want to time how long a block of code takes. You can write a class with `__enter__` and `__exit__`:

```python
import time

class Timer:
    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed = time.perf_counter() - self.start
        print(f"Elapsed: {self.elapsed:.4f}s")
        return # return True if you want to suppress any errors

with Timer():
    time.sleep(1.5)

> Elapsed: 1.5003s
```

The `__exit__` method receives information about any exception that occurred.

# Conclusion
Context managers are one of those Python features that make your code both safer and easier to read. Whenever you find yourself writing a `try/finally` block to ensure cleanup happens, that's a signal to reach for a context manager instead. For simple cases, `contextlib.contextmanager` is your best friend. It lets you define the setup and teardown in a single function without any class boilerplate. For more complex cases where you need to inspect or handle exceptions at teardown, a class with `__enter__` and `__exit__` gives you full control.
