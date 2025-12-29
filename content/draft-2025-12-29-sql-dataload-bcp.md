---
title: Load data faster into SQL with bcp
date: 2025-12-29
summary: There are many tools that load data into SQL, but bcp can probably load it faster.
---
# What even is bcp?
[bcp](https://learn.microsoft.com/en-us/sql/tools/bcp-utility?view=sql-server-ver17&tabs=windows) is a tool from Microsoft that specializes in bulk copy (hence the name) into a SQL database. It is only available as a command-line tool, which might be a downside for some. In my experience, command-line tools are the most reliable tools. bcp is also available on Linux, which makes sense given Azure's existence. I will note that the Linux version has one feature that I will talk about later that makes it better than the Windows version.

# Installation process

