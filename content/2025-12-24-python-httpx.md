---
title: Build your own API client using requests and httpx
date: 2025-12-24
summary: The `requests` module is popular for interacting with APIs on Python. You can easily check how web APIs work and build a prototype in minutes. However, it's not the most efficient use of time since the sc<Find>ript is I/O-bound. Try using `httpx` instead!
---
# Data source
For this article, I'll be using the [Federval Reserve Bank at St. Louis (FRED) API Version 1](https://fred.stlouisfed.org/docs/api/fred/). To follow along, please create an account and generate an API key. Familiarize yourself with the [FRED API Terms of Use](https://fred.stlouisfed.org/docs/api/terms_of_use.html).

# Sample code
I uploaded some example API client code to my [GitHub repo](https://github.com/taehoonsong/blog-examples/tree/requests-vs-httpx) for this blog post. Clone the repo with the following command:

```
git clone -b requests-vs-httpx https://github.com/taehoonsong/blog-examples.git ./requests-vs-httpx
```

and initialize project with (assuming you have [uv](https://github.com/astral-sh/uv) installed)

```
cd requests-vs-httpx && uv sync
```

if you're just using `pip`

```
cd requests-vs-httpx && pip install -r requirements.txt
```

The main branch doesn't have anything, so make sure to include `-b requests-vs-httpx` to specify the branch. Once cloned, add a `.env` file inside the `requests-vs-httpx` folder with the your FRED API key. The `.env` file should look like this:

```
FRED_API=<YOUR API KEY HERE>
```

# Synchronous API client
You're assigned to write a Python script that retrieves some economic data. For sake of this example, let's say the data provider limits the API by only allowing one month of data per request. Many real-world APIs have some sort of rate limit, so I put this artificial limit instead. Based on a quick Google search, you find out that the `requests` module is the go-to tool for handling web requests on Python. You find a helpful repo with an [example synchronous API client](https://github.com/taehoonsong/blog-examples/blob/requests-vs-httpx/src/01-requests.py). Let's test this out.

```
>>> uv run 01-requests.py
>>> `requests` took: 2.8 seconds to download data from 2025-01-01 to 2025-12-31.
```

This result will vary depending on the state of the API and your internet connection, but this doesn't seem too bad at all. Only 2.8 seconds to download 12 months of data. You can simply build your example based on this script and be done with the project. However, you know you can make the script more efficient if you use asynchronous (async) code.

# What's wrong with synchronous code?
There's nothing inherently wrong with synchronous code. Depending on the task, you may want the code to be strictly synchronous. In many cases, however, your computer ends up wasting a lot of time waiting for something to happen. This mainly occurs when operations are I/O-bound. Web requests are a perfect example of this. In the synchrounous example above, each request took about 230ms on average, which may be plenty fast depending on your goals. However, after the first API request, each subsequent request doesn't go out until the previous request gets a response. This means if there's an issue in one of the requests, all subsequent requests will be waiting.

# Asynchronous API client
The better way to do this would be to submit all requests at once and wait for the responses as they come in. This is what async code allows us to do. Here's an [example async API client](https://github.com/taehoonsong/blog-examples/blob/requests-vs-httpx/src/02-httpx.py). The trade-off is that you have to use `asyncio` to invoke async code and there are specific rules about what you can and cannot use. For example, you cannot simply pass a list or range to an asynchronous for loop because Python cannot guarantee the order of operations. So, I have to generate the list of parameters first and pass that to the client. But, the benefit is clear:

```
>>> uv run 02-httpx.py
>>> `httpx` took: 0.5 seconds to download data from 2025-01-01 to 2025-12-31.
```

That's nearly an six-fold reduction in time. The difference will be more apparent when you're dealing with even more requests.

# What should I use?
This depends on the scope of your project. If you're making a few web requests and slightly longer run times are acceptable, using synchronous code makes sense. It's also much easier to follow the code. I will note that `httpx` also supports synchronous clients, so there's no need to use `requests`. When you look at the [synchronous client example](https://github.com/taehoonsong/blog-examples/blob/requests-vs-httpx/src/01-requests.py), you'll notice that I'm using f-strings to pass in the API parameters, whereas in the [async client example](https://github.com/taehoonsong/blog-examples/blob/requests-vs-httpx/src/02-httpx.py), I'm passing a dictionary to the client. This is only one of the niceties that `httpx` has over `requests`.

Now, if you're making hundreds of web requests, each millisecond starts to matter. If you haven't tried out writing asynchronous code, I highly encourage you to try. Even though it's a bit more work to set up the client, the time savings may be worth it.
