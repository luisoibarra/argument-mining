import logging as log
import sys

# Code taken from https://github.com/UKPLab/coling2018-xling_argument_mining
# With some modifications on the reading from files

# project argument spans from source to target document
# Steffen Eger
# 03/2018

# SAMPLE USAGE:
# python2 projectArguments.py train_full.dat essays.aligned essays.aligned.bidirectional
#
# Inputs: 
#         $x_full.dat: train annotated data in source language
#         essays.aligned: aligned sentences in source and target language (source sentences must all be in train/dev/test.dat)
#         essays.aligned.bidirectional: word alignments (e.g., produced by fast_align)
#         essays.projected: Where to export the projected conll tags in target language

def readDoc(fn,index0=1):
  hh=[]
  hd = {}
  h=[]
  for line in open(fn):
    line = line.strip()
    if line=="":
      if h!=[]: 
        hh.append(h)
        str=" ".join([x[0] for x in h])
        hd[str] = h
      h=[]
    else:
      x = line.split("\t")
      word,label = x[index0],x[-1]
      h.append((word,label))
  if h!=[]:
    hh.append(h)
    str=" ".join([x[0] for x in h])
    hd[str] = h
  return hh, hd

K=1

def isConsecutive(lst,descending=False):
  last = None
  for x in lst:
    if last is not None:
      next = last-1 if descending else last+1
      if x!=next: return False
    last = x
  return True   

def findExtremeConsecutive(lst,reverse=True,k=1):
  s = sorted(lst,reverse=reverse)
  for ix,x in enumerate(s):
    mylst = s[ix:ix+k]
    if isConsecutive(mylst,descending=reverse): return x
  return s[0]

def detect_bios(labels):
  indices = []
  startComponent=False
  startindex = None
  type = None
  for index,tok in enumerate(labels):
    word,token = tok
    if startComponent==True and token.startswith("B-"):
      endindex = index-1
      indices.append((startindex,endindex,type))
      startindex = index
      type = token.split(":")[0][2:]
      startComponent = True
    elif startComponent==True and token.startswith("O"):
      endindex = index-1
      indices.append((startindex,endindex,type))
      startComponent = False
    elif token.startswith("B-"):
      type = token.split(":")[0][2:]
      startComponent = True
      startindex = index
  if token.startswith("I-"):
     endindex = index
     indices.append((startindex,endindex,type))
  return indices

def getTranslationIndices(indices,align, tag):
  h = {}
  for y in align.split():
    a,b = list(map(int,y.split("-")))
    if a in h:
      h[a] = h[a]+[b]
    else:
      h[a] = [b]
  #print(h,align,indices)
  #sys.exit(1)
  aligns=[]
  for x in indices:
    start,end,type = x
    q = []
    for z in range(start,end+1):
      #print("-->",z,h)
      #print(h[z])
      q.append( h.get(z,None) )
    qq = list(filter(lambda x: x!=None,q))
    flat_list = [item for sublist in qq for item in sublist]
    #print("##->",flat_list,x)
    #print(flat_list); sys.exit(1)
    # YOU MAY WANT TO CHANGE THIS
    indexStart,indexEnd = min(flat_list),max(flat_list)
    for myK in range(K,0,-1):
      indexStart,indexEnd = findExtremeConsecutive(flat_list,reverse=False,k=K),findExtremeConsecutive(flat_list,reverse=True,k=myK)
      if len(aligns)>0:
        indexEndPrev = aligns[-1][1]
        indexStartPrev = aligns[-1][0]
        if indexStart<=indexEndPrev:
          # Intersection isn't empty
          sys.stderr.write(f"Projection overlaps near to {indexStart} {indexEndPrev}.\nOverlap: {tag[1][indexStart:indexEndPrev+1]}\n")
          if indexEnd<indexStartPrev: 
            sys.stderr.write("%s: Li'l non-monotonity\n"%(tag,))
            break 
          indexStart = indexEndPrev+1
      if indexStart<=indexEnd: break
    if indexStart>indexEnd:
        sys.stderr.write(str(aligns))
        sys.stderr.write("%s: ERROR SOMEWHERE: %d %d\n"%(tag, indexStart,indexEnd)); 
        #sys.exit(1)
        print(indices)
    aligns.append((indexStart,indexEnd,type))
  #print(aligns)
  return aligns

def printout(sequence,fout,type="O"):
  for itoken,token in enumerate(sequence):
    if type!="O": 
      if itoken==0:
        pre="B-"
      else:
        pre="I-"
    else:
      pre="" 
    fout.write(token+"\t"+pre+type+"\n")

def process(sentences,sentences_alignments,labels,fout,verbose=False):
  n = len(sentences)
  last = 0
  for i in range(len(sentences)):
    en,de = sentences[i]
    en_tokens = en.split()
    de_tokens = de.split()
    m = len(en_tokens)
    align = sentences_alignments[i].strip()
    curLabels = labels[last:last+m]
    indices = detect_bios(curLabels)
    last = last+m
    if None in [x for y in indices for x in y]:
      log.warning(f"None in indices. Skipping projection:\nLabels: {curLabels}\nAlignment: {sentences[i]}")
      continue
    #print(en_tokens,"\t",curLabels,"\t",de_tokens,"\t",indices)
    #print(align)
    aligns = sorted( getTranslationIndices(indices,align, sentences[i]) )
    if verbose:
      print("ALIGNS",aligns,de)
    #if aligns!=[]:
    prev = 0
    for start,end,type in aligns:
      if start>end: continue
      before = de_tokens[prev:start]
      middle = de_tokens[start:end+1]
      if before!=[]: printout(before,fout)
      printout(middle,fout,type)
      prev = end+1
    after = de_tokens[prev:]
    if after!=[]:
      printout(after,fout)
      #sys.exit(1)

try:

  argv = sys.argv

  train,train_hash = readDoc(argv[1], index0=0)

  alignedText = argv[2]
  alignments = argv[3]
  
  exportFile = argv[4]

  fp_lines=open(alignments).readlines()
except Exception as e:
  print("""
python projectArguments.py train_full.dat essays.aligned essays.aligned.bidirectional export.projection

Inputs: 
        $train_full.dat: annotated data in source language
        essays.aligned: aligned sentences in source and target language
        essays.aligned.bidirectional: word alignments (e.g., produced by fast_align)
        essays.projected: Where to export the projected conll tags in target language
""")
  log.exception(e)
  exit(1)

try:
  acc=[]
  sentences=[]
  sentences_alignments=[]
  with open(exportFile, "w") as fout:
    for i, line in enumerate(open(alignedText)):
      line = line.strip()
      en,de = line.split(" ||| ")
      sentences.append((en,de))
      sentences_alignments.append(fp_lines[i])
      acc+=en.split()
      acc_text = " ".join(acc)
      #print(acc_text+"<--")
      for hash in [train_hash]:
        if acc_text in hash:
          labels = hash[acc_text]
          process(sentences,sentences_alignments,labels,fout)
          fout.write("\n")
          acc = []
          sentences=[]
          sentences_alignments=[]
        else:
          log.warning(f"{acc_text} wasn't found")
except Exception as e:
  log.exception(e)
  exit(1)
