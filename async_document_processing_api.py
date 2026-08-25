from fastapi import FastAPI
import asyncio
import argparse
from pathlib import Path

parser=argparse.ArgumentParser()
parser.add_argument("document")
args=parser.parse_args() 

async def worker(worker_name,queue)->str:
    while True:
        try :
            input_doc=await queue.get()
            with open(input_doc, "r") as f:
                content=f.read()
                word_count=len(content.split())
                lines=sum(1 for line in content.splitlines())
                #Assuming an average human reads one word per second
                result=f"This is {worker_name}. The average reading time is {int(word_count/60)} minutes and {word_count%60} seconds. The above document has {lines} lines."
                return result
        except Exception as e:
            print("File could not be opened")
            return "Error occurred while processing the document"
        finally:
            queue.task_done()

async def main()->None:
    queue=asyncio.Queue() #create the queue
    document=args.document
    await queue.put(document) #add the document (jobs) in queue. This is generally the job of a producer.

    tasks=[] #Create tasks, they are not executed yet.
    for i in range(3):
        task=asyncio.create_task(worker(f"worker{i}", queue))
        tasks.append(task)
    #Tasks are executed when they are awaited. as_completed ensures we get whatever finishes first
    for task in asyncio.as_completed(tasks):
        result=await task
        print(result)

    await queue.join() # Waits for all tasks in the queue to be completed. It kind of counts the tasks using the queue.task_done() in the worker code.

    for task in tasks:
        task.cancel() # we shut down the idle workers doing nothing. Well, we ask them to shut down.

    await asyncio.gather(*tasks, return_exceptions=True) #This waits for the workers to actually shut down. Dont want main shutting down before the workers now, do we?
    print(result)

    
asyncio.run(main())