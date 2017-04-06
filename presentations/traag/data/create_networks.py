import random
import numpy as np
import pandas as pd
import sys
sys.path.append('../notebook')
import igraph as ig
import louvain
import ighelper
import matplotlib.pyplot as plt
import seaborn as sns
from palettable.colorbrewer.qualitative import Set1_9

bbox=(0, 0, 900, 500);

def write_graph(G, filename):
  d = {attr: G.vs[attr] for attr in G.vertex_attributes()};
  d['node'] = [v.index for v in G.vs]
  node_df = pd.DataFrame(d)
  node_df.to_csv(filename + '_nodes.csv', index=False)
  
  d = {attr: G.es[attr] for attr in G.edge_attributes()}
  d['v1'], d['v2'] = zip(*G.get_edgelist());
  link_df = pd.DataFrame(d)
  link_df.to_csv(filename + '_links.csv', index=False)

#%% 
# Set random seed to ensure always consitent results
random.seed(0)
# Load Zachary graph
G = ig.Graph.Famous('Zachary')
layout = G.layout_fruchterman_reingold();
layout.fit_into((0, 0, 1, 1), keep_aspect_ratio=False)
G['layout'] = layout
G.vs['x'], G.vs['y'] = zip(*G['layout'].coords)
#%% Centralities
G.vs['degree'] = G.degree()
G.vs['pagerank'] = G.pagerank()
G.vs['eigenvector_centrality'] = G.eigenvector_centrality()
G.vs['betweenness'] = G.betweenness(G.vs)
#%%
write_graph(G, 'karate')
#%%
G = ig.Graph.Famous('Zachary')
G.vs['label'] = [v.index for v in G.vs]
G.vs['x'], G.vs['y'] = zip(*layout.coords)
G.delete_vertices(0)
G.vs['cluster'] = np.array(G.clusters().membership) + 1
write_graph(G, 'karate_components')
#%%
G = ig.Graph.Famous('Zachary')
G.vs['label'] = [v.index for v in G.vs]
G.vs['x'], G.vs['y'] = zip(*layout.coords)
#%%
H = G.induced_subgraph(G.neighborhood(0))
# Set random seed to ensure always consitent results
random.seed(0)
layout_subgraph = H.layout_fruchterman_reingold(seed=zip(H.vs['x'], H.vs['y']));
layout_subgraph.fit_into((0, 0, 1, 1));
H.vs['x'], H.vs['y'] = zip(*layout_subgraph.coords)
H.es['type'] = ['e1' if 0 in (e.source, e.target) else 'e2' for e in H.es]
write_graph(H, 'karate_ego')
#%%
# Set random seed to ensure always consitent results
random.seed(0)
G = ighelper.GraphFromURL('https://storage.googleapis.com/css-files/sociopatterns.graphml', data_dir='../notebook/data/')
G = G.clusters().giant()
layout = G.layout_fruchterman_reingold(weights='weight');
layout.fit_into((0, 0, 1, 1), keep_aspect_ratio=False)
G['layout'] = layout
#%%
pink = Set1_9.hex_colors[7]
blue = Set1_9.hex_colors[1]
gender_partition = ig.VertexClustering.FromAttribute(G, 'gender')  
ig.plot(G, 
        bbox=bbox,
        layout=G['layout'],
        target='../figures/sociopatterns_gender.pdf',
        edge_width=0.02*np.array(G.es['weight']), 
        edge_color='gray', 
        vertex_size=8, 
        vertex_frame_width=1,
        vertex_frame_color='white',
        vertex_color=[pink if v['gender'] == 'F' else blue for v in G.vs])
#%%
class_partition = ig.VertexClustering.FromAttribute(G, 'class')  
ig.plot(class_partition, 
        bbox=bbox,
        layout=G['layout'],
        target='../figures/sociopatterns_class.pdf',
        edge_width=0.02*np.array(G.es['weight']), 
        edge_color='gray', 
        vertex_size=8,
        vertex_frame_width=1,
        vertex_frame_color='white',        
        palette=ig.PrecalculatedPalette(Set1_9.hex_colors))
