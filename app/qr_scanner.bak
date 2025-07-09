# qr_scanner.py – Enhanced QR scanner with overlay support
import logging
import numpy as np
import cv2
from pyzbar.pyzbar import decode
from PySide6.QtCore import QObject, Signal, Slot, QTimer, QRect
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
        self.debounce_timer = QTimer()

        self.session.setCamera(self.camera)
        self.session.setVideoSink(self.video_sink)

        logger.debug("Connecting videoFrameChanged")
        print("Connecting videoFrameChanged")
        self.video_sink.videoFrameChanged.connect(self.processFrame)
        logger.debug(f"Camera is active? {self.camera.isActive()}")

        logger.debug("Connected.")

        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.setInterval(3000)  # 3 seconds debounce

        logger.debug("QR Scanner initialized.")

    @Slot()
    def start(self):
        logger.debug("Starting camera for QR scanning.")
        self.camera.start()

    @Slot()
    def stop(self):
        logger.debug("Stopping camera.")
        self.camera.stop()

    @Slot()
    def restart(self):
        logger.debug("Restarting scanner after detection.")
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
        width = image.width()
        height = image.height()
        depth = image.depth() // 8
        ptr = image.bits()
        arr = np.array(ptr, dtype=np.uint8).reshape((height, width, depth))

        gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
        decoded = decode(gray)

        for obj in decoded:
            data = obj.data.decode("utf-8")
            logger.info(f"QR Code Scanned: {data}")
            (x, y, w, h) = obj.rect
            self.qrBoundingBox.emit(x, y, w, h)
            logger.debug(f"Emitting bounding box: x={x}, y={y}, w={w}, h={h}")
            self.qrScanned.emit(data)
            self.stop()
            self.debounce_timer.start()
            return
    # @Slot(QVideoFrame)
    # def processFrame(self, frame: QVideoFrame):
    #     logger.debug("processFrame called")
    #     if not frame.isValid():
    #         logger.warning("Invalid frame")
    #         return

    #     image = frame.toImage()
    #     if image.isNull():
    #         logger.warning("Frame toImage() failed")
    #         return

    #     logger.debug(f"Frame size: {image.width()}x{image.height()}, format: {image.format()}")

    #     try:
    #         image = image.convertToFormat(QImage.Format.Format_RGB888)
    #     except Exception as e:
    #         logger.error(f"Image format conversion failed: {e}")
    #         return

    #     width, height = image.width(), image.height()
    #     ptr = image.bits()
    #     ptr.setsize(image.sizeInBytes())

    #     arr = np.array(ptr, dtype=np.uint8).reshape((height, width, 3))
    #     gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)

    #     decoded = decode(gray)
    #     logger.debug(f"Decoded count: {len(decoded)}")

    #     for obj in decoded:
    #         data = obj.data.decode("utf-8")
    #         rect = obj.rect
    #         logger.info(f"QR Code Detected: {data} at {rect}")
    #         self.boundingBox.emit(rect.left, rect.top, rect.width, rect.height)
    #         self.qrScanned.emit(data)
    #         self.camera.stop()
    #         break

    @Slot(QObject)
    def setVideoOutput(self, video_output):
        if not video_output:
            logger.warning("Received null video output.")
            return

        self.video_output = video_output

        # Set up camera and session
        self.camera = QCamera()
        self.session = QMediaCaptureSession()

        logger.debug(f"QML videoSink type: {type(self.video_output)}")
        logger.debug(f"video_output.videoSink: {self.video_output.property('videoSink')}")

        self.video_sink = QVideoSink()
        self.video_sink.videoFrameChanged.connect(self.processFrame)

        self.session.setCamera(self.camera)
        self.session.setVideoSink(self.video_sink)

        # Tell QML VideoOutput to use our sink
        self.video_output.setProperty("videoSink", self.video_sink)
        self.start()

        logger.debug("Camera, session, and video sink initialized.")

