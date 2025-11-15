---
title: Did you assume independence?
date: 2021-05-30
summary: Many statistical formulas and theorems assumes or requires statistical independence. But what if you can't assume independence?
---
# Introduction
Many popular statistical procedures, such as hypothesis testing and linear regression, include the assumption of independence. Assuming independence makes the math much simpler and can be a reasonable assumption depending on how the data was collected. Even though I lumped them together, hypothesis tests and regression have different assumptions of independence. For example, a t-test will assume that observations are randomly selected from a t-distribution, specifically a simple random sample. On the other hand, regression generally assumes that the residuals are independent from each other, meaning after accounting for the effects of all predictor variables.

You might be familiar with looking at diagnostic plots such as Q-Q plots and residual plots after a regression model is fit to check the validity of these assumptions. Well, have you considered how to check your independence assumption for hypothesis testing? Did you just *assume* independence? In this post, I’ll go over some simple nonparametric methods to test for independence in hypothesis testing. Nonparametric tests are useful when you don’t want to have any assumptions about the distribution of your observations or when you simply don’t know.

# Runs Test
The runs test is a nonparametric statistical test that checks if a sequence of observations are independent. The idea behind it is quite simple: you can calculate the expected number of runs (consecutive observations with the same outcome) and see how likely or unlikely that outcome is if the observations are truly random and independent. If the number of runs is too low, the observations might be positively correlated; if the number of runs is too high, then the observations may be negatively correlated.

## Binary random variable
Let’s start with a binary (or Bernoulli) random variable. Consider the following sequence of 20 outcomes:

```math
\begin{gathered}
1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1
\end{gathered}
```

In the above sequence, there are 5 runs, 3 of which are 1’s and the others are 0’s. Now, what’s the expected number of runs for a 20-element-long sequence of binary outcomes? Let $I_k$ be an indicator variable that is equal to 1 if a new run starts in position $k$ and 0 otherwise. This suggests that $I_k=1$ when the element in the $(k-1)$-th position is different from the $k$-th element. If the $(k-1)$-th element and the $k$-th are the same, then a run would not start at position $k$ by definition. This means that the number of runs, $R$, can be written as

```math
\begin{gathered}
R=1+I_2+I_3+\cdots+I_n
\end{gathered}
```

where $n= n_1 + n_2$ and $n_1$ and $n_2$ represent the number of 1’s and 0’s, respectively. There is a 1 because there is always at least 1 run even if all the element are the same and there are no new runs in the sequence. Then the probability that $I_k=1$ is:

```math
\begin{aligned}
P(I_k=1)&=\frac{\binom{2}{1}\binom{n-2}{n_1-1}}{\binom{n}{n_1}}\\
\\
&=\frac{\frac{2(n-2)!}{(n_1-1)![n-2-(n_1-1)]!}}{\frac{n!}{n_1!(n-n_2)!}}\\
\\
&=\frac{\frac{2(n-2)!}{(n_1-1)!(n_2-1)!}}{\frac{n!}{n_1!n_2!}}\\
\\
&=\frac{2n_1n_2}{n(n-1)}
\end{aligned}
```

Notice that this is also the expected value of $I_k$ because it is a binary variable. Let’s dissect the first fraction to understand why this is the correct probability. In the denominator, $$\binom{n}{n_1}$$ represents the number of ways you can arrange 1’s from the total number of elements. Since the location of 0’s depend on where the 1’s are, we cover all possible arrangements of all elements. In the numerator, $$\binom{2}{1}$$ represents the number of ways you can arrange the 0 and 1 in the $k$-th position to start a new run so that $I_k=1$. Either you have a 1 in the $(k-1)$-th position and a 0 in the $k$-th position, or you have a 0 in the $(k-1)$-th position and a 1 in the $k$-th position. You have to choose one element out of two possibilities (0 or 1). Then, $$\binom{n-2}{n_1-1}$$ is the number of ways to arrange the others. You’ve already used up two elements from the total (hence $n-2$) because you know there’s a new run in position $k$ and you used up a single 1 from the total number of 1’s (hence $n_1-1$). Now we can calculate the expected number of runs:

```math
\begin{aligned}
E[R] &= E[1+I_2+\cdots+I_n]\\
\\
&= 1 + (n-1)E[I_k]\\
\\
&= 1 + (n-1)\frac{2n_1n_2}{n(n-1)}\\
\\
&=1+\frac{2n_1n_2}{n}
\end{aligned}
```

The variance of $R$ is a bit more involved, but it comes out to:

