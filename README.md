# CAN UDS Diagnostic Tester

Enhanced CAN UDS (Unified Diagnostic Services) tool with intelligent session management and automatic CAN interface configuration.

## 🚀 Key Features

### CAN Interface Management
- **Automatic Configuration**: Integrated system commands for CAN interface setup
- **Multi-Mode Support**: Standard CAN and CANFD mode switching  
- **Dynamic Baudrate**: Configurable baudrate settings
- **Interface Detection**: Automatic detection and status monitoring

### Enhanced Diagnostic Session Management
- **ID Change Detection**: Automatically detects diagnostic ID changes
- **Session Switching**: Intelligent prompts for session management
- **Connection History**: Track and review connection history
- **Prerequisites Validation**: Smart validation of configuration requirements

### Core UDS Services
- **Service 0x22**: ReadDataByIdentifier implementation
- **Service 0x27**: SecurityAccess with configurable algorithms
- **Multi-Identifier Support**: Read multiple DIDs in a single operation
- **Response Formatting**: Intelligent data formatting and display

### User Experience
- **Interactive Shell**: Command-line interface with help system
- **Context-Aware Prompts**: Intelligent error messages and suggestions
- **Configuration Validation**: Real-time validation of settings
- **Comprehensive Logging**: Detailed logging for debugging

## 📁 Project Structure

```
CAN UDS Tester/
├── can_tester.py              # Main interactive application
├── core/
│   ├── __init__.py
│   └── can_manager.py         # CAN interface management
├── commands/
│   ├── __init__.py
│   ├── set_command.py         # Enhanced configuration command
│   └── connect_command.py     # Intelligent connection management
├── modules/
│   ├── __init__.py
│   ├── read_data_module.py    # UDS Service 0x22
│   └── security_access_module.py  # UDS Service 0x27
├── tests/
│   ├── __init__.py
│   └── test_basic_functionality.py
├── requirements.txt
├── usage_examples.py
└── README.md
```

## 🛠 Installation

1. Clone the repository:
```bash
git clone https://github.com/Thanosss/Ai.git
cd Ai
```

2. Install dependencies (optional - uses Python standard library only):
```bash
pip install -r requirements.txt
```

3. Run the interactive tool:
```bash
python can_tester.py
```

## 📖 Usage Examples

### Basic Configuration
```bash
# Start the interactive tool
python can_tester.py

# Configure CAN interface
CAN-UDS> set -i can0 -b 500000 -m can

# Set diagnostic IDs
CAN-UDS> set -s 733 -t 73b

# Connect to diagnostic session
CAN-UDS> connect
```

### High-Speed CANFD Setup
```bash
# Configure CANFD interface
CAN-UDS> set -i can1 -b 1000000 -m canfd

# Set different diagnostic IDs
CAN-UDS> set -s 700 -t 708

# Connect with new configuration
CAN-UDS> connect
```

### Diagnostic Operations
```bash
# Read single data identifier
CAN-UDS> read 0x1000

# Read multiple identifiers
CAN-UDS> read 0x1000 0x1001 0x1002

# Perform security access
CAN-UDS> security 1

# Check overall status
CAN-UDS> status
```

### Session Management
```bash
# List saved sessions
CAN-UDS> set --list-sessions

# List available interfaces
CAN-UDS> set --list-interfaces

# Check connection status
CAN-UDS> connect --status

# View connection history
CAN-UDS> connect --history
```

## 🔧 Command Reference

### Set Command
Configure CAN interface and diagnostic IDs:
- `set -i <interface>` - Set CAN interface
- `set -b <baudrate>` - Set baudrate (default: 500000)
- `set -m <mode>` - Set mode (can/canfd)
- `set -s <source_id>` - Set source diagnostic ID
- `set -t <target_id>` - Set target diagnostic ID
- `set --list-interfaces` - List available CAN interfaces
- `set --list-sessions` - List saved diagnostic sessions

### Connect Command
Manage diagnostic connections:
- `connect` - Establish diagnostic connection
- `connect --status` - Show connection status
- `connect --history` - Show connection history
- `connect --disconnect` - Disconnect from session

### Diagnostic Commands
- `read <DID> [DID2] ...` - Read data by identifier(s)
- `security <level>` - Perform security access
- `security status` - Show security access status
- `security reset` - Reset security access state

### System Commands
- `status` - Show overall system status
- `help [command]` - Show help information
- `clear` - Clear screen
- `exit` - Exit the application

## 🧪 Testing

Run the basic functionality tests:
```bash
python tests/test_basic_functionality.py
```

View usage examples:
```bash
python usage_examples.py
```

## 🎯 Design Highlights

### Intelligent Session Management
- **ID Change Detection**: When diagnostic IDs change, the tool prompts you to:
  - Continue with current IDs
  - Revert to previous IDs
  - Cancel the operation

### Smart Configuration Validation
- **Prerequisites Check**: Validates CAN interface and diagnostic ID configuration
- **Context-Aware Messages**: Provides specific guidance for missing configuration
- **Auto-Detection**: Automatically detects interface status and availability

### Enhanced User Experience
- **Interactive Prompts**: Clear options and guidance for complex operations
- **Connection History**: Track and review previous connections
- **Comprehensive Status**: Real-time status information for all components

## 🔍 Key Improvements

This redesigned version focuses on practical usage with:

1. **Removed Complexity**: Eliminated unnecessary configuration files
2. **Enhanced Interactivity**: Added intelligent prompts and session management
3. **Better Validation**: Comprehensive prerequisite checking
4. **Improved UX**: Context-aware error messages and suggestions
5. **Simplified Structure**: Clean, modular architecture focused on core functionality

## 📝 Development Notes

- Uses Python standard library only for core functionality
- Modular design allows easy extension of UDS services
- Mock implementations for testing without actual CAN hardware
- Comprehensive logging for debugging and monitoring
- Designed for both development and production use

## 🤝 Contributing

Feel free to contribute improvements, additional UDS services, or enhanced features. The modular design makes it easy to extend functionality while maintaining the core user experience.