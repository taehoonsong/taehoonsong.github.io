---
title: Test blog 3
date: 2024-09-10
summary: Let's test some code rendering!
---

# This is a blog post
## Subtitle 1
Hello world! Let's use some math! $a^2+b^2=c^2$.

What about some Euler's identity:

```math
e^{\pi i}+1 = 0
```

Or **Cauchy-Schwarz Inequality**:

$$\left( \sum_{k=1}^n a_k b_k \right)^2 \leq \left( \sum_{k=1}^n a_k^2 \right) \left( \sum_{k=1}^n b_k^2 \right)$$


Dorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

## Subtitle 2
```python
import polars as pl
from pathlib import Path

def get_df(file_path: Path) -> pl.DataFrame:
  return pl.from_csv(file_path, separator="\t")
```

```sql
declare @criterion as [int] = 2;

with tmp (id, sort_order) as (
  select id, row_number over (partition by group_id order by tran_date)
  from trx
  where tran_date between dateadd(month, -2, getdate()) and getdate()
)
select t1.id
from table1 as t1
inner join tmp on tmp.id = t1.id
where tmp.sort_order = @criterion
```