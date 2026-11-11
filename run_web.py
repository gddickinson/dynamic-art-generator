"""Start the Dynamic Art Generator web app on http://127.0.0.1:8112 (local only).

Needs: pip install -r requirements-web.txt
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run("web.app:app", host="127.0.0.1", port=8112)
