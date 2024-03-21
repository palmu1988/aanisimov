def test_sanity(
    get_sensor_info,
    get_sensor_reading,
    set_sensor_name,
    set_reading_interval,
    reset_to_factory,
):

    set_sensor_name("Updated_sensor_name")

    set_reading_interval(5)

    sensor_info = get_sensor_info()

    sensor_name = sensor_info.get("name")
    assert isinstance(sensor_name, str), "Sensor name is not a string"

    assert sensor_name == "Updated_sensor_name", "Sensor name was not updated"

    sensor_hid = sensor_info.get("hid")
    assert isinstance(sensor_hid, str), "Sensor hid is not a string"

    sensor_model = sensor_info.get("model")
    assert isinstance(sensor_model, str), "Sensor model is not a string"

    sensor_firmware_version = sensor_info.get("firmware_version")
    assert isinstance(
        sensor_firmware_version, int
    ), "Sensor firmware version is not a int"

    sensor_reading_interval = sensor_info.get("reading_interval")
    assert isinstance(
        sensor_reading_interval, int
    ), "Sensor reading interval is not a string"

    assert sensor_reading_interval == 5, "Sensor reading interval was not updated"

    sensor_reading = get_sensor_reading()
    assert isinstance(
        sensor_reading, float
    ), "Sensor doesn't seem to register temperature"

    reset_to_factory()

    print("Sanity test passed")
