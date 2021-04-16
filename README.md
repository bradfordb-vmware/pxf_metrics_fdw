# PXF Metrics FDW

This repo is part of Greenplum HackDay 2021.
It contains a Postgres FDW implemented with [Multicorn][0] for querying [PXF][1] metrics from `psql`.

**THIS IS A PROOF OF CONCEPT AND SHOULD NOT BE USED IN PRODUCTION ENVIRONMENT.**

## Setup Multicorn

Clone and build the following [fork][2] of Multicorn that supports compiling against GPDB 7.

```bash
git clone -b gpdb7 https://github.com/bradfordb-vmware/Multicorn.git
cd Multicorn
source $GPHOME/greenplum_path.sh
make
make install
```

Create the `multicorn` extension in your Greenplum database

```sql
CREATE EXTENSION multicorn;
```



## Install FDW

```bash
sudo python3 setup.py install
```

```sql
CREATE SERVER pxf_metrics_srv FOREIGN DATA WRAPPER multicorn
options (
  wrapper 'pxf_metrics_fdw.PxfMetricsForeignDataWrapper'
);

CREATE FOREIGN TABLE pxf_metrics (
    name character varying,
    count real
) server pxf_metrics_srv;
```

Once the foreign table is created, you can query it to see the latest PXF metric

```console
bboyle=# select * from pxf_metrics ;
        name        |     count
--------------------+---------------
 pxf.bytes.sent     | 3.5466772e+09
 pxf.fragments.sent |            28
 pxf.records.sent   | 4.0297264e+07
(3 rows)
```

<!-- References -->
[0]: https://multicorn.org/
[1]: https://github.com/greenplum-db/pxf/
[2]: https://github.com/bradfordb-vmware/Multicorn/tree/gpdb7