#%%
random.seed(0)
H = class_partition.subgraph(0)
layout = H.layout_fruchterman_reingold(weights='weight');
layout.fit_into((0, 0, 1, 1), keep_aspect_ratio=False)
H['layout'] = layout
ig.plot(H, 
        bbox=bbox,
        layout=H['layout'],
        target='../figures/sociopatterns_class_0_gender.pdf',
        edge_width=0.02*np.array(H.es['weight']), 
        edge_color='gray', 
        vertex_size=14,
        vertex_frame_width=1,
        vertex_frame_color='white',        
        vertex_color=[pink if v['gender'] == 'F' else blue for v in H.vs])
#%%
np.random.seed(0)
G.vs['opinion'] = 0
G.vs['new_opinion'] = np.random.randint(2, size=G.vcount())

idx = 0;
while G.vs['opinion'] != G.vs['new_opinion']:
    G.vs['opinion'] = G.vs['new_opinion']
    ig.plot(G, 
            bbox=bbox,
            layout=G['layout'],
            target='../figures/social_influence/sociopatterns_opinion_{0}.pdf'.format(idx),
            edge_width=0.02*np.array(G.es['weight']), 
            edge_color='gray', 
            vertex_size=8,
            vertex_frame_width=1,
            vertex_frame_color='white',        
            vertex_color=G.vs['opinion'],
            palette=ig.PrecalculatedPalette(Set1_9.hex_colors))    
    idx += 1;
    for v in G.vs:
        v['new_opinion'] = 1*(sum(G.vs[G.neighbors(v)]['opinion']) > 0.5*v.degree())
#%%
G.assortativity_nominal(G.vs['opinion'])

#%%
# Set random seed to ensure always consistent results
random.seed(0)
# Load Zachary graph
G = ig.Graph.Famous('Zachary')
layout = G.layout_fruchterman_reingold();
layout.fit_into((0, 0, 1, 1), keep_aspect_ratio=False)
G['layout'] = layout
#%%
G.vs['degree'] = G.degree()
G.vs['pagerank'] = G.pagerank()
G.vs['eigenvector_centrality'] = G.eigenvector_centrality()
G.vs['betweenness'] = G.betweenness(G.vs)
#%%
ig.plot(G, 
        bbox=bbox,
        layout=G['layout'],
        target='../figures/centralities/karate_degree.pdf'.format(idx),
        edge_color='gray', 
        vertex_size=8*np.sqrt(np.array(G.vs['degree'])),
        vertex_frame_width=1,
        vertex_frame_color='white',  
        vertex_color='gray',
        palette=ig.PrecalculatedPalette(Set1_9.hex_colors))
#%%
paths = [];
for v in G.vs:
  paths.extend(G.get_shortest_paths(v, G.vs, output="epath"))
  
G.es['color'] = 'gray'
for path in paths:
  es = G.es[path]
  vertices = set([e.source for e in es]).union(set([e.target for e in es]))
  if 0 in vertices:
    es['color'] = Set1_9.hex_colors[0] # Red
  else:
    for e in es:
      if e['color'] == 'gray':
        e['color'] = Set1_9.hex_colors[1] # Blue

#%%

ig.plot(G, 
        bbox=bbox,
        layout=G['layout'],
        target='../figures/centralities/karate_betweenness.pdf'.format(idx),
        #edge_color='gray',
        vertex_label=[v.index for v in G.vs],
        vertex_size=2*np.sqrt(np.array(G.vs['betweenness'])) + 10,
        vertex_frame_width=1,
        vertex_frame_color='white',  
        vertex_color='gray',
        palette=ig.PrecalculatedPalette(Set1_9.hex_colors))
