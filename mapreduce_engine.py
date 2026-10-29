import time
from collections import defaultdict
from multiprocessing import Pool, cpu_count
import pandas as pd

def map_worker(chunk: pd.DataFrame):
#For each row we calculate key - value
    mapped_revenue = []
    mapped_cities = []

    for row in chunk.itertuples(index=False):
        mapped_revenue.append((row.category, row.total_amount))  # pyright: ignore[reportAttributeAccessIssue]
        mapped_cities.append((row.city, 1))  # pyright: ignore[reportAttributeAccessIssue]

    return {"category_rev": mapped_revenue, "city_orders": mapped_cities}

def reduce_sum(items: list[float] | list[int]):
        #reduce phase ,calculate with the given key
    return round(sum(items), 2)

class HadoopSimulator:
    num_partitions: int
    timings: dict[str, float]

    def __init__(self, num_partitions: int | None = None):
        self.num_partitions = num_partitions or cpu_count()
        self.timings = {}

    def run(self, df: pd.DataFrame):
        print("\n" + "="*50)
        print(f"[*] СТАРТИРАНЕ НА HADOOP / MAPREDUCE СИМУЛАЦИЯ ({self.num_partitions} дяла)")
        print("="*50)

        # 1. PARTITIONING
        t0 = time.time()
        chunk_size = len(df) // self.num_partitions
        chunks = [df.iloc[i * chunk_size : (i + 1) * chunk_size if i != self.num_partitions - 1 else len(df)]
                  for i in range(self.num_partitions)]
        self.timings['partitioning'] = time.time() - t0
        print(f"1. [Partitioning] {len(df):,} записа разделени на {len(chunks)} дяла за {self.timings['partitioning']:.4f}s")

        # 2. MAP ФАЗА (Паралелна през Multiprocessing Pool)
        t0 = time.time()
        with Pool(processes=self.num_partitions) as pool:
            map_results = pool.map(map_worker, chunks)
        self.timings['map'] = time.time() - t0
        print(f"2. [Map] Изпълнени Map задачи на всички ядра за {self.timings['map']:.4f}s")

        # 3. SHUFFLE & SORT ФАЗА
        t0 = time.time()
        shuffled_cat_rev = defaultdict(list)
        shuffled_city_orders = defaultdict(list)

        for partition_res in map_results:
            for cat, rev in partition_res["category_rev"]:
                shuffled_cat_rev[cat].append(rev)
            for city, count in partition_res["city_orders"]:
                shuffled_city_orders[city].append(count)
        self.timings['shuffle'] = time.time() - t0
        print(f"3. [Shuffle & Sort] Реорганизиране и групиране по ключове за {self.timings['shuffle']:.4f}s")

        # 4. REDUCE ФАЗА
        t0 = time.time()
        reduced_category_revenue = {k: reduce_sum(v) for k, v in shuffled_cat_rev.items()}
        reduced_city_orders = {k: sum(v) for k, v in shuffled_city_orders.items()}
        self.timings['reduce'] = time.time() - t0
        print(f"4. [Reduce] Агрегиране на стойностите за {self.timings['reduce']:.4f}s")

        # 5. RESULT FORMATTING
        total_time = sum(self.timings.values())
        self.timings['total_mr'] = total_time
        print(f"5. [Result] Пълен MapReduce цикъл завършен за {total_time:.4f}s\n")

        res_cat_df = pd.DataFrame(list(reduced_category_revenue.items()), columns=['Category', 'TotalRevenue']).sort_values(by='TotalRevenue', ascending=False)
        res_city_df = pd.DataFrame(list(reduced_city_orders.items()), columns=['City', 'OrderCount']).sort_values(by='OrderCount', ascending=False)

        return {
            "category_revenue": res_cat_df,
            "city_orders": res_city_df,
            "timings": self.timings
        }
