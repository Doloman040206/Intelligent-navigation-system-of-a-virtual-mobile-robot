from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from config.settings import OUTPUT_DIR

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.titlesize": 13,
    "axes.labelsize": 10,
    "legend.fontsize": 9,
    "figure.titlesize": 15,
    "savefig.dpi": 180,
    "savefig.bbox": "tight",
})


SCENARIO_LABELS = {
    "favorable": "Сприятливі",
    "moderate": "Помірні",
    "unfavorable": "Несприятливі",
}


def _number(value):
    if value is None:
        return np.nan

    try:
        return float(value)
    except (TypeError, ValueError):
        return np.nan


def _scenario_labels(rows):
    labels = []

    for row in rows:
        key = row.get("scenario")
        title = row.get("scenario_uk")

        labels.append(
            title
            or SCENARIO_LABELS.get(key, str(key or "Сценарій"))
        )

    return labels


def _values(rows, field):
    return [_number(row.get(field)) for row in rows]


def _save(fig, output_dir, filename):
    output_dir.mkdir(parents=True, exist_ok=True)

    path = output_dir / filename

    fig.tight_layout()
    fig.savefig(path, format="png")
    plt.close(fig)

    print(f"Графік збережено: {path}")


def _grouped_bar(
    rows,
    output_dir,
    filename,
    title,
    ylabel,
    baseline_field,
    adaptive_field,
    value_format=None,
):
    labels = _scenario_labels(rows)
    baseline = _values(rows, baseline_field)
    adaptive = _values(rows, adaptive_field)

    x = np.arange(len(labels))
    width = 0.36

    fig, ax = plt.subplots(figsize=(9, 5))

    ax.bar(
        x - width / 2,
        baseline,
        width,
        label="Baseline",
    )

    ax.bar(
        x + width / 2,
        adaptive,
        width,
        label="Adaptive",
    )

    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)

    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)

    if value_format:
        for container in ax.containers:
            ax.bar_label(
                container,
                fmt=value_format,
                padding=3,
                fontsize=8,
            )

    _save(fig, output_dir, filename)


def _difference_bar(
    rows,
    output_dir,
    filename,
    title,
    ylabel,
    baseline_field,
    adaptive_field,
    percent=False,
):
    labels = _scenario_labels(rows)
    differences = []

    for row in rows:
        baseline = _number(row.get(baseline_field))
        adaptive = _number(row.get(adaptive_field))

        if np.isnan(baseline) or np.isnan(adaptive):
            differences.append(np.nan)
            continue

        difference = adaptive - baseline

        if percent:
            if baseline == 0:
                differences.append(np.nan)
                continue

            difference = difference / abs(baseline) * 100

        differences.append(difference)

    x = np.arange(len(labels))

    fig, ax = plt.subplots(figsize=(9, 5))

    bars = ax.bar(x, differences)

    ax.axhline(
        0,
        linewidth=1,
        linestyle="--",
    )

    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)

    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)

    ax.bar_label(
        bars,
        fmt="%.3f" if percent else "%.2f",
        padding=3,
        fontsize=8,
    )

    _save(fig, output_dir, filename)


def _risk_reduction_chart(rows, output_dir):
    labels = _scenario_labels(rows)
    reductions = []

    for row in rows:
        baseline = _number(row.get("baseline_mean_risk"))
        adaptive = _number(row.get("adaptive_mean_risk"))

        if np.isnan(baseline) or np.isnan(adaptive) or baseline == 0:
            reductions.append(np.nan)
        else:
            reductions.append(
                (baseline - adaptive) / abs(baseline) * 100
            )

    x = np.arange(len(labels))

    fig, ax = plt.subplots(figsize=(9, 5))

    bars = ax.bar(x, reductions)

    ax.axhline(0, linewidth=1, linestyle="--")

    ax.set_title("Відсоткова зміна модельованого ризику")
    ax.set_ylabel("Зменшення ризику, %")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)

    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)

    ax.bar_label(
        bars,
        fmt="%.2f%%",
        padding=3,
        fontsize=8,
    )

    _save(
        fig,
        output_dir,
        "comparison_risk_reduction.png",
    )


