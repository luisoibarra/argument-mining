
# Download spanish word embeddings
# Extracted from https://github.com/dccuchile/spanish-word-embeddings
echo "Downloading Spanish Glove Embeddings"
curl https://users.dcc.uchile.cl/~jperez/word-embeddings/glove-sbwc.i25.vec.gz -o glove-sbwc.i25.vec.gz
gzip -d glove-sbwc.i25.vec.gz
mv glove-sbwc.i25.vec ./../data/glove-sbwc.i25.vec

# Download english word embeddings
echo "Downloading English Glove Embeddigns"
curl https://downloads.cs.stanford.edu/nlp/data/glove.840B.300d.zip -o glove.840B.300d.zip
unzip glove.840B.300d.zip
rm glove.840B.300d.zip
mv glove.840B.300d.txt ./../data/glove.840B.300d.txt
