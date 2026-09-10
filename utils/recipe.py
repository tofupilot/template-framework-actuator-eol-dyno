"""End-of-line dyno recipe for a humanoid joint actuator: a frameless motor
on a 100:1 harmonic reducer with an absolute output encoder, driven over
EtherCAT from a 48 V bus.

Datasheet values the limits derive from: motor torque constant 0.105 Nm/A
(measured under stall with a transducer in arXiv 2202.12395), reducer
ratio 100, rated output 60 Nm at 30 rpm, peak 120 Nm. Harmonic Drive
specifies the no-load running torque after a run-in of 2 h at 2000 rpm
input; this template runs a time-scaled 10 min run-in and reads it at the
end. Efficiency and ripple limits are the pack maker's own; Kistler-class
transducers resolve 0.05 % of range, so the bench is not the limit."""

RATIO = 100
MOTOR_KT_NM_PER_A = 0.105
RATED_TORQUE_NM = 60.0
PEAK_TORQUE_NM = 120.0
RATED_SPEED_RPM = 30.0  # output
BUS_V = 48.0

RUN_IN_MINUTES = 10.0
RUN_IN_INPUT_RPM = 2000.0
NO_LOAD_TORQUE_MAX_NM = 0.20  # input-referred at 2000 rpm, 20 C

KT_CURRENT_STEPS_A = [0.0, 5.0, 10.0, 15.0, 20.0, 25.0]
KT_OUTPUT_EXPECTED = MOTOR_KT_NM_PER_A * RATIO  # 10.5 Nm/A before losses

MAP_SPEEDS_RPM = [5.0, 15.0, 30.0, 45.0]
MAP_TORQUES_NM = [15.0, 30.0, 45.0, 60.0]

RIPPLE_SPEED_RPM = 3.0
RIPPLE_LOAD_NM = 30.0

TIME_SCALE = 0.0  # mock returns the run-in in one call