def _risk_length_scatter(rows, output_dir):
    fig, ax = plt.subplots(figsize=(8, 6))

    baseline_lengths = _values(rows, "baseline_length_m")
    baseline_risks = _values(rows, "baseline_mean_risk")

    adaptive_lengths = _values(rows, "adaptive_length_m")
    adaptive_risks = _values(rows, "adaptive_mean_risk")

    ax.scatter(
        baseline_lengths,
        baseline_risks,
        label="Baseline",
        marker="o",
        s=75,
    )

    ax.scatter(
        adaptive_lengths,
        adaptive_risks,
        label="Adaptive",
        marker="s",
        s=75,
    )

    labels = _scenario_labels(rows)

    for index, label in enumerate(labels):
        if (
            not np.isnan(adaptive_lengths[index])
            and not np.isnan(adaptive_risks[index])
        ):
            ax.annotate(
                label,
                (
                    adaptive_lengths[index],
                    adaptive_risks[index],
                ),
                xytext=(5, 6),
                textcoords="offset points",
                fontsize=8,
            )

    ax.set_title("Залежність модельованого ризику від довжини маршруту")
    ax.set_xlabel("Довжина маршруту, м")
    ax.set_ylabel("Середній модельований ризик")

    ax.legend()
    ax.grid(linestyle="--", alpha=0.4)

    _save(
        fig,
        output_dir,
        "comparison_risk_vs_length.png",
    )


def _weather_response_chart(rows, output_dir):
    labels = _scenario_labels(rows)

    weather_risk = _values(rows, "overall_weather_risk")
    baseline_risk = _values(rows, "baseline_mean_risk")
    adaptive_risk = _values(rows, "adaptive_mean_risk")

    x = np.arange(len(labels))

    fig, ax = plt.subplots(figsize=(9, 5))

    ax.plot(
        x,
        weather_risk,
        marker="o",
        linewidth=2,
        label="Загальний погодний ризик",
    )

    ax.plot(
        x,
        baseline_risk,
        marker="s",
        linewidth=2,
        label="Ризик Baseline",
    )

    ax.plot(
        x,
        adaptive_risk,
        marker="^",
        linewidth=2,
        label="Ризик Adaptive",
    )

    ax.set_title("Реакція показників на зміну погодних умов")
    ax.set_ylabel("Значення ризику")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)

    ax.legend()
    ax.grid(linestyle="--", alpha=0.4)

    _save(
        fig,
        output_dir,
        "comparison_weather_response.png",
    )


def _metrics_overview(rows, output_dir):
    labels = _scenario_labels(rows)

    metrics = [
        (
            "Довжина маршруту",
            "baseline_length_m",
            "adaptive_length_m",
            "м",
        ),
        (
            "Модельований ризик",
            "baseline_mean_risk",
            "adaptive_mean_risk",
            "ризик",
        ),
        (
            "Вартість маршруту",
            "baseline_cost",
            "adaptive_cost",
            "умовні одиниці",
        ),
        (
            "Час планування",
            "baseline_planning_time_ms",
            "adaptive_planning_time_ms",
            "мс",
        ),
    ]

    fig, axes = plt.subplots(
        2,
        2,
        figsize=(12, 8),
    )

    for ax, (title, baseline_field, adaptive_field, unit) in zip(
        axes.flat,
        metrics,
    ):
        x = np.arange(len(labels))
        width = 0.36

        baseline = _values(rows, baseline_field)
        adaptive = _values(rows, adaptive_field)

        ax.bar(
            x - width / 2,
            baseline,
            width,
            label="Baseline",
        )

        ax.bar(
            x + width / 2,
            adaptive,
            width,
            label="Adaptive",
        )

        ax.set_title(title)
        ax.set_ylabel(unit)
        ax.set_xticks(x)
        ax.set_xticklabels(labels)

        ax.grid(axis="y", linestyle="--", alpha=0.4)
        ax.set_axisbelow(True)

    handles, legend_labels = axes.flat[0].get_legend_handles_labels()

    fig.legend(
        handles,
        legend_labels,
        loc="upper center",
        ncol=2,
    )

    fig.suptitle(
        "Загальний огляд показників Baseline та Adaptive",
        y=1.02,
    )

    _save(
        fig,
        output_dir,
        "comparison_metrics_overview.png",
    )


