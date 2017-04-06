import igraph as ig
import requests
import os

def GraphFromURL(url, format=None, data_dir='data/'):
 
  filename = url.split('/')[-1]

  if not os.path.exists(data_dir):
    os.makedirs(data_dir)

  if not os.path.exists(data_dir + filename):
    r = requests.get(url) 
    with open('data/' + filename, 'wb') as f:
      f.write(r.content.replace('\r\n', '\n'))
      f.close()
    
  G = ig.Graph.Read(data_dir + filename, format=format)
  return G