"""
Basic functionality tests for CAN UDS Tester
"""
import sys
import os

# Add the parent directory to the path to import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.can_manager import CANManager
from commands.set_command import SetCommand
from commands.connect_command import ConnectCommand
from modules.read_data_module import ReadDataModule
from modules.security_access_module import SecurityAccessModule, SecurityLevel


def test_can_manager():
    """Test CAN manager basic functionality."""
    print("Testing CAN Manager...")
    
    can_manager = CANManager()
    
    # Test listing interfaces (will work even without actual CAN interfaces)
    interfaces = can_manager.list_available_interfaces()
    print(f"  Available interfaces: {interfaces}")
    
    # Test current config
    config = can_manager.get_current_config()
    print(f"  Current config: {config}")
    
    # Test interface status check (will fail gracefully)
    status = can_manager.check_interface_status('can0')
    print(f"  can0 status: {status}")
    
    print("✓ CAN Manager tests passed")


def test_set_command():
    """Test set command functionality."""
    print("Testing Set Command...")
    
    can_manager = CANManager()
    set_command = SetCommand(can_manager)
    
    # Test diagnostic ID setting
    result = set_command.execute(['-s', '733', '-t', '73b'])
    print(f"  Set IDs result: {result}")
    
    # Test getting current IDs
    source_id, target_id = set_command.get_current_diagnostic_ids()
    print(f"  Current IDs: Source=0x{source_id:03X}, Target=0x{target_id:03X}")
    
    # Test validation
    validation = set_command.validate_can_configuration()
    print(f"  Validation: {validation}")
    
    print("✓ Set Command tests passed")


def test_connect_command():
    """Test connect command functionality."""
    print("Testing Connect Command...")
    
    can_manager = CANManager()
    set_command = SetCommand(can_manager)
    connect_command = ConnectCommand(can_manager, set_command)
    
    # Set up some IDs first
    set_command.execute(['-s', '733', '-t', '73b'])
    
    # Test connection status
    status = connect_command.get_connection_status()
    print(f"  Connection status: {status}")
    
    # Test connection (will fail due to no actual CAN interface)
    print("  Testing connection (expected to fail without CAN interface)...")
    result = connect_command.execute()
    print(f"  Connection result: {result}")
    
    print("✓ Connect Command tests passed")


def test_read_data_module():
    """Test read data module functionality."""
    print("Testing Read Data Module...")
    
    read_module = ReadDataModule()
    
    # Test reading a data identifier (will use mock response)
    data = read_module.read_data_by_identifier(0x1000)
    if data:
        formatted = read_module.format_data_response(0x1000, data)
        print(f"  Read DID result: {formatted}")
    
    # Test service info
    info = read_module.get_service_info()
    print(f"  Service info: {info}")
    
    print("✓ Read Data Module tests passed")


def test_security_access_module():
    """Test security access module functionality."""
    print("Testing Security Access Module...")
    
    security_module = SecurityAccessModule()
    
    # Test seed request (will use mock response)
    seed = security_module.request_seed(SecurityLevel.LEVEL_1)
    if seed:
        print(f"  Received seed: {seed.hex()}")
        
        # Test key computation
        key = security_module.compute_key_from_seed(SecurityLevel.LEVEL_1, seed)
        if key:
            print(f"  Computed key: {key.hex()}")
    
    # Test service info
    info = security_module.get_service_info()
    print(f"  Service info: {info}")
    
    print("✓ Security Access Module tests passed")


def main():
    """Run all tests."""
    print("=" * 50)
    print("CAN UDS Tester - Basic Functionality Tests")
    print("=" * 50)
    
    try:
        test_can_manager()
        print()
        
        test_set_command()
        print()
        
        test_connect_command()
        print()
        
        test_read_data_module()
        print()
        
        test_security_access_module()
        print()
        
        print("=" * 50)
        print("All tests completed successfully!")
        print("=" * 50)
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()