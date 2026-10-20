from fastapi import FastAPI
import asyncio
import argparse
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
import uuid

parser=argparse.ArgumentParser()
parser.add_argument("document",nargs="+")
args=parser.parse_args() 

@dataclass
class FileJob:
    jobID:str
    file:Path
@dataclass
class FileJobSuccess:
    jobID:str
    file:Path
    result:str
@dataclass
class FileJobFailure:
    jobID:str
    file:Path
    error:str

job_tracking_status={}

def file_processing(input_doc)->tuple[int, int]:
    with open(input_doc, "r") as f:
        content=f.read()
        word_count=len(content.split())
        lines=sum(1 for line in content.splitlines())
    return word_count,lines

async def worker(worker_name,queue,res_queue)->None:
    while True:

        Job=await queue.get()
        job_tracking_status[Job.jobID]="Processing"
        try :
        #Assuming an average human reads one word per second
            word_count, lines = file_processing(Job.file)
            avg_reading_time=f" {int(word_count/60)} minutes and {word_count%60} seconds"
            result=f"{worker_name}: The average reading time is {avg_reading_time}. The above document has {lines} lines."
            job_tracking_status[Job.jobID]="Completed"
            await res_queue.put(FileJobSuccess(jobID=Job.jobID, file=Job.file, result=result))
            await asyncio.sleep(0)
        except Exception as e:
            job_tracking_status[Job.jobID]="Failed"
            await res_queue.put(FileJobFailure(jobID=Job.jobID, file=Job.file, error=str(e)))
        finally:
            queue.task_done()

async def main()->None:
    queue=asyncio.Queue() #create the queue
    res_queue: asyncio.Queue[FileJobSuccess | FileJobFailure] = asyncio.Queue()
    documents=args.document
    counter=0

    for document in documents:
        job_id=str(uuid.uuid4())
        job_tracking_status[job_id]="Queued"
        Job=FileJob(jobID=job_id, file=Path(document))
        await queue.put(Job) #add the document (jobs) in queue. This is generally the job of a producer.
        counter+=1
    
    tasks=[] #Create tasks, they are not executed yet.
    for i in range(3):
        task=asyncio.create_task(worker(f"worker{i}", queue,res_queue))
        tasks.append(task)
    #Tasks are executed when they are awaited. as_completed ensures we get whatever finishes first
    await queue.join() # Waits for all tasks in the queue to be completed. It kind of counts the tasks using the queue.task_done() in the worker code.
    for output in range(counter):
        try : 
            output=await res_queue.get()
            if isinstance(output, FileJobSuccess):
                print(f"Job ID : {output.jobID}: {job_tracking_status[output.jobID]}, result: {output.result}")
            else:
                print(f"Job ID : {output.jobID}: {job_tracking_status[output.jobID]}, error: {output.error}")
        finally:
            res_queue.task_done()
    for task in tasks:
        task.cancel() # we shut down the idle workers doing nothing. Well, we ask them to shut down.

    await asyncio.gather(*tasks, return_exceptions=True) #This waits for the workers to actually shut down. Dont want main shutting down before the workers now, do we?

    
asyncio.run(main())