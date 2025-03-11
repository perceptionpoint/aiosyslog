# aiosyslog

## Description
Syslog client for Python3 (RFC 3164/5424) using AysncIO


Supported RFC specs:
* RFC3164 (https://www.ietf.org/rfc/rfc3164.txt)
* RFC5424 (https://www.ietf.org/rfc/rfc5424.txt)


## Features
- Implemented with AsyncIO tasks in mind.
- Supports TCP, UDP, and TLS.
- Supports client certificate authentication.

## Example
- basic cli
```bash
python3.12 pysyslogclient/cli.py --server 127.0.0.1 --port 6514 --protocol tcp --message "test message"
```

- cli using client authentication
```bash
python3.12 pysyslogclient/cli.py --server 127.0.0.1 --port 6514 --protocol tls --cafile my_server_certificate.crt  --certfile my_client_cert.crt --keyfile my_private_key.key --message "test message over tls with client cert authentication"
```
- in your own code
	see [example.py](example.py)
