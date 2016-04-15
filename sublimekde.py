import os
import sublime
import sublime_plugin
import subprocess
import threading


class KdeFileDialog(sublime_plugin.WindowCommand):
    def getWindowId(self):
        winId = subprocess.check_output(['xdotool', 'getactivewindow'])
        return winId.strip()

    def getCwd(self):
        cwd = os.getcwd()
        view = self.window.active_view()
        if view:
            fn = view.file_name()
            if fn:
                cwd = os.path.dirname(fn)
        return cwd


class OpenWithKdeCommand(KdeFileDialog):
    def run(self):
        process = subprocess.Popen(
            ['kdialog',
             '--attach',
             KdeFileDialog.getWindowId(self),
             '--multiple',
             '--getopenfilename',
             KdeFileDialog.getCwd(self)],
            stdout=subprocess.PIPE
        )
        t = DialogThread(process, self.on_open)
        t.start()

    def on_open(self, file_name):
        for i in file_name.split():
            self.window.open_file(i)


class SaveWithKdeCommand(KdeFileDialog):
    def run(self):
        process = subprocess.Popen(['kdialog',
                                    '--attach',
                                    KdeFileDialog.getWindowId(self),
                                    '--getsavefilename',
                                    KdeFileDialog.getCwd(self)],
                                   stdout=subprocess.PIPE)
        t = DialogThread(process, self.on_save)
        t.start()

    def on_save(self, file_name):
        self.window.active_view().retarget(file_name)
        self.window.run_command('save')


class OpenKonsoleCommand(sublime_plugin.WindowCommand):
    def run(self):
        cwd = os.getcwd()
        view = self.window.active_view()
        if view:
            fn = view.file_name()
            if fn:
                cwd = os.path.dirname(fn)

        subprocess.Popen(['konsole', '--separate', '--workdir', cwd])


class DialogThread(threading.Thread):
    def __init__(self, process, callback):
        self.process = process
        self.callback = callback
        super(DialogThread, self).__init__()

    def run(self):
        stdout_data, stderr_data = self.process.communicate()
        if not self.process.returncode:

            def run_callback():
                self.callback(stdout_data.strip().decode('utf-8'))

            sublime.set_timeout(run_callback, 0)
