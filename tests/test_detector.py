import pytest


from openclem.structures import DetectorSettings, ConnectionSettings, ConnectionType
from openclem.detectors.demo.demo import DemoDetector


# import fixtures from test_structures.py
from test_structures import detector_settings, connection_settings_software


@pytest.fixture
def detector(detector_settings: DetectorSettings) -> DemoDetector:
    return DemoDetector(detector_settings)

def test_demo_detector(detector: DemoDetector,  detector_settings: DetectorSettings):

    det = detector

    assert det.name == detector_settings.name
    assert det.connection.type == detector_settings.connection.type
    assert det.connection.settings == detector_settings.connection.settings
    assert det.pixel_size == detector_settings.pixel_size
    assert det.resolution == detector_settings.resolution
    assert det.exposure_mode == detector_settings.exposure_mode
    assert det.trigger_edge == detector_settings.trigger_edge
    assert det.trigger_source == detector_settings.trigger_source
    assert det.camera == None

    det.init_camera()
    assert det.camera == "DemoCamera"