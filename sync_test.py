import csv
from time import sleep
import httpx
import requests
from timeit import default_timer as timer
import matplotlib.pyplot as plt


REPEATS = 100
URLS = ['https://httpstat.us/200', "http://127.0.0.1:8000"]

def make_httpx_call(url: str):
    print(f"start httpx {url}")
    results = []
    for _ in range(REPEATS):
        t1 = timer()
        r = httpx.get(url)
        t2 = timer()
        secs = t2 - t1
        results.append(secs*1000)
        print(f"req: {_}")
        sleep(0.1)
    print("finished https")
    return results


def make_requests_call(url: str):
    print(f"start requests {url}")

    results = []
    for _ in range(REPEATS):
        t1 = timer()
        r = requests.get(url)
        t2 = timer()
        secs = t2 - t1
        results.append(secs*1000)
        print(f"req: {_}")
        sleep(0.1)
    print("finished requests")
    return results


def make_requests_session_call(url: str):
    print(f"start requests session {url}")
    results = []
    with requests.Session() as client:
        for _ in range(REPEATS):
            t1 = timer()
            r = client.get(url)
            t2 = timer()
            secs = t2 - t1
            results.append(secs*1000)
            print(f"req: {_}")

            sleep(0.1)
    print("finished requests session")
    return results


def make_httpx_client_call(url: str):
    print(f"start httpx client {url}")
    results = []
    with httpx.Client() as client:
        for _ in range(REPEATS):
            t1 = timer()
            r = client.get(url)
            t2 = timer()
            secs = t2 - t1
            results.append(secs*1000)
            print(f"req: {_}")
            sleep(0.1)
    print("finished httpx client")
    return results


def main():
    urls = URLS 
    results = {}
    for url in urls:
        results[url] = []
        httpx_result = make_httpx_call(url)
        httpx_client_results = make_httpx_client_call(url)
        requests_results = make_requests_call(url)
        requests_session_results = make_requests_session_call(url)
        for httpx_r, httpx_cli_res, req_res, req_ses_res in zip(httpx_result, httpx_client_results, requests_results, requests_session_results):
            results[url].append(
                {
                    "url": url,
                    "httpx": httpx_r,
                    "httpx_client": httpx_cli_res,
                    "requests": req_res,
                    "requests_session": req_ses_res
                }
            )

    with open("./sync_results.csv", "w") as f:
        writer = csv.DictWriter(f, fieldnames=["url", "httpx", "httpx_client", "requests", "requests_session"])
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
        plt.plot(indices, [_["httpx"] for _ in res], label="httpx", color="red")
        plt.plot(indices, [_["httpx_client"] for _ in res], label="httpx.Client()", color="blue")
        plt.plot(indices, [_["requests"] for _ in res], label="requests", color="green")
        plt.plot(indices, [_["requests_session"] for _ in res], label="requests.Session()", color="orange")
        plt.legend()
        start = start + page

    plt.show()


if __name__ == '__main__':
    main()