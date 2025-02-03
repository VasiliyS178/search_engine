import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.api.base import main_router
from src.core.config import settings


app = FastAPI(title=settings.APP_TITLE, version=settings.PROJECT_VERSION)

app.include_router(main_router)
app.mount('/static', StaticFiles(directory='src/static'), 'static')


if __name__ == '__main__':
    uvicorn.run('src.main:app', reload=False, host='0.0.0.0', port=8000)
