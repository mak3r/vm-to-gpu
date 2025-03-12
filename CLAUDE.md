# VM-to-GPU Development Guide

## Build Commands
- `make install` - Build and install RPM package
- `make uninstall` - Remove installed package
- `make rpm` - Build RPM package without installing
- `make clean` - Clean build artifacts
- `make container` - Build container with application
- `make code-ai` - Run container with application

## Code Style Guidelines
- **Imports**: Standard library first, then third-party (e.g., GTK)
- **Indentation**: 4 spaces
- **Naming**:
  - Classes: PascalCase (e.g., `VMToGPUApp`)
  - Methods/Functions/Variables: snake_case (e.g., `get_lsusb_devices`)
  - Constants: UPPER_SNAKE_CASE (e.g., `CONFIG_DIR`)
- **Error Handling**: Add appropriate try/except blocks for file I/O and external commands
- **Comments**: Add explanatory comments for complex operations
- **Structure**: Keep UI components separated (left_ui.py, right_ui.py, buttons.py)
- **Configuration**: Use config_manager.py for all config operations

## Architecture
The application manages USB passthrough to VMs with these components:
- Main window (main.py) - Entry point with GTK application
- Left panel (left_ui.py) - Shows VM domains
- Right panel (right_ui.py) - Shows USB devices
- Bottom panel (buttons.py) - Shows action buttons
- Config manager (config_manager.py) - Handles configuration