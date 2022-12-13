from pathlib import Path
from zipfile import ZipFile
from utils.console_utils import make_command, run_bash_command
from segmenter.models.train import train as train_segmenter
from link_prediction.models.train import train as train_link_predictor
import streamlit as st

st.title("Training")

data_path = Path(__file__, "../../../data").resolve()
scripts_path = str((data_path / ".." / "scripts").resolve())

ex = st.expander("Upload models")
segmenter_file = ex.file_uploader("Upload segmenter model", "zip", help="Upload a zip file containing the trained segmenter models. The file must be the segmenter zip downloaded from colab.")
if segmenter_file is not None and ex.button("Extract segmenter"):
    zip_file = ZipFile(segmenter_file)
    zip_file.extractall(data_path / "segmenter_corpus")
    segmenter_file.close()
    zip_file.close()
    del zip_file
    del segmenter_file
link_predictor_file = ex.file_uploader("Upload link predictor model", "zip", help="Upload a zip file containing the trained link predictor models. The file must be the link predictor zip downloaded from colab.")
if link_predictor_file is not None and ex.button("Extract link predictor"):
    zip_file = ZipFile(link_predictor_file)
    zip_file.extractall(data_path / "link_prediction")
    link_predictor_file.close()
    zip_file.close()
    del zip_file
    del link_predictor_file

# Select corpus
corpus_dir = data_path / "projection"
options = sorted([path.name for path in corpus_dir.iterdir() if path.is_dir() and path.name[0] != "_"], key=lambda x: "" if x == "cdcp" else x)
corpus_name = st.selectbox("Corpus selection:", options, help="Select the corpus to train with. The folder should be at data/projection and contain dev, test and train folders")

options = ["spanish", "english"]
corpus_language = st.selectbox("Corpus language:", options)

st.header("Segmenter:")

epochs = st.slider("Epochs segmenter", 1, 120, 100, step=1)
# use_pos = st.checkbox("Use POS features", True)
# use_char_cnn = st.checkbox("Use Char CNN features", True)
# use_char_lstm = st.checkbox("Use Char LSTM features", True)
# use_res = st.checkbox("Use residual connections", True)
# use_norm = st.checkbox("Use normalization", True)
# use_dense = st.checkbox("Use final dense layer", True)

if Path(data_path, "segmenter_corpus", corpus_name, f"{corpus_language}_pos_model_cnn_lstm_blstm_resnet_norm_dn_lower_crf").exists():
    st.info("Segmenter exists.")
if st.button("Train segmenter"):
    with st.spinner("Training segmenter ..."):
        
        use_script = True # If not then memory leak with the models
        if use_script:
            # Calling script
            command = make_command(*[
                "cd",
                scripts_path,
                "&&",
                "./train_segmenter.sh",
                corpus_name,
                corpus_language,
                "--epochs",
                str(epochs),
                # "--with_pos",
                # str(use_pos),
                # "--with_resnet",
                # str(use_res),
                # "--with_layer_normalization",
                # str(use_norm),
                # "--with_cnn",
                # str(use_char_cnn),
                # "--with_lstm",
                # str(use_char_lstm),
                # "--with_dn",
                # str(use_dense),
            ])
            run_bash_command(command)
        else:
            # Calling method
            train_segmenter(
                corpus_tag=corpus_name, 
                language=corpus_language,
                epochs=int(epochs),
                # with_pos=use_pos,
                # with_resnet=use_res,
                # with_layer_normalization=use_norm,
                # with_cnn=use_char_cnn,
                # with_lstm=use_char_lstm,
                # with_dn=use_dense
            )
        
        st.info("Segmenter trained")


st.header("Link predictor:")

epochs = st.slider("Epochs link predictor", 1, 120, 70, step=1)
# multi_head_att = st.checkbox("Use multi-head attention", False)
# att = st.checkbox("Use attention", False)
# pooling = st.slider("Pooling", 1, 15, 10, step=1)
# dropout = st.slider("Dropout", 0.0, 1.0, 0.1)
# learning_rate = st.slider("Learning rate", 0.001, 0.006, 0.003, step=0.001, format="%.3f")
# patience = st.slider("Patience", 0, 20, 5, step=1)
# return_best = st.checkbox("Return best", False)

if Path(data_path, "link_prediction", corpus_name, f"{corpus_language}_model_0.003_10_0.1_5_False").exists():
    st.info("Link predictor exists.")
if st.button("Train link predictor"):
    with st.spinner("Training link predictor ..."):
        
        use_script = True # If not then memory leak with the models
        if use_script:
            # Calling script
            command = make_command(*[
                "cd",
                scripts_path,
                "&&",
                "./train_link_predictor.sh",
                corpus_name,
                corpus_language,
                "--epochs",
                str(epochs),
                # "--dropout",
                # str(dropout),
                # "--encoder_pool_size",
                # str(pooling),
                # "--with_attention",
                # str(att),
                # "--with_multi_head_attention",
                # str(multi_head_att),
                # "--lr_alpha",
                # str(learning_rate),
                # "--patience",
                # str(patience),
                # "--return_best",
                # str(return_best),
            ])
            run_bash_command(command)
        else:
            # Calling method
            train_link_predictor(
                corpus_tag=corpus_name, 
                language=corpus_language,
                epochs=int(epochs),
                # dropout=dropout,
                # encoder_pool_size=int(pooling),
                # with_attention=att,
                # with_multi_head_attention=multi_head_att,
                # lr_alpha=learning_rate,
                # patience=int(patience),
                # return_best=return_best,
            )
        st.info("Link predictor trained")

