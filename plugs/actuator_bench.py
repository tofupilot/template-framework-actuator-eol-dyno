"""Actuator dyno bench (mock): four-quadrant load, inline torque transducer
with angle output, DC-bus power analyzer, and the EtherCAT drive of the
actuator under test, one plug because the readings depend on each other.

Maps to a Magtrol WB eddy-current or a servo-motor load, a Kistler 4503B
dual-range torque transducer (class 0.05, angle +-0.03 deg, 10 kHz), a
Yokogawa WT-class power analyzer on the 48 V bus, and an Elmo or
Kollmorgen EtherCAT drive on a real-time target. The mock synthesizes a
healthy actuator: motor Kt on datasheet, reducer efficiency 0.80 at rated
falling at light load, no-load torque that settles during run-in as the
grease redistributes, and torque ripple dominated by the wave generator's
second harmonic. Swap for classes speaking the drive's CoE objects and
SCPI; the phases stay unchanged.
"""

import numpy as np

from utils.recipe import BUS_V, MOTOR_KT_NM_PER_A, RATED_TORQUE_NM, RATIO


class ActuatorBench:
    def __init__(self):
        self._rng = np.random.default_rng(4503)
        self._kt = MOTOR_KT_NM_PER_A * (1.0 + self._rng.normal(0.0, 0.006))
        self._eff_rated = 0.80 + self._rng.normal(0.0, 0.008)
        self._no_load_start_nm = 0.19
        self._no_load_end_nm = 0.11 + self._rng.normal(0.0, 0.006)
        self._ripple_pct = 1.4 + self._rng.normal(0.0, 0.08)
        self._temp_c = 22.0
        self._enabled = False
        # self.drive = pysoem...; self.dyno = pyvisa...; self.pa = pyvisa...
        print("Actuator bench connected, dyno unloaded, drive disabled")

    # --- drive -------------------------------------------------------------

    def drive_identify(self):
        return {"firmware": "3.2.7", "ratio": RATIO, "encoder_bits": 19, "bus_v": BUS_V}

    def drive_config(self):
        return {"current_limit_a": 30, "pole_pairs": 21, "commutation": "sincos", "brake": "none"}

    def enable(self):
        self._enabled = True

    def disable(self):
        self._enabled = False

    def temperature_c(self):
        return round(self._temp_c + self._rng.normal(0.0, 0.1), 1)

    # --- run-in -------------------------------------------------------------

    def run_in(self, input_rpm, minutes):
        """Unloaded run at input_rpm; no-load torque logged every 10 s,
        input-referred, settling as the grease finds its film. Time-scaled."""
        t = np.arange(0.0, minutes * 60.0 + 10.0, 10.0)
        tau = 180.0
        torque = self._no_load_end_nm + (self._no_load_start_nm - self._no_load_end_nm) * np.exp(-t / tau)
        torque += self._rng.normal(0.0, 0.003, t.size)
        self._temp_c = 22.0 + 9.0 * (1.0 - np.exp(-minutes * 60.0 / 400.0))
        return {"time_s": t.tolist(), "torque_nm": torque.round(4).tolist()}

    # --- stall torque constant ------------------------------------------------

    def stall_torque_nm(self, current_a):
        """Dyno locked, q-axis current commanded, output torque from the
        transducer. Below ~2 A the reducer's static friction eats the torque."""
        friction = 1.6
        raw = self._kt * RATIO * 0.86 * current_a
        out = max(0.0, raw - friction) if current_a > 0 else 0.0
        return round(out + self._rng.normal(0.0, 0.08), 3)

    # --- efficiency map ---------------------------------------------------------

    def operating_point(self, speed_rpm, torque_nm):
        """Dyno holds torque_nm at speed_rpm on the output; returns shaft
        power from the transducer and electrical power from the analyzer."""
        mech_w = torque_nm * speed_rpm * 2.0 * np.pi / 60.0
        load_frac = torque_nm / RATED_TORQUE_NM
        speed_frac = speed_rpm / 30.0
        eff = self._eff_rated * (1.0 - 0.28 * (1.0 - load_frac) ** 2) * (1.0 - 0.06 * max(0.0, speed_frac - 1.0))
        eff += self._rng.normal(0.0, 0.004)
        elec_w = mech_w / eff
        return {"mech_w": round(mech_w, 2), "elec_w": round(elec_w, 2), "bus_a": round(elec_w / BUS_V, 3)}

    # --- ripple ---------------------------------------------------------------

    def ripple_capture(self, speed_rpm, load_nm):
        """One output revolution at low speed under constant load, torque
        against angle from the transducer at 0.1 deg. The wave generator
        puts two cycles per input revolution on the output: 2 x ratio per
        output revolution."""
        angle = np.arange(0.0, 360.0, 0.1)
        rad = np.deg2rad(angle)
        amp = load_nm * self._ripple_pct / 100.0 / 2.0
        torque = load_nm + amp * np.sin(2 * RATIO * rad) + 0.25 * amp * np.sin(RATIO * rad + 0.7) + 0.15 * amp * np.sin(2 * rad)
        torque += self._rng.normal(0.0, 0.02, angle.size)
        return {"angle_deg": angle.round(1).tolist(), "torque_nm": torque.round(4).tolist()}

    def unload(self):
        pass

    def __del__(self):
        print("Dyno unloaded, drive disabled, bench released")
