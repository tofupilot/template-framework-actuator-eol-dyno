def identify(measurements, bench, unit, log):
    """Setup: EtherCAT link up, firmware and drive configuration read
    before the dyno moves. A drive with the wrong pole-pair count or
    current limit would produce plausible torque numbers at the wrong
    operating point."""
    ident = bench.drive_identify()
    measurements.firmware_version = ident["firmware"]
    measurements.drive_config = bench.drive_config()
    measurements.temperature_start_c = bench.temperature_c()
    unit.metadata["reducer_ratio"] = ident["ratio"]
    unit.metadata["encoder_bits"] = ident["encoder_bits"]
    log.info(f"Actuator {unit.serial_number}: fw {ident['firmware']}, ratio {ident['ratio']}:1, {ident['encoder_bits']}-bit output encoder, {measurements.temperature_start_c} C")
