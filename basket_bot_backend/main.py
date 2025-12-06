from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Pozwalamy frontendowi (który zaraz stworzymy) łączyć się z tym backendem
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Backend działa poprawnie!"}

@app.get("/api/matches")
async def get_matches():
    # Tymczasowe dane testowe (mock)
    return [
        {
            "id": 1,
            "venue": "Hala OSiR Mokotów",
            "date": "Dzisiaj, 18:00",
            "price": "15 PLN",
            "slots": "7/10",
            "status": "open"
        },
        {
            "id": 2,
            "venue": "Hala Ursynów",
            "date": "Jutro, 19:30",
            "price": "20 PLN",
            "slots": "10/10",
            "status": "full"
        }
    ]
