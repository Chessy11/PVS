from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from routers import (user_register_route, 
                     speech_process_route, 
                     call_status_route, 
                     twiml_response_route, 
                     checker_route, 
                     balance_route,
          
                     )
from database.db import Base, engine
from utils.ngrok_config import set_ngrok_url
from dotenv import load_dotenv
from pyngrok import ngrok
import uvicorn
import logging
import os



load_dotenv()


def start_ngrok(port):
    ngrok_tunnel = ngrok.connect(port)
    print(f"Ngrok tunnel established at: {ngrok_tunnel.public_url}")
    set_ngrok_url(ngrok_tunnel.public_url)
    
app = FastAPI(root_path="/")

@app.get("testfile")
async def get_test_file():
    file_path = "/home/OffPower/Work/phone-verification-system/static/beep1.mp3"
    return FileResponse(file_path)

app.mount("/static", StaticFiles(directory="/home/OffPower/Work/phone-verification-system/static"), name="static")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn")

async def startup():
    print("Starting up the application: Phone verification system")
    if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        print("Using Google Credentials from:", os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
        start_ngrok(8080)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
            
async def shutdown():
    print("Shutting down")
    ngrok.disconnect()


app.add_event_handler("startup", startup)
app.add_event_handler("shutdown", shutdown)


origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(user_register_route.router)
app.include_router(speech_process_route.router)
app.include_router(call_status_route.router)
app.include_router(twiml_response_route.router)
app.include_router(checker_route.router)
app.include_router(balance_route.router)
app.include_router(stripe_route.router)
app.include_router(paypal_route.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080)