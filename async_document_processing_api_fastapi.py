from fastapi import FastAPI, HTTPException,UploadFile,File
import asyncio
from pathlib import Path
from dataclasses import dataclass
import uuid
from contextlib import asynccontextmanager
import shutil
from typing import List
from fastapi.responses import HTMLResponse,JSONResponse

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



class DocumentProcessor:

    def __init__(self)->None:
        #resources here, the queues for now
        self.queue :asyncio.Queue[FileJob] = asyncio.Queue()
        #self.res_queue=asyncio.Queue()
        self.tasks:List[asyncio.Task[None]]=[]
        self.job_tracking_status:dict[str,str]={}
        self.job_results: dict[str, FileJobSuccess | FileJobFailure] = {}  #how do i define type hints for queues?

    async def start(self)->None:
            #initialise 3 workers
            for i in range(3):
                task=asyncio.create_task(self.worker(f"worker{i}"))
                self.tasks.append(task)

    async def worker(self, worker_name:str) -> None:
        
        while True:
            Job=await self.queue.get()
            self.job_tracking_status[Job.jobID]="Processing"
            try :
            #Assuming an average human reads one word per second
                word_count, lines = self.file_processing(Job.file)
                avg_reading_time=f" {int(word_count/60)} minutes and {word_count%60} seconds"
                result=f"{worker_name}: The average reading time is {avg_reading_time}. The above document has {lines} lines."
                self.job_tracking_status[Job.jobID]="Completed"
                self.job_results[Job.jobID]=FileJobSuccess(jobID=Job.jobID, file=Job.file, result=result)
                await asyncio.sleep(0)
            except Exception as e:
                self.job_tracking_status[Job.jobID]="Failed"
                self.job_results[Job.jobID]=FileJobFailure(jobID=Job.jobID, file=Job.file, error=str(e))
            finally:
                self.queue.task_done()

    def file_processing(self,input_doc:Path)->tuple[int, int]:
        with open(input_doc, "r") as f:
            content=f.read()
            word_count=len(content.split())
            lines=sum(1 for line in content.splitlines())
        return word_count,lines
    
    async def submit_job(self,document:Path)-> str:
        #add the job in the queue.
        job_id=str(uuid.uuid4())
        self.job_tracking_status[job_id]="Queued"
        Job=FileJob(jobID=job_id, file=document)
        await self.queue.put(Job)
        #self.counter+=1

        return job_id
    
    def get_job_status(self,job_id:str)->str|None:
        if job_id in self.job_tracking_status: 
            return self.job_tracking_status[job_id]
        else:
            return None

    def get_job_result(self,job_id:str)->FileJobSuccess | FileJobFailure | None:
        result=self.job_results.get(job_id)

        if isinstance(result, FileJobSuccess):
            return result
        elif isinstance(result, FileJobFailure):
            return result
        else :
            return None

    
    async def shutdown(self)->None:
        await self.queue.join() # Waits for all tasks in the queue to be completed. It kind of counts the tasks using the queue.task_done() in the worker code.
        for task in self.tasks:
            task.cancel() # we shut down the idle workers doing nothing. Well, we ask them to shut down.
    
        await asyncio.gather(*self.tasks, return_exceptions=True) #This waits for the workers to actually shut down. Dont want main shutting down before the workers now, do we?
        

@asynccontextmanager
async def lifespan(app: FastAPI):
    processor = DocumentProcessor()
    await processor.start()

    app.state.processor = processor

    yield

    await processor.shutdown()


app = FastAPI(lifespan=lifespan)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
        <head>
            <title>Async Document Processing API</title>
        </head>
        <body>
            <h1>Async Document Processing API</h1>
            <p>Upload documents and process them asynchronously.</p>
            <a href="/docs">Explore API Documentation</a>
        </body>
    </html>
    """

@app.post("/upload")
async def upload_file(file:UploadFile=File(...))->dict[str,str]:
    if not file.filename or not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are supported")
    file_path = UPLOAD_DIR / f"{uuid.uuid4()}.txt"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    job_id = await app.state.processor.submit_job(file_path)
    return {"job_id": job_id}

@app.get("/jobs/{job_id}")
def get_job_status(job_id: str)->JSONResponse:
    status = app.state.processor.get_job_status(job_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return JSONResponse(status_code=200,content={"status": status})

@app.get("/jobs/{job_id}/results")
def get_job_result(job_id: str)->JSONResponse:
    
    result = app.state.processor.get_job_result(job_id)
    if isinstance(result, FileJobSuccess):
        return JSONResponse(status_code=200,content={"status":"Completed","result": result.result})
    elif isinstance(result, FileJobFailure):
        return JSONResponse(status_code=200,content={"status":"Failed","error": result.error})
    else:
        if app.state.processor.get_job_status(job_id) is None:
            raise HTTPException(status_code=404, detail="Job not found")
        else:
            return JSONResponse(status_code=202,content={"status":"Processing"})