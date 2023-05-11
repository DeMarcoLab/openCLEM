import numpy as np
from typing import Union
import tifffile as tff
import json
import os
from pathlib import Path
import traceback
from dataclasses import dataclass
from enum import Enum


class TriggerEdge(Enum):
    """Trigger edge"""

    RISING = 1
    FALLING = 2


class TriggerSource(Enum):
    """Trigger source"""

    SOFTWARE = 1
    EXTERNAL = 2
    INTERNAL = 3


class ExposureMode(Enum):
    """Exposure mode"""

    TIMED = 1
    TRIGGER_WIDTH = 2


class ImageFormat(Enum):
    """Image format"""

    TIFF = 1
    PNG = 2
    JPG = 3


class ImageMode(Enum):
    """Image mode"""

    SINGLE = "single"
    LIVE = "live"


# TODO: merge with SerialSettings into a CommsSettings class?
@dataclass
class SocketSettings:
    """Settings class for socket connections"""

    host: str
    port: int
    timeout: int = 5.0  # TODO: universal timing

    @staticmethod
    def __from_dict__(settings: dict) -> "SocketSettings":
        if settings is None:
            return None

        socket_settings = SocketSettings(
            host=settings["host"],
            port=settings["port"],
            timeout=settings["timeout"],
        )
        return socket_settings

    def __to_dict__(self) -> dict:
        return {
            "host": self.host,
            "port": self.port,
            "timeout": self.timeout,
        }


@dataclass
class SerialSettings:
    """Serial settings"""

    port: str = None
    baudrate: int = 9600
    timeout: float = 0.1

    @staticmethod
    def __from_dict__(settings: dict) -> "SerialSettings":
        # TODO: check if this is ok
        if settings is None:
            return None
        return SerialSettings(
            port=settings["port"],
            baudrate=settings["baudrate"],
            timeout=settings["timeout"],
        )

    def __to_dict__(self) -> dict:
        if self is None:
            return None

        return {
            "port": self.port,
            "baudrate": self.baudrate,
            "timeout": self.timeout,
        }


class ConnectionType(Enum):
    SERIAL = "serial"
    SOCKET = "socket"
    SOFTWARE = "software"


@dataclass
class ConnectionSettings:
    type: ConnectionType
    settings: Union[SerialSettings, SocketSettings]

    def __to_dict__(self) -> dict:
        return {
            "type": self.type.name,
            "settings": self.settings.__to_dict__()
            if self.settings is not None
            else None,
        }

    @staticmethod
    def __from_dict__(settings: dict) -> "ConnectionSettings":
        connection_type = ConnectionType[settings["type"].upper()]
        if connection_type == ConnectionType.SERIAL:
            connection_settings = ConnectionSettings(
                type=connection_type,
                settings=SerialSettings.__from_dict__(settings.get("settings", None)),
            )
        elif connection_type == ConnectionType.SOCKET:
            connection_settings = ConnectionSettings(
                type=connection_type,
                settings=SocketSettings.__from_dict__(settings.get("settings")),
            )
        elif connection_type == ConnectionType.SOFTWARE:
            connection_settings = ConnectionSettings(
                type=connection_type,
                settings=None,
            )
        else:
            raise ValueError(f"Invalid connection type: {connection_type}")
        return connection_settings

@dataclass
class WorkflowSettings:
    n_rows: int = 1
    n_cols: int = 1
    dx: float = 0.0
    dy: float = 0.0
    n_slices: int = 1
    dz: float = 0.0
    return_to_origin: bool = True

    def __to_dict__(self) -> dict:
        return dict(
            n_rows=self.n_rows,
            n_cols=self.n_cols,
            dx=self.dx,
            dy=self.dy,
            n_slices=self.n_slices,
            dz=self.dz,
            return_to_origin=self.return_to_origin,
        )
    
    @staticmethod
    def __from_dict__(settings: dict) -> "WorkflowSettings":
        workflow_settings = WorkflowSettings(
            n_rows=settings["n_rows"],
            n_cols=settings["n_cols"],
            dx=settings["dx"],
            dy=settings["dy"],
            n_slices=settings["n_slices"],
            dz=settings["dz"],
            return_to_origin=settings["return_to_origin"],
        )
        return workflow_settings