def generate_comparison_plots(
    rows,
    comparison_rows=None,
    output_dir=None,
):
    if isinstance(comparison_rows, (str, Path)) and output_dir is None:
        output_dir = comparison_rows
        comparison_rows = None

    output_dir = Path(output_dir or OUTPUT_DIR)

    if not rows:
        print("Немає даних для побудови порівняльних графіків.")
        return []

    output_dir.mkdir(parents=True, exist_ok=True)

    generated_files = []

    _grouped_bar(
        rows,
        output_dir,
        "comparison_route_length.png",
        "Порівняння довжини маршрутів",
        "Довжина маршруту, м",
        "baseline_length_m",
        "adaptive_length_m",
        "%.2f",
    )
    generated_files.append("comparison_route_length.png")


    _grouped_bar(
        rows,
        output_dir,
        "comparison_modelled_risk.png",
        "Порівняння модельованого ризику маршрутів",
        "Середній модельований ризик",
        "baseline_mean_risk",
        "adaptive_mean_risk",
        "%.4f",
    )
    generated_files.append("comparison_modelled_risk.png")

    _grouped_bar(
        rows,
        output_dir,
        "comparison_route_cost.png",
        "Порівняння вартості маршрутів",
        "Умовна вартість маршруту",
        "baseline_cost",
        "adaptive_cost",
        "%.2f",
    )
    generated_files.append("comparison_route_cost.png")

    _grouped_bar(
        rows,
        output_dir,
        "comparison_planning_time.png",
        "Порівняння часу планування",
        "Час планування, мс",
        "baseline_planning_time_ms",
        "adaptive_planning_time_ms",
        "%.2f",
    )
    generated_files.append("comparison_planning_time.png")

    _grouped_bar(
        rows,
        output_dir,
        "comparison_edge_count.png",
        "Порівняння кількості ребер маршруту",
        "Кількість ребер",
        "baseline_edge_count",
        "adaptive_edge_count",
        "%.0f",
    )
    generated_files.append("comparison_edge_count.png")

    _difference_bar(
        rows,
        output_dir,
        "comparison_risk_difference.png",
        "Різниця модельованого ризику Adaptive - Baseline",
        "Різниця ризику",
        "baseline_mean_risk",
        "adaptive_mean_risk",
    )
    generated_files.append("comparison_risk_difference.png")

    _difference_bar(
        rows,
        output_dir,
        "comparison_length_difference.png",
        "Різниця довжини маршрутів Adaptive - Baseline",
        "Різниця довжини, м",
        "baseline_length_m",
        "adaptive_length_m",
    )
    generated_files.append("comparison_length_difference.png")

    _difference_bar(
        rows,
        output_dir,
        "comparison_length_difference_percent.png",
        "Відносна зміна довжини маршруту",
        "Зміна довжини, %",
        "baseline_length_m",
        "adaptive_length_m",
        percent=True,
    )
    generated_files.append("comparison_length_difference_percent.png")

    _risk_reduction_chart(rows, output_dir)
    generated_files.append("comparison_risk_reduction.png")

    _risk_length_scatter(rows, output_dir)
    generated_files.append("comparison_risk_vs_length.png")

    _weather_response_chart(rows, output_dir)
    generated_files.append("comparison_weather_response.png")

    _metrics_overview(rows, output_dir)
    generated_files.append("comparison_metrics_overview.png")

    print(
        f"\nПобудовано графіків: {len(generated_files)}"
    )
    print(f"Каталог збереження: {output_dir.resolve()}")

    return generated_files
