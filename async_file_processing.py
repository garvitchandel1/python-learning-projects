import asyncio
from dataclasses import dataclass
from pathlib import Path

@dataclass
class FileJob:
    input_path:Path
    output_path:Path


async def worker(name,queue):
    
    while True:
        Job=await queue.get()

        file=Job.input_path

        try :
            with file.open("r") as f:
                content=f.read()
                word_count=len(content.split())
                lines=sum(1 for line in content.splitlines())
                #Assuming an average human reads one word per second
                result1=f"Worker {name}: {word_count} words, {lines} lines"
                result2=f"The average reading time is {int(word_count/60)} minutes and {word_count%60} seconds"
                # output=Path(Job.output_path)
                # output.write_text(f"{result1}\n{result2}")
                print(f"Worker {name}: Finished processing {Job.input_path}")
        except Exception as e:
            print("File could not be opened")
        finally:
            queue.task_done()
        


async def producer():

    p=Path("D:\\Switch\\Python\\files\\")

    for child in p.iterdir():
        job=FileJob(input_path=Path(child),output_path=f"D:\\Switch\\Python\\files\\processed_{child.name}")
        yield job


async def main():
    queue=asyncio.Queue()
    async for job in producer():
        await queue.put(job)
        print(f"Job added to queue: {job.input_path}")

    tasks=[]
    for i in range(2):
        task=asyncio.create_task(worker(f"worker{i}",queue))
        tasks.append(task)

    await queue.join()

    for task in tasks:
        task.cancel()
    # Wait until all worker tasks are cancelled.
    
    await asyncio.gather(*tasks, return_exceptions=True)


asyncio.run(main())