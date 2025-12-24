---
title: Easy asynchronous requests using httpx
date: 2025-12-24
summary: The requests module is popular for interacting with APIs on Python. However, this is unnecessarily slow due to its synchronous nature. Try using httpx instead for your next project!
---
# Motivation
You need some data from an API and you're able to quickly write a working prototype using Python that retrieves data from this API. While it was fine for testing, you realize the code is not fast enough for production. You've heard that asynchronous (async) functions are better for performance when dealing with I/O-bound operations. Since you already built a prototype that works, you'd also like to not change too much. You don't want to rewrite those pesky unit tests.

# Data source
For this article, I'll be using the [Federval Reserve Bank at St. Louis (FRED) API Version 1](https://fred.stlouisfed.org/docs/api/fred/). To follow along, please create an account and generate an API key. Familiarize yourself with the [FRED API Terms of Use](https://fred.stlouisfed.org/docs/api/terms_of_use.html).

# Synchronous code

