from typing import Any, Optional

import voluptuous as vol
from pymodbus.client import AsyncModbusTcpClient

from homeassistant import data_entry_flow
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_HOST, CONF_DEVICE
from pysungrow import identify
from pysungrow.identify import NotASungrowDeviceException

from .const import DOMAIN, DEFAULT_NAME

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_DEVICE): str
    }
)

class SungrowFlowHandler(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(
        self, user_input: Optional[dict[str, Any]] = None
    ) -> data_entry_flow.FlowResult:
        errors = {}
        if user_input is not None:
            host = user_input[CONF_HOST]

            try:
                client = AsyncModbusTcpClient(host, port=502)
                serial_number, device, output_type = await identify(client, slave=1)
            except NotASungrowDeviceException:
                errors[CONF_HOST] = "connection_error"
            else:
                await self.async_set_unique_id(serial_number)
                self._abort_if_unique_id_configured(updates={CONF_HOST: host})

                return self.async_create_entry(
                    title=DEFAULT_NAME,
                    data={
                        CONF_HOST: host,
                        CONF_DEVICE: device.name,
                    },
                )

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(
    {
        vol.Required(CONF_HOST): str,
    }
), errors=errors
        )
