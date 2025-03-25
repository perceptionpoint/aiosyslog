class UnknownSyslogResponseError(Exception):
    pass

class SyslogConnectionFailure(Exception):
    pass

class SyslogConnectionTimeout(Exception):
    pass

class ClientCertificateLoadError(Exception):
    pass

class ServerCertificateLoadError(Exception):
    pass


