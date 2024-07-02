from typing import Final
from enum import StrEnum

DOMAIN: Final = "wolf"

DEFAULT_HOST: Final = "0.0.0.0"
DEFAULT_PORT: Final = 12004

WOLF: Final = "Wolf"
WOLF_ISM8: Final = "ISM8"

WOLF_DEFAULT_DEVICES: Final = ["Heizgeraet1", "Systembedienmodul"]


class SENSOR_TYPES(StrEnum):
    """Datapoint classes according to wolf_ism8 datapoint types"""

    DPT_SWITCH = "DPT_Switch"
    DPT_BOOL = "DPT_Bool"
    DPT_ENABLE = "DPT_Enable"
    DPT_OPENCLOSE = "DPT_OpenClose"
    DPT_SCALING = "DPT_Scaling"
    DPT_VALUE_TEMP = "DPT_Value_Temp"
    DPT_VALUE_TEMPD = "DPT_Value_Tempd"
    DPT_TEMPD = "DPT_Tempd"
    DPT_VALUE_PRES = "DPT_Value_Pres"
    DPT_POWER = "DPT_Power"
    DPT_VALUE_VOLUME_FLOW = "DPT_Value_Volume_Flow"
    DPT_TIMEOFDAY = "DPT_TimeOfDay"
    DPT_DATE = "DPT_Date"
    DPT_FLOWRATE_M3 = "DPT_FlowRate_m3/h"
    DPT_HVACMODE = "DPT_HVACMode"
    DPT_DHWMODE = "DPT_DHWMode"
    DPT_HVACCONTRMODE = "DPT_HVACContrMode"
