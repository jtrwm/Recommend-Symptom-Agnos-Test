from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Union
import uvicorn
from recommender_model import SymptomRecommender, load_and_clean_data

FILE_NAME = 'ai_symptom_picker.csv'
df_cleaned, col_gender, col_age, col_symptom = load_and_clean_data(FILE_NAME)
recommender = SymptomRecommender(df_cleaned, col_gender, col_age, col_symptom)

app = FastAPI(title="Agnos Symptom Recommender API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/symptoms-list")
def get_all_symptoms(gender: str = None):
    if gender:
        sorted_symptoms = recommender.get_symptoms_by_gender(gender)
    else:
        sorted_symptoms = sorted(recommender.all_unique_symptoms)
    
    return {"symptoms": sorted_symptoms}

class SymptomRequest(BaseModel):
    gender: str
    age: int
    symptoms: Union[str, List[str]]

@app.get("/")
def serve_webpage():
    return FileResponse("index.html")

@app.post("/recommend")
def get_recommendation(request: SymptomRequest):
    result = recommender.recommend(
        gender=request.gender, 
        age=request.age, 
        input_symptoms=request.symptoms
    )
    return result

if __name__ == "__main__":
    print("Starting API Server on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)