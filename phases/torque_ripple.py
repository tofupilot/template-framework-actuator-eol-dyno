import numpy as np

from utils.recipe import RATED_TORQUE_NM, RATIO, RIPPLE_LOAD_NM, RIPPLE_SPEED_RPM


def torque_ripple(measurements, bench, log):
    """One output revolution at 3 rpm under 30 Nm, torque against angle.
    Peak-to-peak ripple as a percentage of rated torque, and the dominant
    order from an FFT over the revolution: a healthy harmonic drive shows
    2 x ratio (the wave generator), a damaged flexspline or a bad bearing
    shows elsewhere."""
    cap = bench.ripple_capture(RIPPLE_SPEED_RPM, RIPPLE_LOAD_NM)
    torque = np.array(cap["torque_nm"])
    ripple = torque - torque.mean()
    spectrum = np.abs(np.fft.rfft(ripple))
    order = int(np.argmax(spectrum[1:]) + 1)  # cycles per output revolution

    measurements.ripple.x_axis = cap["angle_deg"]
    measurements.ripple.y_axis.torque = cap["torque_nm"]
    measurements.ripple.y_axis.torque.aggregations.pp_pct_rated = float(100.0 * (torque.max() - torque.min()) / RATED_TORQUE_NM)
    measurements.ripple.y_axis.torque.aggregations.dominant_order = order
    log.info(f"Ripple {100.0 * (torque.max() - torque.min()) / RATED_TORQUE_NM:.2f} % of rated p-p, dominant order {order} (2 x ratio = {2 * RATIO})")
