from fastapi import FastAPI
from pydantic import BaseModel
import sys
from io import StringIO
import traceback
import re

app = FastAPI()

class CodeRequest(BaseModel):
    code: str

def execute_python_code(code: str):
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
        exec(code)

        output = sys.stdout.getvalue()

        return {
            "success": True,
            "output": output
        }

    except Exception:
        output = traceback.format_exc()

        return {
            "success": False,
            "output": output
        }

    finally:
        sys.stdout = old_stdout


@app.post("/code-interpreter")
def code_interpreter(req: CodeRequest):

    execution = execute_python_code(req.code)

    if execution["success"]:
        return {
            "error": [],
            "result": execution["output"]
        }

    match = re.search(
        r'File "<string>", line (\d+)',
        execution["output"]
    )

    if match:
        error_lines = [int(match.group(1))]
    else:
        error_lines = []

    return {
        "error": error_lines,
        "result": execution["output"]
    }
