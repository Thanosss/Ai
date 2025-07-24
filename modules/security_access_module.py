"""
Security Access Module (UDS Service 0x27)
Implements UDS SecurityAccess service for authentication and authorization.
"""
import logging
import hashlib
import secrets
from typing import Optional, Dict, Any, Callable
from enum import Enum

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security access levels."""
    LEVEL_1 = 0x01
    LEVEL_2 = 0x02
    LEVEL_3 = 0x03
    LEVEL_4 = 0x04


class SecurityAccessModule:
    """UDS Service 0x27 - SecurityAccess implementation."""
    
    def __init__(self, can_interface=None):
        self.can_interface = can_interface
        self.service_id = 0x27
        self.positive_response_id = 0x67
        self.current_security_level: Optional[SecurityLevel] = None
        self.active_sessions: Dict[int, Dict[str, Any]] = {}
        self.seed_key_algorithms: Dict[SecurityLevel, Callable] = {}
        self._setup_default_algorithms()
    
    def request_seed(self, security_level: SecurityLevel) -> Optional[bytes]:
        """
        Request seed for security access.
        
        Args:
            security_level: Security level to request access for
            
        Returns:
            bytes: Seed value if successful, None if failed
        """
        try:
            level_value = security_level.value
            # For seed request, use odd sub-function (level * 2 - 1)
            sub_function = (level_value * 2) - 1
            
            request_data = [self.service_id, sub_function]
            
            logger.info(f"Requesting seed for security level {level_value}")
            
            response = self._send_uds_request(request_data)
            
            if response and len(response) >= 2:
                response_service = response[0]
                response_sub_function = response[1]
                
                if response_service == self.positive_response_id and response_sub_function == sub_function:
                    if len(response) > 2:
                        seed = bytes(response[2:])
                        
                        # Store session information
                        self.active_sessions[level_value] = {
                            'seed': seed,
                            'timestamp': self._get_timestamp(),
                            'attempts': 0
                        }
                        
                        logger.info(f"Received seed for level {level_value}: {seed.hex()}")
                        return seed
                    else:
                        logger.info(f"Security level {level_value} already unlocked")
                        self.current_security_level = security_level
                        return b''  # Empty seed indicates already unlocked
                else:
                    logger.error(f"Invalid response for seed request level {level_value}")
                    return None
            else:
                logger.error(f"No valid response received for seed request level {level_value}")
                return None
                
        except Exception as e:
            logger.error(f"Error requesting seed for level {security_level.value}: {e}")
            return None
    
    def send_key(self, security_level: SecurityLevel, key: bytes) -> bool:
        """
        Send key for security access.
        
        Args:
            security_level: Security level
            key: Computed key value
            
        Returns:
            bool: True if access granted, False otherwise
        """
        try:
            level_value = security_level.value
            # For key sending, use even sub-function (level * 2)
            sub_function = level_value * 2
            
            request_data = [self.service_id, sub_function] + list(key)
            
            logger.info(f"Sending key for security level {level_value}")
            
            response = self._send_uds_request(request_data)
            
            if response and len(response) >= 2:
                response_service = response[0]
                response_sub_function = response[1]
                
                if response_service == self.positive_response_id and response_sub_function == sub_function:
                    self.current_security_level = security_level
                    logger.info(f"Security access granted for level {level_value}")
                    
                    # Clean up session
                    if level_value in self.active_sessions:
                        del self.active_sessions[level_value]
                    
                    return True
                else:
                    logger.error(f"Security access denied for level {level_value}")
                    # Increment attempt counter
                    if level_value in self.active_sessions:
                        self.active_sessions[level_value]['attempts'] += 1
                    return False
            else:
                logger.error(f"No valid response received for key send level {level_value}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending key for level {security_level.value}: {e}")
            return False
    
    def compute_key_from_seed(self, security_level: SecurityLevel, seed: bytes) -> Optional[bytes]:
        """
        Compute key from seed using registered algorithm.
        
        Args:
            security_level: Security level
            seed: Seed value
            
        Returns:
            bytes: Computed key if successful, None if failed
        """
        try:
            if security_level in self.seed_key_algorithms:
                algorithm = self.seed_key_algorithms[security_level]
                key = algorithm(seed)
                logger.debug(f"Computed key for level {security_level.value}: {key.hex()}")
                return key
            else:
                logger.error(f"No algorithm registered for security level {security_level.value}")
                return None
                
        except Exception as e:
            logger.error(f"Error computing key from seed: {e}")
            return None
    
    def perform_security_access(self, security_level: SecurityLevel) -> bool:
        """
        Perform complete security access sequence (request seed + send key).
        
        Args:
            security_level: Security level to unlock
            
        Returns:
            bool: True if access granted, False otherwise
        """
        try:
            # Step 1: Request seed
            seed = self.request_seed(security_level)
            if seed is None:
                return False
            
            # If seed is empty, already unlocked
            if len(seed) == 0:
                return True
            
            # Step 2: Compute key
            key = self.compute_key_from_seed(security_level, seed)
            if key is None:
                logger.error(f"Failed to compute key for security level {security_level.value}")
                return False
            
            # Step 3: Send key
            return self.send_key(security_level, key)
            
        except Exception as e:
            logger.error(f"Error performing security access for level {security_level.value}: {e}")
            return False
    
    def register_seed_key_algorithm(self, security_level: SecurityLevel, algorithm: Callable[[bytes], bytes]):
        """
        Register a seed-key algorithm for a security level.
        
        Args:
            security_level: Security level
            algorithm: Function that takes seed bytes and returns key bytes
        """
        self.seed_key_algorithms[security_level] = algorithm
        logger.info(f"Registered seed-key algorithm for security level {security_level.value}")
    
    def get_current_security_level(self) -> Optional[SecurityLevel]:
        """
        Get current security level.
        
        Returns:
            SecurityLevel: Current security level if any, None otherwise
        """
        return self.current_security_level
    
    def reset_security_access(self):
        """Reset security access state."""
        self.current_security_level = None
        self.active_sessions.clear()
        logger.info("Security access state reset")
    
    def _setup_default_algorithms(self):
        """Setup default seed-key algorithms."""
        
        def simple_algorithm(seed: bytes) -> bytes:
            """Simple XOR-based algorithm for testing."""
            key = bytearray()
            for i, byte in enumerate(seed):
                key.append(byte ^ (0xAA if i % 2 == 0 else 0x55))
            return bytes(key)
        
        def hash_algorithm(seed: bytes) -> bytes:
            """Hash-based algorithm."""
            return hashlib.sha256(seed + b'secret_key').digest()[:4]
        
        # Register default algorithms
        self.register_seed_key_algorithm(SecurityLevel.LEVEL_1, simple_algorithm)
        self.register_seed_key_algorithm(SecurityLevel.LEVEL_2, hash_algorithm)
    
    def _send_uds_request(self, request_data: list) -> Optional[list]:
        """
        Send UDS request through CAN interface.
        
        Args:
            request_data: UDS request data bytes
            
        Returns:
            list: Response data bytes if successful, None if failed
        """
        # This is a placeholder implementation
        logger.debug(f"Sending UDS request: {' '.join(f'{b:02X}' for b in request_data)}")
        
        # Simulate responses for testing
        if request_data[0] == self.service_id:
            sub_function = request_data[1]
            
            # Seed request (odd sub-function)
            if sub_function % 2 == 1:
                # Generate a mock seed
                seed = secrets.token_bytes(4)
                response = [self.positive_response_id, sub_function] + list(seed)
                logger.debug(f"Received UDS response: {' '.join(f'{b:02X}' for b in response)}")
                return response
            
            # Key send (even sub-function)  
            else:
                # Always accept key for testing
                response = [self.positive_response_id, sub_function]
                logger.debug(f"Received UDS response: {' '.join(f'{b:02X}' for b in response)}")
                return response
        
        return None
    
    def _get_timestamp(self) -> float:
        """Get current timestamp."""
        import time
        return time.time()
    
    def get_service_info(self) -> Dict[str, Any]:
        """
        Get information about this service.
        
        Returns:
            dict: Service information
        """
        return {
            'service_name': 'SecurityAccess',
            'service_id': f'0x{self.service_id:02X}',
            'positive_response_id': f'0x{self.positive_response_id:02X}',
            'current_security_level': self.current_security_level.value if self.current_security_level else None,
            'active_sessions': len(self.active_sessions),
            'registered_algorithms': [level.value for level in self.seed_key_algorithms.keys()]
        }