@dataclass
class ImageSettings:
    """Image settings"""

    pixel_size: float = 0.0
    exposure: float = 0.0
    n_images: int = 1
    mode: ImageMode = ImageMode.SINGLE
    path: Path = None
    workflow: WorkflowSettings = None

    @staticmethod
    def __from_dict__(settings: dict) -> "ImageSettings":
        return ImageSettings(
            pixel_size=settings["pixel_size"],
            exposure=settings["exposure"],
            n_images=settings["n_images"],
            mode=ImageMode[settings.get("mode", "SINGLE")],
            path=Path(settings.get("path", None)),
            workflow = settings.get("workflow", None)
        )

    def __to_dict__(self) -> dict:
        return {
            "pixel_size": self.pixel_size,
            "exposure": self.exposure,
            "n_images": self.n_images,
            "mode": self.mode.name,
            "path": str(self.path) if self.path is not None else None,
            "workflow": self.workflow.__to_dict__() if self.workflow is not None else None,
        }


@dataclass
class LaserSettings:
    name: str
    serial_id: str
    wavelength: float
    power: float
    exposure_time: float  # s
    enabled: bool
    color: list

    @staticmethod
    def __from_dict__(settings: dict) -> "LaserSettings":
        laser_settings = LaserSettings(
            name=settings["name"],
            serial_id=settings.get("serial_id", None),
            wavelength=settings["wavelength"],
            power=settings["power"],
            exposure_time=settings["exposure_time"],
            enabled=settings["enabled"],
            color=settings["color"],
        )
        return laser_settings

    def __to_dict__(self) -> dict:
        return {
            "name": self.name,
            "serial_id": self.serial_id,
            "wavelength": self.wavelength,
            "power": self.power,
            "exposure_time": self.exposure_time,
            "color": self.color,
            "enabled": self.enabled,
        }


@dataclass
class LaserControllerSettings:
    """Laser controller settings"""

    name: str
    laser: str
    connection: ConnectionSettings

    @staticmethod
    def __from_dict__(settings: dict) -> "LaserControllerSettings":
        laser_controller_settings = LaserControllerSettings(
            name=settings["name"],
            connection=ConnectionSettings.__from_dict__(settings["connection"]),
            laser=settings["laser"],
        )
        return laser_controller_settings

    def __to_dict__(self) -> dict:
        return {
            "name": self.name,
            "connection": self.connection.__to_dict__(),
            "laser": self.laser,
        }


@dataclass
class DetectorSettings:
    """Detector settings"""

    name: str
    connection: ConnectionSettings
    pixel_size: float
    resolution: list[int]
    trigger_source: TriggerSource = TriggerSource.SOFTWARE
    trigger_edge: TriggerEdge = TriggerEdge.RISING
    exposure_mode: ExposureMode = ExposureMode.TRIGGER_WIDTH
    timeout: int = 1000  # ms

    @staticmethod
    def __from_dict__(settings: dict) -> "DetectorSettings":
        detector_settings = DetectorSettings(
            name=settings["name"],
            connection=ConnectionSettings.__from_dict__(settings["connection"]),
            pixel_size=settings["pixel_size"],
            resolution=settings["resolution"],
            trigger_source=TriggerSource[settings["trigger_source"]],
            trigger_edge=TriggerEdge[settings["trigger_edge"]],
            exposure_mode=ExposureMode[settings["exposure_mode"]],
            timeout=settings["timeout"],
        )
        return detector_settings

    def __to_dict__(self) -> dict:
        return {
            "name": self.name,
            "connection": self.connection.__to_dict__(),
            "pixel_size": self.pixel_size,
            "resolution": self.resolution,
            "trigger_source": self.trigger_source.name,
            "trigger_edge": self.trigger_edge.name,
            "exposure_mode": self.exposure_mode.name,
            "timeout": self.timeout,
        }


