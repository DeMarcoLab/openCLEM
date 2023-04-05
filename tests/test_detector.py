import pytest


from openclem.structures import DetectorSettings, ConnectionSettings, ConnectionType
from openclem.detectors.demo.demo import DemoDetector


@pytest.fixture
def det_settings():
    return DetectorSettings(
        name="demo",
        connection=ConnectionSettings(
            type=ConnectionType.SOFTWARE,
            settings=None,
        ),
        pixel_size=1e-6,
        resolution=[2048, 2048],
    )


def test_demo_detector(det_settings: DetectorSettings):
    det = DemoDetector(det_settings)

    assert det.name == det_settings.name
    assert det.connection.type == ConnectionType.SOFTWARE
    assert det.pixel_size == det_settings.pixel_size
    assert det.resolution == det_settings.resolution
    assert det.exposure_mode == det_settings.exposure_mode
    assert det.trigger_edge == det_settings.trigger_edge
    assert det.trigger_source == det_settings.trigger_source
    assert det.camera == None
