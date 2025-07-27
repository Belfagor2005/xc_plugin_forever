import os
import ssl
import threading
import time
from urllib.request import Request, urlopen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.ProgressBar import ProgressBar
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from twisted.internet import reactor
from .. import _

SKIN_imagedownloadScreen = """
<screen position="center,center" size="600,200" title="Download in corso">
    <widget name="activityslider" position="10,30" size="580,20" />
    <widget name="package" position="10,60" size="580,30" font="Regular;20" />
    <widget name="status" position="10,100" size="580,60" font="Regular;18" />
</screen>
"""


class DownloadThread(threading.Thread):
    def __init__(
            self,
            url,
            target,
            progress_callback,
            completion_callback,
            error_callback):
        super().__init__()
        self.url = url
        self.target = target
        self.progress_callback = progress_callback
        self.completion_callback = completion_callback
        self.error_callback = error_callback
        self._stop_event = threading.Event()
        self.start_time = time.time()

    def run(self):
        try:
            target_dir = os.path.dirname(self.target)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)

            req = Request(self.url)
            req.add_header(
                'User-Agent',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36')

            try:
                context = ssl._create_unverified_context()
                response = urlopen(req, context=context, timeout=30)
            except BaseException:
                response = urlopen(req, timeout=30)

            total_size = int(response.headers.get('Content-Length', 0))
            block_size = 1024 * 8
            downloaded = 0

            with open(self.target, 'wb') as f:
                while True:
                    if self._stop_event.is_set():
                        f.close()
                        try:
                            os.remove(self.target)
                        except BaseException:
                            pass
                        return

                    buffer = response.read(block_size)
                    if not buffer:
                        break

                    downloaded += len(buffer)
                    f.write(buffer)

                    elapsed = time.time() - self.start_time
                    speed = downloaded / elapsed / 1024 if elapsed > 0 else 0  # KB/s
                    remaining = (total_size - downloaded) / \
                        (speed * 1024) if speed > 0 else 0

                    self.progress_callback(
                        downloaded, total_size, speed, remaining)

            self.completion_callback()

        except Exception as e:
            self.error_callback(str(e))

    def stop(self):
        self._stop_event.set()


class imagedownloadScreen(Screen):
    def __init__(self, session, name='', target='', url=''):
        Screen.__init__(self, session)
        self.skin = SKIN_imagedownloadScreen

        self.target = target
        self.name = name
        self.url = url

        self.downloading = False
        self.success = False
        self.error_message = ""

        self["activityslider"] = ProgressBar()
        self["activityslider"].setRange((0, 100))
        self["activityslider"].setValue(0)
        self["status"] = Label(_("Preparando il download..."))
        self["package"] = Label(name)

        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions"],
            {
                "ok": self.dexit,
                "cancel": self.dexit
            },
            -1
        )

        self.onLayoutFinish.append(self.startDownload)

    def startDownload(self):
        """Avvia il processo di download in un thread separato"""
        self.downloading = True
        self.setTitle(_("Download in corso"))
        self["status"].setText(_("Connessione al server..."))

        self.download_thread = DownloadThread(
            self.url,
            self.target,
            self.updateProgress,
            self.downloadCompleted,
            self.downloadFailed
        )
        self.download_thread.start()

    def updateProgress(self, current, total, speed, remaining):
        reactor.callFromThread(
            self._updateProgressGUI,
            current,
            total,
            speed,
            remaining)

    def downloadCompleted(self):
        reactor.callFromThread(self._downloadCompletedGUI)

    def downloadFailed(self, error_message):
        reactor.callFromThread(self._downloadFailedGUI, error_message)

    def _updateProgressGUI(self, current, total, speed, remaining):
        """Aggiorna gli elementi GUI (chiamato nel thread principale)"""
        if total > 0:
            percent = int(100 * current / total)
            self["activityslider"].setValue(percent)

            status = _("Scaricamento: %d%% - Velocità: %.1f KB/s - Tempo rimanente: %d sec") % (
                percent, speed, remaining)
            self["status"].setText(status)
            self.setTitle(_("Download: %d%%") % percent)

    def _downloadCompletedGUI(self):
        """Aggiorna la GUI per download completato (thread principale)"""
        self.downloading = False
        self.success = True
        self["status"].setText(_("Download completato con successo!"))
        self["activityslider"].setValue(100)
        self.setTitle(_("Download completato"))

    def _downloadFailedGUI(self, error_message):
        """Aggiorna la GUI per errore (thread principale)"""
        self.downloading = False
        self.success = False
        self.error_message = error_message

        if "401" in self.error_message:
            self.error_message = _("Accesso non autorizzato (401)")
        elif "404" in self.error_message:
            self.error_message = _("Risorsa non trovata (404)")
        elif "timed out" in self.error_message:
            self.error_message = _("Timeout della connessione")

        self["status"].setText(self.error_message)
        self.setTitle(_("Download fallito"))

        if os.path.exists(self.target):
            try:
                os.remove(self.target)
            except BaseException:
                pass

    def dexit(self):
        """Gestisce l'uscita dallo schermo"""
        if self.downloading:
            self.session.openWithCallback(
                self.confirmAbort,
                MessageBox,
                _("Vuoi davvero interrompere il download?"),
                MessageBox.TYPE_YESNO
            )
        else:
            self.close(self.success)

    def confirmAbort(self, answer):
        """Conferma l'interruzione del download"""
        if answer:
            if self.download_thread:
                try:
                    self.download_thread.stop()
                except BaseException:
                    pass

            if os.path.exists(self.target):
                try:
                    os.remove(self.target)
                except BaseException:
                    pass

            self.close(False)

    def close(self, success=False):
        """Chiude lo schermo"""
        if self.download_thread and self.download_thread.is_alive():
            try:
                self.download_thread.stop()
            except BaseException:
                pass

        Screen.close(self, success)
