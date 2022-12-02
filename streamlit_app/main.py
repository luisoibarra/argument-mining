if __name__ == "__main__":
    import sys
    from pathlib import Path
    path = str(Path(__file__, "..", "..").resolve())
    if path not in sys.path:
        sys.path.insert(0, path)

import streamlit as st
from pathlib import Path
from streamlit_app.st_utils import process_texts, create_zip_str
import pandas as pd
from io import StringIO


st.title("Argument Mining")

data_path = Path(__file__, "../../data").resolve()

# Select segmenter
segmenter_path = data_path / "segmenter_corpus"
options = [path.name for path in segmenter_path.iterdir() if path.is_dir() and path.name[0] != "_"]
segmenter_name = st.selectbox("Segmenter selection:", options)
st.session_state["segmenter_name"] = segmenter_name

# Select link prediction
link_prediction_path = data_path / "link_prediction"
options = [path.name for path in link_prediction_path.iterdir() if path.is_dir() and path.name[0] != "_"]
link_predictor_name = st.selectbox("Link predictor selection:", options)
st.session_state["link_predictor_name"] = link_predictor_name

language = st.selectbox("Language selection", ["spanish"])
st.session_state["language"] = language

new_segmenter_key = f"segmenter_{segmenter_name}_{language}"
new_link_predictor_key = f"link_prediction_{link_predictor_name}_{language}"

# Segmenter
if "segmenter_key" in st.session_state:
    st.info(f"Segmenter {st.session_state['segmenter_key']} Loaded")
else:
    st.error(f"Segmenter not loaded")
if st.button("Load segmenter"):
    with st.spinner("Loading segmenter ..."):
        if "segmenter_key" in st.session_state and st.session_state["segmenter_key"] != new_segmenter_key:
            st.session_state.pop(st.session_state["segmenter_key"])
            st.session_state.pop("segmenter_key")
        if "segmenter_key" not in st.session_state:
            from segmenter.tf_segmenter import TensorflowArgumentSegmenter
            # from segmenter.segmenter import RandomArgumentSegmenter

            st.session_state['segmenter_key'] = new_segmenter_key
            segmenter = TensorflowArgumentSegmenter(segmenter_name, language)
            # segmenter = RandomArgumentSegmenter(["MajorClaim", "Claim", "Premise"])
            st.session_state[new_segmenter_key] = segmenter
        if "segmenter_key" in st.session_state:
            st.info(f"Segmenter {st.session_state['segmenter_key']} Loaded")

# Link Preditor
if "link_predictor_key" in st.session_state:
    st.info(f"Link Predictor {st.session_state['link_predictor_key']} Loaded")
else:
    st.error(f"Link Predictor not loaded")
if st.button("Load link predictor"):
    with st.spinner("Loading link predictor ..."):
        # Delete previous models
        if "link_predictor_key" in st.session_state and st.session_state["link_predictor_key"] != new_link_predictor_key:
            st.session_state.pop(st.session_state["link_predictor_key"])
            st.session_state.pop("link_predictor_key")
        if "link_predictor_key" not in st.session_state:
            from link_prediction.tf_link_predictor import TensorflowLinkPredictor
            # from link_prediction.link_predictor import RandomLinkPredictor

            st.session_state['link_predictor_key'] = new_link_predictor_key
            link_predictor = TensorflowLinkPredictor(link_predictor_name, language)
            # link_predictor = RandomLinkPredictor(["MajorClaim", "Claim", "Premise"], ["attacks", "supports"])
            st.session_state[new_link_predictor_key] = link_predictor
        if "link_predictor_key" in st.session_state:
            st.info(f"Link Predictor {st.session_state['link_predictor_key']} Loaded")

# Inference


if "segmenter_key" in st.session_state:
    segmenter = st.session_state[st.session_state["segmenter_key"]]
else:
    segmenter = None

if "link_predictor_key" in st.session_state:
    link_predictor = st.session_state[st.session_state["link_predictor_key"]]
else:
    link_predictor = None


options = ["text", "file"]
input_format = st.selectbox("Pick input format", options)

if input_format == options[0]:
    text = st.text_input("Input:")
elif input_format == options[1]:
    text = None
    file = st.file_uploader("Upload file:")
    if file is not None:
        stringio = StringIO(file.getvalue().decode("utf-8"))
        text = stringio.read()
    else:
        st.error(f"{file} not uploaded.")

if text:
    if st.button("Process input"):
        
        with st.spinner("Processing ..."):
            result, brat_txt = process_texts(
                {
                    "file.txt": text
                }, 
                language, 
                segmenter_name, 
                segmenter=segmenter, 
                link_predictor=link_predictor)
            arg, rel, non_arg = list(result.values())[0]
            brat_ann, brat_txt = list(brat_txt.values())[0]
            zipstr = create_zip_str({"file.txt": brat_txt, "file.ann": brat_ann})

        text_df = pd.concat([arg, non_arg], ignore_index=True).sort_values(by="prop_init")
        st.dataframe(text_df)
        st.dataframe(rel)

        text = ""
        for i, row in text_df.iterrows():
            if not pd.isna(row['prop_id']):
                key = rel['prop_id_source'] == row["prop_id"]
            else:
                key = []

            prop_relations = rel[key]

            if prop_relations.empty:
                relation_tag = ""
            else:
                relation_tag = "-".join(f"{row['relation_type']}-{row['prop_id_target']-row['prop_id_source']}" for i, row in prop_relations.iterrows())
            if not pd.isna(row['prop_type']):
                prop_tag = "{" + f"{row['prop_type']}" + (f"-{relation_tag}" if relation_tag else "") + "}"
                text += f"[{row['prop_text']}] {prop_tag}\n"
            else:
                text += f"{row['prop_text']}\n"
        st.write(text)


        st.download_button("Download annotation", zipstr, "file.zip")
