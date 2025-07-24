"""
Set Command
Enhanced command for CAN interface configuration, baudrate settings, and diagnostic session management.
"""
import argparse
import logging
from typing import Optional, Dict, Any
from core.can_manager import CANManager

logger = logging.getLogger(__name__)


class SetCommand:
    """Enhanced set command with CAN interface auto-configuration and session management."""
    
    def __init__(self, can_manager: CANManager):
        self.can_manager = can_manager
        self.current_source_id: Optional[int] = None
        self.current_target_id: Optional[int] = None
        self.diagnostic_sessions: Dict[str, Dict[str, int]] = {}
    
    def execute(self, args: list) -> bool:
        """
        Execute the set command with provided arguments.
        
        Args:
            args: Command arguments
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            parser = self._create_parser()
            parsed_args = parser.parse_args(args)
            
            success = True
            
            # Handle CAN interface configuration
            if parsed_args.interface:
                baudrate = parsed_args.baudrate or 500000  # Default baudrate
                mode = parsed_args.mode or "can"  # Default mode
                
                logger.info(f"Configuring CAN interface: {parsed_args.interface}, "
                           f"baudrate: {baudrate}, mode: {mode}")
                
                success &= self.can_manager.configure_interface(
                    parsed_args.interface, baudrate, mode
                )
                
                if success:
                    print(f"✓ CAN interface {parsed_args.interface} configured successfully")
                    print(f"  Baudrate: {baudrate} bps")
                    print(f"  Mode: {mode.upper()}")
                else:
                    print(f"✗ Failed to configure CAN interface {parsed_args.interface}")
            
            # Handle diagnostic ID configuration
            if parsed_args.source or parsed_args.target:
                if parsed_args.source:
                    self.current_source_id = int(parsed_args.source, 16) if isinstance(parsed_args.source, str) else parsed_args.source
                    logger.info(f"Set source diagnostic ID: 0x{self.current_source_id:03X}")
                    print(f"✓ Source diagnostic ID set to: 0x{self.current_source_id:03X}")
                
                if parsed_args.target:
                    self.current_target_id = int(parsed_args.target, 16) if isinstance(parsed_args.target, str) else parsed_args.target
                    logger.info(f"Set target diagnostic ID: 0x{self.current_target_id:03X}")
                    print(f"✓ Target diagnostic ID set to: 0x{self.current_target_id:03X}")
                
                # Save session configuration
                if self.current_source_id and self.current_target_id:
                    session_name = f"session_{self.current_source_id:03X}_{self.current_target_id:03X}"
                    self.diagnostic_sessions[session_name] = {
                        'source_id': self.current_source_id,
                        'target_id': self.current_target_id
                    }
                    logger.info(f"Diagnostic session saved: {session_name}")
            
            # Handle session listing
            if parsed_args.list_sessions:
                self.list_diagnostic_sessions()
            
            # Handle interface listing
            if parsed_args.list_interfaces:
                self.list_can_interfaces()
            
            return success
            
        except Exception as e:
            logger.error(f"Error executing set command: {e}")
            print(f"✗ Error: {e}")
            return False
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser for set command."""
        parser = argparse.ArgumentParser(
            description="Configure CAN interface and diagnostic IDs",
            add_help=False
        )
        
        # CAN interface configuration
        parser.add_argument('-i', '--interface', 
                          help='CAN interface name (e.g., can0)')
        parser.add_argument('-b', '--baudrate', type=int,
                          help='CAN baudrate (default: 500000)')
        parser.add_argument('-m', '--mode', choices=['can', 'canfd'],
                          help='CAN mode: can (standard) or canfd')
        
        # Diagnostic ID configuration
        parser.add_argument('-s', '--source',
                          help='Source diagnostic ID (hex format, e.g., 733)')
        parser.add_argument('-t', '--target', 
                          help='Target diagnostic ID (hex format, e.g., 73b)')
        
        # Information commands
        parser.add_argument('--list-sessions', action='store_true',
                          help='List saved diagnostic sessions')
        parser.add_argument('--list-interfaces', action='store_true',
                          help='List available CAN interfaces')
        
        return parser
    
    def list_diagnostic_sessions(self):
        """List all saved diagnostic sessions."""
        if not self.diagnostic_sessions:
            print("No diagnostic sessions saved.")
            return
        
        print("\nSaved Diagnostic Sessions:")
        print("-" * 50)
        for session_name, config in self.diagnostic_sessions.items():
            print(f"  {session_name}:")
            print(f"    Source ID: 0x{config['source_id']:03X}")
            print(f"    Target ID: 0x{config['target_id']:03X}")
        
        # Show current session
        if self.current_source_id and self.current_target_id:
            print(f"\nCurrent Session:")
            print(f"  Source ID: 0x{self.current_source_id:03X}")
            print(f"  Target ID: 0x{self.current_target_id:03X}")
    
    def list_can_interfaces(self):
        """List available CAN interfaces."""
        interfaces = self.can_manager.list_available_interfaces()
        
        if not interfaces:
            print("No CAN interfaces found.")
            return
        
        print("\nAvailable CAN Interfaces:")
        print("-" * 30)
        
        for interface in interfaces:
            status = self.can_manager.check_interface_status(interface)
            status_str = "UP" if status.get('up', False) else "DOWN"
            print(f"  {interface}: {status_str}")
        
        # Show current configuration
        config = self.can_manager.get_current_config()
        if config['interface']:
            print(f"\nCurrent Configuration:")
            print(f"  Interface: {config['interface']}")
            print(f"  Baudrate: {config['baudrate']} bps")
            print(f"  Mode: {config['mode'].upper()}")
    
    def get_current_diagnostic_ids(self) -> tuple:
        """
        Get current diagnostic IDs.
        
        Returns:
            tuple: (source_id, target_id)
        """
        return (self.current_source_id, self.current_target_id)
    
    def load_session(self, session_name: str) -> bool:
        """
        Load a saved diagnostic session.
        
        Args:
            session_name: Name of the session to load
            
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        if session_name in self.diagnostic_sessions:
            config = self.diagnostic_sessions[session_name]
            self.current_source_id = config['source_id']
            self.current_target_id = config['target_id']
            logger.info(f"Loaded diagnostic session: {session_name}")
            return True
        else:
            logger.error(f"Diagnostic session not found: {session_name}")
            return False
    
    def validate_can_configuration(self) -> Dict[str, Any]:
        """
        Validate current CAN configuration.
        
        Returns:
            dict: Validation results
        """
        config = self.can_manager.get_current_config()
        validation = {
            'interface_configured': config['interface'] is not None,
            'interface_up': False,
            'diagnostic_ids_set': self.current_source_id is not None and self.current_target_id is not None,
            'ready': False
        }
        
        if config['interface']:
            status = self.can_manager.check_interface_status(config['interface'])
            validation['interface_up'] = status.get('up', False)
        
        validation['ready'] = (validation['interface_configured'] and 
                              validation['interface_up'] and 
                              validation['diagnostic_ids_set'])
        
        return validation
    
    def get_help_text(self) -> str:
        """Get help text for the set command."""
        return """
Set Command Usage:

CAN Interface Configuration:
  set -i can0 -b 500000 -m can      # Configure standard CAN mode
  set -i can0 -b 500000 -m canfd    # Configure CANFD mode

Diagnostic ID Configuration:
  set -s 733 -t 73b                 # Set source and target diagnostic IDs

Information Commands:
  set --list-interfaces             # List available CAN interfaces
  set --list-sessions              # List saved diagnostic sessions

Examples:
  set -i can0 -b 500000 -s 733 -t 73b  # Complete configuration
  set -i can1 -b 1000000 -m canfd      # High-speed CANFD setup
"""