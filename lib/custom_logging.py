import json
from typing import Dict

def log_message_http(logger, timestamp, client, method, uri, user_agent) -> Dict:
    """
    Builds an HTTP log message as a dictionary.
    """
    logger.info(
        json.dumps({
            'MessageType': 'Data',
            'Timestamp': str(timestamp),
            'SrcAddr': client.host,
            'Sport': client.port,
            'User-Agent': user_agent,
            'Method': method.decode(),
            'Path': uri.decode()
            }
        )
    )
