---
title: Test blog
date: 2025-11-09
summary: We're testing out some math rendering here!
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

## Subtitle 2
```python
import polars as pl
from pathlib import Path

def get_df(file_path: Path) -> pl.DataFrame:
  return pl.from_csv(file_path, separator="\t")
```
### Subsubtitle
Here's a photo of me:
![Profile pic of me in 2021](../img/profile.jpeg)

# Major title 2

LINUX!
