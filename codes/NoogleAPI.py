from fastapi import FastAPI, UploadFile, File, Form
import uvicorn, time
import NoogleDriver
from noogleai import NoogleAI
from fastapi.middleware.cors import CORSMiddleware
from tempfile import NamedTemporaryFile

app = FastAPI()


origins = [
    "http://localhost",
    "http://127.0.0.1:5500",# Add more allowed origins here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


NoogleDriver.driverReady.wait()
noogleDriver = NoogleDriver.noogleDriver
print(noogleDriver)

@app.post("/hear")
async def NoogleAPI(audioForm: UploadFile = File(None), ask: str = Form(None)):
    st = time.time()
    if audioForm:
        with NamedTemporaryFile(delete=False, suffix=".mp3") as tempAudioFile:
            tempAudioPath = tempAudioFile.name
            tempAudioFile.write(audioForm.file.read())
        client = NoogleAI(audioForm=open(tempAudioPath, "rb"))
    else:
        print("----------------------ask is----------------", ask)
        client = NoogleAI(text_instruction=ask)
    summarized = await client.summarizeResults(driver=noogleDriver)
    print("time took:", time.time() - st)
    return summarized


if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=8888)