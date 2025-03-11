import asyncio
import logging
import os
import signal

from aiosyslog.syslog_client import FAC_SYSLOG, SEV_DEBUG, SyslogClientRFC5424

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

pid = os.getpid()
task_dict = {}


# loop sending messages to a syslog server using TLS with client authentication
async def send_message_loop(host='127.0.0.1', port=6514):
    cert_data = dict(
        cafile='server.crt',
        certfile='client.crt',
        keyfile='client.key',
    )
    client = SyslogClientRFC5424(server=host, port=port, proto='tls', cert_data=cert_data)
    i = 1
    while True:
        logger.info(f"sending message #{i} to {host}:{port}")
        _ = await client.log(
            f"test message {i}", facility=FAC_SYSLOG, severity=SEV_DEBUG, program="SyslogClient", pid=pid
        )
        i += 1
        await asyncio.sleep(1)


def cancel_tasks(loop):
    """Cancel all tasks in the loop gracefully"""
    for task in asyncio.all_tasks(loop):
        task.cancel()


async def main():
    # these servers have a different response time by design to make sure this works in the loop without interruptions
    task_dict["sender_a"] = asyncio.create_task(send_message_loop(port=6514))
    task_dict["sender_b"] = asyncio.create_task(send_message_loop(port=6516))
    await asyncio.gather(*task_dict.values())


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Set up signal handling
    loop.add_signal_handler(signal.SIGINT, lambda: cancel_tasks(loop))
    loop.add_signal_handler(signal.SIGTERM, lambda: cancel_tasks(loop))

    try:
        loop.run_until_complete(main())
    except asyncio.CancelledError:
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.remove_signal_handler(sig)
        print("CancelledError caught, cleaning up...")
    finally:
        # Ensure proper cleanup
        logger.warning("finished running")
        loop.close()
