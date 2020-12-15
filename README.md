# Prometheus Exporter

A wrapper over Python [`prometheus_client`](https://github.com/prometheus/client_python) that lets you add metrics to any Python application in an instant using Python function decorators.

## Why?

The `prometheus_client` library is pretty cool, but it also requires you to write more than a couple of lines to get started with exporting metrics. This library is a wrapper that aims to reduce the effort to export metrics from any Python application. With this library, a developer ends up just adding a decorator to the function for which the metric needs to be exported.

## Installation

As of now, there are no packages available on PyPi. To install this library from git, run:

```sh
$ pip install git+https://github.com/Thunderbottom/prometheus-exporter-py.git
```

## Usage

Check [`example.py`](/example.py) for the usage example.

## Contributions

PRs for feature requests, bug fixes are welcome. Feel free to open an issue for bugs and discussions about the exporter functionality.

## License

```
MIT License

Copyright (c) 2020 Chinmay Pai

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
