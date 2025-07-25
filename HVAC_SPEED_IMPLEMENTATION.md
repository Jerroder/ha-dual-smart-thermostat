# HVAC Speed Control Implementation

## Overview

This implementation adds user-configurable HVAC speed control to the Dual Smart Thermostat component. Instead of the system automatically managing HVAC power levels based only on temperature difference, users can now manually select speed modes like "auto", "low", "medium", "high" through the Home Assistant UI.

## Key Features

1. **User Interface Integration**: Uses Home Assistant's native `FAN_MODE` feature to display speed options in the thermostat UI
2. **Automatic and Manual Modes**: Supports both automatic power calculation and manual speed selection
3. **State Persistence**: Remembers the selected speed mode across Home Assistant restarts
4. **Configurable Speed Options**: Allows customization of available speed modes
5. **Seamless Integration**: Works with existing power management system

## Files Modified/Created

### New Files Created:

- `custom_components/dual_smart_thermostat/managers/hvac_speed_manager.py` - Main speed management logic

### Files Modified:

- `custom_components/dual_smart_thermostat/const.py` - Added speed control constants
- `custom_components/dual_smart_thermostat/climate.py` - Added FAN_MODE support and speed control integration
- `custom_components/dual_smart_thermostat/managers/feature_manager.py` - Added speed control feature detection
- `custom_components/dual_smart_thermostat/managers/hvac_power_manager.py` - Integrated manual speed override
- `config/configuration.yaml` - Added configuration example

## Configuration Options

Add these options to your thermostat configuration:

```yaml
climate:
  - platform: dual_smart_thermostat
    name: Smart Thermostat with Speed Control
    heater: switch.heater
    cooler: switch.cooler
    target_sensor: sensor.room_temp
    # ... other configuration ...

    # Enable manual HVAC speed control
    hvac_speed_manual: true

    # Define available speed modes (optional)
    hvac_speed_modes: ["auto", "low", "medium", "high"]

    # Power level configuration for fine-tuning
    hvac_power_levels: 5
    hvac_power_min: 1
    hvac_power_max: 5
```

### Configuration Parameters:

- **`hvac_speed_manual`** (boolean, optional): Enable manual speed control. Default: false
- **`hvac_speed_modes`** (list, optional): Available speed modes. Default: ["auto", "low", "medium", "high"]
- **`hvac_power_levels`** (integer, optional): Total power levels for mapping. Default: 5
- **`hvac_power_min`** (integer, optional): Minimum power level. Default: 1
- **`hvac_power_max`** (integer, optional): Maximum power level. Default: 5

## How It Works

### Speed to Power Mapping

The system automatically maps user-selected speed modes to internal power levels:

- **"auto"**: Uses automatic power calculation based on temperature difference
- **"low"**: Maps to lower power levels (e.g., level 1-2)
- **"medium"**: Maps to medium power levels (e.g., level 3)
- **"high"**: Maps to higher power levels (e.g., level 4-5)

### User Interface

When speed control is enabled, users will see a fan control dropdown in the thermostat UI with options like:

- Auto
- Low
- Medium
- High

### State Management

- Selected speed mode is saved as an entity attribute
- Mode is restored after Home Assistant restarts
- Switching to "auto" re-enables automatic power calculation
- Manual modes override automatic calculation

## Integration Points

### HvacSpeedManager Class

```python
class HvacSpeedManager(StateManager):
    def __init__(self, hass: HomeAssistant, config: ConfigType)
    def set_speed_mode(self, speed_mode: str) -> None
    def get_manual_power_level(self) -> int | None
    def is_auto_mode(self) -> bool
    def apply_old_state(self, old_state) -> None
```

### Climate Entity Extensions

```python
@property
def fan_mode(self) -> str | None:
    """Return the current fan mode."""

@property
def fan_modes(self) -> list[str] | None:
    """Return the list of available fan modes."""

async def async_set_fan_mode(self, fan_mode: str) -> None:
    """Set new fan mode (HVAC speed)."""
```

### Power Manager Integration

The existing `HvacPowerManager` now checks for manual speed mode before performing automatic calculations:

```python
def update_hvac_power(self, strategy, target_env_attr, hvac_action):
    # Check if manual speed mode is active
    if self.speed_manager and not self.speed_manager.is_auto_mode:
        manual_power_level = self.speed_manager.get_manual_power_level()
        # Use manual power level
    else:
        # Use automatic calculation
```

## Usage Example

1. **Enable Speed Control**: Add `hvac_speed_manual: true` to your configuration
2. **Restart Home Assistant**: Load the new configuration
3. **Access Speed Control**: Open your thermostat in the UI
4. **Select Speed**: Choose from the fan mode dropdown (Auto/Low/Medium/High)
5. **Monitor Operation**: The thermostat will use your selected speed instead of automatic calculation

## Benefits

1. **User Control**: Gives users direct control over HVAC intensity
2. **Energy Management**: Allows manual selection of lower speeds for energy savings
3. **Comfort Preferences**: Users can choose higher speeds for faster temperature changes
4. **Noise Control**: Lower speeds typically mean quieter operation
5. **Flexibility**: Easy switching between automatic and manual modes

## Technical Notes

- Speed modes are mapped to power levels evenly across the configured range
- "Auto" mode preserves the original automatic power calculation behavior
- State persistence ensures settings survive Home Assistant restarts
- The implementation follows Home Assistant's climate entity patterns
- All existing functionality remains unchanged when speed control is disabled
