"""
Connect Command  
Enhanced command with diagnostic ID change detection and session switching options.
"""
import logging
from typing import Optional, Dict, Any
from core.can_manager import CANManager

logger = logging.getLogger(__name__)


class ConnectCommand:
    """Enhanced connect command with ID change detection and session management."""
    
    def __init__(self, can_manager: CANManager, set_command=None):
        self.can_manager = can_manager
        self.set_command = set_command
        self.connection_status = False
        self.last_known_ids: Optional[tuple] = None
        self.connection_history: list = []
    
    def execute(self, args: list = None) -> bool:
        """
        Execute the connect command.
        
        Args:
            args: Optional command arguments
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Check if CAN interface is configured and ready
            if not self._validate_prerequisites():
                return False
            
            # Check for diagnostic ID changes
            if self._check_id_changes():
                if not self._handle_id_change_prompt():
                    print("Connection cancelled due to ID changes.")
                    return False
            
            # Perform connection
            success = self._establish_connection()
            
            if success:
                self.connection_status = True
                current_ids = self.set_command.get_current_diagnostic_ids() if self.set_command else (None, None)
                self.last_known_ids = current_ids
                
                # Add to connection history
                self._add_to_history(current_ids)
                
                logger.info("Diagnostic connection established successfully")
                print("✓ Diagnostic connection established successfully")
                self._display_connection_info()
            else:
                print("✗ Failed to establish diagnostic connection")
                logger.error("Failed to establish diagnostic connection")
            
            return success
            
        except Exception as e:
            logger.error(f"Error executing connect command: {e}")
            print(f"✗ Connection error: {e}")
            return False
    
    def disconnect(self) -> bool:
        """
        Disconnect from diagnostic session.
        
        Returns:
            bool: True if disconnection successful, False otherwise
        """
        try:
            if not self.connection_status:
                print("Not currently connected.")
                return True
            
            # Perform disconnection logic here
            # This could involve sending diagnostic session control to default session
            
            self.connection_status = False
            logger.info("Diagnostic connection terminated")
            print("✓ Diagnostic connection terminated")
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting: {e}")
            print(f"✗ Disconnection error: {e}")
            return False
    
    def _validate_prerequisites(self) -> bool:
        """
        Validate that all prerequisites for connection are met.
        
        Returns:
            bool: True if prerequisites are met, False otherwise
        """
        if not self.set_command:
            print("✗ Set command not available for validation")
            return False
        
        validation = self.set_command.validate_can_configuration()
        
        if not validation['interface_configured']:
            print("✗ CAN interface not configured. Use 'set -i <interface>' first.")
            return False
        
        if not validation['interface_up']:
            print("✗ CAN interface is not up. Check interface configuration.")
            return False
        
        if not validation['diagnostic_ids_set']:
            print("✗ Diagnostic IDs not configured. Use 'set -s <source> -t <target>' first.")
            return False
        
        return True
    
    def _check_id_changes(self) -> bool:
        """
        Check if diagnostic IDs have changed since last connection.
        
        Returns:
            bool: True if IDs have changed, False otherwise
        """
        if not self.set_command or not self.last_known_ids:
            return False
        
        current_ids = self.set_command.get_current_diagnostic_ids()
        return current_ids != self.last_known_ids
    
    def _handle_id_change_prompt(self) -> bool:
        """
        Handle user interaction when diagnostic IDs have changed.
        
        Returns:
            bool: True if user chooses to continue, False otherwise
        """
        current_ids = self.set_command.get_current_diagnostic_ids() if self.set_command else (None, None)
        
        print("\n⚠️  Diagnostic ID Configuration Change Detected")
        print("-" * 50)
        
        if self.last_known_ids:
            print(f"Previous IDs: Source=0x{self.last_known_ids[0]:03X}, Target=0x{self.last_known_ids[1]:03X}")
        
        if current_ids[0] and current_ids[1]:
            print(f"Current IDs:  Source=0x{current_ids[0]:03X}, Target=0x{current_ids[1]:03X}")
        
        print("\nOptions:")
        print("1. Continue with current IDs")
        print("2. Revert to previous IDs")
        print("3. Cancel connection")
        
        while True:
            try:
                choice = input("\nSelect option (1-3): ").strip()
                
                if choice == '1':
                    print("✓ Continuing with current diagnostic IDs")
                    return True
                elif choice == '2':
                    if self.last_known_ids and self.set_command:
                        # Revert to previous IDs
                        self.set_command.current_source_id = self.last_known_ids[0]
                        self.set_command.current_target_id = self.last_known_ids[1]
                        print(f"✓ Reverted to previous IDs: Source=0x{self.last_known_ids[0]:03X}, Target=0x{self.last_known_ids[1]:03X}")
                        return True
                    else:
                        print("✗ Cannot revert - no previous IDs available")
                        return False
                elif choice == '3':
                    return False
                else:
                    print("Invalid choice. Please select 1, 2, or 3.")
                    
            except KeyboardInterrupt:
                print("\nConnection cancelled by user.")
                return False
            except Exception as e:
                print(f"Input error: {e}")
                return False
    
    def _establish_connection(self) -> bool:
        """
        Establish the diagnostic connection.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        # This is a placeholder for actual connection logic
        # In a real implementation, this would:
        # 1. Send diagnostic session control requests
        # 2. Verify communication with the target ECU
        # 3. Handle any necessary authentication
        
        config = self.can_manager.get_current_config()
        current_ids = self.set_command.get_current_diagnostic_ids() if self.set_command else (None, None)
        
        logger.info(f"Attempting connection via {config['interface']} "
                   f"(Source: 0x{current_ids[0]:03X}, Target: 0x{current_ids[1]:03X})")
        
        # Simulate connection process
        import time
        print("Establishing diagnostic connection...")
        time.sleep(1)  # Simulate connection delay
        
        # In a real implementation, this would involve actual CAN communication
        # For now, we'll assume success if prerequisites are met
        return True
    
    def _display_connection_info(self):
        """Display current connection information."""
        config = self.can_manager.get_current_config()
        current_ids = self.set_command.get_current_diagnostic_ids() if self.set_command else (None, None)
        
        print("\nConnection Information:")
        print("-" * 30)
        print(f"CAN Interface: {config['interface']}")
        print(f"Baudrate: {config['baudrate']} bps")
        print(f"Mode: {config['mode'].upper()}")
        
        if current_ids[0] and current_ids[1]:
            print(f"Source ID: 0x{current_ids[0]:03X}")
            print(f"Target ID: 0x{current_ids[1]:03X}")
        
        print(f"Status: {'Connected' if self.connection_status else 'Disconnected'}")
    
    def _add_to_history(self, ids: tuple):
        """
        Add connection to history.
        
        Args:
            ids: Tuple of (source_id, target_id)
        """
        import time
        
        entry = {
            'timestamp': time.time(),
            'source_id': ids[0],
            'target_id': ids[1],
            'interface': self.can_manager.get_current_config()['interface']
        }
        
        self.connection_history.append(entry)
        
        # Keep only last 10 connections
        if len(self.connection_history) > 10:
            self.connection_history.pop(0)
    
    def show_connection_history(self):
        """Display connection history."""
        if not self.connection_history:
            print("No connection history available.")
            return
        
        print("\nConnection History:")
        print("-" * 60)
        
        for i, entry in enumerate(reversed(self.connection_history[-5:]), 1):
            import time
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(entry['timestamp']))
            print(f"{i}. {timestamp} - Interface: {entry['interface']}, "
                  f"IDs: 0x{entry['source_id']:03X}/0x{entry['target_id']:03X}")
    
    def is_connected(self) -> bool:
        """
        Check if currently connected.
        
        Returns:
            bool: True if connected, False otherwise
        """
        return self.connection_status
    
    def get_connection_status(self) -> Dict[str, Any]:
        """
        Get detailed connection status.
        
        Returns:
            dict: Connection status information
        """
        current_ids = self.set_command.get_current_diagnostic_ids() if self.set_command else (None, None)
        config = self.can_manager.get_current_config()
        
        return {
            'connected': self.connection_status,
            'interface': config.get('interface'),
            'baudrate': config.get('baudrate'),
            'mode': config.get('mode'),
            'source_id': current_ids[0],
            'target_id': current_ids[1],
            'last_known_ids': self.last_known_ids,
            'history_count': len(self.connection_history)
        }
    
    def get_help_text(self) -> str:
        """Get help text for the connect command."""
        return """
Connect Command Usage:

Basic Connection:
  connect                           # Connect with current configuration
  
Connection Management:
  connect --disconnect             # Disconnect from current session
  connect --status                 # Show connection status
  connect --history               # Show connection history

The connect command will:
1. Validate CAN interface configuration
2. Check diagnostic ID settings
3. Detect ID changes and prompt for action
4. Establish diagnostic connection
5. Provide session switching options

Prerequisites:
- CAN interface must be configured (use 'set -i <interface>')  
- Diagnostic IDs must be set (use 'set -s <source> -t <target>')
"""