#%%
eig = np.ones(G.vcount())/G.vcount();
A = np.array(list(G.get_adjacency()));
for idx in range(5):
  ig.plot(G, 
          bbox=bbox,
          layout=G['layout'],
          target='../figures/centralities/karate_eigenvector_{0}.pdf'.format(idx),
          edge_color='gray', 
          vertex_size=4*G.vcount()*np.sqrt(eig),
          vertex_frame_width=1,
          vertex_frame_color='white',  
          vertex_color='gray',
          palette=ig.PrecalculatedPalette(Set1_9.hex_colors))
  eig = A.dot(eig)
  eig /= eig.sum()
#%%
eig = np.array(G.vs['eigenvector_centrality']);
eig /= eig.sum();
ig.plot(G, 
        bbox=bbox,
        layout=G['layout'],
        target='../figures/centralities/karate_eigenvector.pdf'.format(idx),
        edge_color='gray', 
        vertex_size=4*G.vcount()*np.sqrt(eig),
        vertex_frame_width=1,
        vertex_frame_color='white',  
        vertex_color='gray',
        palette=ig.PrecalculatedPalette(Set1_9.hex_colors))
#%%
random.seed(0)
v = G.vs[31];
for idx in range(10):
  
  G.vs['color'] = Set1_9.hex_colors[1]
  v['color'] = Set1_9.hex_colors[0]
  G.vs[G.neighbors(v)]['color'] = Set1_9.hex_colors[2]

  G.es['width'] = 1
  G.es['color'] = 'gray'
  G.es[G.incident(v)]['width'] = 2
  G.es[G.incident(v)]['color'] = 'black'
  
  ig.plot(G, 
          bbox=bbox,
          layout=G['layout'],
          target='../figures/centralities/karate_pagerank_{0}.pdf'.format(idx),
          vertex_size=3*G.vcount()*np.sqrt(G.vs['pagerank']),
          vertex_frame_width=1,
          vertex_frame_color='white',
          palette=ig.PrecalculatedPalette(Set1_9.hex_colors))
  if idx == 4:
    v = G.vs[1]; # Jump
  else:
    v = v.neighbors()[random.randint(0, v.degree() - 1)]

#%%
# Set random seed to ensure always consitent results
random.seed(0)
G = ighelper.GraphFromURL('https://storage.googleapis.com/css-files/sociopatterns.graphml', data_dir='../notebook/data/')
G = G.clusters().giant()
layout = G.layout_fruchterman_reingold(weights='weight');
layout.fit_into((0, 0, 1, 1), keep_aspect_ratio=False)
G['layout'] = layout
#%%
class_partition = ig.VertexClustering.FromAttribute(G, 'class')  
ig.plot(class_partition, 
        bbox=bbox,
        layout=G['layout'],
        target='../figures/sociopatterns_class_weak_links.pdf',
        edge_width=0.02*np.array(G.es['weight']), 
        edge_color=['gray' if e['weight'] < np.mean(G.es['weight']) else 'black' for e in G.es], 
        vertex_size=8,
        vertex_frame_width=1,
        vertex_frame_color='white',
        palette=ig.PrecalculatedPalette(Set1_9.hex_colors))
#%%
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
jaccard_similarity = G.similarity_jaccard(pairs=G.get_edgelist());
df = pd.DataFrame({'jaccard': jaccard_similarity, 
                   'weight': G.es['weight']})
df['jaccard_group'] = np.round(df['jaccard'], 1)

sns.boxplot(x='jaccard_group', y='weight', data=df, color='lightgray')
plt.ylabel('Weight')
plt.xlabel('Jaccard similarity')
plt.yscale('log')
plt.savefig('../figures/weight_overlap.pdf')
#%%

G.vs['clustering'] = G.transitivity_local_undirected()
most_broker = min(G.vs, key=lambda v: v['clustering'])

G.vs['color'] = 'gray'
most_broker['color'] = Set1_9.hex_colors[0]
G.vs[G.neighbors(most_broker)]['color'] = Set1_9.hex_colors[1]

