"""
CAN UDS Tester
Main application with diagnostic session management and intelligent user interaction.
"""
import cmd
import logging
import sys
from typing import Dict, Any, Optional

from core.can_manager import CANManager
from commands.set_command import SetCommand
from commands.connect_command import ConnectCommand
from modules.read_data_module import ReadDataModule
from modules.security_access_module import SecurityAccessModule, SecurityLevel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('can_tester.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class CANTester(cmd.Cmd):
    """Interactive CAN UDS tester with session management."""
    
    intro = """
    ╔══════════════════════════════════════════════════════════════════╗
    ║                    CAN UDS Diagnostic Tester                    ║
    ║                                                                  ║
    ║  Enhanced version with CAN interface auto-configuration         ║
    ║  and intelligent diagnostic session management                   ║
    ╚══════════════════════════════════════════════════════════════════╝
    
    Type 'help' for available commands or 'help <command>' for specific help.
    """
    
    prompt = 'CAN-UDS> '
    
    def __init__(self):
        super().__init__()
        self.can_manager = CANManager()
        self.set_command = SetCommand(self.can_manager)
        self.connect_command = ConnectCommand(self.can_manager, self.set_command)
        self.read_data_module = ReadDataModule()
        self.security_access_module = SecurityAccessModule()
        
        # Session state tracking
        self.session_state = {
            'current_session': 'default',
            'session_history': [],
            'last_command_check': None
        }
        
        logger.info("CAN UDS Tester initialized")
    
    def precmd(self, line: str) -> str:
        """Process command before execution - check for session changes."""
        # Skip session check for set and connect commands
        skip_commands = ['set', 'connect', 'help', 'exit', 'quit', '']
        
        cmd_name = line.split()[0] if line.strip() else ''
        if cmd_name not in skip_commands:
            self._check_session_state()
        
        return line
    
    def do_set(self, arg: str):
        """
        Configure CAN interface and diagnostic IDs.
        
        Usage: set [options]
        
        Use 'help set' for detailed options.
        """
        if not arg.strip():
            print(self.set_command.get_help_text())
            return
        
        args = arg.split()
        self.set_command.execute(args)
    
    def help_set(self):
        """Help for set command."""
        print(self.set_command.get_help_text())
    
    def do_connect(self, arg: str):
        """
        Connect to diagnostic session.
        
        Usage: connect [options]
        
        Use 'help connect' for detailed options.
        """
        args = arg.split() if arg.strip() else []
        
        # Handle special arguments
        if '--disconnect' in args:
            self.connect_command.disconnect()
        elif '--status' in args:
            status = self.connect_command.get_connection_status()
            self._display_connection_status(status)
        elif '--history' in args:
            self.connect_command.show_connection_history()
        else:
            self.connect_command.execute(args)
    
    def help_connect(self):
        """Help for connect command."""
        print(self.connect_command.get_help_text())
    
    def do_read(self, arg: str):
        """
        Read data by identifier (UDS Service 0x22).
        
        Usage: read <DID> [DID2] [DID3] ...
        
        Example: read 0x1000 0x1001 0x1002
        """
        if not self._ensure_connected():
            return
        
        if not arg.strip():
            print("Usage: read <DID> [DID2] [DID3] ...")
            print("Example: read 0x1000 0x1001")
            return
        
        try:
            # Parse DIDs from arguments
            did_strings = arg.split()
            dids = []
            
            for did_str in did_strings:
                if did_str.startswith('0x') or did_str.startswith('0X'):
                    did = int(did_str, 16)
                else:
                    did = int(did_str, 16) if len(did_str) <= 4 else int(did_str)
                dids.append(did)
            
            # Read data for each DID
            if len(dids) == 1:
                data = self.read_data_module.read_data_by_identifier(dids[0])
                if data is not None:
                    formatted = self.read_data_module.format_data_response(dids[0], data)
                    print(f"✓ {formatted}")
                else:
                    print(f"✗ Failed to read DID 0x{dids[0]:04X}")
            else:
                results = self.read_data_module.read_multiple_identifiers(dids)
                print(f"\nReading {len(dids)} data identifiers:")
                print("-" * 50)
                
                for did, data in results.items():
                    if data is not None:
                        formatted = self.read_data_module.format_data_response(did, data)
                        print(f"✓ {formatted}")
                    else:
                        print(f"✗ Failed to read DID 0x{did:04X}")
                        
        except ValueError as e:
            print(f"✗ Invalid DID format: {e}")
        except Exception as e:
            logger.error(f"Error reading data: {e}")
            print(f"✗ Error reading data: {e}")
    
    def do_security(self, arg: str):
        """
        Perform security access (UDS Service 0x27).
        
        Usage: 
          security <level>           # Perform security access for level
          security status            # Show current security status
          security reset             # Reset security access
        
        Example: security 1
        """
        if not self._ensure_connected():
            return
        
        if not arg.strip():
            print("Usage: security <level|status|reset>")
            return
        
        args = arg.split()
        command = args[0].lower()
        
        if command == 'status':
            self._show_security_status()
        elif command == 'reset':
            self.security_access_module.reset_security_access()
            print("✓ Security access state reset")
        else:
            try:
                level_num = int(command)
                if 1 <= level_num <= 4:
                    security_level = SecurityLevel(level_num)
                    success = self.security_access_module.perform_security_access(security_level)
                    
                    if success:
                        print(f"✓ Security access granted for level {level_num}")
                    else:
                        print(f"✗ Security access denied for level {level_num}")
                else:
                    print("✗ Security level must be 1-4")
                    
            except ValueError:
                print("✗ Invalid security level. Use 1-4, 'status', or 'reset'")
            except Exception as e:
                logger.error(f"Error in security access: {e}")
                print(f"✗ Security access error: {e}")
    
    def do_status(self, arg: str):
        """
        Show overall system status.
        """
        print("\n" + "="*60)
        print("                    SYSTEM STATUS")
        print("="*60)
        
        # CAN interface status
        config = self.can_manager.get_current_config()
        print(f"\nCAN Interface:")
        if config['interface']:
            status = self.can_manager.check_interface_status(config['interface'])
            status_str = "UP" if status.get('up', False) else "DOWN"
            print(f"  Interface: {config['interface']} ({status_str})")
            print(f"  Baudrate: {config['baudrate']} bps")
            print(f"  Mode: {config['mode'].upper()}")
        else:
            print("  Interface: Not configured")
        
        # Diagnostic IDs
        source_id, target_id = self.set_command.get_current_diagnostic_ids()
        print(f"\nDiagnostic IDs:")
        if source_id and target_id:
            print(f"  Source ID: 0x{source_id:03X}")
            print(f"  Target ID: 0x{target_id:03X}")
        else:
            print("  IDs: Not configured")
        
        # Connection status
        connection_status = self.connect_command.get_connection_status()
        print(f"\nConnection:")
        print(f"  Status: {'Connected' if connection_status['connected'] else 'Disconnected'}")
        
        # Security status
        current_level = self.security_access_module.get_current_security_level()
        print(f"\nSecurity Access:")
        if current_level:
            print(f"  Level: {current_level.value}")
        else:
            print("  Level: Not authenticated")
        
        # Session information
        print(f"\nSession:")
        print(f"  Current: {self.session_state['current_session']}")
        print(f"  History: {len(self.session_state['session_history'])} entries")
    
    def do_clear(self, arg: str):
        """Clear the screen."""
        import os
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def do_exit(self, arg: str):
        """Exit the CAN UDS Tester."""
        if self.connect_command.is_connected():
            print("Disconnecting from diagnostic session...")
            self.connect_command.disconnect()
        
        print("Thank you for using CAN UDS Tester!")
        logger.info("CAN UDS Tester exiting")
        return True
    
    def do_quit(self, arg: str):
        """Alias for exit."""
        return self.do_exit(arg)
    
    def do_EOF(self, arg: str):
        """Handle Ctrl+D."""
        print("\nExiting...")
        return self.do_exit(arg)
    
    def _ensure_connected(self) -> bool:
        """
        Ensure we have an active diagnostic connection.
        
        Returns:
            bool: True if connected, False otherwise
        """
        if not self.connect_command.is_connected():
            print("✗ Not connected to diagnostic session. Use 'connect' first.")
            return False
        return True
    
    def _check_session_state(self):
        """Check if session state has changed and provide intelligent prompts."""
        current_ids = self.set_command.get_current_diagnostic_ids()
        
        # Check if IDs have changed but we're still "connected"
        if (self.connect_command.is_connected() and 
            self.connect_command.last_known_ids and 
            current_ids != self.connect_command.last_known_ids):
            
            print("\n⚠️  Diagnostic ID mismatch detected!")
            print(f"   Connected IDs: Source=0x{self.connect_command.last_known_ids[0]:03X}, "
                  f"Target=0x{self.connect_command.last_known_ids[1]:03X}")
            print(f"   Current IDs:   Source=0x{current_ids[0]:03X}, "
                  f"Target=0x{current_ids[1]:03X}")
            print("   Consider running 'connect' to establish connection with current IDs.")
            print()
    
    def _display_connection_status(self, status: Dict[str, Any]):
        """Display detailed connection status."""
        print("\nConnection Status:")
        print("-" * 30)
        print(f"Connected: {'Yes' if status['connected'] else 'No'}")
        
        if status['interface']:
            print(f"Interface: {status['interface']}")
            print(f"Baudrate: {status['baudrate']} bps")
            print(f"Mode: {status['mode'].upper()}")
        
        if status['source_id'] and status['target_id']:
            print(f"Source ID: 0x{status['source_id']:03X}")
            print(f"Target ID: 0x{status['target_id']:03X}")
        
        if status['last_known_ids']:
            print(f"Last Known IDs: Source=0x{status['last_known_ids'][0]:03X}, "
                  f"Target=0x{status['last_known_ids'][1]:03X}")
        
        print(f"History Entries: {status['history_count']}")
    
    def _show_security_status(self):
        """Show detailed security access status."""
        info = self.security_access_module.get_service_info()
        current_level = self.security_access_module.get_current_security_level()
        
        print("\nSecurity Access Status:")
        print("-" * 30)
        print(f"Current Level: {current_level.value if current_level else 'None'}")
        print(f"Active Sessions: {info['active_sessions']}")
        print(f"Available Algorithms: {info['registered_algorithms']}")
    
    def emptyline(self):
        """Handle empty line input."""
        pass


def main():
    """Main entry point."""
    try:
        tester = CANTester()
        tester.cmdloop()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"Unexpected error: {e}")


if __name__ == '__main__':
    main()