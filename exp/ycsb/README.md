# Official YCSB with RocksDB 11.8.1 (KSC2026 RocksDB/YCSB-A experiment)

The senior asked for the official YCSB and the latest RocksDB. The upstream rocksdb binding pins rocksdbjni 6.2.2 and
has no way to turn the write-ahead log off, so it is patched (`ycsb-rocksdb-11.8.1.patch`, 4 files):

- `pom.xml`: `rocksdb.version` 6.2.2 → 11.8.1 (RocksJava from Maven Central, same RocksDB release as `~/jsw/rocksdb`)
- `RocksDBClient.java`: `OptionsUtil.loadOptionsFromFile` uses the `ConfigOptions` overload (the old one is gone in
  RocksJava 11.x); new properties `rocksdb.disablewal` and `rocksdb.sync` set `WriteOptions` for every put/delete
- `RocksDBOptionsFileTest.java`: same API change in the test; `rocksdb/README.md`: the two properties

Build (2026-10-24, OpenJDK 17.0.20.1, Maven 3.8.7; binding tests pass, 5/5):

```bash
git clone https://github.com/brianfrankcooper/YCSB.git && cd YCSB
git checkout ae02b31f                      # master of 2026-10-20
git am ../nvmevirt/exp/ycsb/ycsb-rocksdb-11.8.1.patch
mvn -B -pl site.ycsb:rocksdb-binding -am clean package
tar -xzf rocksdb/target/ycsb-rocksdb-binding-0.18.0-SNAPSHOT.tar.gz -C ../ycsb-dist
```

Run (from the unpacked directory): `java -cp "lib/*" site.ycsb.Client -load|-t -db site.ycsb.db.rocksdb.RocksDBClient
-P workloads/workloada -p rocksdb.dir=<db> -p rocksdb.optionsfile=<ini> -p rocksdb.disablewal=true|false ...`.
The options file must contain `[CFOptions "usertable"]` and `[TableOptions/BlockBasedTable "usertable"]` sections
(YCSB stores its records in the column family `usertable`); `block_size` and `block_cache` go there.
