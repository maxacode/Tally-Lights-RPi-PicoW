import socketpool
import wifi
from adafruit_httpserver import Server, MIMETypes
from connectToWlan import mainFunc
from getConfig import getConfig
from asyncio import create_task, gather, run, sleep as async_sleep
from adafruit_httpserver import (
    Server,
    REQUEST_HANDLED_RESPONSE_SENT,
    Request,
    FileResponse,
)
import npDone
npDone.setNeo(npDone.red, 1, 0)

from mdns import Server as MServ
md = MServ(wifi.radio)
md.hostname = 'aj'

config = getConfig("baseConfig.json")
mainFunc(config, True)



pool = socketpool.SocketPool(wifi.radio)
server = Server(pool, "/templates", debug=True)


@server.route("/")
def base(request: Request):
    """
    Serve the default index.html file.
    """
    return FileResponse(request, "index.html")


# Start the server.
server.start(str(wifi.radio.ipv4_address))


async def handle_http_requests():
    while True:
        # Process any waiting requests
        pool_result = server.poll()

        if pool_result == REQUEST_HANDLED_RESPONSE_SENT:
            # Do something only after handling a request
            pass

        await async_sleep(0)


async def do_something_useful():
    while True:
        # Do something useful in this section,
        # for example read a sensor and capture an average,
        # or a running total of the last 10 samples
        for x in range(0, 5):
            for y in range(50,200,40):
                npDone.setNeo((y,0,y), .5, x)
                npDone.setNeo(npDone.red, .5, 2)
                
        await async_sleep(1)

        # If you want you can stop the server by calling server.stop() anywhere in your code


async def main():
    await gather(
        create_task(handle_http_requests()),
        create_task(do_something_useful()),
    )


run(main())