from time import sleep
from conftest import wait
import logging
import pytest

from requests import post

log = logging.getLogger(__name__)
METHOD_ERROR_CODE = -32000
METHOD_ERROR_MSG = "Method execution error"
PARSE_ERROR_CODE = -32700
PARSE_ERROR_MSG = "Parse error"
INVALID_REQUEST_CODE = -32600
INVALID_REQUEST_MSG = "Invalid request"
METHOD_NOT_FOUND_CODE = -32601
METHOD_NOT_FOUND_MSG = "Method not found"
INVALID_PARAMS_CODE = -32602
INVALID_PARAMS_MSG = "Invalid params"


def test_sanity(get_sensor_info, get_sensor_reading):
    sensor_info = get_sensor_info()

    sensor_name = sensor_info.name
    assert isinstance(sensor_name, str), "Sensor name is not a string"

    sensor_hid = sensor_info.hid
    assert isinstance(sensor_hid, str), "Sensor hid is not a string"

    sensor_model = sensor_info.model
    assert isinstance(sensor_model, str), "Sensor model is not a string"

    sensor_firmware_version = sensor_info.firmware_version
    assert isinstance(
        sensor_firmware_version, int
    ), "Sensor firmware version is not a int"

    sensor_reading_interval = sensor_info.reading_interval
    assert isinstance(
        sensor_reading_interval, int
    ), "Sensor reading interval is not a string"

    sensor_reading = get_sensor_reading()
    assert isinstance(
        sensor_reading, float
    ), "Sensor doesn't seem to register temperature"

    log.info("Sanity test passed")


def test_set_sensor_name(get_sensor_info, set_sensor_name):
    """
    1. Set sensor name to "new_name".
    2. Get sensor_info.
    3. Validate that current sensor name matches the name set in Step 1.
    """
    log.info("Set  sensor name different from default")
    new_sensor_name = "Updated_sensor_name"
    set_sensor_name(new_sensor_name)

    log.info("Get sensor_info")
    updated_sensor_info = get_sensor_info()

    log.info("Validate that current sensor name matches the name set in Step 1")
    current_sensor_name = updated_sensor_info.name
    assert (
        current_sensor_name == new_sensor_name
    ), f"Sensor name was not updated, expected name:{new_sensor_name}"


def test_set_empty_sensor_name(get_sensor_info, set_sensor_name):
    """
    1. Get original sensor name.
    2. Set sensor name to an empty string.
    3. Validate that sensor responds with an error.
    4. Get current sensor name.
    5. Validate that sensor name didn't change.
    """

    log.info("Get original sensor name")
    sensor_info = get_sensor_info()
    original_sensor_name = sensor_info.name

    log.info("Set sensor name to an empty string")
    set_empty_sensor_name_response = set_sensor_name("")

    assert set_empty_sensor_name_response.get(
        "code"
    ) and set_empty_sensor_name_response.get(
        "message"
    ), "Sensor response doesn't seem to be an error"
    assert (
        set_empty_sensor_name_response.get("code") == METHOD_ERROR_CODE
    ), "Error code does not match expected"
    assert (
        set_empty_sensor_name_response.get("message") == METHOD_ERROR_MSG
    ), "Error message does not match expected"

    log.info("Get current sensor name")
    sensor_info = get_sensor_info()
    current_sensor_name = sensor_info.name

    log.info("Validate that sensor name didn't change")
    assert original_sensor_name == current_sensor_name, "Sensor name is invalid!"


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
    log.info("Set sensor reading interval to 1")
    new_reading_interval = 1
    updated_sensor_info = set_sensor_reading_interval(new_reading_interval)

    log.info("Validate that sensor reading interval is set to interval from Step 1")
    assert (
        updated_sensor_info.reading_interval == new_reading_interval
    ), f"Sensor reading interval was not updated, expected interval {new_reading_interval}"

    log.info("Get sensor reading")
    sensor_reading_before_wait = get_sensor_reading()

    log.info("Wait for interval specified in Step 1")
    sleep(new_reading_interval)

    log.info("Get sensor reading")
    sensor_reading_after_wait = get_sensor_reading()

    log.info("Validate that reading from tep 4 doesn't equal reading from Step 6")
    assert (
        sensor_reading_before_wait != sensor_reading_after_wait
    ), f"Sensor readings after {new_reading_interval} second of waiting are equal to readings before waiting"


