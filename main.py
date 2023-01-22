import uvicorn
from src.functions.core.config import settings as c

if __name__ == "__main__":
    uvicorn.run("src.functions.apps:app", host=c.host, port=c.port, reload=c.debug)