@dataclass
class SynchroniserSettings:
    name: str
    pins: dict[str:int]
    connection: ConnectionSettings = None

    @staticmethod
    def __from_dict__(settings: dict) -> "SynchroniserSettings":
        trigger_settings = SynchroniserSettings(
            name=settings["name"],
            pins=settings["pins"],
            connection=ConnectionSettings.__from_dict__(
                settings.get("connection", None)
            ),
        )
        return trigger_settings

    def __to_dict__(self) -> dict:
        return {
            "name": self.name,
            "pins": self.pins,
            "connection": self.connection.__to_dict__(),
        }


@dataclass
class SynchroniserMessage:
    """Synchroniser message"""

    exposures: list[float]
    pins: dict[str:int]
    mode: ImageMode = ImageMode.SINGLE
    n_slices: int = 0
    trigger_edge: TriggerEdge = TriggerEdge.RISING

    def __to_dict__(self) -> dict:
        return {
            "exposures": self.exposures,
            "pins": self.pins,
            "mode": self.mode.name,
            "n_slices": self.n_slices,
            "trigger_edge": self.trigger_edge.name,
        }

    @staticmethod
    def __from_dict__(settings: dict) -> "SynchroniserMessage":
        synchroniser_message = SynchroniserMessage(
            exposures=settings["exposures"],
            pins=settings["pins"],
            mode=ImageMode[settings["mode"].upper()],
            n_slices=settings["n_slices"],
            trigger_edge=TriggerEdge[settings["trigger_edge"]],
        )
        return synchroniser_message



@dataclass
class ObjectiveSettings:
    name: str
    connection: ConnectionSettings
    magnification: float = 1.0

    @staticmethod
    def __from_dict__(settings: dict) -> "ObjectiveSettings":
        objective_settings = ObjectiveSettings(
            name=settings["name"],
            magnification=settings["magnification"],
            connection=ConnectionSettings.__from_dict__(settings["connection"]),
        )
        return objective_settings

    def __to_dict__(self) -> dict:
        return {
            "name": self.name,
            "magnification": self.magnification,
            "connection": self.connection.__to_dict__(),
        }


@dataclass
class MicroscopeSettings:
    """Microscope settings"""

    name: str
    lasers: list[LaserSettings]
    detector: DetectorSettings = None
    laser_controller: LaserControllerSettings = None
    objective_stage: ObjectiveSettings = None
    synchroniser: SynchroniserSettings = None
    online: bool = False

    @staticmethod
    def __from_dict__(settings: dict) -> "MicroscopeSettings":

        microscope_settings = MicroscopeSettings(
            name=settings["name"],
            detector=DetectorSettings.__from_dict__(settings["detector"]),
            laser_controller=LaserControllerSettings.__from_dict__(
                settings["laser_controller"]
            ),
            lasers=[LaserSettings.__from_dict__(laser) for laser in settings["lasers"]],
            objective_stage=ObjectiveSettings.__from_dict__(
                settings["objective_stage"]
            ),
            synchroniser=SynchroniserSettings.__from_dict__(settings["synchroniser"]),
            online=settings["online"],
        )
        return microscope_settings

    def __to_dict__(self) -> dict:
        return {
            "name": self.name,
            "detector": DetectorSettings.__to_dict__(self.detector),
            "laser_controller": LaserControllerSettings.__to_dict__(
                self.laser_controller
            ),
            "lasers": [LaserSettings.__to_dict__(laser) for laser in self.lasers],
            "objective_stage": ObjectiveSettings.__to_dict__(self.objective_stage),
            "synchroniser": SynchroniserSettings.__to_dict__(self.synchroniser),
            "online": self.online,
        }

@dataclass
class OpenLMStagePosition:
    x: float
    y: float
    z: float
    r: float
    t: float

    def __to_dict__(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "r": self.r,
            "t": self.t,
        }
    
    @staticmethod
    def __from_dict__(settings: dict) -> "OpenLMStagePosition":
        stage_position = OpenLMStagePosition(
            x=settings["x"],
            y=settings["y"],
            z=settings["z"],
            r=settings["r"],
            t=settings["t"],
        )
        return stage_position

