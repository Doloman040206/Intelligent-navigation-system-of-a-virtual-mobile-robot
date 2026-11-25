import csv
import json

from config.settings import OUTPUT_DIR
from core.decision_module import assess_weather
from core.route_planner import plan_route
from experiments.comparison_plots import generate_comparison_plots
from experiments.metrics import (
    build_comparison_rows,
    summarize,
    summarize_comparisons,
)
from experiments.scenarios import TEST_WEATHER_SCENARIOS


def _write_csv(path, rows):
    if not rows:
        path.write_text("", encoding="utf-8-sig")
        return

    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(rows[0].keys()),
        )
        writer.writeheader()
        writer.writerows(rows)


def _write_json(path, data):
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def run_experiment(graph, city, selected_mode):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    rows = []
    origin = (city.start_lat, city.start_lon)
    target = (city.target_lat, city.target_lon)

    print("\n=== КОНТРОЛЬОВАНИЙ ЕКСПЕРИМЕНТ ===")

    for key, title, weather in TEST_WEATHER_SCENARIOS:
        decision = assess_weather(weather, selected_mode)

        baseline = plan_route(
            graph,
            origin,
            target,
            decision=decision,
            adaptive=False,
        )

        adaptive = plan_route(
            graph,
            origin,
            target,
            decision=decision,
            adaptive=True,
        )

        baseline_success = bool(baseline["success"])
        adaptive_success = bool(adaptive["success"])

        row = {
            "scenario": key,
            "scenario_uk": title,
            "weather_source": weather.source,
            "temperature_c": weather.temperature_c,
            "precipitation_mm": weather.precipitation_mm,
            "wind_kmh": weather.wind_kmh,
            "weather_category": decision["category"],
            "overall_weather_risk": decision["overall_risk"],
            "selected_mode": selected_mode,
            "recommended_mode": decision["recommended_mode"],

            "baseline_success": baseline_success,
            "adaptive_success": adaptive_success,
            "success": adaptive_success,

            "baseline_length_m": baseline["length_m"],
            "adaptive_length_m": adaptive["length_m"],

            "baseline_mean_risk": baseline["mean_segment_risk"],
            "adaptive_mean_risk": adaptive["mean_segment_risk"],

            "baseline_cost": baseline["route_cost"],
            "adaptive_cost": adaptive["route_cost"],

            "baseline_edge_count": baseline["edge_count"],
            "adaptive_edge_count": adaptive["edge_count"],

            "baseline_planning_time_ms": baseline["planning_time_ms"],
            "adaptive_planning_time_ms": adaptive["planning_time_ms"],

            "decision_time_ms": decision["decision_time_ms"],
        }

        rows.append(row)

        print(
            f"{title}: "
            f"погодні умови={decision['overall_risk']:.3f}; "
            f"Baseline={baseline['length_m']:.2f} м, "
            f"ризик={baseline['mean_segment_risk']:.4f}; "
            f"Adaptive={adaptive['length_m']:.2f} м, "
            f"ризик={adaptive['mean_segment_risk']:.4f}"
        )

    experiment_path = OUTPUT_DIR / "experiment_results.csv"
    _write_csv(experiment_path, rows)

    summary = summarize(rows)
    summary.update({
        "city": city.city,
        "selected_mode": selected_mode,
        "hypothesis": (
            "Погодна адаптація може зменшувати в нас "
            "вразливість маршруту в тому випадку, якщо ми порівнюємо її з плануванням лише за довжиною."
        ),
        "note": (
            "Baseline — алгоритм Дейкстри за довжиною."
        ),
    })

    summary_path = OUTPUT_DIR / "experiment_summary.json"
    _write_json(summary_path, summary)

    comparison_rows = build_comparison_rows(rows)
    comparison_path = OUTPUT_DIR / "comparison_results.csv"
    _write_csv(comparison_path, comparison_rows)

    comparison_summary = summarize_comparisons(
        comparison_rows,
        city=city.city,
        selected_mode=selected_mode,
    )
    comparison_summary_path = OUTPUT_DIR / "comparison_summary.json"
    _write_json(comparison_summary_path, comparison_summary)

    generated_plots = generate_comparison_plots(
        comparison_rows,
        OUTPUT_DIR,
    )

    print("\n=== РЕЗУЛЬТАТИ ПОРІВНЯННЯ ===")
    print(f"Таблиця експерименту: {experiment_path}")
    print(f"Зведення експерименту: {summary_path}")
    print(f"Таблиця порівняння: {comparison_path}")
    print(f"Зведення порівняння: {comparison_summary_path}")
    print(f"Створено графіків: {len(generated_plots)}")

    for plot_path in generated_plots:
        print(f"Графік: {plot_path}")

    return rows, summary
