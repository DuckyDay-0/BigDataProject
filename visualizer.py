import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def create_visualizations(df: pd.DataFrame, benchmark_results: dict[str, float], output_dir: str = "output") -> list[str]:
    os.makedirs(output_dir, exist_ok=True)
    sns.set_theme(style="whitegrid")
    generated_charts = []

    # 1. Earnings grouped by product categories
    plt.figure(figsize=(10, 5))
    cat_rev = df.groupby("category")["total_amount"].sum().reset_index().sort_values(by="total_amount", ascending=False)  # pyright: ignore[reportAttributeAccessIssue]
    sns.barplot(data=cat_rev, x="category", y="total_amount", palette="crest")
    plt.title("Общ приход по категории (лв.)", fontsize=14, weight='bold')
    plt.xlabel("Категория", fontsize=11)
    plt.ylabel("Приход (лв.)", fontsize=11)
    plt.xticks(rotation=25)
    chart1 = os.path.join(output_dir, "chart_category_revenue.png")
    plt.tight_layout()
    plt.savefig(chart1, dpi=300)
    plt.close()
    generated_charts.append(chart1)

    # 2. Monthly earnings
    df_temp = df.copy()
    df_temp['month'] = pd.to_datetime(df_temp['timestamp']).dt.to_period('M').astype(str)
    monthly_rev = df_temp.groupby('month')['total_amount'].sum().reset_index()  # pyright: ignore[reportAttributeAccessIssue]

    plt.figure(figsize=(11, 5))
    sns.lineplot(data=monthly_rev, x='month', y='total_amount', marker='o', color='#2b5c8f', linewidth=2.5)
    plt.title("Месечна динамика на приходите за последната 1 година", fontsize=14, weight='bold')
    plt.xlabel("Месец", fontsize=11)
    plt.ylabel("Оборот (лв.)", fontsize=11)
    plt.xticks(rotation=45)
    chart2 = os.path.join(output_dir, "chart_monthly_trend.png")
    plt.tight_layout()
    plt.savefig(chart2, dpi=300)
    plt.close()
    generated_charts.append(chart2)

    # 3. Payment method
    plt.figure(figsize=(7, 7))
    pay_counts = df['payment_method'].value_counts()
    colors = sns.color_palette('pastel')[0:len(pay_counts)]
    plt.pie(pay_counts, labels=[str(x) for x in pay_counts.index], autopct='%1.1f%%', startangle=90, colors=colors, wedgeprops={'width': 0.4, 'edgecolor': 'w'})
    plt.title("Дял на предпочитаните платежни методи", fontsize=14, weight='bold')
    chart3 = os.path.join(output_dir, "chart_payment_distribution.png")
    plt.tight_layout()
    plt.savefig(chart3, dpi=300)
    plt.close()
    generated_charts.append(chart3)

    # 4. Framework benchmark
    plt.figure(figsize=(9, 5))
    bench_df = pd.DataFrame(list(benchmark_results.items()), columns=['Framework', 'Time_sec']).sort_values(by="Time_sec")
    ax4 = sns.barplot(data=bench_df, x="Framework", y="Time_sec", palette="magma")
    for p in ax4.patches:
        ax4.annotate(f"{p.get_height():.3f} s",  # pyright: ignore[reportAttributeAccessIssue]
                     (p.get_x() + p.get_width() / 2., p.get_height()),  # pyright: ignore[reportAttributeAccessIssue]
                     ha='center', va='baseline', fontsize=10, color='black',
                     xytext=(0, 4), textcoords='offset points')
    plt.title("Сравнителен бенчмарк за обработка на набора от данни", fontsize=14, weight='bold')
    plt.xlabel("Фреймуърк / Двигател", fontsize=11)
    plt.ylabel("Време за изпълнение (секунди)", fontsize=11)
    chart4 = os.path.join(output_dir, "chart_benchmark_comparison.png")
    plt.tight_layout()
    plt.savefig(chart4, dpi=300)
    plt.close()
    generated_charts.append(chart4)

    print(f"[+] Генерирани са {len(generated_charts)} визуализации в '{output_dir}/'")
    return generated_charts
