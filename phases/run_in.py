import numpy as np

from utils.recipe import RUN_IN_INPUT_RPM, RUN_IN_MINUTES


def run_in(measurements, bench, ui, log):
    """Unloaded run-in at 2000 rpm input. The no-load running torque is
    only meaningful after the grease has redistributed, which is why the
    reducer maker specifies it after a run; the value at the end of the
    run is the one with a limit, the curve is there for the trend."""
    bench.enable()
    cap = bench.run_in(RUN_IN_INPUT_RPM, RUN_IN_MINUTES)
    t = np.array(cap["time_s"])
    torque = np.array(cap["torque_nm"])
    ui.run_in_progress = 100
    final = float(torque[t >= t[-1] - 60.0].mean())

    measurements.no_load.x_axis = (t / 60.0).round(2).tolist()
    measurements.no_load.y_axis.torque = cap["torque_nm"]
    measurements.no_load.y_axis.torque.aggregations.final_nm = final
    measurements.no_load.y_axis.torque.aggregations.settle_pct = float(100.0 * (torque[:3].mean() - final) / torque[:3].mean())
    measurements.temperature_after_run_in_c = bench.temperature_c()
    log.info(f"No-load torque {torque[0]:.3f} -> {final:.3f} Nm input-referred over {RUN_IN_MINUTES:.0f} min, {measurements.temperature_after_run_in_c} C")
