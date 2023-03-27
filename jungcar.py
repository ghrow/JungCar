# -*- coding: utf-8 -*-
"""JungCar.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1183PGehhctWo71BvEuWhdv9lSu0BtiIz
"""



import numpy as np

from collections import OrderedDict

class Relu:
  def __init__(self):
    self.mask = None

    def forward(self, x):
      self.mask = (x <= 0)
      out = x.copy()
      out[self.mask] = 0

      return out
    
    def backward(self, dout):
      dout[self.mask] = 0
      dx = dout

      return dx

class Affine:
    def __init__(self, W, b):
      self.W = W
      self.b = b
      self.x = None
      self.dW = None
      self.db = None
    
    def forward(self, x):
      self.x = x
      out = np.dot(x, self.W) + self

      return out
    
    def backward(self, dout):
      dx = np.dot(dout, self.W.T)
      self.dW = np.dot(self.x.T, dout)
      self.db = np.sum(dout, axis=0)

      return dx

def softmax(a):
 exp_a = np.exp(a)
 sum_exp_a = np.sum(exp_a)
 y = exp_a / sum_exp_a
  
 return y

def cross_entropy_error(y, t):
  if y.ndim == 1:
    t = t.reshape(1, t.size)
    y = y.reshape(1, y.size)

  batch_size = y.shape[0]


  return -np.sum(np.log(y[np.arange(batch_size), t] + 1e-7)) / batch_size

class SoftMaxWithLoss:
  def __init__(self):
    self.loss = None
    self.y = None
    self.t = None

  def forward(self, x, t):
    self.t = t
    self.y = softmax(x)
    self.loss = cross_entropy_error(self.y, self.t)
    return self.loss

  def backward(self, dout=1):
    batch_size = self.t.shape[0]
    dx = (self.y - self.t) / batch_size

    return dx

def im2col (X, filter_h, filter_w, stride=1, pad=0):
  n, c, h, w = X.shape # input data 모양

  out_h = (h + 2 * pad - filter_h) // stride + 1
  out_w = ( w + 2 * pad - filter_w) // stride + 1
 
 # add padding to height and width
  in_X = np.pad(X, [ (0,0),(0,0),(pad,pad),(pad,pad)], 'constant')
  out = np.zeros((n,c, filter_h, filter_w, out_h, out_w))

  for h in range(filter_h):
    h_end = h + stride * out_h
    for w in range(filter_w):
      w_end = w + stride * out_w
      out[:, :, h, w, :, :] = in_X[:, :, h:h_end:stride, w:w_end:stride]

    out = out.transpose(0,4,5,1,2,3).reshape(n * out_h * out_w, -1)
    return out

class Convolution:
  def __init__(self, W, b, stride=1, pad=0):
    self.W = W
    self.b = b
    self.stride = stride
    self.pad = pad

  def forward(self, x):
    FN, C ,FH, FW = self.W.shape
    N, C, H, W = x.shape
    out_h = int(1 + (H + 2*self.pad - FH) / self.stride)
    out_w = int(1 + (W + 2*self.pad - FW) / self.stride)

    col = im2col(x, FH, FW , self.stride, self.pad)
    col_W = self.W.reshape(FN, -1).T
    out = np.dot(col, col_W) + self.b

    out = out.reshape(N, out_h, out_w, -1).transpose(0, 3, 1, 2)

    return out