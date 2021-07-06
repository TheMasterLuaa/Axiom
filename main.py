# All of this is possible by the amazing job the maker of PyEngine3D did, thanks! :D

__version__ = 2021.1

# Importing python integrated modules, BUT THEY ARE NEEDED!
import sys
import os
import time

# Part 1 of making code go faster!
from multiprocessing import Process

# # Part 2 of MCGF!
#from numba import jit

# Importing OpenGL;
# In some day, ill add Vulkan support.
import OpenGL
OpenGL.ERROR_CHECKING = True
OpenGL.ERROR_LOGGING = True
OpenGL.FULL_LOGGING = False
OpenGL.ALLOW_NUMPY_SCALARS = True

from PyEngine3D.Common import CustomQueue, CustomPipe
from PyEngine3D.App import CoreManager
from PyEngine3D.Utilities import AutoEnum, Config


class GUIEditor(AutoEnum):
    CLIENT_MODE = ()
    QT = ()
    TKINTER = ()

#@jit(nopython=True)
def run(editor=GUIEditor.QT, project_filename=""):
    appCmdQueue = None
    uiCmdQueue = None
    pipe1, pipe2 = None, None
    editor_process = None

    config = Config("config.ini")

    # load last project file
    if "" == project_filename and config.hasValue('Project', 'recent'):
        last_project = config.getValue('Project', 'recent')
        if os.path.exists(last_project):
            project_filename = last_project

    # other process - GUIEditor
    if editor != GUIEditor.CLIENT_MODE:
        appCmdQueue = CustomQueue()
        uiCmdQueue = CustomQueue()
        pipe1, pipe2 = CustomPipe()

        # Select GUI backend
        if editor == GUIEditor.QT:
            from PyEngine3D.UI.QT.MainWindow import run_editor
        elif editor == GUIEditor.TKINTER:
            from PyEngine3D.UI.TKInter.MainWindow import run_editor
        editor_process = Process(target=run_editor, args=(project_filename, uiCmdQueue, appCmdQueue, pipe2))
        editor_process.start()

    # Client process
    coreManager = CoreManager.instance()
    result = coreManager.initialize(appCmdQueue, uiCmdQueue, pipe1, project_filename)
    if result:
        coreManager.run()
        next_next_open_project_filename = coreManager.get_next_open_project_filename()
    else:
        next_next_open_project_filename = ""

    # GUI Editor process end
    if editor_process:
        editor_process.join()

    return next_next_open_project_filename  # reload or not


if __name__ == "__main__":
    editor = GUIEditor.TKINTER

    # run program!!
    project_filename = sys.argv[1] if len(sys.argv) > 1 else ""
    next_open_project_filename = run(editor, project_filename)
    if os.path.exists(next_open_project_filename):
        executable = sys.executable
        args = sys.argv[:]
        if len(args) > 1:
            args[1] = next_open_project_filename
        else:
            args.append(next_open_project_filename)
        args.insert(0, sys.executable)
        time.sleep(1)
        os.execvp(executable, args)
