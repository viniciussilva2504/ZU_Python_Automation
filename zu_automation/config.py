"""Runtime configuration for the Android test target and Appium server."""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class AppConfig:
    appium_url: str = "http://127.0.0.1:4723"
    device_name: str = "emulator-5554"
    app_package: str = "pt.continente.ZU"
    app_activity: str = "pt.continente.ZU.MainActivity"

    @classmethod
    def from_environment(cls):
        return cls(
            appium_url=os.getenv("ZU_APPIUM_URL", cls.appium_url),
            device_name=os.getenv("ZU_DEVICE_NAME", cls.device_name),
            app_package=os.getenv("ZU_APP_PACKAGE", cls.app_package),
            app_activity=os.getenv("ZU_APP_ACTIVITY", cls.app_activity),
        )
