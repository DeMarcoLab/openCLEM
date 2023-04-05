import pytest

from openclem.structures import (ConnectionSettings, ConnectionType,
                                 DetectorSettings, ExposureMode, ImageSettings,
                                 LaserControllerSettings, LaserSettings,
                                 MicroscopeSettings, ObjectiveSettings,
                                 SerialSettings, SocketSettings,
                                 SynchroniserMessage, SynchroniserSettings,
                                 TriggerEdge, TriggerSource, ImageMode)

######### ConnectionSettings #########

@pytest.fixture
def serial_settings() -> SerialSettings:
    return SerialSettings(
        port="COM1",
        baudrate=9600,
        timeout=1,
    )


@pytest.fixture
def socket_settings() -> SocketSettings:
    return SocketSettings(
        host="localhost",
        port=5000,
        timeout=1,
    )

@pytest.fixture
def connection_settings_serial(serial_settings: SerialSettings) -> ConnectionSettings:
    return ConnectionSettings(
        type=ConnectionType.SERIAL,
        settings=serial_settings,
    )

@pytest.fixture
def connection_settings_socket(socket_settings: SocketSettings) -> ConnectionSettings:
    return ConnectionSettings(
        type=ConnectionType.SOCKET,
        settings=socket_settings,
    )

@pytest.fixture
def connection_settings_software() -> ConnectionSettings:
    return ConnectionSettings(
        type=ConnectionType.SOFTWARE,
        settings=None,
    )


def test_serial_settings(serial_settings:SerialSettings):

    assert serial_settings.port == "COM1"
    assert serial_settings.baudrate == 9600
    assert serial_settings.timeout == 1

    # __to_dict__
    assert serial_settings.__to_dict__() == {
        "port": "COM1",
        "baudrate": 9600,
        "timeout": 1,
    }

    # __from_dict__
    assert serial_settings.__from_dict__(serial_settings.__to_dict__()) == serial_settings

def test_socket_settings(socket_settings:SocketSettings):
    
    assert socket_settings.host == "localhost"
    assert socket_settings.port == 5000
    assert socket_settings.timeout == 1

    # __to_dict__
    assert socket_settings.__to_dict__() == {
        "host": "localhost",
        "port": 5000,
        "timeout": 1,
    }

    # __from_dict__
    assert socket_settings.__from_dict__(socket_settings.__to_dict__()) == socket_settings


def test_connection_settings_serial(connection_settings_serial: ConnectionSettings):
    assert connection_settings_serial.type == ConnectionType.SERIAL
    assert connection_settings_serial.settings.port == "COM1"
    assert connection_settings_serial.settings.baudrate == 9600
    assert connection_settings_serial.settings.timeout == 1

    # __to_dict__
    assert connection_settings_serial.__to_dict__() == {
        "type": "SERIAL",
        "settings": {
            "port": "COM1",
            "baudrate": 9600,
            "timeout": 1,
        },
    }

    # __from_dict__
    assert connection_settings_serial.__from_dict__(connection_settings_serial.__to_dict__()) == connection_settings_serial


def test_connection_settings_socket(connection_settings_socket: ConnectionSettings):
    assert connection_settings_socket.type == ConnectionType.SOCKET
    assert connection_settings_socket.settings.host == "localhost"
    assert connection_settings_socket.settings.port == 5000
    assert connection_settings_socket.settings.timeout == 1

    # __to_dict__
    assert connection_settings_socket.__to_dict__() == {
        "type": "SOCKET",
        "settings": {
            "host": "localhost",
            "port": 5000,
            "timeout": 1,
        },
    }

    # __from_dict__
    assert connection_settings_socket.__from_dict__(connection_settings_socket.__to_dict__()) == connection_settings_socket

def test_connection_settings_software(connection_settings_software: ConnectionSettings):
    assert connection_settings_software.type == ConnectionType.SOFTWARE
    assert connection_settings_software.settings == None

    # __to_dict__
    assert connection_settings_software.__to_dict__() == {
        "type": "SOFTWARE",
        "settings": None,
    }

    # __from_dict__
    assert connection_settings_software.__from_dict__(connection_settings_software.__to_dict__()) == connection_settings_software


######### LaserSettings #########

