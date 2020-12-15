from functools import wraps
from typing import Any, Callable, Dict, List, Set, Tuple
from timeit import default_timer as timer
from numbers import Number

from prometheus_client import Counter, Enum, Histogram, Gauge, Summary
from prometheus_client.exposition import choose_encoder
from prometheus_client import REGISTRY


def singleton(cls):
    """
    Decorator to generate a singleton, prevents
    from creating multiple instances of a class
    """
    instance = None

    def get_instance(*args, **kwargs):
        nonlocal instance
        if instance is None:
            instance = cls(*args, **kwargs)
        return instance

    return get_instance


@singleton
class PrometheusExporter(object):
    """
    PrometheusExporter is a wrapper for prometheus_client
    that lets you set export metrics from your application to
    Prometheus with ease.

    The wrapper lets you create an instance of prometheus_client
    and has methods that lets you export metrics as Counter,
    Gauge, Histogram, or Summary

    Example:
        from prometheus_exporter import PrometheusExporter

        m = PrometheusExporter(labels={"label": "value"})

        # increases the counter on each function call
        @m.counter("default_counter", "A Default Counter",
                    labels={"label": "other_value"})
        def func():
            do_something()

        # To use the function's return value as the metric value
        # set defer=True in the decorator
        #
        # Setting defer calls the function only when the /metrics
        # endpoint is called
        @m.gauge("default_gauge", "A Default Gauge", defer=True)
        def another_func():
            # sets the default_gauge metric value to the return value
            return do_something()

        # You can also create a metric to use across multiple functions
        # using enum and info
        # enum requires a set of default states and can be used to set
        # the status of a function call
        enum = m.enum("default_enum", "Enumerator metric for states",
                      states=["state 1", "state 2"])

        def enum_example():
            enum.state('state 1')
            do_something()
            enum.state('state 2')

        # info is an instance of gauge that can be used across
        # multiple functions
        info = m.info("info_metric", "An instance of Gauge")

        def set_info():
            v = do_something()
            info.set(v)

        def set_info_2():
            v = do_something_else()
            info.set(v)

        # Use the handler to generate a string containing all
        # the metrics in the registry
        # This will be the application's /metrics endpoint
        def get_metrics():
            return metrics.handle()
    """
    def __init__(self, labels: Dict[str, Any] = None,
                 registry: object = None) -> None:
        """
        Initializes an instance of PrometheusExporter

        :param labels: a dict consisting of default labels and their values
            to be set on all metrics in the registry
        :param registry: an instance of prometheus_client registry to use
        """
        self._default_labels: Dict[str, Any] = labels or {}
        # use prometheus_client registry as the default
        self.registry: object = registry or REGISTRY
        self.deferred_metrics: Set[Tuple[Callable, Callable, object]] = set()

    def handle(self, accept_header: str = None) -> str:
        """
        Handler for the metrics endpoint. Generates a string
        containing all the metrics in the registry.

        :param accept_header: the HTTP Accept header for the output metrics,
            should be set to application/openmetrics-text to generate
            openmetrics-compatible output. Defaults to None.
        """
        for fn, mfunc, metric in self.deferred_metrics:
            try:
                start = timer()
                resp = fn()
                if not isinstance(resp, Number):
                    resp = float(resp)
            except BaseException:
                raise

            if isinstance(metric, (Histogram, Summary)):
                end = max(timer() - start, 0)
                mfunc(metric, end)
            else:
                mfunc(metric, resp)

        encoder, _ = choose_encoder(accept_header)
        return encoder(self.registry)

    def counter(self, name: str = None, desc: str = None,
                labels: Dict[str, str] = None, func: Callable = None,
                defer: bool = False, **kwargs):
        """
        A wrapped instance of Counter from the prometheus_client. Use counter
        to track the number of function calls

        :param name: the name of the counter metric
        :param desc: the description for the metric
        :param labels: a dict containing labels for the metric
        :param func: a callable that will be used as an invocatio
            for the metric
        :param defer: a boolean indicating whether the metric value
            needs to be set on calling the /metrics endpoint.
        :param: kwargs: additional arguments for creating a Counter.
        """
        if func is None:
            func = lambda m, t: m.inc()

        return self.__register(Counter, func,
                               kwargs, name, desc, defer=defer,
                               labels=labels, registry=self.registry)

    def gauge(self, name: str = None, desc: str = None,
              labels: Dict[str, str] = None, func: Callable = None,
              defer: bool = False, **kwargs):
        """
        A wrapped instance of Gauge from the prometheus_client. Use gauge
        to track method invocations or use it to set metrics value based on
        the function's return value

        :param name: the name of the gauge metric
        :param desc: the description for the metric
        :param labels: a dict containing labels for the metric
        :param func: a callable that will be used as an invocation
            for the metric
        :param defer: a boolean indicating whether the metric value
            needs to be set on calling the /metrics endpoint.
        :param: kwargs: additional arguments for creating a Gauge.
        """
        if func is None:
            func = lambda m, v: m.set(v)

        return self.__register(Gauge, func,
                               kwargs, name, desc, defer=defer,
                               labels=labels, registry=self.registry)

    def histogram(self, name: str = None, desc: str = None,
                  labels: Dict[str, str] = None, func: Callable = None,
                  defer: bool = False, **kwargs):
        """
        A wrapped instance of Histogram from the prometheus_client.
        Use Histogram to track the duration of a function call

        :param name: the name of the histogram metric
        :param desc: the description for the metric
        :param labels: a dict containing labels for the metric
        :param func: a callable that will be used as an invocation
            for the metric
        :param defer: a boolean indicating whether the metric value
            needs to be set on calling the /metrics endpoint.
        :param: kwargs: additional arguments for creating a Histogram.
        """
        if func is None:
            func = lambda m, t: m.observe(t)

        return self.__register(Histogram, func,
                               kwargs, name, desc, defer=defer,
                               labels=labels, registry=self.registry)

    def summary(self, name: str = None, desc: str = None,
                labels: Dict[str, str] = None, func: Callable = None,
                defer: bool = False, **kwargs):
        """
        A wrapped instance of Summary from the prometheus_client. Use summary
        to track the duration of a function call

        :param name: the name of the summary metric
        :param desc: the description for the metric
        :param labels: a dict containing labels for the metric
        :param func: a callable that will be used as an invocation
            for the metric
        :param defer: a boolean indicating whether the metric value
            needs to be set on calling the /metrics endpoint.
        :param: kwargs: additional arguments for creating a Summary.
        """
        if func is None:
            func = lambda m, t: m.observe(t)

        return self.__register(Summary, func,
                               kwargs, name, desc, defer=defer,
                               labels=labels, registry=self.registry)

    def info(self, name: str = None, desc: str = None, value: float = 0.0,
             labels: Dict[str, str] = None) -> object:
        """
        An instance of Gauge to track ad-hoc metric values in any function

        :param name: the name of the info metric
        :param desc: the description for the metric
        :param value: the initial value to be set for the metric
        :param labels: a dict containing the labels for the metric
        """
        labels = labels or {}

        g = Gauge(name, desc, tuple(labels.keys()), registry=self.registry)
        if len(labels) > 0:
            g = g.labels(list(labels.values()))
        g.set(value)

        return g

    def enum(self, name: str = None, desc: str = None,
             states: List[str] = None,
             labels: Dict[str, str] = None) -> object:
        """
        A wrapped instance of Enum from the prometheus_client. Use enum
        to track the state of a function call

        :param name: the name of the enum metric
        :param desc: the description for the metric
        :param states: the states that the enum metric can have
        :param labels: a dict containing the labels for the metric
        """
        if states is None or not isinstance(states, (List, Tuple)):
            raise ValueError(f"Enum requires a list of states,\
                             cannot use value of type: {type(states).__name__}")

        labels = labels or {}
        e = Enum(name, desc, tuple(labels.keys()), registry=self.registry,
                 states=states)

        if len(labels) > 0:
            e = e.labels(list(labels.values()))

        return e

    def __register(self, metric_type: object, metric_fn: Callable,
                   metric_kwargs: Any, name: str, desc: str,
                   defer: bool = False, labels: Dict[str, str] = None,
                   registry: object = None):
        """
        Decorator logic for the metrics wrapper

        :param metric_type: the metric type from the prometheus_client
        :param metric_fn: the callable to use for invoking the metrics
            function. Must contain two arguments `(metric, arg)`
        :param metric_kwargs: additional params required to be passed while
            creating the metric.
        :param name: the name of the metric to be registered
        :param desc: the description of the metric to be registered
        :param defer: a boolean indicating whether the metric should be
            gathered on function call or on the /metrics endpoint
        :param labels: a dict containing the label keys and values to be
            attached to the metrics
        :param registry: the prometheus_client registry to use for the metrics
        """
        labels = self.__combine_labels(labels)
        metric = metric_type(name, desc, labelnames=tuple(labels.keys()),
                             registry=registry, **metric_kwargs)
        if len(labels) > 0:
            metric = metric.labels(list(labels.values()))

        def decorator(f):
            if defer:
                self.deferred_metrics.add((f, metric_fn, metric))

            @wraps(f)
            def inner(*args, **kwargs):
                try:
                    start = timer()
                    resp = f(*args, **kwargs)
                except BaseException:
                    raise
                if not defer:
                    end = max(timer() - start, 0)
                    metric_fn(metric, end)
                return resp
            return inner

        return decorator

    def __combine_labels(self,
                         labels: Dict[str, str] = None) -> Dict[Any, Any]:
        """
        Combines the passed labels with the default labels for the metrics
        :param labels: the dict containing the label keys and
            values to be merged with the default metric labels
        """
        labels = labels.copy() if labels else {}
        if self._default_labels:
            labels.update(self._default_labels.copy())

        return labels
