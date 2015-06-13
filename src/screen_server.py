from bottle import route, run, template, request, abort
from PIL import Image
from PIL import ImageDraw
from PIL import ImageEnhance
import time
from rgbmatrix import Adafruit_RGBmatrix
from os import listdir
from os.path import isfile, join
import glob
# Rows and chain length are both required parameters:
matrix = Adafruit_RGBmatrix(32, 1)

# Bitmap example w/graphics prims
image = Image.new("1", (32, 32)) # Can be larger than matrix if wanted!!
draw  = ImageDraw.Draw(image)    # Declare Draw instance before prims

# 24-bit RGB scrolling example.
# The adafruit.png image has a couple columns of black pixels at
# the right edge, so erasing after the scrolled image isn't necessary.
# curl -XPOST -H "Content-Type: application/json" localhost:8080/block -d '{"block":"durt"}
matrix.Clear()

blocks = [ f.split('.png')[0] for f in listdir('./minecraft') if isfile(join('./minecraft',f)) ]
current_block = 'Grass.png'
displayState = True;
brightness = 1.0;

def load_block(block):
    global brightness;
    matrix.Clear()
    current_block = block
    image = Image.open(join('./minecraft/', block +'.png'))
    enhancer = ImageEnhance.Color(image)
    image = enhancer.enhance(brightness);
    image.load()
    matrix.SetImage(image.im.id, 0, 0)

@route('/power', method='POST')
def switch_display():
  global displayState
  displayState = not displayState
  if displayState == False:
    matrix.Clear()
  else:
    load_block(current_block)

@route('/brightness', method='POST')
def brighness():
  global brightness;
  brightness = request.json.get('brightness')

@route('/grow', method='POST')
def grow():
  block = request.json.get('block')
  for f in sorted(glob.glob("./minecraft/%s_stage_*" %block)):
    matrix.Clear()
    image = Image.open(f)
    image.load()
    matrix.SetImage(image.im.id, 0, 0)
    time.sleep(1.0)

@route('/blocks')
def get_block():
    return {'blocks' :blocks}

@route('/block', method='POST')
def set_block():
    global current_block
    block = request.json.get('block')
    if block in blocks:
      load_block(block)

      # matrix.Clear()
      # current_block = block
      # image = Image.open(join('./minecraft/', block))
      # image.load()
      # matrix.SetImage(image.im.id, 0, 0)
      # # time.sleep(1.0)
    else:
         abort(400, "Sorry, unknown block type: %s" % block)

run(host='localhost', port=8080)