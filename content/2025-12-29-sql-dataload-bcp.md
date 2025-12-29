---
title: Load data faster into SQL with bcp
date: 2025-12-29
summary: There are many tools that load data into SQL, but bcp can probably load it faster.
---
# What even is bcp?
[bcp](https://learn.microsoft.com/en-us/sql/tools/bcp-utility?view=sql-server-ver17&tabs=windows) is a tool from Microsoft that specializes in bulk copy (hence the name) into a SQL database. It is only available as a command-line (CLI) tool, which might be a downside for some. In my experience, CLI tools are the most reliable tools. bcp is also available on Linux and MacOS, which makes sense given Azure's existence. I will note that the Linux/MacOS version has one feature that I will talk about later that makes it better than the Windows version.

# Installation process
## Windows
You have to install the Microsoft Command Line Utilities for SQL Server, which is separate from the ODBC Driver. My only gripe is that I wish bcp was available via `winget`. The ODBC Driver is, so I don't see why this tool isn't included (The `Microsoft.Sqlcmd` package on `winget` does not include bcp, unfortunately). Linux and MacOS can also use their respective package managers to install bcp.

## Linux and MacOS
There's a [separate guide for installing bcp](https://learn.microsoft.com/en-us/sql/linux/sql-server-linux-setup-tools?view=sql-server-ver17&tabs=redhat-install%2Codbc-ubuntu-1804) for these operating systems.

# Advantages of using bcp
Short answer: speed. When using an ORM tool like [SQLAlchemy](https://www.sqlalchemy.org/), I was able to load a dataset with ~1 million rows and 80 fields (about 1 GiB) in about 30 minutes into a table without any indices. I have a 1Gbps upload link, so it's not a network issue. I tried using [`use_insertmanyvalues`](https://docs.sqlalchemy.org/en/21/core/connections.html#engine-insertmanyvalues), but it still took about 20 minutes. I could reduce the time to about ~10 minutes by loading into a temp table, but that increases complexity and isn't always viable depending on the size of the data.

Using bcp, however, this load took about 2 minutes. No messing around with options, just default settings. There is a catch as always. bcp will not load a file if the file and target table have the exact same schema. This means that the order of the columns matter, and if your table as an identity column that is automatically generated, the file should have an identity column too. For example, let's say the target table has an integer identity column that is auto-incremented. In order for bcp to load the file, I'll add a column of zeros to the file with the same column name. While this is a little annoying, it might be worth the hassle if you have large datasets that take forever to load otherwise.

# Disadvantages of using bcp
## Inflexible
Like I mentioned above, bcp will not work if the columns match exactly. So, when you want to load a sparse dataset where many columns are empty or nulls, it might be burdensome to generate those columns just so you can use bcp. In this case, it may be easier to use an ORM like SQLAlchemy to specify exactly which columns you intend to load.

## Authentication
This is why I still use SQLAlchemy even though I prefer the speed of bcp. At the time of writing, bcp on Windows **does not** support token-based authentication. This is non-negotiable for me. I would much rather wait a bit longer for my data to load than to pass my username and password into a CLI tool. In fact, we disable SQL logins for security and only rely on Microsoft Entra Authentication. In the documentation, bcp technically support Entra authentication with the `-G` flag. However, it does not work reliably in my work environment with MFA enabled. I wish bcp on Windows supported token based authentication, because it's much easier to implement on apps. The Linux/MacOS version of bcp supports tokens, so I know it's possible.

## Extra dependency
This might not be a huge problem, but it is annoying nonetheless. I used to rely on bcp for work when my work used to have SQL logins. I wrote a wrapper for it in Python to invoke it with the correct arguments. It worked well, but having an extra dependency that could not be easily installed through a script (at least on Windows) was a bummer for onboarding new users. Then once we moved to Entra only, I replaced bcp with a custom loader using SQLAlchemy.

# Should you use bcp?
As always, it depends. If you're using SQL logins, then why not give it a try? It's much faster than any ORM I've used. You might need to process your data file to match the target table, but the trade-off is ungodly speed. It's basically only limited by your network speed to the server. On the other hand, if you find out that Entra authentication doesn't work (like my situation), then you might be doomed, unless you can have a Linux or MacOS machine to load data. I wish I could have a Linux machine for work, but alas, we can't have everything.
