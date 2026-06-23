import aiohttp
import asyncio
from dataclasses import dataclass, field
import time
from typing import Optional
@dataclass
class URLResult:
     url:str
     content_type:str
     body:str
     success:bool
     error:str
     response_time:float
     status:Optional[int]=None

async def url_fetcher(session,url_input,sem):
    retry = 3
    while retry:
        async with sem:
            print(f"Acquired Semaphore for {url_input}")
            print(f"Starting {url_input}")
            status=None
            content_type='' 
            body=''
            success=False
            error='No Error'
            response_time=0
            try :
                start=time.monotonic()
                async with session.get(url_input) as response:
                    status=response.status
                    content_type=response.headers['content-type']

                    html = await response.text()
                    body=html[:15]
                    success=True
                response_time=time.monotonic()-start
                print(f"Finished {url_input}")
                return URLResult(url=url_input, status=status, content_type=content_type, body=body, success=success, error=error, response_time=response_time)
            
            except Exception as e:
                status=None
                error=str(e)
                success=False
                retry -= 1
                
        if retry !=0 : await asyncio.sleep(2)    
    print(f"Failed to fetch {url_input}")
    return URLResult(url=url_input, status=status, content_type=content_type, body=body, success=success, error=error, response_time=response_time)
            
        

async def main():
    urls = [
    "https://google.com",
    "https://github.com",
    "https://openai.com",
    "https://stackoverflow.com",
    "https://python.org",
    "https://reddit.com",
    "https://wikipedia.org",
    "https://microsoft.com",
    "https://amazon.com",
    "https://youtube.com",

    # Some that should fail
    "https://this-domain-does-not-exist-123456.com",
    "https://definitely-not-a-real-site-xyz.org",

    # Some pages likely to return non-200 responses
    "https://httpbin.org/status/404",
    "https://httpbin.org/status/500",
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/2",
    "https://httpbin.org/delay/3",
    "https://httpbin.org/delay/4",
    "https://httpbin.org/delay/5",]
    
    sem=asyncio.Semaphore(2)
    async with aiohttp.ClientSession() as session:
         
        tasks=[url_fetcher(session,url,sem) for url in urls]
        results=await asyncio.gather(*tasks)
        for result in results:
            print(result)
    
    summary(results)

def summary(results):
    total_urls=len(results)
    successful_urls=len([r for r in results if r.success])
    failed_urls=total_urls-successful_urls

    average_time=(sum(r.response_time for r in results if r.success))/(successful_urls if successful_urls > 0 else 1)
    fastest_response=float('inf')
    slowest_response=0
    fastest_url=''
    slowest_url=''
    for r in results:
        if r.success:
            if r.response_time < fastest_response:
                fastest_response=r.response_time
                fastest_url=r.url
            if r.response_time > slowest_response:
                slowest_response=r.response_time
                slowest_url=r.url
    print(f"Total URLs: {total_urls}")
    print(f"Successful URLs: {successful_urls}")
    print(f"Failed URLs: {failed_urls}")
    print(f"Average Response Time: {average_time}")
    print(f"Fastest Response Time: {fastest_response}")
    print(f"Slowest Response Time: {slowest_response}")
    print(f"Fastest URL: {fastest_url}")
    print(f"Slowest URL: {slowest_url}")

asyncio.run(main())
