from PIL import Image
import cv2

class Cutter:

    def __init__(self, video_path):
        self.video = cv2.VideoCapture(video_path)
    
    def get_frames(self, skip=59):
        while (True):
            ret, frame = self.video.read()
            if ret:
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                im_pil = Image.fromarray(img)
                b = False
                for i in range(skip):
	                try:
	                    self.video.grab()
	                except:
	                    b = True
	                    break
                yield im_pil
                if b:
                    break
            else:
                break
        self.video.release()
    
    def release(self):
        self.video.release()

