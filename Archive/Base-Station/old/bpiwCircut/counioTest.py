import asyncio, countio, board


async def catch_interrupt(pin):
    """Print a message when pin goes low."""
    with countio.Counter(pin) as interrupt:
        while True:
            if interrupt.count > 0:
                interrupt.count = 0
                print("interrupted!")
            # Let another task run.
            await asyncio.sleep(0)


async def main():
    interrupt_task = asyncio.create_task(catch_interrupt(board.GP16))
    await asyncio.gather(interrupt_task)

asyncio.run(main())