import igraph as ig
import requests
import os

def GraphFromURL(url, format=None):
 
  filename = url.split('/')[-1]

  if not os.path.exists('data/' + filename):
    r = requests.get(url) 
    with open('data/' + filename, 'wb') as f:
      f.write(r.content.replace('\r\n', '\n'))
      f.close()
    
  G = ig.Graph.Read('data/' + filename, format=format)
  return G