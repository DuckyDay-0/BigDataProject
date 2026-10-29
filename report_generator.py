import os
from typing import Any
from tabulate import tabulate

def generate_reports(metadata: dict[str, Any], output_dir: str = "output"):
    os.makedirs(output_dir, exist_ok=True)

    # 1. Console
    mr_table = tabulate(
        [[step.capitalize(), f"{sec:.4f} s"] for step, sec in metadata['mr_timings'].items()],
        headers=["Фаза на MapReduce", "Време (сек)"], tablefmt="github"
    )
    bench_table = tabulate(
        [[fw, f"{sec:.4f} s"] for fw, sec in metadata['benchmarks'].items()],
        headers=["Фреймуърк", "Време (сек)"], tablefmt="github"
    )

    txt_content = f"""=======================================================
     ОТЧЕТ ЗА ИЗПЪЛНЕНИЕ НА BIG DATA АНАЛИЗ
=======================================================
Брой обработени транзакции: {metadata['total_records']:,}
Общ оборот в набора данни: {metadata['total_revenue']:,.2f} лв.
Уникални категории: {metadata['num_categories']}
Градове в обхвата: {metadata['num_cities']}

--- 1. ВРЕМЕНА НА HADOOP / MAPREDUCE ФАЗИТЕ ---
{mr_table}

--- 2. СРАВНИТЕЛЕН АНАЛИЗ (BENCHMARK) ---
{bench_table}

--- 3. ОСНОВНИ ИЗВОДИ ОТ АНАЛИЗА ---
1. Архитектурен модел: Фазата 'Map' и 'Shuffle' поемат най-голям дял от изчисленията при чист MapReduce модел.
2. Фреймуърци: Инструменти като Dask и Ray демонстрират минимален overhead при средни обеми памет, докато PySpark изисква първоначално време за вдигане на JVM / SparkContext, но показва превъзходство при мащабиране към терабайти.
3. Бизнес извод: Най-доходна категория е '{metadata['top_category']}', а градът с най-голям брой поръчки е '{metadata['top_city']}'.
=======================================================
"""
    txt_path = os.path.join(output_dir, "analysis_report.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(txt_content)

    # 2.HTML report with the visuals
    html_content = f"""<!DOCTYPE html>
<html lang="bg">
<head>
    <meta charset="UTF-8">
    <title>Big Data Анализ и Hadoop Симулация</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 30px; background-color: #f7f9fc; color: #2c3e50; }}
        h1, h2 {{ color: #1a365d; }}
        .metric-card {{ background: white; padding: 15px 25px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.08); display: inline-block; margin-right: 15px; margin-bottom: 20px; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #2b6cb0; }}
        table {{ border-collapse: collapse; width: 60%; background: white; margin: 15px 0; border-radius: 6px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        th, td {{ padding: 10px 14px; text-align: left; border-bottom: 1px solid #e2e8f0; }}
        th {{ background-color: #2b6cb0; color: white; }}
        .grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-top: 20px; }}
        .chart-box {{ background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.08); text-align: center; }}
        .chart-box img {{ max-width: 100%; height: auto; border-radius: 4px; }}
        ul {{ background: white; padding: 20px 40px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.08); }}
        li {{ margin-bottom: 10px; line-height: 1.5; }}
    </style>
</head>
<body>
    <h1>Отчет за Big Data анализ и Hadoop/MapReduce симулация</h1>

    <div>
        <div class="metric-card"><div>Общ брой записи</div><div class="metric-value">{metadata['total_records']:,}</div></div>
        <div class="metric-card"><div>Общ оборот</div><div class="metric-value">{metadata['total_revenue']:,.2f} лв.</div></div>
        <div class="metric-card"><div>Топ Категория</div><div class="metric-value">{metadata['top_category']}</div></div>
        <div class="metric-card"><div>Водещ град</div><div class="metric-value">{metadata['top_city']}</div></div>
    </div>

    <h2>1. Hadoop / MapReduce Симулация (Времена по фази)</h2>
    <table>
        <tr><th>Фаза</th><th>Време за изпълнение</th></tr>
        {''.join(f"<tr><td>{k.capitalize()}</td><td>{v:.4f} s</td></tr>" for k, v in metadata['mr_timings'].items())}
    </table>

    <h2>2. Сравнителен бенчмарк на Big Data фреймуърци</h2>
    <table>
        <tr><th>Фреймуърк / Модул</th><th>Време за обработка</th></tr>
        {''.join(f"<tr><td>{k}</td><td>{v:.4f} s</td></tr>" for k, v in metadata['benchmarks'].items())}
    </table>

    <h2>3. Графични визуализации</h2>
    <div class="grid">
        <div class="chart-box"><h3>Приход по категории</h3><img src="chart_category_revenue.png" /></div>
        <div class="chart-box"><h3>Месечен тренд</h3><img src="chart_monthly_trend.png" /></div>
        <div class="chart-box"><h3>Методи на плащане</h3><img src="chart_payment_distribution.png" /></div>
        <div class="chart-box"><h3>Бенчмарк сравнение</h3><img src="chart_benchmark_comparison.png" /></div>
    </div>

    <h2>4. Изводи и заключение</h2>
    <ul>
        <li><strong>Ефективност на модела:</strong> Custom MapReduce имплементацията ясно илюстрира стъпките <em>Partitioning &rarr; Map &rarr; Shuffle &rarr; Reduce</em>, като паралелното разпределение намалява драстично Map времето.</li>
        <li><strong>Сравнение:</strong> <em>Dask</em> и <em>Ray</em> се настройват изключително лесно в Python екосистемата и дават отлична скорост за in-memory изчисления. <em>PySpark</em> предоставя цялостната индустриална сигурност на Catalyst и RDD разпределението.</li>
        <li><strong>Интерпретация:</strong> Анализът на продажбите идентифицира най-силно представящите се продуктови категории и периоди от годината с пиково натоварване.</li>
    </ul>
</body>
</html>
"""
    html_path = os.path.join(output_dir, "analysis_report.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[+] Репортите са генерирани:\n    - {txt_path}\n    - {html_path}")
    print("\n" + txt_content)
