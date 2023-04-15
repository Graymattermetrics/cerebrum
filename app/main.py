import fastapi

app = fastapi.FastAPI()


@app.get("/config")
async def get_config():
    with open("./assets/config.yaml", "r") as f:
        return f.read()
    
