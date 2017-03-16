#!/usr/bin/env python
# -*- coding: utf-8 -*-

# FractalCaptcha.py v 0.1
# (c) Alexandr A Alexeev 2011 | http://eax.me/

from PIL import Image, ImageDraw, ImageFont, ImageFilter
from random import random
from numpy import mgrid, exp

def gaussian_grid(size = 5):
    m = size/2
    n = m+1  # remember python is 'upto' n in the range below
    x, y = mgrid[-m:n,-m:n]
    # multiply by a factor to get 1 in the corner of the grid
    # ie for a 5x5 grid   fac*exp(-0.5*(2**2 + 2**2)) = 1
    fac = exp(m**2)
    g = fac*exp(-0.5*(x**2 + y**2))
    return g.round().astype(int)



class GAUSSIAN(ImageFilter.BuiltinFilter):
    name = "GAUSSIAN"
    gg = gaussian_grid().flatten().tolist()
    filterargs = (5,5), sum(gg), 0, tuple(gg)

def captcha(secret, width=200, height=80,
    fontName='arial.ttf', fontSize=54,
    gaussian = 1):
  mask = Image.new('RGBA', (width, height))
  font = ImageFont.truetype(fontName, fontSize)

  x_offset = -10
  draw = ImageDraw.Draw(mask)
  for i in range(len(secret)):
    x_offset += 20 + int(random()*20)
    y_offset = -10 + int(random()*30)
    draw.text((x_offset, y_offset), secret[i], font=font)

  # последний символ также должен быть повернут
  angle = -10 + int(random()*15)
  mask = mask.rotate(angle)

  bg = plazma(width, height)
  fg = plazma(width, height)
  result = Image.composite(bg, fg, mask)

  if gaussian > 0:
    for i in range(gaussian):
      result = result.filter(GAUSSIAN)

  # почему-то blur иногда не действует на границах капчи
  # использовать crop?
  return result

# генерируем "плазму" размером width x height
def plazma(width, height):
  img = Image.new('RGB', (width, height))
  pix = img.load();

  for xy in [(0,0), (width-1, 0), (0, height-1), (width-1, height-1)]:
    rgb = []
    for i in range(3):
      rgb.append(int(random()*256))
    pix[xy[0],xy[1]] = (rgb[0], rgb[1], rgb[2])

  plazmaRec(pix, 0, 0, width-1, height-1)
  return img

# рекурсивная составля функции plazma
def plazmaRec(pix, x1, y1, x2, y2):
  if (abs(x1 - x2) <= 1) and (abs(y1 - y2) <= 1):
    return

  rgb = []
  for i in range(3):
    rgb.append((pix[x1, y1][i] + pix[x1, y2][i])/2)
    rgb.append((pix[x2, y1][i] + pix[x2, y2][i])/2)
    rgb.append((pix[x1, y1][i] + pix[x2, y1][i])/2)
    rgb.append((pix[x1, y2][i] + pix[x2, y2][i])/2)

    tmp = (pix[x1, y1][i] + pix[x1, y2][i] +
           pix[x2, y1][i] + pix[x2, y2][i])/4
    diagonal =  ((x1-x2)**2 + (y1-y2)**2)**0.5
    while True:
      delta = int ( ((random() - 0.5)/100 * min(100, diagonal))*255 )
      if (tmp + delta >= 0) and (tmp + delta <= 255):
        tmp += delta
        break
    rgb.append(tmp)

  pix[x1, (y1 + y2)/2] = (rgb[0], rgb[5], rgb[10])
  pix[x2, (y1 + y2)/2]= (rgb[1], rgb[6], rgb[11])
  pix[(x1 + x2)/2, y1] = (rgb[2], rgb[7], rgb[12])
  pix[(x1 + x2)/2, y2] = (rgb[3], rgb[8], rgb[13])
  pix[(x1 + x2)/2, (y1 + y2)/2] = (rgb[4], rgb[9], rgb[14])

  plazmaRec(pix, x1, y1, (x1+x2)/2, (y1+y2)/2)
  plazmaRec(pix, (x1+x2)/2, y1, x2, (y1+y2)/2)
  plazmaRec(pix, x1, (y1+y2)/2, (x1+x2)/2, y2)
  plazmaRec(pix, (x1+x2)/2, (y1+y2)/2, x2, y2)

'''if __name__ == '__main__':
  result = captcha("text")
  result.save("result.gif", "gif")'''
