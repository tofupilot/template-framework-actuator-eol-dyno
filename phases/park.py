def park(measurements, bench, log):
    """Teardown: dyno unloaded, drive disabled, housing temperature read
    so a hot actuator is not handed to the next station."""
    bench.unload()
    bench.disable()
    measurements.temperature_end_c = bench.temperature_c()
    log.info(f"Parked, housing at {measurements.temperature_end_c} C")
