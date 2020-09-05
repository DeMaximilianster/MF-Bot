from PIL import Image
from presenter.logic.nudity.nudity import Nudity
from presenter.logic.nudity.compresser import Compresser
from presenter.logic.nudity.cutter import Cutter


def check_video_for_nudity(vid_path="input.mp4"):
	compresser = Compresser()
	cutter = Cutter(vid_path)
	nudity = Nudity()

	frames = cutter.get_frames()
	frame = next(frames)
	compressed = compresser.compress(frame)
	compressed.save("temp.jpg", optimize=True)
	prev1 = 0
	prev2 = 0
	current = nudity.score("temp.jpg")
	while (current+prev1+prev2)/3 < 0.9: #Бывает, что сетка определяет контент как взрослый только потому, что видны ноги
	    try:
	        frame = next(frames)
	    except:
	        break
	    compressed = compresser.compress(frame)
	    compressed.save("temp.jpg", optimize=True)
	    current, prev1, prev2 = nudity.score("temp.jpg"), current, prev1
	    #print(current, prev1, prev2, (current+prev1+prev2)/3)
	else:
	    return True
	return False

def check_photo_for_nudity(photo_path="input.jpg"):
	img = Image.open(photo_path)
	compresser = Compresser()
	compressed = compresser.compress(img)
	compressed.save("temp.jpg")
	nudity = Nudity()
	return nudity.score("temp.jpg")
print(check_video_for_nudity())