import argparse
import asyncio
import os

from syslog_client import (
    FAC_SYSLOG,
    SEV_DEBUG,
    SyslogClientRFC3164,
    SyslogClientRFC5424,
)


async def main():
    parser = argparse.ArgumentParser(description="AIO Syslog client")
    parser.add_argument("--server", "-s", type=str, help="Server name", required=True)
    parser.add_argument("--port", "-p", type=int, help="Port number", default=514)
    parser.add_argument(
        "--protocol", "-t", choices=["tcp", "udp", "tls"], help="Used transprot protocol", default="udp"
    )
    parser.add_argument("--rfc", "-r", choices=["5424", "3164"], help="RFC to use", default="5424")
    parser.add_argument("--program", "-o", type=str, help="Program name", default="SyslogClient")
    parser.add_argument("--pid", "-i", type=int, help="PID of program", default=os.getpid())
    parser.add_argument("--message", "-m", type=str, help="Message to send", required=True)
    parser.add_argument("--cafile", type=str, help="Server CA certificate", required=False, default="server.crt")
    parser.add_argument("--certfile", type=str, help="Client Certificate", required=False, default="client.crt")
    parser.add_argument("--keyfile", type=str, help="Client Private Key", required=False, default="client.key")

    args = parser.parse_args()
    cert_data = None
    if args.protocol.upper() == 'TLS':
        cert_data = dict(
            cafile=args.cafile,
            certfile=args.certfile,
            keyfile=args.keyfile,
        )

    if args.rfc == "5424":
        client = SyslogClientRFC5424(server=args.server, port=args.port, proto=args.protocol, cert_data=cert_data)
    else:
        client = SyslogClientRFC3164(server=args.server, port=args.port, proto=args.protocol, cert_data=cert_data)

    _ = await client.log(args.message, facility=FAC_SYSLOG, severity=SEV_DEBUG, program=args.program, pid=args.pid)


if __name__ == "__main__":
    asyncio.run(main())
