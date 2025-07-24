"""
CAN Interface Manager
Handles CAN interface configuration, mode switching, and status detection.
"""
import subprocess
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class CANManager:
    """CAN interface management with support for standard CAN and CANFD modes."""
    
    def __init__(self):
        self.current_interface: Optional[str] = None
        self.current_baudrate: Optional[int] = None
        self.current_mode: Optional[str] = None
        self.interface_status: Dict[str, Any] = {}
    
    def configure_interface(self, interface: str, baudrate: int, mode: str = "can") -> bool:
        """
        Configure CAN interface with specified parameters.
        
        Args:
            interface: CAN interface name (e.g., 'can0')
            baudrate: Baudrate for the interface
            mode: Mode - 'can' for standard CAN, 'canfd' for CANFD
            
        Returns:
            bool: True if configuration successful, False otherwise
        """
        try:
            # First, bring down the interface if it's up
            self._execute_command(f"sudo ip link set {interface} down")
            
            if mode.lower() == "canfd":
                # Configure CANFD mode
                cmd = f"sudo ip link set {interface} type can bitrate {baudrate} dbitrate {baudrate * 4} fd on"
            else:
                # Configure standard CAN mode
                cmd = f"sudo ip link set {interface} type can bitrate {baudrate}"
            
            success = self._execute_command(cmd)
            if success:
                # Bring up the interface
                success = self._execute_command(f"sudo ip link set {interface} up")
                
                if success:
                    self.current_interface = interface
                    self.current_baudrate = baudrate
                    self.current_mode = mode.lower()
                    logger.info(f"CAN interface {interface} configured: {baudrate} bps, mode: {mode}")
                    return True
            
            logger.error(f"Failed to configure CAN interface {interface}")
            return False
            
        except Exception as e:
            logger.error(f"Error configuring CAN interface: {e}")
            return False
    
    def check_interface_status(self, interface: str) -> Dict[str, Any]:
        """
        Check the status of a CAN interface.
        
        Args:
            interface: CAN interface name
            
        Returns:
            dict: Interface status information
        """
        try:
            result = subprocess.run(['ip', 'link', 'show', interface], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                status = {
                    'exists': True,
                    'up': 'UP' in result.stdout,
                    'interface': interface,
                    'raw_output': result.stdout
                }
            else:
                status = {
                    'exists': False,
                    'up': False,
                    'interface': interface,
                    'error': result.stderr
                }
            
            self.interface_status[interface] = status
            return status
            
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout checking interface {interface}")
            return {'exists': False, 'up': False, 'interface': interface, 'error': 'Timeout'}
        except Exception as e:
            logger.error(f"Error checking interface status: {e}")
            return {'exists': False, 'up': False, 'interface': interface, 'error': str(e)}
    
    def list_available_interfaces(self) -> list:
        """
        List all available CAN interfaces.
        
        Returns:
            list: List of available CAN interface names
        """
        try:
            result = subprocess.run(['ip', 'link', 'show', 'type', 'can'], 
                                  capture_output=True, text=True, timeout=10)
            
            interfaces = []
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'can' in line and ':' in line:
                        # Extract interface name
                        parts = line.split(':')
                        if len(parts) >= 2:
                            interface_name = parts[1].strip().split('@')[0]
                            if interface_name.startswith('can'):
                                interfaces.append(interface_name)
            
            return interfaces
            
        except Exception as e:
            logger.error(f"Error listing CAN interfaces: {e}")
            return []
    
    def get_current_config(self) -> Dict[str, Any]:
        """
        Get current CAN interface configuration.
        
        Returns:
            dict: Current configuration details
        """
        return {
            'interface': self.current_interface,
            'baudrate': self.current_baudrate,  
            'mode': self.current_mode,
            'status': self.interface_status.get(self.current_interface, {})
        }
    
    def reset_interface(self, interface: str) -> bool:
        """
        Reset a CAN interface (bring down and up).
        
        Args:
            interface: CAN interface name
            
        Returns:
            bool: True if reset successful, False otherwise
        """
        try:
            success = self._execute_command(f"sudo ip link set {interface} down")
            if success:
                success = self._execute_command(f"sudo ip link set {interface} up")
                if success:
                    logger.info(f"CAN interface {interface} reset successfully")
                    return True
            
            logger.error(f"Failed to reset CAN interface {interface}")
            return False
            
        except Exception as e:
            logger.error(f"Error resetting CAN interface: {e}")
            return False
    
    def _execute_command(self, command: str) -> bool:
        """
        Execute a system command.
        
        Args:
            command: Command to execute
            
        Returns:
            bool: True if command executed successfully, False otherwise
        """
        try:
            logger.debug(f"Executing command: {command}")
            result = subprocess.run(command.split(), capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logger.debug(f"Command executed successfully: {command}")
                return True
            else:
                logger.warning(f"Command failed: {command}, stderr: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {command}")
            return False
        except Exception as e:
            logger.error(f"Error executing command '{command}': {e}")
            return False