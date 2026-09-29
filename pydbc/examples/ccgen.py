import sys
from pathlib import Path

from pydbc.api.imports import import_dbc
from pydbc.cgen.generators import MicroPythonCanAppGenerator, SocketCanCGenerator, PythonCanAppGenerator

session = import_dbc(sys.argv[1], debug=False, logLevel="DEBUG")

mpy = MicroPythonCanAppGenerator(session)
py_code = mpy.render(app_name="mpy_app")  # optional filter by message names
Path("micropython_app.py").write_text(py_code, encoding="utf-8")

sc = SocketCanCGenerator(session)
c_code = sc.render(program_name="socketcan_app")  # optional filter
Path("socketcan_app.c").write_text(c_code, encoding="utf-8")

pc = PythonCanAppGenerator(session)
pc_code = pc.render(app_name="python_app")
Path("python_app.py").write_text(pc_code, encoding="utf-8")