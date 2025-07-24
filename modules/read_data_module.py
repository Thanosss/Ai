"""
Read Data Module (UDS Service 0x22)
Implements UDS ReadDataByIdentifier service for diagnostic data retrieval.
"""
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class ReadDataModule:
    """UDS Service 0x22 - ReadDataByIdentifier implementation."""
    
    def __init__(self, can_interface=None):
        self.can_interface = can_interface
        self.service_id = 0x22
        self.positive_response_id = 0x62
        self.data_cache: Dict[int, bytes] = {}
    
    def read_data_by_identifier(self, data_identifier: int) -> Optional[bytes]:
        """
        Read data by identifier using UDS service 0x22.
        
        Args:
            data_identifier: 16-bit data identifier (DID)
            
        Returns:
            bytes: Data bytes if successful, None if failed
        """
        try:
            # Construct UDS request: Service ID + Data Identifier (2 bytes)
            did_high = (data_identifier >> 8) & 0xFF
            did_low = data_identifier & 0xFF
            request_data = [self.service_id, did_high, did_low]
            
            logger.info(f"Sending ReadDataByIdentifier request for DID 0x{data_identifier:04X}")
            
            # Send request through CAN interface (placeholder - would use actual CAN implementation)
            response = self._send_uds_request(request_data)
            
            if response and len(response) >= 3:
                response_service = response[0]
                response_did = (response[1] << 8) | response[2]
                
                if response_service == self.positive_response_id and response_did == data_identifier:
                    data = response[3:] if len(response) > 3 else b''
                    self.data_cache[data_identifier] = data
                    logger.info(f"Successfully read {len(data)} bytes for DID 0x{data_identifier:04X}")
                    return data
                else:
                    logger.error(f"Invalid response for DID 0x{data_identifier:04X}")
                    return None
            else:
                logger.error(f"No valid response received for DID 0x{data_identifier:04X}")
                return None
                
        except Exception as e:
            logger.error(f"Error reading data by identifier 0x{data_identifier:04X}: {e}")
            return None
    
    def read_multiple_identifiers(self, identifiers: List[int]) -> Dict[int, Optional[bytes]]:
        """
        Read multiple data identifiers.
        
        Args:
            identifiers: List of data identifiers to read
            
        Returns:
            dict: Mapping of identifier to data (None if failed)
        """
        results = {}
        for did in identifiers:
            results[did] = self.read_data_by_identifier(did)
        return results
    
    def get_cached_data(self, data_identifier: int) -> Optional[bytes]:
        """
        Get cached data for a data identifier.
        
        Args:
            data_identifier: Data identifier
            
        Returns:
            bytes: Cached data if available, None otherwise
        """
        return self.data_cache.get(data_identifier)
    
    def clear_cache(self):
        """Clear the data cache."""
        self.data_cache.clear()
        logger.info("Data cache cleared")
    
    def format_data_response(self, data_identifier: int, data: bytes) -> str:
        """
        Format data response for display.
        
        Args:
            data_identifier: Data identifier
            data: Raw data bytes
            
        Returns:
            str: Formatted response string
        """
        if not data:
            return f"DID 0x{data_identifier:04X}: No data"
        
        hex_data = ' '.join(f'{b:02X}' for b in data)
        ascii_data = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in data)
        
        return f"DID 0x{data_identifier:04X}: {hex_data} (ASCII: {ascii_data})"
    
    def _send_uds_request(self, request_data: List[int]) -> Optional[List[int]]:
        """
        Send UDS request through CAN interface.
        
        Args:
            request_data: UDS request data bytes
            
        Returns:
            list: Response data bytes if successful, None if failed
        """
        # This is a placeholder implementation
        # In a real implementation, this would:
        # 1. Format the request according to ISO-TP protocol
        # 2. Send via CAN interface
        # 3. Handle multi-frame responses
        # 4. Return the response data
        
        logger.debug(f"Sending UDS request: {' '.join(f'{b:02X}' for b in request_data)}")
        
        # Simulate a response for testing
        if request_data[0] == self.service_id:
            # Return a mock positive response
            response = [self.positive_response_id] + request_data[1:] + [0x01, 0x02, 0x03, 0x04]
            logger.debug(f"Received UDS response: {' '.join(f'{b:02X}' for b in response)}")
            return response
        
        return None
    
    def get_service_info(self) -> Dict[str, Any]:
        """
        Get information about this service.
        
        Returns:
            dict: Service information
        """
        return {
            'service_name': 'ReadDataByIdentifier',
            'service_id': f'0x{self.service_id:02X}',
            'positive_response_id': f'0x{self.positive_response_id:02X}',
            'cached_identifiers': list(self.data_cache.keys()),
            'cache_size': len(self.data_cache)
        }