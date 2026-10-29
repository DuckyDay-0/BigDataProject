import time
import pandas as pd
import dask.dataframe as dd
import ray
import logging

def benchmark_dask(csv_path: str):
    #Dask, calculate earnings for categories
    t0 = time.time()
    ddf = dd.read_csv(csv_path)
    res = ddf.groupby("category")["total_amount"].sum().compute()
    elapsed = time.time() - t0
    return elapsed, res

def benchmark_ray(df: pd.DataFrame):
    if not ray.is_initialized():
        ray.init(ignore_reinit_error=True, logging_level=logging.ERROR)

    t0 = time.time()
    num_cpus = 4
    chunk_size = len(df) // num_cpus
    chunks = [df.iloc[i * chunk_size : (i + 1) * chunk_size if i != num_cpus - 1 else len(df)] for i in range(num_cpus)]

    @ray.remote
    def ray_agg_worker(sub_df):
        return sub_df.groupby("category")["total_amount"].sum()

    futures = [ray_agg_worker.remote(c) for c in chunks]
    results = ray.get(futures)
    combined = pd.concat(results).groupby("category").sum()
    elapsed = time.time() - t0

    ray.shutdown()
    return elapsed, combined

def benchmark_pyspark(csv_path: str):
    #PySpark
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import sum as _sum

    t0 = time.time()
    try:
        spark = SparkSession.builder \
            .appName("BigDataCourseProject") \
            .master("local[*]") \
            .config("spark.driver.memory", "2g") \
            .config("spark.ui.showConsoleProgress", "false") \
            .getOrCreate()
    except Exception as e:
        raise RuntimeError(f"PySpark initialization failed (likely due to incompatible Java version, requires Java 17+): {e}")

    spark.sparkContext.setLogLevel("ERROR")

    sdf = spark.read.option("header", "true").option("inferSchema", "true").csv(csv_path)
    res_df = sdf.groupBy("category").agg(_sum("total_amount").alias("TotalRevenue")).toPandas()

    spark.stop()
    elapsed = time.time() - t0
    return elapsed, res_df
