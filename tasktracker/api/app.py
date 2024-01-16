from fastapi import FastAPI, Request
from starlette.responses import RedirectResponse

from .tasks.app import router as tasks_router
from .users.app import router as users_router

app = FastAPI(title="TaskTracker API", version="0.1.0")
app.include_router(tasks_router, prefix="/tasks")
app.include_router(users_router, prefix="/users")


@app.get("/")
async def index(request: Request) -> RedirectResponse:
    if "access_token" not in request.cookies:
        return RedirectResponse("/users/sign-in")
    return RedirectResponse("/tasks/my-tasks")
