from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.ai import generate_latex_response
from app.schemas import LatexRequest, LatexResponse

app = FastAPI(title="LaTeX Bot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="app/templates")


@app.get("/")
def root():
    return {"message": "LaTeX Bot API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/mid", response_class=HTMLResponse)
def mid(request: Request):
    return templates.TemplateResponse("mid.html", {"request": request})


@app.post("/latex", response_model=LatexResponse)
def create_latex(request: LatexRequest):
    try:
        return generate_latex_response(request.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))