ig.plot(G,         
        bbox=bbox,
        target='../figures/most_broker.pdf',
        layout=G['layout'],
        edge_width=0.02*np.array(G.es['weight']), 
        edge_color='lightgray',
        vertex_size=3.0/np.array(G.vs['clustering']),
        vertex_frame_width=1,
        vertex_frame_color='white')

#%%
least_broker = max(G.vs.select(_degree_ge=most_broker.degree()), key=lambda v: v['clustering'])
                   
G.vs['color'] = 'gray'
least_broker['color'] = Set1_9.hex_colors[0]
G.vs[G.neighbors(least_broker)]['color'] = Set1_9.hex_colors[1]

ig.plot(G,         
        bbox=bbox,
        target='../figures/least_broker.pdf',
        layout=G['layout'],
        edge_width=0.02*np.array(G.es['weight']), 
        edge_color='lightgray',
        vertex_size=3.0/np.array(G.vs['clustering']),
        vertex_frame_width=1,
        vertex_frame_color='white')

#%%
from collections import Counter

def entropy(lst):
    freq = Counter(lst);
    prob = [float(f)/len(lst) for f in freq.itervalues()]
    return -sum(prob*np.log(prob))

entropy_node = [entropy(G.vs[G.neighbors(v)]['class']) for v in G.vs];

plt.plot(1 - np.array(G.vs['clustering']), entropy_node, '.')
plt.xlabel('Broker')
plt.ylabel('Entropy')
plt.savefig('../figures/brokerage.pdf')

#%%
def spreading(G, initial_node, p):
    G.vs['infected'] = False
    infect_nodes = [initial_node]
    while infect_nodes:
        v = infect_nodes.pop()
        v['infected'] = True
        for u in G.vs[G.neighbors(v)]:
            if not u['infected'] and np.random.rand() < p:
                infect_nodes.append(u)
    return sum(G.vs['infected'])

def repeat_spreading(G, p, n_runs):
    return np.mean([spreading(G, G.vs[np.random.randint(G.vcount())], p) for idx in range(n_runs)])
#%%
random.seed(0)
G = ighelper.GraphFromURL('https://storage.googleapis.com/css-files/sociopatterns.graphml', data_dir='../notebook/data/')
G = G.clusters().giant()
layout = G.layout_fruchterman_reingold(weights='weight');
layout.fit_into((0, 0, 1, 1), keep_aspect_ratio=False)
G['layout'] = layout  

G_random = ig.Graph.Erdos_Renyi(n=G.vcount(), m=G.ecount())
G_random_config = ig.Graph.Degree_Sequence(G.degree())
#%%
n_runs = 1000
p_list = np.linspace(0, 0.1, 50)
nb_infected = [repeat_spreading(G, p, n_runs) for p in p_list]
nb_infected_random = [repeat_spreading(G_random, p, n_runs) for p in p_list]
nb_infected_random_config = [repeat_spreading(G_random_config, p, n_runs) for p in p_list]
G_scale_free = ig.Graph.Barabasi(n=G.vcount(), m=int(np.mean(G.degree())))
nb_infected_scale_free = [repeat_spreading(G_scale_free, p, n_runs) for p in p_list]
#%%
from scipy.interpolate import spline
plt.plot(p_list, np.array(nb_infected)/float(G.vcount()), label='Empirical')
plt.plot(p_list, np.array(nb_infected_random)/float(G.vcount()), label='Random')
plt.plot(p_list, np.array(nb_infected_random_config)/float(G.vcount()), label='Random Configuration')
plt.plot(p_list, np.array(nb_infected_scale_free)/float(G.vcount()), label='Scale Free')
plt.xlim(0, 0.1)
plt.xlabel('Probability')
plt.ylabel('Infected')
plt.legend(loc='best')
plt.savefig('../figures/infection.pdf')