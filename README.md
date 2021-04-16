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
    name text,
    count real,
    server text[],
    segment int[],
    profile text[],
    "user" text[]
) server pxf_metrics_srv;
```

Once the foreign table is created, you can query it to see the latest PXF metric

```console
bboyle=# select * from pxf_metrics ;
        name        |     count     |   server   | segment |  profile   |   user
--------------------+---------------+------------+---------+------------+----------
 pxf.bytes.sent     | 3.5466772e+09 | {hdfs_hdp} | {0,1,2} | {hdfs:csv} | {bboyle}
 pxf.fragments.sent |            28 | {hdfs_hdp} | {0,1,2} | {hdfs:csv} | {bboyle}
 pxf.records.sent   | 4.0297264e+07 | {hdfs_hdp} | {0,1,2} | {hdfs:csv} | {bboyle}
(3 rows)
```

You can select a subset of the columns

```console
bboyle=# select name, count from pxf_metrics;
        name        |     count
--------------------+---------------
 pxf.bytes.sent     | 3.5466772e+09
 pxf.fragments.sent |            28
 pxf.records.sent   | 4.0297264e+07
(3 rows)
```

You can filter by tags (e.g., `server`, `segment`, etc.)

```console
bboyle=# SELECT * FROM pxf_metrics WHERE segment @> '{0}' ;
        name        |     count     |   server   | segment |  profile   |   user
--------------------+---------------+------------+---------+------------+----------
 pxf.bytes.sent     | 1.2079597e+09 | {hdfs_hdp} | {0}     | {hdfs:csv} | {bboyle}
 pxf.fragments.sent |             9 | {hdfs_hdp} | {0}     | {hdfs:csv} | {bboyle}
 pxf.records.sent   | 1.3723606e+07 | {hdfs_hdp} | {0}     | {hdfs:csv} | {bboyle}
(3 rows)
```

You can combine filters across different colums

```console
bboyle=# SELECT * FROM pxf_metrics WHERE segment @> '{0}' AND name LIKE 'pxf.bytes%';
      name      |     count     |   server   | segment |  profile   |   user
----------------+---------------+------------+---------+------------+----------
 pxf.bytes.sent | 1.2079597e+09 | {hdfs_hdp} | {0}     | {hdfs:csv} | {bboyle}
(1 row)
```

You can filter across  multiple tags

```console
bboyle=# SELECT * FROM pxf_metrics WHERE segment @> '{0}' AND profile @> '{hdfs:text}';
        name        |    count     |   server   | segment |   profile   |   user
--------------------+--------------+------------+---------+-------------+----------
 pxf.bytes.sent     | 5.410815e+08 | {hdfs_hdp} | {0}     | {hdfs:text} | {bboyle}
 pxf.fragments.sent |            5 | {hdfs_hdp} | {0}     | {hdfs:text} | {bboyle}
 pxf.records.sent   | 6.146536e+06 | {hdfs_hdp} | {0}     | {hdfs:text} | {bboyle}
(3 rows)
```

<!-- References -->
[0]: https://multicorn.org/
[1]: https://github.com/greenplum-db/pxf/
[2]: https://github.com/bradfordb-vmware/Multicorn/tree/gpdb7
