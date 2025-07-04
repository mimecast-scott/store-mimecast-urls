from fastapi import FastAPI, HTTPException
from pickledb import PickleDB

app = FastAPI()

# Load the PickleDB database (non-dump on set mode)
#db = PickleDB('./data/mimecast_urls.json')

@app.get("/get")
async def get_value(key: str):
    db = PickleDB('./data/mimecast_urls.json')
    """
    Retrieve the value associated with the given key from the PickleDB file.
    """
    if not db.get(key):
        raise HTTPException(status_code=404, detail=f"Key '{key}' not found.")
    value = db.get(key)
    return {"key": key, "value": value}

@app.get("/getAll")
async def get_All_Key():
    db = PickleDB('./data/mimecast_urls.json')
    """
    Retrieve the value associated with the given key from the PickleDB file.
    """
    allKeys = db.all()
    output = {
                "total" : len(allKeys),
                "keys" : allKeys
    }
    return output

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("decodeapi:app", host="0.0.0.0", port=8000, reload=True)
