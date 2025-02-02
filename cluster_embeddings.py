from sklearn.cluster import KMeans
import numpy as np
import pandas as pd

def cluster(embeddings, k=9):
    kmeans = KMeans(n_clusters = k, random_state = 0).fit(embeddings)
    centers = dict()
    for j in range(kmeans.cluster_centers_.shape[0]):
      centers[j] = kmeans.cluster_centers_[j]
    return kmeans.labels_, centers

# Just do this recursively
def hierarchical_clustering(embeddings, d=4, k=9):
    if d == 1:
        return cluster(embeddings, k)
    else:
        labels, centers = cluster(embeddings, k=k)
        final_labels = np.array([0]*len(labels))
        final_centers = dict()
        for i in range(k):
            embeds = embeddings[labels == i]
            if embeds.shape[0] >= 20:
              # If there are enough points, we recluster. This produces k new clusters labelled
              # 0-(k-1)
              labs, ctrs = hierarchical_clustering(embeds, d=d-1, k=k)
              if d > 1:
                # We actually should never hit the case d <= 1. 
                # In this case, we need to add to the labels to differentiate.
                labs = labs + (k**(d-1)*i)
              final_labels[labels == i] = labs
              # Do the same with the cluster centers into the dictionary
              for key,v in ctrs.items():
                final_centers[k**(d-1)*i + key] = v
            else:
              # If we can't cluster again, just keep all these points assigned
              # to the same label and cluster.
              final_labels[labels == i] = (labels[labels == i] + (k**(d-1)*i))
              final_centers[k**(d-1)*i + i] = centers[i]

    return final_labels, final_centers


# Hardcode the saved embeddings.
#file_list = ['2982.npy', '5957.npy', '8947.npy', '11913.npy', '14871.npy', '15999.npy', '19026.npy', '22024.npy', '24980.npy', '27932.npy',
#'30922.npy', '31999.npy', '34924.npy', '37886.npy', '40937.npy', '43916.npy', '46884.npy', '47999.npy', '50916.npy', '53917.npy', '56945.npy',
#'59930.npy', '62918.npy', '63999.npy', '66982.npy', '70012.npy', '73028.npy', '76025.npy', '78946.npy', '79999.npy']
#

file_list = ['3069.npy', '6129.npy', '9201.npy', '12240.npy', '15272.npy', '15999.npy', '19118.npy', '22200.npy', '25245.npy', '28305.npy',
'31398.npy', '31999.npy', '35010.npy', '38063.npy', '41239.npy', '44290.npy', '47333.npy', '47999.npy', '51003.npy', '54089.npy', '57194.npy',
'60246.npy', '63304.npy', '63999.npy', '67064.npy', '70193.npy', '73325.npy', '76381.npy', '79403.npy', '79999.npy']
arrs = [] 

#This is where things can get memory heavy
for i in range(len(file_list)):
  print(i)
  inp = np.load('vgg_embeddings/' + file_list[i])
  #if i < 18 or i > 23:
  #  inp = np.load('embeddings2/' + file_list[i])
  #else:
  #  inp = np.load('embeddings3/' + file_list[i])

  if file_list[i] in ['15999.npy', '31999.npy', '47999.npy', '63999.npy', '79999.npy']:
    for j in range(inp.shape[0]):
      if np.sum(inp[j]) == 0:
        inp = inp[:j,:]
        break 
  arrs.append(inp)

data = np.concatenate(arrs, axis=0)
print(data.shape)
res, ctrs = hierarchical_clustering(data, d=4, k=9)
print(res.shape)
np.save('vgg_res.npy', res)
url_map = dict()
ct = 0

id_to_res = dict()

for k in range(5):
  with open('vgg_correspondences' + str(k) + '.txt','r') as f:
    urls = f.read().split(' ')
  
    for j in range(len(urls)-1):
      if j == 0:
        url_map[urls[j]] = [ct]
        ct += 1
      else:
        idx = urls[j].split('h')[0]
        print(idx)
        cur_url = urls[j][len(urls[j].split('h')[0]):]
        if cur_url in url_map:
          url_map[cur_url].append(ct)
          id_to_res[int(idx)] = ct
          ct += 1
        else:
          url_map[cur_url] = [ct]
          ct += 1
          id_to_res[int(idx)] = ct

print(ct)
inv_url_map = dict()
ct = 0
for k,v in url_map.items():
  # k is url, v is number
  it = 0
  v.sort()
  for idx in v:
    inv_url_map[idx] = (k, it)
    ct += 1
    it += 1
    print(ct)

map_tokens_to_gifs = dict()
for i in range(res.shape[0]):
  if res[i] in map_tokens_to_gifs:
    map_tokens_to_gifs[res[i]].append(inv_url_map[i])
  else:
    map_tokens_to_gifs[res[i]] = [inv_url_map[i]]

print(map_tokens_to_gifs[6092])
np.save('vgg_tks_to_gifs.npy', map_tokens_to_gifs)

print('done')
#cols = ['URL', 'CAPTION']
#caps = pd.read_csv('../TGIF-Release-master/data/tgif-v1.0.tsv', names=cols, sep='\t')
#
#out = open('training1.tsv', 'w')

# Create training file
#for index, row in caps.iterrows():
#  clusters = []
#  url = row['URL']
#  caption = row['CAPTION']
#  if url in url_map:
#    clusters = url_map[url]
#    for i in range(len(clusters)):
#      clusters[i] = res[clusters[i]]
#    out_str = (caption + " [SEP]")
#    for i in range(len(clusters)):
#      out_str += " v" + str(clusters[i])
#    out.write(out_str + '\n')
#
#out.close()
