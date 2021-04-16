# PXF Metrics FDW

This repo is part of Greenplum HackDay 2021.
It contains a Postgres FDW implemented with Multicorn[0] for querying PXF[1] metrics from `psql`.

**THIS IS A PROOF OF CONCEPT AND SHOULD NOT BE USED IN PRODUCTION ENVIRONMENT.**

## Setup Multicorn

```sql
CREATE EXTENSION multicorn;

CREATE SERVER pxf_metrics_srv FOREIGN DATA WRAPPER multicorn
options (
  wrapper 'pxf_metrics_fdw.PxfMetricsForeignDataWrapper'
);

CREATE FOREIGN TABLE pxf_metrics (
    name character varying,
    count real
) server pxf_metrics_srv;
```

## Install FDW

```bash
sudo python3 setup.py install
```

<!-- References -->
[0]: https://multicorn.org/
[1]: https://github.com/greenplum-db/pxf/
