def _mean(values):
    values = [
        float(value)
        for value in values
        if value is not None
    ]

    if not values:
        return None

    return round(sum(values) / len(values), 4)


def _percent_change(baseline, adaptive):
    if baseline is None or adaptive is None:
        return None

    baseline = float(baseline)
    adaptive = float(adaptive)

    if baseline == 0:
        return 0.0 if adaptive == 0 else None

    return round(
        ((adaptive - baseline) / abs(baseline)) * 100.0,
        4,
    )


def _risk_reduction_percent(baseline, adaptive):
    if baseline is None or adaptive is None:
        return None

    baseline = float(baseline)
    adaptive = float(adaptive)

    if baseline == 0:
        return 0.0 if adaptive == 0 else None

    return round(
        ((baseline - adaptive) / abs(baseline)) * 100.0,
        4,
    )


def success_rate(rows, field="success"):
    if not rows:
        return 0.0

    successful = sum(
        bool(row.get(field, False))
        for row in rows
    )

    return round(
        100.0 * successful / len(rows),
        2,
    )


def summarize(rows):
    baseline_successful = [
        row for row in rows
        if row.get("baseline_success", False)
    ]

    adaptive_successful = [
        row for row in rows
        if row.get("adaptive_success", row.get("success", False))
    ]

    return {
        "scenario_count": len(rows),

        "baseline_successful_routes": len(baseline_successful),
        "adaptive_successful_routes": len(adaptive_successful),

        "baseline_success_rate_percent": success_rate(
            rows,
            "baseline_success",
        ),
        "adaptive_success_rate_percent": success_rate(
            rows,
            "adaptive_success",
        ),

        "successful_routes": len(adaptive_successful),
        "route_success_rate_percent": success_rate(
            rows,
            "adaptive_success",
        ),

        "mean_baseline_route_length_m": _mean(
            row["baseline_length_m"]
            for row in baseline_successful
        ),
        "mean_adaptive_route_length_m": _mean(
            row["adaptive_length_m"]
            for row in adaptive_successful
        ),

        "mean_baseline_modelled_risk": _mean(
            row["baseline_mean_risk"]
            for row in baseline_successful
        ),
        "mean_adaptive_modelled_risk": _mean(
            row["adaptive_mean_risk"]
            for row in adaptive_successful
        ),

        "mean_baseline_route_cost": _mean(
            row["baseline_cost"]
            for row in baseline_successful
        ),
        "mean_adaptive_route_cost": _mean(
            row["adaptive_cost"]
            for row in adaptive_successful
        ),

        "mean_baseline_edge_count": _mean(
            row["baseline_edge_count"]
            for row in baseline_successful
        ),
        "mean_adaptive_edge_count": _mean(
            row["adaptive_edge_count"]
            for row in adaptive_successful
        ),

        "mean_baseline_planning_time_ms": _mean(
            row["baseline_planning_time_ms"]
            for row in baseline_successful
        ),
        "mean_adaptive_planning_time_ms": _mean(
            row["adaptive_planning_time_ms"]
            for row in adaptive_successful
        ),

        "mean_decision_time_ms": _mean(
            row["decision_time_ms"]
            for row in rows
        ),
    }


