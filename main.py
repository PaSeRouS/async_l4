import asyncio


async def tcp_chat():
    reader, writer = await asyncio.open_connection(
        'minechat.dvmn.org',
        5000
    )

    while not reader.at_eof():
        data = await reader.readline()
        print(data.decode())


def main():
    asyncio.run(tcp_chat())


if __name__ == '__main__':
    main()
