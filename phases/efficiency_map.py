import numpy as np

from utils.recipe import MAP_SPEEDS_RPM, MAP_TORQUES_NM, RATED_SPEED_RPM, RATED_TORQUE_NM


def efficiency_map(measurements, bench, log):
    """Sixteen operating points, four speeds by four torques, shaft power
    from the transducer over electrical power from the bus analyzer."""
    speeds, torques, effs = [], [], []
    for s in MAP_SPEEDS_RPM:
        for q in MAP_TORQUES_NM:
            op = bench.operating_point(s, q)
            speeds.append(s)
            torques.append(q)
            effs.append(100.0 * op["mech_w"] / op["elec_w"])
    bench.unload()
    effs = np.array(effs)
    i_rated = [i for i, (s, q) in enumerate(zip(speeds, torques)) if s == RATED_SPEED_RPM and q == RATED_TORQUE_NM][0]

    measurements.efficiency.x_axis = list(range(1, len(effs) + 1))
    measurements.efficiency.y_axis.speed = speeds
    measurements.efficiency.y_axis.torque = torques
    measurements.efficiency.y_axis.efficiency = effs.round(2).tolist()
    measurements.efficiency.y_axis.efficiency.aggregations.at_rated_pct = float(effs[i_rated])
    measurements.efficiency.y_axis.efficiency.aggregations.min_pct = float(effs.min())
    log.info(f"Efficiency {effs.min():.1f}..{effs.max():.1f} %, {effs[i_rated]:.1f} % at rated {RATED_TORQUE_NM:.0f} Nm / {RATED_SPEED_RPM:.0f} rpm")
