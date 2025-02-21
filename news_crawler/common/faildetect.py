import requests
from urllib3.exceptions import ProtocolError, SSLError
from http.client import RemoteDisconnected
import ssl

import logging
LOG = logging.getLogger(__name__)

def check_fail(error:Exception):
    if isinstance(error,requests.ConnectionError):
        if isinstance(error.__context__, ProtocolError):
            if error.__context__.__context__ is not None and isinstance(error.__context__.__context__,RemoteDisconnected):
                return "Remote Disconect" # esto es algo raro, server desconecta a mitad..
        cause=error.__context__.__cause__
        
        if cause is None:
            LOG.debug ("   No cause: "+str(error))
            return "Generic Error, cuase is None"    
        #LOG.debug(cause)
        if cause.__cause__ is not None and isinstance(cause.__cause__,OSError):
            LOG.debug ("   OS: "+str(cause))
            return "OS "+str(cause.__cause__)
        if isinstance(cause,SSLError):
            if isinstance(cause.__context__, ssl.SSLCertVerificationError):
                return "SSL "+cause.__context__.verify_message
            if isinstance(cause.__context__, ssl.SSLEOFError):
                return "SSL EOF (No HTTPS??)"
            
        LOG.debug (str(cause))
        LOG.debug ("   General cause: "+str(error))
        return "Generic Error, cuase not checked"
    LOG.debug ("   Gen Error: "+str(error))
    LOG.debug (str(error))

    return "Generic Error, not checked"