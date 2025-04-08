import asyncio
import logging
import socket
import ssl
from datetime import datetime
from .const import FAC_USER, SEV_INFO
from .helpers import datetime2rfc3339
from .tmpfile import TempFile
from . import exceptions as exc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


class SyslogClient:
    def __init__(
        self,
        server: str,
        port: int,
        proto: str = 'UDP',
        forceipv4: bool = False,
        clientname: str = None,
        rfc: str = None,
        maxMessageLength: int = 2048,
        cert_data: dict = dict(),
        timeout: int = 30
    ) -> None:
        self.socket = None
        self.server = server
        self.port = port
        self.proto = proto
        self.rfc = rfc
        self.maxMessageLength = maxMessageLength
        self.forceipv4 = forceipv4
        self.clientname=clientname
        self.use_tls = True if proto.upper() == 'TLS' else False
        self.ssl_context = None
        self.timeout = timeout
        if self.use_tls:
            self.cafile = cert_data['cafile']
            self.certfile = cert_data.get('certfile')
            self.keyfile = cert_data.get('keyfile')

        if self.clientname is None:
            self.clientname = socket.getfqdn() or socket.gethostname() or "aiosyslog-client"

    async def send(self, message: bytes):
        message = message[: self.maxMessageLength]
        if self.proto.upper() == "UDP":
            res = await self._send_udp(message)
            return res
        elif self.proto.upper() in ["TCP", "TLS"]:
            res = await self._send_tcp(message)
            return res
        else:
            raise ValueError("Unsupported protocol. Use 'udp','tcp' or 'tls'")

    async def _send_udp(self, message):
        loop = asyncio.get_running_loop()
        transport, _ = await loop.create_datagram_endpoint(
            lambda: asyncio.DatagramProtocol(), remote_addr=(self.server, self.port)
        )
        transport.sendto(message)
        transport.close()

    def get_ssl_context(self):
        ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        try:
            # can pass the content of the file directly. kinda hacky, but whatever.
            if self.cafile.startswith("-----BEGIN"):
                ssl_context.load_verify_locations(cadata=self.cafile)
            else:
                ssl_context.load_verify_locations(self.cafile)
        except Exception as ex:
            raise exc.ServerCertificateLoadError(f"Could not load server certificate: {ex}")
        # if using client certificate authentication
        if self.certfile and self.keyfile:
            try:
                if self.certfile.startswith("-----BEGIN") and self.keyfile.startswith("-----BEGIN"):
                        # this is kinda not effective at all, ngl.. but i dont wanna store keys on the drive.
                        with TempFile(self.certfile) as cert, TempFile(self.keyfile) as key:
                            ssl_context.load_cert_chain(certfile=cert.path, keyfile=key.path)
                else:
                    ssl_context.load_cert_chain(certfile=self.certfile, keyfile=self.keyfile)
            except Exception as ex:
                raise exc.ClientCertificateLoadError(f"Could not load client certificate: {ex}")
        return ssl_context

    # TODO: add a timeout decorator?
    async def _send_tcp(self, message):
        if self.use_tls and self.ssl_context is None:
            self.ssl_context=self.get_ssl_context()
        try:
            _, conn = await asyncio.wait_for(
                asyncio.open_connection(self.server, self.port, ssl=self.ssl_context),
                timeout=self.timeout
            )
            conn.write(message)
            await conn.drain()
            conn.close()
            await conn.wait_closed()
        except asyncio.TimeoutError:
            raise exc.SyslogConnectionTimeout(f"Timed out waiting, server={self.server}:{self.port}")
        except OSError as ex:
            e_str=str(ex)
            if "Errno 61" in e_str:
                raise exc.SyslogConnectionFailure(f"Connection refused, server={self.server}:{self.port}")
            elif "Errno 8" in e_str:
                raise exc.SyslogConnectionFailure(f"Invalid server name provided, server={self.server}:{self.port}")
            else:
                raise exc.SyslogUnmanagedSocketError(f"Unknown OSError exception: {ex}")
        except Exception as ex:
            raise exc.UnknownSyslogResponseError(f"uknown error while sending message: {ex}")


class SyslogClientRFC5424(SyslogClient):
    def __init__(
        self,
        server: str,
        port: int,
        proto: str = 'udp',
        forceipv4: bool = False,
        clientname: str = None,
        cert_data: dict = dict(),
        timeout: int = 30
    ) -> None:
        super().__init__(
            server=server,
            port=port,
            proto=proto,
            forceipv4=forceipv4,
            clientname=clientname,
            rfc='5424',
            maxMessageLength=4096,
            cert_data=cert_data,
            timeout=timeout
        )

    async def log(
        self,
        message: str,
        facility: int = FAC_USER,
        severity: int = SEV_INFO,
        timestamp: datetime = None,
        hostname: str = None,
        version: int = 1,
        program: str = None,
        pid: int = None,
        msgid: int = None,
    ):
        pri = facility * 8 + severity
        timestamp_s = (
            datetime2rfc3339(datetime.utcnow(), is_utc=True)
            if timestamp is None
            else datetime2rfc3339(timestamp, is_utc=False)
        )
        # wtf is this for..
        hostname_s = self.clientname if hostname is None else hostname
        appname_s = "-" if program is None else program
        procid_s = "-" if pid is None else pid
        msgid_s = "-" if msgid is None else msgid

        formatted_payload = "<%i>%i %s %s %s %s %s %s\n" % (
            pri,
            version,
            timestamp_s,
            hostname_s,
            appname_s,
            procid_s,
            msgid_s,
            message,
        )
        response = await self.send(formatted_payload.encode('utf-8'))
        return response


class SyslogClientRFC3164(SyslogClient):
    def __init__(
        self,
        server: str,
        port: int,
        proto: str = 'udp',
        forceipv4: bool = False,
        clientname: str = None,
        cert_data: dict = dict(),
        timeout: int = 30
    ) -> None:
        super().__init__(
            server=server,
            port=port,
            proto=proto,
            forceipv4=forceipv4,
            clientname=clientname,
            rfc='3164',
            maxMessageLength=2048,
            cert_data=cert_data,
            timeout=timeout
        )

    async def log(
        self,
        message: str,
        facility: int = FAC_USER,
        severity: int = SEV_INFO,
        timestamp: datetime = datetime.now(),
        hostname: str = None,
        program: str = "SyslogClient",
        pid: int = None,
    ) -> None:
        pri = facility * 8 + severity
        timestamp_s = timestamp.strftime("%b %d %H:%M:%S")
        hostname_s = self.clientname if hostname is None else hostname

        if pid is not None:
            program += "[%i]" % (pid)

        d = "<%i>%s %s %s: %s\n" % (pri, timestamp_s, hostname_s, program, message)

        response = await self.send(d.encode('ASCII', 'ignore'))
        return response


if __name__ == '__main__':
    import doctest

    doctest.testmod()