```math
\begin{aligned}
Var[R] &= Var[1+I_2+I_3+\cdots+I_n]\\
\\
&= Var[I_2+I_3+\cdots+I_n]\\
\\
&= \sum_{k=2}^n Var[I_k] + \sum_{k=2}^n \sum_{j\neq k} Cov[I_j,I_k]\\
\\
&=(n-1)p-(n-1)^2p^2+\sum_{k=2}^n \sum_{j\neq k}E[I_jI_k]\\
\\
&=(n-1)p-(n-1)^2p^2+(n-2)p+2(n_1-1)(n_2-1)p\\
\\
&=\frac{2n_1n_2(2n_1n_2-n)}{n^2(n-1)}\\
\\
&=\frac{(E[R]-1)(E[R]-2)}{n-1}
\end{aligned}
```

where $2 \leq j \leq n$. Try deriving this result for yourself. You should breakout $E[I_jI_k]$ into two scenarios: (1) $j=k\pm1$ and (2) $j\neq\pm1$. Now that you have the expected number of runs, you can compare it to the observed number of runs to see how likely the observed number of runs is. You can calculate the exact p-value:

```math
\begin{aligned}
P(|R-E[R]| \geq r) &= P(R-E[R] \geq r) \cup P(R-E[R] \leq -r)\\
\\
&=P(R \geq r + E[R]) \cup P(R \leq E[R] -r)
\end{aligned}
```

or use the following Normal approximation:

```math
\text{two-sided p-value} =
\begin{cases}
2\Phi\left(\frac{r + 0.5 - E[R]}{\sqrt{Var[R]}}\right), &r > E[R]\\
\\
2\Phi\left(\frac{E[R]+ 0.5 -r}{\sqrt{Var[R]}}\right), &r \leq E[R]
\end{cases}
```

where $r$ is the observed number of runs and $\Phi$ is the cumulative distribution function of a standard Normal distribution.

## Non-binary random variable
What if your random variable is a numerical? Well, you can dichotomize your numerical observations by checking if they are above or below the median. Observations equal to the median are omitted in this case.

# Rank von Neumann Test
Yet another test of randomness is called the rank von Neumann test. As you can tell from the name, this test uses ranks. Suppose that $X_i$ where $i \in \{1,2,\dots,n\}$ are independent and identically distributed (i.i.d.) continuous random variables with mean $\mu$ and variance $\sigma^2$. If $X_i$’s are truly i.i.d.,

```math
E\left[\sum_{i=1}^{n-1}[rank(X_i) - rank(X_{i+1})]^2 \right] = \frac{(n-1)(n^2+n)}{6}
```

If there are no ties in the data (guaranteed if the random variables are continuous),

```math
\begin{aligned}
\sum_{i=1}^n\left[ rank(X_i) - \overline{rank(X)}\right]^2 &= \sum_{i=1}^n\left[rank(X_i) - \frac{n+1}{2}\right]\\
\\
&= \sum_{i=1}^n \left[i - \frac{n+1}{2} \right]^2 \\
\\
&=\frac{(n-1)(n^2+n)}{12}
\end{aligned}
```

Therefore, the test statistic $V$:

```math
V = \frac{\sum_{i=1}^{n-1}[rank(X_i) - rank(X_{i+1})]^2}{\sum_{i=1}^n\left[ rank(X_i) - \overline{rank(X)}\right]^2}
```

has an expectation of 2 if $X_i$’s are i.i.d.

```math
E[V] = E\left[\frac{\sum_{i=1}^{n-1}[rank(X_i) - rank(X_{i+1})]^2}{\sum_{i=1}^n\left[ rank(X_i) - \overline{rank(X)}\right]^2} \right]= \frac{\frac{(n-1)(n^2+n)}{6}}{\frac{(n-1)(n^2+n)}{12}} = 2
```

Under the null hypothesis that the $X_i$’s are i.i.d., the distribution of $B=\frac{V}{4}$ can be approximated by a Beta distribution where both shape parameters are

```math
\alpha = \frac{1}{2}\left[\frac{5n(n+1)(n-1)^2}{(n-2)(5n^2-2n-9)}-1\right]
```

If you’d rather stick to $V$, the distribution of $V$ can be approximated by a Normal distribution with mean 2 (remember that $E[V]=2$), and variance

```math
\frac{4(n-2)(5n^2-2n-9)}{5n(n+1)(n-1)^2}
```

# Conclusion
There are other tests of randomness but these are the popular nonparametric tests. These may look intimidating at first, but the underlying principles are fairly simple. Additionally, the R package `randtests` have many nonparametric tests, including the ones introduced in this post (note that the rank von Neumann test is listed as the Bartels rank test in the `randtests` package). I hope you stop just assuming independence, as violation of this assumption can seriously affect the validity of your conclusions.
