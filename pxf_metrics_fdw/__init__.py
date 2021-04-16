import logging
from multicorn import ForeignDataWrapper
from multicorn.utils import log_to_postgres
import requests


class PxfMetricsForeignDataWrapper(ForeignDataWrapper):

    def __init__(self, options, columns):
        super(PxfMetricsForeignDataWrapper, self).__init__(options, columns)
        self.actuator = ActuatorMetrics()
        self.columns = columns

    def execute(self, quals, columns):

        pxf_metric_names = self.actuator.list_metrics('pxf')
        tag_filters = list(self.get_tag_filters_from_quals(quals))
        log_to_postgres(f"quals {quals}, columns {columns}, tag filters {tag_filters}", logging.DEBUG)

        for p in pxf_metric_names:
            line = self.actuator.get_metric_data(p, tag_filters)
            line["name"] = p
            yield line

    def get_tag_filters_from_quals(self, quals):
        for q in quals:
            if q.operator == "@>":
                yield {"tag": q.field_name, "value": q.value[0]}

class ActuatorMetrics:

    def __init__(self, port=5888):
        self.base_url = f"http://localhost:{port}/actuator/metrics"

    def list_metrics(self, prefix):
        resp = requests.get(self.base_url)
        body = resp.json()
        return [n for n in body['names'] if n.startswith(prefix)]

    def get_metric_data(self, name, tag_filters):
        resp = requests.get(f"{self.base_url}/{name}", params=[self.format_tag_filter(t) for t in tag_filters])
        body = resp.json()
        metric_data = self.unnest_tags(body)
        metric_data["count"] = self.get_metric_count(body)

        # need to add a tag for each tag filter
        for t in tag_filters:
            metric_data[t["tag"]] = [t["value"]]

        return metric_data

    def get_metric_count(self, resp_body):
        return [m['value'] for m in resp_body['measurements'] if m['statistic'] == 'COUNT'][0]

    def unnest_tags(self, resp_body):
        return {t["tag"]: t["values"] for t in resp_body["availableTags"]}

    def format_tag_filter(self, tag_filter):
        return ("tag", f"{tag_filter['tag']}:{tag_filter['value']}")
