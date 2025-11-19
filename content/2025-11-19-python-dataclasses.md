---
title: Reduce boilerplate code with Python dataclasses
date: 2025-11-19
summary: Setting up a class just to store some data can be annoying because of all the boilerplate code required. Let's look at some solutions to make your life a little easier.
---
# Motivation
You made a simple program that uses a rectangle. You could specify the length and width for each function that is going to use the rectangle. But, you're a smart programmer. You're going to wrap them in a dictionary or a class so you can easily move the entire rectangle data in one argument. Let's say you would prefer a class because maybe there's a couple of helpful utility functions to include with the data. In regular Python, it may look something like this:

```python
class Rectangle:
  def __init__(self, length: float, width: float) -> None:
    self.length = length
    self.width = width

  @property
  def area(self) -> float:
    return self.length * self.width

  @property
  def perimeter(self) -> float:
    return 2 * (self.length + self.width)
```

Simple enough. But later, you realize that the `print` method only shows the memory address of the object, which isn't helpful at all. So you implement a `__repr__` method to your class. You also need to compare two rectangles, so you implement the `__eq__` method as well.

```python
from __future__ import annotations

class Rectangle:
  ...

  def __eq__(self, other: "Rectangle") -> bool:
    return self.length == other.length & self.width == other.width

  def __repr__(self) -> str:
    return f"Rectangle(length={self.length}, width={self.width})"
```

Wait, you also need to check if length and width are non-zero positive numbers. Let's add a check in the init stage. The final class looks like:

```python
from __future__ import annotations

class Rectangle:
  def __init__(self, length: float, width: float) -> None:
    if length <= 0:
      raise ValueError("Length must be positive.")

    if width <= 0:
      raise ValueError("Width must be positive.")

    self.length = length
    self.width = width

  @property
  def area(self) -> float:
    return self.length * self.width

  @property
  def perimeter(self) -> float:
    return 2 * (self.length + self.width)

  def __eq__(self, other: "Rectangle") -> bool:
    return self.length == other.length & self.width == other.width

  def __repr__(self) -> str:
    return f"Rectangle(length={self.length}, width={self.width})"
```

If your entire project has this one class, this doesn't seem so bad. However, it's likely that you're going have more classes. If not now, then probably later. What about a Circle class or a Cube class? Will you have to write all this boilerplate every time you make a new object for your program? If you read the title of the blog, you know the answer is: **No**.

# Dataclasses
Python dataclasses offer a easy to use decorator that can handle most of your dataclass needs. For example, the Rectangle class from above can be written as:

```python
from dataclasses import dataclass

@dataclass
class Rectangle:
  length: float
  width: float

  def __post_init__(self) -> None:
    if length <= 0:
      raise ValueError("Length must be positive.")

    if width <= 0:
      raise ValueError("Wdith must be positive.")

  @property
  def area(self) -> float:
    return self.length * self.width

  @property
  def perimeter(self) -> float:
    return 2 * (self.length + self.width)
```

You can see that we no longer need to have the `__init__`, `__eq__`, and `__repr__` methods, leaving only the class specific details for you to implement. The decorator also took care of `__hash__`, which we forgot to implement in the original Rectangle class. These methods are required for certain features to work, but can be tedious to implement if all you want is a simple class to hold some data. The `dataclasses` module exists to solve this exact issue. I hope it's not difficult to see why dataclasses can be so helpful in your projects.

# Alternatives
## Built-in alternatives
What if you don't need properties? Well, then I would highly suggest `NamedTuple` or `TypedDict`, depending on your use case. Let's convert the Rectangle class into each of these.

```python
from typing import NamedTuple, TypedDict

class T_Rectangle(NamedTuple):
  length: float
  width: float

a = T_Rectangle(2, 5)
print(a)
> T_Rectangle(length=2, width=5)

class D_Rectangle(TypedDict):
  length: float
  width: float

b = D_Rectangle(length=3, width=6) # must use keyword arguments
print(b)
> { 'length': 3, 'width': 6 }
```

You can immediately notice that `TypedDict` is very different just by looking at the `print` statement. That's because, under the hood, it's just a regular Python dictionary. On the other hand, `NamedTuple` looks pretty similar to our Rectangle class and for simple objects `NamedTuple` might be better than a dataclass. You can even add the `area` and `perimeter` methods to the `NamedTuple` object. However, there are caveats.

1. Because `NamedTuple` is a `tuple` in disguise, you cannot modify values after initialization. Depending on what you want to do, this may be good or bad. To freeze the values for a dataclass object, you can use `@dataclass(frozen=True)`.
2. It's not "pythonic" to add methods to a `NamedTuple` class, even though Python lets you. If you really need the extra performance of a `NamedTuple` over a dataclass, maybe Python isn't the correct language for your project.

## Pydantic
One of the most popular alternatives to dataclasses is the [pydantic package](https://github.com/pydantic/pydantic). It provides much more granular control over the class, such as continuous validation of data. A regular Python dataclass can validate data at the initialization stage, but Pydantic allows you to validate data as the attribute is updated. So, this package is the go-to solution when building/dealing with APIs. Pydantic's capabilities are too much to cover in this blog post, but I highly recommend readers to check if out if you need strict control over every piece of data in your project. Here's what the Rectangle class would look like using pydantic:

```python
from pydantic import ConfigDict, PositiveFloat
from pydantic.dataclasses import dataclass


@dataclass(config=ConfigDict(validate_assignment=True))
class Rectangle:
    length: PositiveFloat
    width: PositiveFloat

    @property
    def area(self) -> float:
        return self.length * self.width

    @property
    def perimeter(self) -> float:
        return 2 * (self.length + self.width)
```

The `validate_assignment=True` tells pydantic to revalidate the data when a new value is assigned. This ensures that both `length` and `width` are positive. You can implement this without pydantic, using getters and setters. However, this allows you to focus on the implementation details over data validation. However, because we're dealing with Python, you can override anything you want. For example, we can bypass Pydantic's validator by using `__setattr__`:

```python
r = Rectangle(length=5, width=10)

object.__setattr__(r, "length", -1)
print(r)

> Rectangle(length=-1, width=10.0)
```

But, if you're doing this, I hope you know what you're doing because you're going against the intended design of the class.

# Conclusion
Python being Python, there are many ways to solve one problem. In order to reduce boilerplate code for data-centric objects, start with the built-in `dataclasses` module and see if it meets all of your needs. You could look into `NamedTuple` or `TypedDict`, if you think a regular dataclass is unnecessary. However, if you find yourself trying to implement more checks into your dataclass, maybe it's time to use `pydantic` and let it handle all the boilerplate code for you. It might be more upfront work, but it can save you tons of time by removing unnecessary debugging and testing down the road.