def build_comparison_rows(rows):
    comparisons = []

    for row in rows:
        baseline_risk = row.get("baseline_mean_risk")
        adaptive_risk = row.get("adaptive_mean_risk")

        baseline_length = row.get("baseline_length_m")
        adaptive_length = row.get("adaptive_length_m")

        baseline_cost = row.get("baseline_cost")
        adaptive_cost = row.get("adaptive_cost")

        baseline_time = row.get("baseline_planning_time_ms")
        adaptive_time = row.get("adaptive_planning_time_ms")

        baseline_edges = row.get("baseline_edge_count")
        adaptive_edges = row.get("adaptive_edge_count")

        risk_difference = (
            round(float(adaptive_risk) - float(baseline_risk), 6)
            if baseline_risk is not None and adaptive_risk is not None
            else None
        )

        if risk_difference is None:
            risk_status = "not_comparable"
        elif risk_difference < -1e-9:
            risk_status = "decreased"
        elif risk_difference > 1e-9:
            risk_status = "increased"
        else:
            risk_status = "unchanged"

        comparison = {
            "scenario": row.get("scenario"),
            "scenario_uk": row.get("scenario_uk"),
            "weather_category": row.get("weather_category"),
            "overall_weather_risk": row.get("overall_weather_risk"),
            "temperature_c": row.get("temperature_c"),
            "precipitation_mm": row.get("precipitation_mm"),
            "wind_kmh": row.get("wind_kmh"),
            "selected_mode": row.get("selected_mode"),

            "baseline_success": row.get("baseline_success"),
            "adaptive_success": row.get("adaptive_success"),

            "baseline_length_m": baseline_length,
            "adaptive_length_m": adaptive_length,
            "length_difference_m": (
                round(float(adaptive_length) - float(baseline_length), 4)
                if baseline_length is not None and adaptive_length is not None
                else None
            ),
            "length_change_percent": _percent_change(
                baseline_length,
                adaptive_length,
            ),

            "baseline_mean_risk": baseline_risk,
            "adaptive_mean_risk": adaptive_risk,
            "risk_difference": risk_difference,
            "risk_change_percent": _percent_change(
                baseline_risk,
                adaptive_risk,
            ),
            "risk_reduction_percent": _risk_reduction_percent(
                baseline_risk,
                adaptive_risk,
            ),
            "risk_status": risk_status,

            "baseline_cost": baseline_cost,
            "adaptive_cost": adaptive_cost,
            "cost_difference": (
                round(float(adaptive_cost) - float(baseline_cost), 4)
                if baseline_cost is not None and adaptive_cost is not None
                else None
            ),
            "cost_change_percent": _percent_change(
                baseline_cost,
                adaptive_cost,
            ),

            "baseline_edge_count": baseline_edges,
            "adaptive_edge_count": adaptive_edges,
            "edge_count_difference": (
                int(adaptive_edges) - int(baseline_edges)
                if baseline_edges is not None and adaptive_edges is not None
                else None
            ),

            "baseline_planning_time_ms": baseline_time,
            "adaptive_planning_time_ms": adaptive_time,
            "planning_time_difference_ms": (
                round(float(adaptive_time) - float(baseline_time), 4)
                if baseline_time is not None and adaptive_time is not None
                else None
            ),
            "planning_time_change_percent": _percent_change(
                baseline_time,
                adaptive_time,
            ),
        }

        comparisons.append(comparison)

    return comparisons


def summarize_comparisons(comparison_rows, city, selected_mode):
    comparable_risk = [
        row for row in comparison_rows
        if row.get("risk_difference") is not None
    ]

    comparable_length = [
        row for row in comparison_rows
        if row.get("length_difference_m") is not None
    ]

    comparable_cost = [
        row for row in comparison_rows
        if row.get("cost_difference") is not None
    ]

    comparable_time = [
        row for row in comparison_rows
        if row.get("planning_time_difference_ms") is not None
    ]

    return {
        "city": city,
        "selected_mode": selected_mode,
        "scenario_count": len(comparison_rows),

        "risk_decreased_scenarios": sum(
            row["risk_status"] == "decreased"
            for row in comparable_risk
        ),
        "risk_unchanged_scenarios": sum(
            row["risk_status"] == "unchanged"
            for row in comparable_risk
        ),
        "risk_increased_scenarios": sum(
            row["risk_status"] == "increased"
            for row in comparable_risk
        ),

        "mean_baseline_risk": _mean(
            row["baseline_mean_risk"]
            for row in comparable_risk
        ),
        "mean_adaptive_risk": _mean(
            row["adaptive_mean_risk"]
            for row in comparable_risk
        ),
        "mean_risk_difference": _mean(
            row["risk_difference"]
            for row in comparable_risk
        ),
        "mean_risk_reduction_percent": _mean(
            row["risk_reduction_percent"]
            for row in comparable_risk
        ),

        "mean_baseline_length_m": _mean(
            row["baseline_length_m"]
            for row in comparable_length
        ),
        "mean_adaptive_length_m": _mean(
            row["adaptive_length_m"]
            for row in comparable_length
        ),
        "mean_length_difference_m": _mean(
            row["length_difference_m"]
            for row in comparable_length
        ),
        "mean_length_change_percent": _mean(
            row["length_change_percent"]
            for row in comparable_length
        ),

        "mean_baseline_cost": _mean(
            row["baseline_cost"]
            for row in comparable_cost
        ),
        "mean_adaptive_cost": _mean(
            row["adaptive_cost"]
            for row in comparable_cost
        ),
        "mean_cost_difference": _mean(
            row["cost_difference"]
            for row in comparable_cost
        ),

        "mean_baseline_planning_time_ms": _mean(
            row["baseline_planning_time_ms"]
            for row in comparable_time
        ),
        "mean_adaptive_planning_time_ms": _mean(
            row["adaptive_planning_time_ms"]
            for row in comparable_time
        ),
        "mean_planning_time_difference_ms": _mean(
            row["planning_time_difference_ms"]
            for row in comparable_time
        ),

        "baseline_success_rate_percent": success_rate(
            comparison_rows,
            "baseline_success",
        ),
        "adaptive_success_rate_percent": success_rate(
            comparison_rows,
            "adaptive_success",
        ),
    }