@dataclass
class UserMetadata:
    username: str = "Default"
    name: str = "Default"
    email: str = "Default"
    institution: str = "Default"
    date: str = None

    def __to_dict__(self) -> dict:
        return dict(
            username=self.username,
            name=self.name,
            email=self.email,
            institution=self.institution,
            date=self.date,
        )
    
    @staticmethod
    def __from_dict__(settings: dict) -> "UserMetadata":
        user_metadata = UserMetadata(
            username=settings["username"],
            name=settings["name"],
            email=settings["email"],
            institution=settings["institution"],
            date=settings["date"],

        )
        return user_metadata



@dataclass
class LightImageMetadata:
    n_channels: int  # number of channels
    channels: list[int]  # channel indices
    time: float  # time of acquisition
    lasers: list[LaserSettings]  # laser settings
    detector: DetectorSettings  # detector settings
    objective: ObjectiveSettings  # objective settings
    image: ImageSettings  # image settings
    sync: SynchroniserMessage  # sync settings
    stage: OpenLMStagePosition # stage position
    user: UserMetadata # user metadata

    def __to_dict__(self) -> dict:
        return dict(
            n_channels=self.n_channels,
            channels=self.channels,
            time=self.time,
            lasers=[l.__to_dict__() for l in self.lasers],
            detector=self.detector.__to_dict__(),
            objective=self.objective,  # TODO: this is only the position currently
            image=self.image.__to_dict__(),
            sync=self.sync.__to_dict__(),
            stage=self.stage.__to_dict__(),
            user=self.user.__to_dict__(),
        )

    @classmethod
    def __from_dict__(cls, data: dict) -> "LightImageMetadata":
        return cls(
            n_channels=data["n_channels"],
            channels=data["channels"],
            time=data["time"],
            lasers=[LaserSettings.__from_dict__(l) for l in data["lasers"]],
            detector=DetectorSettings.__from_dict__(data["detector"]),
            objective=data["objective"],  # TODO: this is only the position currently
            image=ImageSettings.__from_dict__(data["image"]),
            sync=SynchroniserMessage.__from_dict__(data["sync"]),
            stage=OpenLMStagePosition.__from_dict__(data["stage"]),
            user=None, #UserMetadata.__from_dict__(data["user"]) TODO: update
        )

    def __repr__(self) -> str:
        return f"LightImageMetadata(n_channels={self.n_channels}, channels={self.channels}, time={self.time}, lasers={self.lasers}, detector={self.detector}, objective={self.objective}, image={self.image}, sync={self.sync})"




@dataclass
class LightImage:
    data: np.ndarray
    metadata: LightImageMetadata

    def __to_dict__(self) -> dict:
        return dict(
            data=self.data,
            metadata=self.metadata.__to_dict__(),
        )

    @classmethod
    def __from_dict__(cls, data: dict) -> "LightImage":
        return cls(
            data=data["data"],
            metadata=LightImageMetadata.__from_dict__(data["metadata"]),
        )

    def __repr__(self) -> str:
        return "\n".join([f"image: {self.data.shape}" f"metadata: {self.metadata}"])

    def save(self, path: Path) -> None:
        """Save image as tiff with metadata in tiff description"""

        # create  directory if it does not exist
        dir = os.path.dirname(path)
        if dir != "":
            os.makedirs(dir, exist_ok=True)
        path = Path(path).with_suffix(".tif")

        if self.metadata is not None:
            metadata_dict = self.metadata.__to_dict__()
        else:
            metadata_dict = None
        tff.imwrite(
            path,
            self.data,
            metadata=metadata_dict,
        )

    @classmethod
    def load(cls, path: Path) -> "LightImage":
        with tff.TiffFile(path) as tiff_image:
            data = tiff_image.asarray()
            try:
                metadata = json.loads(
                    tiff_image.pages[0].tags["ImageDescription"].value
                )
                metadata = LightImageMetadata.__from_dict__(metadata)
            except Exception as e:
                metadata = None
                print(traceback.format_exc())
        return cls(data=data, metadata=metadata)



@dataclass
class TileSettings:
    n_rows: int
    n_cols: int
    shift: float