@pytest.fixture
def laser_settings(connection_settings_serial: ConnectionSettings) -> LaserSettings:

    return LaserSettings(
        name="demo",
        serial_id=1,
        wavelength=408,
        power=0.5,
        exposure_time=0.1,
        enabled=True,
        colour=(255, 0, 0),
    )


def test_laser_settings(laser_settings: LaserSettings):

    assert laser_settings.name == "laser"
    assert laser_settings.serial_id == 1
    assert laser_settings.wavelength == 408
    assert laser_settings.power == 0.5
    assert laser_settings.exposure_time == 0.1
    assert laser_settings.enabled == True
    assert laser_settings.colour == (255, 0, 0)

    # __to_dict__
    assert laser_settings.__to_dict__() == {
        "name": "laser",
        "serial_id": 1,
        "wavelength": 408,
        "power": 0.5,
        "exposure_time": 0.1,
        "enabled": True,
        "colour": (255, 0, 0),
    }

    # __from_dict__
    assert laser_settings.__from_dict__(laser_settings.__to_dict__()) == laser_settings

######### LaserControllerSettings #########

@pytest.fixture
def laser_controller_settings(connection_settings_serial: ConnectionSettings) -> LaserControllerSettings:

    return LaserControllerSettings(
        name="demo",
        laser="laser",
        connection=connection_settings_serial,
    )


def test_laser_controller_settings(laser_controller_settings: LaserControllerSettings):
    
    assert laser_controller_settings.name == "laser_controller"
    assert laser_controller_settings.laser == "laser"
    assert laser_controller_settings.connection.type == ConnectionType.SERIAL
    assert laser_controller_settings.connection.settings.port == "COM1"
    assert laser_controller_settings.connection.settings.baudrate == 9600
    assert laser_controller_settings.connection.settings.timeout == 1

    # __to_dict__
    assert laser_controller_settings.__to_dict__() == {
        "name": "laser_controller",
        "laser": "demo",
        "connection": {
            "type": "SERIAL",
            "settings": {
                "port": "COM1",
                "baudrate": 9600,
                "timeout": 1,
            },
        },
    }

    # __from_dict__
    assert laser_controller_settings.__from_dict__(laser_controller_settings.__to_dict__()) == laser_controller_settings



######### DetectorSettings #########

@pytest.fixture
def detector_settings(connection_settings_software: ConnectionSettings) -> DetectorSettings:
    return DetectorSettings(
        name="demo",
        connection=connection_settings_software,
        pixel_size=1e-6,
        resolution=[2048, 2048],
        trigger_source=TriggerSource.EXTERNAL,
        trigger_edge=TriggerEdge.RISING,
        exposure_mode=ExposureMode.TRIGGER_WIDTH,
        timeout=1000,
    )


def test_detector_settings(detector_settings: DetectorSettings):
        
    assert detector_settings.name == "demo"
    assert detector_settings.connection.type == ConnectionType.SOFTWARE
    assert detector_settings.connection.settings == None
    assert detector_settings.pixel_size == 1e-6
    assert detector_settings.resolution == [2048, 2048]
    assert detector_settings.trigger_source == TriggerSource.EXTERNAL
    assert detector_settings.trigger_edge == TriggerEdge.RISING
    assert detector_settings.exposure_mode == ExposureMode.TRIGGER_WIDTH

    # __to_dict__
    assert detector_settings.__to_dict__() == {
        "name": "demo",
        "connection": {
            "type": "SOFTWARE",
            "settings": None,
        },
        "pixel_size": 1e-06,
        "resolution": [2048, 2048],
        "trigger_source": "EXTERNAL",
        "trigger_edge": "RISING",
        "exposure_mode": "TRIGGER_WIDTH",
        "timeout": 1000,
    }

    # __from_dict__
    assert detector_settings.__from_dict__(detector_settings.__to_dict__()) == detector_settings



######### ObjectiveSettings #########

@pytest.fixture
def objective_settings(connection_settings_socket: ConnectionSettings) -> ObjectiveSettings:
    return ObjectiveSettings(
        name="demo",
        magnification=10,
        connection=connection_settings_socket
    )


