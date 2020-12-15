from flask import Flask
from prometheus_exporter import PrometheusExporter
from random import random
from time import sleep

app = Flask(__name__)

# create an instance of the metrics exporter
# pass labels={'label': 'value'} to add default labels
# to all metrics
metrics = PrometheusExporter()
# an instance of info, which is a wrapper over Gauge
# can be used to set metric values across multiple functions
i = metrics.info("some_informative_metric", "Test Information Metrics", labels={'label': 'value'})
# enum can be used to set application state across functions or
# to set the state of a function call
e = metrics.enum("enum_metrics", "Test Enum Metrics", states=['running', 'stopped'])

@app.route("/", methods=["GET"])
def root():
    return """<pre>
The following endpoints are defined:
/gauge: a deferred gauge metric that runs only when /metrics is called,
        otherwise just prints a random value
/multiple: an endpoint with multiple metric decorators set: info, counter, and gauge
        The info metric sets a random value
        The counter metric counts the number of function calls
        The gauge metric stores the time taken for the current function call
/enum: an enum metric that shows the state of the function call
        The function takes 15 seconds to execute, and the metric state changes
        from running to stopped when the function has completed executing
        Go to /metrics in another tab when this endpoint is hit
/metrics: aggregates all the metrics created within the application and displays them
</pre>"""

@app.route("/gauge")
# adds a gauge metric to the function
# defer makes sure that the function is called only
# when the /metrics endpoint is called
@metrics.gauge("test_defer_gauge", "A Gauge metric that runs when metrics endpoint is called", defer=True)
def defer_gauge_test():
    # set the state
    # defer is also used to set the function's return
    # value as the metric value
    return str(random())

@app.route("/multiple")
# look ma, multiple decorators!
# counters can be added to track the number of function calls
# call the /multiple endpoint and then visit the /metrics endpoint
# to see the test_counter increment
@metrics.counter("test_counter", "Test Metric Counter")
# since no defer is specified, the gauge metric will execute only
# when the /multiple endpoint is called
# the gauge metric will contain the function execution time
@metrics.gauge("test_gauge", "A Gauge metric that executes only when the function is called")
def gauge_test():
    # set the value for the info metric
    i.set(random())

    # the return value is irrelevant to the metrics
    # since defer is not set to True
    return str(random())

@app.route("/enum")
def enum_test():
    # let's also try setting the enum metric
    e.state('running')
    sleep(10) # visit the /metrics endpoint here
    e.state('stopped')

    return "Done!"

# the endpoint which will serve the metric data
@app.route('/metrics')
def l():
    # handle() generates the metric data from the registry
    # it also calls all the deferred metric functions
    return metrics.handle().decode('utf-8').replace("\n", "<br>")

app.run(port=3000)
