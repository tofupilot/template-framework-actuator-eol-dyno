import numpy as np

from utils.recipe import KT_CURRENT_STEPS_A, KT_OUTPUT_EXPECTED


def torque_constant(measurements, bench, log):
    """Dyno locked, q-axis current stepped, output torque read on the
    transducer. The slope above the friction knee is the output-referred
    torque constant: motor Kt times ratio times the locked-rotor
    efficiency of the reducer."""
    torque = [bench.stall_torque_nm(i) for i in KT_CURRENT_STEPS_A]
    currents = np.array(KT_CURRENT_STEPS_A)
    t = np.array(torque)
    fit = currents >= 10.0  # above the friction knee
    slope, intercept = np.polyfit(currents[fit], t[fit], 1)
    resid = t[fit] - (slope * currents[fit] + intercept)
    linearity = float(100.0 * np.abs(resid).max() / t[fit].max())

    measurements.stall.x_axis = KT_CURRENT_STEPS_A
    measurements.stall.y_axis.torque = t.round(3).tolist()
    measurements.stall.y_axis.torque.aggregations.kt_nm_per_a = float(slope)
    measurements.stall.y_axis.torque.aggregations.linearity_pct = linearity
    measurements.stall.y_axis.torque.aggregations.friction_knee_nm = float(-intercept)
    log.info(f"Kt {slope:.2f} Nm/A output-referred ({KT_OUTPUT_EXPECTED:.1f} before losses), linearity {linearity:.2f} %, friction knee {-intercept:.2f} Nm")
