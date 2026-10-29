import os
import pandas as pd
from data_generator import generate_dataset
from mapreduce_engine import HadoopSimulator
from framework_benchmark import benchmark_dask, benchmark_ray, benchmark_pyspark
from visualizer import create_visualizations
from report_generator import generate_reports

DATA_FILE = "data/ecommerce_transactions.csv"
NUM_RECORDS = 150_000

def main():
    # Faker data
    if not os.path.exists(DATA_FILE):
        generate_dataset(num_records=NUM_RECORDS, output_path=DATA_FILE)
    else:
        print(f"[*] Използване на вече съществуващия файл с данни: {DATA_FILE}")

    df: pd.DataFrame = pd.read_csv(DATA_FILE)

    # Custom madReduce/Hadoom
    mr_simulator = HadoopSimulator()
    mr_output = mr_simulator.run(df)

    # Benchmark
    print("[*] Стартиране на бенчмарк тестове (Dask, Ray, PySpark)...")
    benchmarks: dict[str, float] = {
        "Custom MapReduce": mr_simulator.timings['total_mr']
    }

    try:
        t_dask, _res_dask = benchmark_dask(DATA_FILE)
        benchmarks["Dask"] = t_dask
        print(f"    - Dask изпълнен за: {t_dask:.4f}s")
    except Exception as e:
        print(f"    - Dask грешка/пропуснат: {e}")

    try:
        t_ray, _res_ray = benchmark_ray(df)
        benchmarks["Ray"] = t_ray
        print(f"    - Ray изпълнен за: {t_ray:.4f}s")
    except Exception as e:
        print(f"    - Ray грешка/пропуснат: {e}")

    try:
        t_spark, _res_spark = benchmark_pyspark(DATA_FILE)
        benchmarks["PySpark"] = t_spark
        print(f"    - PySpark изпълнен за: {t_spark:.4f}s")
    except Exception as e:
        print(f"    - PySpark грешка/пропуснат: {e}")

    # Visuals
    print("[*] Генериране на графики...")
    create_visualizations(df, benchmarks, output_dir="output")

    # Report
    cat_revenue = df.groupby("category")["total_amount"].sum()
    top_cat = str(cat_revenue.idxmax())  # pyright: ignore[reportAttributeAccessIssue]
    city_counts = df["city"].value_counts()
    top_city = str(city_counts.idxmax())  # pyright: ignore[reportAttributeAccessIssue]

    metadata = {
        "total_records": len(df),
        "total_revenue": df["total_amount"].sum(),
        "num_categories": df["category"].nunique(),
        "num_cities": df["city"].nunique(),
        "top_category": top_cat,
        "top_city": top_city,
        "mr_timings": mr_output['timings'],
        "benchmarks": benchmarks
    }

    print("[*] Генериране на финални отчети...")
    generate_reports(metadata, output_dir="output")
    print("\n[✔] ПРОЕКТЪТ ПРИКЛЮЧИ УСПЕШНО!")

if __name__ == "__main__":
    main()
