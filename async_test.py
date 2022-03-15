import csv
from time import sleep
import time
import httpx
import aiohttp
import matplotlib.pyplot as plt
import asyncio


REPEATS = 100
URLS = ['https://httpstat.us/200', "http://127.0.0.1:8000"]

loop = asyncio.get_event_loop()


async def make_aiohttp_client_session_call(url: str):
    print(f"aio> start aiohttp session {url}")
    results = []
    async with aiohttp.ClientSession() as session:
        async def send_request(idx, res, ses):
            t1 = time.monotonic()
            async with ses.get(url) as response:
                pass
            t2 = time.monotonic()
            secs = t2 - t1
            res.append(secs*1000)
            print(f"aio> req: {idx} {secs}")

        await asyncio.gather(*[send_request(_, results, session) for _ in range(REPEATS)])

    print("aio> finished aiohttp session")
    return results


async def make_httpx_async_client_call(url: str):
    print(f"httpx> start httpx client {url}")
    results = []
    async with httpx.AsyncClient() as client:
        async def send_request(idx, res, cl):
            t1 = time.monotonic()
            r = await cl.get(url)
            t2 = time.monotonic()
            secs = t2 - t1
            res.append(secs*1000)
            print(f"httpx> req: {idx} {secs}")
        await asyncio.gather(*[send_request(_, results, client) for _ in range(REPEATS)])
    print("httpx> finished httpx client")
    return results


async def main():
    urls = URLS 
    results = {}
    async def check_urls(url):
        results = []
        httpx_client_results = await make_httpx_async_client_call(url)
        aiohttp_client_results = await make_aiohttp_client_session_call(url)
        for httpx_cli_res, aio_ses_res in zip(httpx_client_results, aiohttp_client_results):
            results.append(
                {
                    "url": url,
                    "httpx_client": httpx_cli_res,
                    "aiohttp_session": aio_ses_res
                }
            )
        return results

    urls_requests = [check_urls(url) for url in urls]
    tasks = await asyncio.gather(*urls_requests)

    results[urls[0]] = tasks[0]
    results[urls[1]] = tasks[1]

    with open("./async_results.csv", "w") as f:
        writer = csv.DictWriter(f, fieldnames=["url", "httpx_client", "aiohttp_session"])
        writer.writeheader()
        for url in urls:
            writer.writerows(results[url])

    
    start = 0
    page = REPEATS

    for idx, (url, res) in enumerate(results.items()):
        indices = [_ for _ in range(len(res))]
        plt.subplot(2, 1, idx+1)
        plt.title(url)
        plt.xlabel("No of request")
        plt.ylabel("Time [ms]")
        plt.plot(indices, [_["httpx_client"] for _ in res], label="httpx.Client()", color="blue")
        plt.plot(indices, [_["aiohttp_session"] for _ in res], label="aiohttp.ClientSession()", color="orange")
        plt.legend()
        start = start + page

    plt.show()


if __name__ == '__main__':
    loop.run_until_complete(main())