@pytest.mark.parametrize("invalid_reading_interval", [0.3, -1])
def test_set_invalid_sensor_reading_interval(
    get_sensor_info, set_sensor_reading_interval, invalid_reading_interval
):
    """
    1. Get original sensor reading interval.
    2. Set interval to < 1
    3. Validate that sensor responds with an error.
    4. Get current sensor reading interval.
    5. Validate that sensor reading interval didn't change.
    """

    log.info("Get original sensor reading interval.")
    sensor_info = get_sensor_info()
    original_sensor_reading_interval = sensor_info.reading_interval

    log.info("Set interval to < 1")
    set_invalid_reading_interval_response = set_sensor_reading_interval(
        invalid_reading_interval
    )
    assert set_invalid_reading_interval_response.get(
        "code"
    ) and set_invalid_reading_interval_response.get(
        "message"
    ), "Sensor response doesn't seem to be an error"
    assert (
        set_invalid_reading_interval_response.get("code") == METHOD_ERROR_CODE
    ), "Error code does not match expected"
    assert (
        set_invalid_reading_interval_response.get("message") == METHOD_ERROR_MSG
    ), "Error message does not match expected"

    log.info("Get current sensor reading interval")
    sensor_info = get_sensor_info()
    current_sensor_reading_interval = sensor_info.reading_interval

    log.info("Validate that sensor reading interval didn't change")
    assert (
        original_sensor_reading_interval == current_sensor_reading_interval
    ), "Sensor reading interval is out of valid range!"


@pytest.mark.parametrize(
    "payload,expected_error_code,expected_error_msg",
    [
        (
            '{"method": "get_methods" "jsonrpc": "2.0", "id": 1}',
            PARSE_ERROR_CODE,
            PARSE_ERROR_MSG,
        ),
        (
            '{"method": "get_methods", "jsonrpc": "1.0", "id": 1}',
            INVALID_REQUEST_CODE,
            INVALID_REQUEST_MSG,
        ),
        (
            '{"method": "get_method", "jsonrpc": "2.0", "id": 1}',
            METHOD_NOT_FOUND_CODE,
            METHOD_NOT_FOUND_MSG,
        ),
        (
            '{"method": "set_reading_interval", "params": {"intervall":  1 }, "jsonrpc": "2.0", "id": 1}',
            INVALID_PARAMS_CODE,
            INVALID_PARAMS_MSG,
        ),
        (
            '{"method": "set_name", "params": {"name":  "" }, "jsonrpc": "2.0", "id": 1}',
            METHOD_ERROR_CODE,
            METHOD_ERROR_MSG,
        ),
    ],
)
def test_sensor_errors(
    sensor_host,
    sensor_port,
    sensor_pin,
    payload,
    expected_error_code,
    expected_error_msg,
):
    sensor_response = post(
        f"{sensor_host}:{sensor_port}/rpc",
        data=payload,
        headers={"Authorization": sensor_pin},
    )

    log.info("Check that the sensor responds with HTTP code 200")
    assert (
        sensor_response.status_code == 200
    ), "Wrong status code from sensor in response in invalid request"

    sensor_response_json = sensor_response.json()

    log.info("Check that the sensor responds with error")
    assert (
        "error" in sensor_response_json
    ), "Sensor did not respond with error to invalid request"

    error_from_sensor = sensor_response_json["error"]

    log.info("Check that the sensor responds with the correct error code")
    assert (
        error_from_sensor.get("code") == expected_error_code
    ), "Sensor did not respond with correct error code"
    log.info("Check that the sensor responds with the correct error message")
    assert (
        error_from_sensor.get("message") == expected_error_msg
    ), "Sensor did not respond with correct error message"


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

    log.info("Upgrade firmware version +1")
    max_firmware_version = 15
    current_firmware_version = None

    while current_firmware_version != max_firmware_version:
        sensor_info = get_sensor_info()
        log.info("Get original sensor firmware version")
        firmware_version_before_update = sensor_info.firmware_version
        log.info("Request firmware update")
        update_firmware()
        wait(
            func=get_sensor_info,
            condition=lambda x: isinstance(x, dict),
            tries=15,
            timeout=1,
        )
        updated_sensor_info = get_sensor_info()
        log.info("Get current sensor firmware version")
        current_firmware_version = updated_sensor_info.firmware_version
        log.info(
            "Validate that current firmware version is +1 to previous firmware version"
        )
        assert (
            current_firmware_version == firmware_version_before_update + 1
        ), "Sensor firmware version was not updated"
        log.info(f"Current firmware version: {current_firmware_version}")

    log.info("Request another firmware update")
    updated_sensor_info = update_firmware()

    wait(
        func=get_sensor_info,
        condition=lambda x: isinstance(x, dict),
        tries=15,
        timeout=1,
    )
    sensor_info = get_sensor_info()
    firmware_version_after_update = sensor_info.firmware_version

    log.info("Validate that sensor doesn't update and responds appropriately")
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
    log.info("Get original sensor info")
    sensor_info = get_sensor_info()
    sensor_info_before_reboot = sensor_info

    log.info("Reboot sensor")
    reboot_response = reboot()
    assert (
        reboot_response == "rebooting"
    ), "Sensor did not return proper text in response to reboot request..."

    log.info("Wait for sensor to come back online")
    wait(
        func=get_sensor_info,
        condition=lambda x: isinstance(x, dict),
        tries=15,
        timeout=1,
    )
    sensor_info = get_sensor_info()
    sensor_info_after_reboot = sensor_info

    log.info("Validate that info from Step 1 is equal to info from Step 4")
    assert (
        sensor_info_before_reboot == sensor_info_after_reboot
    ), "Sensor info after reboot does not match sensor info before reboot"
