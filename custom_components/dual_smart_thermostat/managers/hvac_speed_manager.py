"""HVAC Speed Manager for Dual Smart Thermostat."""

import logging
from typing import Dict, List

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from custom_components.dual_smart_thermostat.const import (
    CONF_HVAC_SPEED_MODES,
    CONF_HVAC_SPEED_MANUAL,
    DEFAULT_HVAC_SPEED_MODES,
)
from custom_components.dual_smart_thermostat.managers.state_manager import StateManager

_LOGGER = logging.getLogger(__name__)


class HvacSpeedManager(StateManager):
    """Manages HVAC speed modes for manual control."""

    def __init__(
        self, hass: HomeAssistant, config: ConfigType
    ) -> None:
        """Initialize the HVAC speed manager."""
        self.hass = hass
        self.config = config
        
        # Get configured speed modes or use defaults
        self._speed_modes = config.get(CONF_HVAC_SPEED_MODES, DEFAULT_HVAC_SPEED_MODES.copy())
        self._manual_mode_enabled = config.get(CONF_HVAC_SPEED_MANUAL, False)
        
        # Current selected speed mode (None means auto/not set)
        self._current_speed_mode = None
        
        # Speed to power level mapping
        self._speed_power_mapping = self._create_speed_power_mapping()
        
        _LOGGER.debug(
            "HVAC Speed Manager initialized - modes: %s, manual: %s", 
            self._speed_modes, 
            self._manual_mode_enabled
        )

    def _create_speed_power_mapping(self) -> Dict[str, int]:
        """Create mapping from speed modes to power levels."""
        mapping = {}
        
        if not self._speed_modes:
            return mapping
            
        # Auto mode uses automatic power calculation
        if "auto" in self._speed_modes:
            mapping["auto"] = -1  # Special value for auto mode
            
        # Map other speed modes to power levels
        speed_modes_without_auto = [mode for mode in self._speed_modes if mode != "auto"]
        num_speeds = len(speed_modes_without_auto)
        
        if num_speeds > 0:
            for i, mode in enumerate(speed_modes_without_auto):
                # Distribute power levels evenly across available speeds
                # From 1 to 5 (or max configured power levels)
                power_level = int((i + 1) * 5 / num_speeds)
                mapping[mode] = max(1, power_level)
                
        _LOGGER.debug("Speed to power mapping: %s", mapping)
        return mapping

    @property
    def is_configured(self) -> bool:
        """Return if speed modes are configured."""
        return self._manual_mode_enabled and len(self._speed_modes) > 0

    @property
    def speed_modes(self) -> List[str]:
        """Return available speed modes."""
        return self._speed_modes.copy() if self._speed_modes else []

    @property
    def current_speed_mode(self) -> str | None:
        """Return current speed mode."""
        return self._current_speed_mode

    @property
    def is_auto_mode(self) -> bool:
        """Return if currently in auto mode."""
        return self._current_speed_mode is None or self._current_speed_mode == "auto"

    def set_speed_mode(self, speed_mode: str) -> None:
        """Set the current speed mode."""
        if speed_mode not in self._speed_modes:
            _LOGGER.warning("Invalid speed mode: %s. Available modes: %s", speed_mode, self._speed_modes)
            return
            
        self._current_speed_mode = speed_mode
        _LOGGER.debug("Speed mode set to: %s", speed_mode)

    def get_manual_power_level(self) -> int | None:
        """Get the power level for current manual speed mode.
        
        Returns:
            int: Power level for manual mode, or None if in auto mode
        """
        if self.is_auto_mode:
            return None
            
        return self._speed_power_mapping.get(self._current_speed_mode, 1)

    def reset_to_auto(self) -> None:
        """Reset speed mode to auto."""
        if "auto" in self._speed_modes:
            self._current_speed_mode = "auto"
        else:
            self._current_speed_mode = None
        _LOGGER.debug("Speed mode reset to auto")

    def apply_old_state(self, old_state) -> None:
        """Apply old state to restore speed mode."""
        if old_state is None or not self.is_configured:
            return
            
        from custom_components.dual_smart_thermostat.const import ATTR_HVAC_SPEED_MODE
        
        old_speed_mode = old_state.attributes.get(ATTR_HVAC_SPEED_MODE)
        
        if old_speed_mode and old_speed_mode in self._speed_modes:
            _LOGGER.debug("Restoring previous speed mode: %s", old_speed_mode)
            self._current_speed_mode = old_speed_mode
        else:
            _LOGGER.debug("No valid previous speed mode found, using auto")
            self.reset_to_auto() 