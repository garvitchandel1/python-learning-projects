from fastapi import FastAPI,Path,HTTPException,Query
import json
from pydantic import BaseModel,Field,computed_field
from typing import Annotated, Literal,Optional
from fastapi.responses import JSONResponse
app=FastAPI()

class Patient(BaseModel):
    id:Annotated[str,Field(...,description="The ID of the patient")]
    name: Annotated[str,Field(...,description="The name of the patient")]
    city: Annotated[str,Field(...,description="The city of the patient")]
    age: Annotated[int,Field(...,description="The age of the patient",gt=0,lt=120)]
    gender: Annotated[Literal["male", "female","other"],Field(...,description="The gender of the patient")]
    height: Annotated[float,Field(...,description="The height of the patient in meters",gt=0)]
    weight: Annotated[float,Field(...,description="The weight of the patient in kilograms",gt=0)]

    @computed_field
    @property
    def bmi(self) ->float:
        bmi=round(self.weight / (self.height ** 2), 2)
        return bmi

    @computed_field
    @property
    def verdict(self) ->str:
        if self.bmi < 18.5:
            return "Underweight"
        elif 18.5 <= self.bmi < 25:
            return "Normal weight"
        elif 25 <= self.bmi < 30:
            return "Overweight"
        else:
            return "Obese"

class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None, description="The name")]
    city: Annotated[Optional[str], Field(default=None, description="The city")]
    age: Annotated[Optional[int], Field(default=None, gt=0, lt=120)]
    gender: Annotated[
        Optional[Literal["male", "female", "other"]],
        Field(default=None)
    ]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]

def load_data():
    with open("patients.json", "r") as f:
        return json.load(f)

def save_data(data):
    with open("patients.json", "w") as f:
        json.dump(data, f)

@app.get("/")
def homepage():
    return{"message" : "Patient Management System API"}

@app.get("/about")
def about():
    return{"message" : "A fully functional API to manage your patients records"}

@app.get("/view")
def view():
    data=load_data()
    return data


@app.get("/patient/{patient_id}")
def view_patient(patient_id: str=Path(...,description="The ID of the patient to retrieve",example="P001")):

    data=load_data()

    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404,detail="Patient not found")


@app.get("/sort")
def sort_patients(sort_by:str=Query(...,description="Sort on the basis of height, weight or bmi"),order:str=Query('asc',description="Sort in asc or desc order")):
    valid_fields=['height','weight','bmi']

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400,detail=f"Invalid field select from {valid_fields}")

    if order not in ['asc','desc']:
        raise HTTPException(status_code=400,detail="Invalid field select between asc or desc")

    sorted_order=True if order=='desc' else False
    data=load_data()
    sorted_data=sorted(data.values(),key=lambda x:x.get(sort_by,0),reverse=sorted_order)

    return sorted_data


@app.post("/create")
def create_patient(patient:Patient):
    data=load_data()

    if patient.id in data:
        raise HTTPException(status_code=400,detail="Patient with this ID already exists")

    data[patient.id]=patient.model_dump(exclude=['id'])

    save_data(data)
    return JSONResponse(status_code=201, content={"message": "Patient created successfully"})

@app.put("/update/{patient_id}")
def update_patient(patient_id:str,patient_update:PatientUpdate):

    data=load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404,detail="Patient not found")

    patient_data=data[patient_id]

    new_data=patient_update.model_dump(exclude_unset=True)

    for key,value in new_data.items():
        patient_data[key]=value

    patient_data['id']=patient_id

    pydantic_patient=Patient(**patient_data)

    patient_data=pydantic_patient.model_dump(exclude=['id'])

    data[patient_id]=patient_data

    save_data(data)
    return JSONResponse(status_code=200, content={"message": "Patient updated successfully"})


@app.delete("/delete/{patient_id}")
def delete_patient(patient_id:str):
    data=load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")
    del data[patient_id]
    save_data(data)
    return JSONResponse(status_code=200, content={"message": "Patient deleted successfully"})