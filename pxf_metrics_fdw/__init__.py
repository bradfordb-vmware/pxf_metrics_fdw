from multicorn import ForeignDataWrapper
import requests


class PxfMetricsForeignDataWrapper(ForeignDataWrapper):

    def __init__(self, options, columns):
        super(PxfMetricsForeignDataWrapper, self).__init__(options, columns)
        self.actuator = ActuatorMetrics()
        self.columns = columns

    def execute(self, quals, columns):

        pxf_metric_names = self.actuator.list_metrics('pxf')

        for p in pxf_metric_names:
            line = {
                "name": p,
                "count": self.actuator.get_metric_count(p)
            }
            yield line

class ActuatorMetrics:

    def __init__(self, port=5888):
        self.base_url = f"http://localhost:{port}/actuator/metrics"

    def list_metrics(self, prefix):
        resp = requests.get(self.base_url)
        body = resp.json()
        return [n for n in body['names'] if n.startswith(prefix)]

    def get_metric_count(self, name):
        resp = requests.get(f"{self.base_url}/{name}")
        body = resp.json()
        # FIXME: what if none?
        return [m['value'] for m in body['measurements'] if m['statistic'] == 'COUNT'][0]