def test_objective_settings(objective_settings: ObjectiveSettings):
            
    assert objective_settings.name == "demo"
    assert objective_settings.magnification == 10
    assert objective_settings.connection.type == ConnectionType.SOCKET
    assert objective_settings.connection.settings.host == "localhost"
    assert objective_settings.connection.settings.port == 5000
    assert objective_settings.connection.settings.timeout == 1

    # __to_dict__
    assert objective_settings.__to_dict__() == {
        "name": "demo",
        "magnification": 10,
        "connection": {
            "type": "SOCKET",
            "settings": {
                "host": "localhost",
                "port": 5000,
                "timeout": 1,
            },
        },
    }

    # __from_dict__
    assert objective_settings.__from_dict__(objective_settings.__to_dict__()) == objective_settings

######### SynchroniserSettings #########

@pytest.fixture
def synchroniser_settings(connection_settings_serial: ConnectionSettings) -> SynchroniserSettings:
    return SynchroniserSettings(
        name="demo",
        pins={"l1":1, "l2":2, "l3":3, "l4":4},
        connection=connection_settings_serial,
    )


def test_synchroniser_settings(synchroniser_settings: SynchroniserSettings):
                
        assert synchroniser_settings.name == "demo"
        assert synchroniser_settings.pins == {"l1":1, "l2":2, "l3":3, "l4":4}
        assert synchroniser_settings.connection.type == ConnectionType.SERIAL
        assert synchroniser_settings.connection.settings.port == "COM1"
        assert synchroniser_settings.connection.settings.baudrate == 9600
        assert synchroniser_settings.connection.settings.timeout == 1
    
        # __to_dict__
        assert synchroniser_settings.__to_dict__() == {
            "name": "demo",
            "pins": {"l1":1, "l2":2, "l3":3, "l4":4},
            "connection": {
                "type": "SERIAL",
                "settings": {
                    "port": "COM1",
                    "baudrate": 9600,
                    "timeout": 1,
                },
            },
        }
    
        # __from_dict__
        assert synchroniser_settings.__from_dict__(synchroniser_settings.__to_dict__()) == synchroniser_settings



######### SynchroniserMessage #########

@pytest.fixture
def synchroniser_message() -> SynchroniserMessage:
    return SynchroniserMessage(
        exposures=[1000, 1000, 1000, 1000],
        pins = {"l1":1, "l2":2, "l3":3, "l4":4},
        mode=ImageMode.LIVE,
        trigger_edge=TriggerEdge.RISING,
        n_slices=4,
    )


def test_synchroniser_message(synchroniser_message: SynchroniserMessage):

    assert synchroniser_message.exposures == [1000, 1000, 1000, 1000]
    assert synchroniser_message.pins == {"l1":1, "l2":2, "l3":3, "l4":4}
    assert synchroniser_message.mode == ImageMode.LIVE
    assert synchroniser_message.trigger_edge == TriggerEdge.RISING
    assert synchroniser_message.n_slices == 4

    # __to_dict__
    assert synchroniser_message.__to_dict__() == {
        "exposures": [1000, 1000, 1000, 1000],
        "pins": {"l1":1, "l2":2, "l3":3, "l4":4},
        "mode": "LIVE",
        "trigger_edge": "RISING",
        "n_slices": 4,
    }

    # __from_dict__
    assert synchroniser_message.__from_dict__(synchroniser_message.__to_dict__()) == synchroniser_message


######### MicroscopeSettings #########

@pytest.fixture
def microscope_settings(
    connection_settings_serial: ConnectionSettings,
    connection_settings_software: ConnectionSettings,
    connection_settings_socket: ConnectionSettings,
    laser_settings: LaserSettings,
    laser_controller_settings: LaserControllerSettings,
    detector_settings: DetectorSettings,
    objective_settings: ObjectiveSettings,
    synchroniser_settings: SynchroniserSettings,

) -> MicroscopeSettings:
    return MicroscopeSettings(
        name="demo",
        lasers=[laser_settings],
        laser_controller=laser_controller_settings,
        detector=detector_settings,
        objective_stage=objective_settings,
        synchroniser=synchroniser_settings,
        online=True,
    )

def test_microscope_settings(microscope_settings: MicroscopeSettings):

    assert microscope_settings.name == "demo"
    assert microscope_settings.lasers[0].name == "demo"
    assert microscope_settings.laser_controller.name == "demo"
    assert microscope_settings.detector.name == "demo"
    assert microscope_settings.objective_stage.name == "demo"
    assert microscope_settings.synchroniser.name == "demo"
    assert microscope_settings.online == True

    # __from_dict__
    assert microscope_settings.__from_dict__(microscope_settings.__to_dict__()) == microscope_settings