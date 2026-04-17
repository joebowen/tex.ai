# TeX.ai

For the love of LaTex <3.

I have devloped a FastAPI web app that converts natural-language math prompts into clean LaTeX and renders the result live in the browser with KaTeX. Too often when I am using a popular LLM do my chats run out of context leading me to waste more of my tokens to get LaTex to render; TeX.ai aims to fix that :)

## Features

- Convert plain English math requests into LaTeX
- Render LaTeX instantly in the browser
- JSON API with structured responses
- Playground UI for testing prompts
- Built with FastAPI, Jinja2, and KaTeX
- OpenAI-compatible backend support via Poe/OpenAI-style API

## Example

**Prompt**
```text
give me the quadratic formula in latex
```

**Response**
```latex
x=\frac{-b\pm\sqrt{b^2-4ac}}{2a}
```

## Project Structure
The following project structure should work as a start

```text
.
├── app/
│   ├── ai.py
│   ├── config.py
│   ├── main.py
│   ├── prompt.py
│   └── schemas.py
├── static/
│   ├── css/
│   └── js/
├── templates/
│   └── index.html
├── .env
├── requirements.txt
└── README.md
```

## Tech Stack
```text
- Backend: FastAPI
- Frontend: HTML, CSS, JavaScript, Jinja2
- Rendering: KaTeX
- LLM API: OpenAI-compatible client (I am using POE)
- Server: Uvicorn
```

## Getting started
1.  Clone the repo
```bash
git clone https://github.com/joebowen/tex.ai
cd tex.ai
```

2. Create and activate an Anaconda environment
```bash
conda create -n math-to-latex python=3.11
conda activate math-to-latex
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Create a .env file
```env
POE_API_KEY=your_api_key_here
POE_BASE_URL=https://api.poe.com/v1
POE_MODEL=your_model_name
```
Note, for this step you may use a different OpenAI-compatible provider, just update the base URL and model accordingly.

5. Run the app
```bash
uvicorn app.main:app --reload
```
and then open
```text
http://127.0.0.1:8000
```

## Further notes
This is up-to-date as of 4/16/2026. As more updates are made, things will be updated accordingly. Unitl then, Happy TeXing!! 😁

-JB



