import fastapi
import yaml
from fastapi.middleware.cors import CORSMiddleware

app = fastapi.FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

@app.get("/config")
async def get_config():
    with open("./assets/config.yaml", "r") as f:
        return yaml.load(f.read(), Loader=yaml.FullLoader)
    
