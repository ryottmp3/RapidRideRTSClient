# qr_scanner.py – stable + working video output and QR scanning

import logging
import numpy as np
import cv2
from pyzbar.pyzbar import decode
from PySide6.QtCore import QObject, Signal, Slot, QTimer
from PySide6.QtMultimedia import QMediaCaptureSession, QCamera, QVideoSink, QVideoFrame
from PySide6.QtGui import QImage

logger = logging.getLogger("rts.qrscanner")

class QrScanner(QObject):
    qrScanned = Signal(str)
    errorOccurred = Signal(str)
    qrBoundingBox = Signal(int, int, int, int)  # x, y, w, h

    def __init__(self):
        super().__init__()
        self.camera = QCamera()
        self.session = QMediaCaptureSession()
        self.video_sink = QVideoSink()
        self.running = False

        self.session.setCamera(self.camera)
        self.session.setVideoSink(self.video_sink)

        self.video_sink.videoFrameChanged.connect(self.processFrame)

        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.setInterval(3000)

        logger.debug("QR Scanner initialized.")

    @Slot(QObject)
    def setVideoOutput(self, video_output):
        if not video_output:
            logger.warning("No video output provided.")
            return

        logger.debug("Assigning video sink to QML VideoOutput")
        video_output.setProperty("videoSink", self.video_sink)
        self.start()

    @Slot()
    def start(self):
        if self.running:
            logger.debug("Camera already running.")
            return
        logger.debug("Starting camera.")
        self.camera.start()
        self.running = True

    @Slot()
    def stop(self):
        if not self.running:
            logger.debug("Camera already stopped.")
            return
        logger.debug("Stopping camera and disconnecting sink.")
        self.session.setVideoSink(None)  # unbind session first
        self.camera.stop()
        self.running = False

    @Slot()
    def restart(self):
        logger.debug("Restarting scanner.")
        self.debounce_timer.stop()
        self.start()

    @Slot(QVideoFrame)
    def processFrame(self, frame: QVideoFrame):
        if self.debounce_timer.isActive():
            return

        if not frame.isValid():
            return

        image = frame.toImage()
        if image.isNull():
            return

        image = image.convertToFormat(QImage.Format.Format_RGB888)
        width, height = image.width(), image.height()
        depth = image.depth() // 8
        ptr = image.bits()
        arr = np.array(ptr, dtype=np.uint8).reshape((height, width, depth))

        gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
        decoded = decode(gray)

        for obj in decoded:
            data = obj.data.decode("utf-8")
            (x, y, w, h) = obj.rect
            self.qrBoundingBox.emit(x, y, w, h)
            logger.info(f"QR Code Detected: {data} at ({x}, {y}, {w}, {h})")
            self.qrScanned.emit(data)
            # self.stop()
            self.debounce_timer.start()
            return

    @Slot()
    def shutdown(self):
        logger.debug("Shutting down QrScanner")
        if self.video_sink:
            try:
                self.video_sink.videoFrameChanged.disconnect()
            except Exception:
                pass
            self.session.setVideoSink(None)
            self.video_sink = None

        if self.camera and self.camera.isActive():
            self.camera.stop()
        self.session.setCamera(None)
        self.camera = None
        self.running = False

