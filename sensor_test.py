from time import sleep
from conftest import wait


def test_sanity(get_sensor_info, get_sensor_reading):
    sensor_info = get_sensor_info()

    sensor_name = sensor_info.get("name")
    assert isinstance(sensor_name, str), "Sensor name is not a string"

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

    sensor_reading = get_sensor_reading()
    assert isinstance(
        sensor_reading, float
    ), "Sensor doesn't seem to register temperature"

    print("Sanity test passed")


def test_set_sensor_name(get_sensor_info, set_sensor_name):
    """
    1. Set sensor name to "new_name".
    2. Get sensor_info.
    3. Validate that current sensor name matches the name set in Step 1.
    """
    print("Set  sensor name different from default")
    new_sensor_name = "Updated_sensor_name"
    set_sensor_name(new_sensor_name)

    print("Get sensor_info")
    updated_sensor_info = get_sensor_info()

    print("Validate that current sensor name matches the name set in Step 1")
    current_sensor_name = updated_sensor_info.get("name")
    assert (
        current_sensor_name == new_sensor_name
    ), f"Sensor name was not updated, expected name:{new_sensor_name}"


def test_set_sensor_reading_interval(
    get_sensor_info, set_sensor_reading_interval, get_sensor_reading
):
    """
    1. Set sensor reading interval to 1.
    2. Get sensor info.
    3. Validate that sensor reading interval is set to interval from Step 1.
    4. Get sensor reading.
    5. Wait for interval specified in Step 1.
    6. Get sensor reading.
    7. Validate that reading from Step 4 doesn't equal reading from Step 6.
    """
    print("Set sensor reading interval to 1")
    new_reading_interval = 1
    updated_sensor_info = set_sensor_reading_interval(new_reading_interval)

    print("Validate that sensor reading interval is set to interval from Step 1")
    current_reading_interval = updated_sensor_info.get("reading_interval")
    assert (
        current_reading_interval == new_reading_interval
    ), f"Sensor reading interval was not updated, expected interval {new_reading_interval}"

    print("Get sensor reading")
    sensor_reading_before_wait = get_sensor_reading()

    print("Wait for interval specified in Step 1")
    sleep(new_reading_interval)

    print("Get sensor reading")
    sensor_reading_after_wait = get_sensor_reading()

    print("Validate that reading from tep 4 doesn't equal reading from Step 6")
    assert (
        sensor_reading_before_wait != sensor_reading_after_wait
    ), f"Sensor readings after {new_reading_interval} second of waiting are equal to readings before waiting"


def test_update_sensor_firmware(get_sensor_info, update_firmware):
    """
    1. Get original sensor firmware version.
    2. Request firmware update.
    3. Get current sensor firmware version.
    4. Validate that current firmware version is +1 to original firmware version.
    5. Repeat steps 1-4 until sensor is at max_firmware_version - 1.
    6. Update sensor to max firmware version.
    7. Validate that sensor is at max firmware version.
    8. Request another firmware update.
    9. Validate that sensor doesn't update and responds appropriately.
    10. Validate that sensor firmware version doesn't change if it's at maximum value.
    """

    print("Upgrade firmware version +1")
    max_firmware_version = 15
    current_firmware_version = None

    while current_firmware_version != max_firmware_version:
        sensor_info = get_sensor_info()
        print("Get original sensor firmware version")
        firmware_version_before_update = sensor_info.get("firmware_version")
        print("Request firmware update")
        update_firmware()
        wait(
            func=get_sensor_info,
            condition=lambda x: isinstance(x, dict),
            tries=15,
            timeout=1,
        )
        updated_sensor_info = get_sensor_info()
        print("Get current sensor firmware version")
        current_firmware_version = updated_sensor_info.get("firmware_version")
        print(
            "Validate that current firmware version is +1 to previous firmware version"
        )
        assert (
            current_firmware_version == firmware_version_before_update + 1
        ), "Sensor firmware version was not updated"
        print(f"Current firmware version: {current_firmware_version}")

    print("Request another firmware update")
    updated_sensor_info = update_firmware()

    wait(
        func=get_sensor_info,
        condition=lambda x: isinstance(x, dict),
        tries=15,
        timeout=1,
    )
    sensor_info = get_sensor_info()
    firmware_version_after_update = sensor_info.get("firmware_version")

    print("Validate that sensor doesn't update and responds appropriately")
    assert (
        updated_sensor_info == "already at latest firmware version"
        and firmware_version_after_update == max_firmware_version
    ), "Something went wrong and firmware version was updated unexpectedly"


def test_reboot(get_sensor_info, reboot):
    """
    Steps:
        1. Get original sensor info.
        2. Reboot sensor.
        3. Wait for sensor to come back online.
        4. Get current sensor info.
        5. Validate that info from Step 1 is equal to info from Step 4.
    """
    print("Get original sensor info")
    sensor_info_before_reboot = get_sensor_info()

    print("Reboot sensor")
    reboot_response = reboot()
    assert (
        reboot_response == "rebooting"
    ), "Sensor did not return proper text in response to reboot request..."

    print("Wait for sensor to come back online")
    sensor_info_after_reboot = wait(
        func=get_sensor_info,
        condition=lambda x: isinstance(x, dict),
        tries=15,
        timeout=1,
    )

    print("Validate that info from Step 1 is equal to info from Step 4")
    assert (
        sensor_info_before_reboot == sensor_info_after_reboot
    ), "Sensor info after reboot does not match sensor info before reboot"
