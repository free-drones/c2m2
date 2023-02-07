import cv2
from dronenet.base_camera import BaseCamera


class Camera(BaseCamera):
  video_source = ''
  def __init__(self, source):
    Camera.video_source = source
    super(Camera, self).__init__()

  @staticmethod
  def frames():
    camera = cv2.VideoCapture(Camera.video_source)
    if not camera.isOpened():
      raise RuntimeError('Could not start camera.')

    while True:
      # read current frame
      _, img = camera.read()

      # encode as a jpeg image and return it
      yield cv2.imencode('.jpg', img)[1].tobytes()
