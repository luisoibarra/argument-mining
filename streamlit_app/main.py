if __name__ == "__main__":
    import sys
    from pathlib import Path
    path = str(Path(__file__, "..", "..").resolve())
    if path not in sys.path:
        sys.path.insert(0, path)

import shutil
import streamlit as st
from pathlib import Path
from streamlit_app.st_utils import is_brat_alive, process_texts, create_zip_str, create_zip, process_texts_console, start_brat
import pandas as pd
from zipfile import ZipFile


st.title("Argument Mining")

data_path = Path(__file__, "../../data").resolve()

# Select segmenter
segmenter_path = data_path / "segmenter_corpus"
segmenter_options = [path.name for path in segmenter_path.iterdir() if path.is_dir() and path.name[0] != "_"]
link_prediction_path = data_path / "link_prediction"
link_prediction_options = [path.name for path in link_prediction_path.iterdir() if path.is_dir() and path.name[0] != "_"]

options = ["files", "text"]
input_format = st.selectbox("Pick input format", options, help="Select the input type:\n\n"
    "text: Input will be plain text and the models will be loaded into memory. This will "
    "allow to rapidly manage individual text but the memory consumption is large.\n\n"
    "files: Input will be a zip file that only contains txt files in the root address. This "
    "version is more fast and less memory consumption for managing several files."
)

options = sorted(set(link_prediction_options).intersection(segmenter_options), key=lambda x: "" if x == "cdcp" else x)
corpus_name = segmenter_name = link_predictor_name = st.selectbox("Corpus selection:", options,
    disabled= input_format == "text" and ("segmenter_key" in st.session_state or "link_predictor_key" in st.session_state),
    help="Select the models trained with this corpus. Default implementation of segmenter and link predictor must be available " + \
    "at data/segmenter_corpus/\$selected_corpus and data/link_prediction/\$selected_corpus. To train the default models go to training tab.")
st.session_state["segmenter_name"] = segmenter_name
st.session_state["link_predictor_name"] = link_predictor_name

language = st.selectbox("Language selection", ["spanish"], help="Corpus final language.")

if input_format == "text":
    new_segmenter_key = f"segmenter_{segmenter_name}_{language}"
    new_link_predictor_key = f"link_prediction_{link_predictor_name}_{language}"

    # Segmenter
    if "segmenter_key" in st.session_state:
        st.info(f"Segmenter {st.session_state['segmenter_key']} Loaded")
    else:
        st.error(f"Segmenter not loaded")
    if "segmenter_key" not in st.session_state and st.button("Load segmenter"):
        with st.spinner("Loading segmenter ..."):
            if "segmenter_key" in st.session_state and st.session_state["segmenter_key"] != new_segmenter_key:
                st.session_state.pop(st.session_state["segmenter_key"])
                st.session_state.pop("segmenter_key")
            if "segmenter_key" not in st.session_state:
                # from segmenter.tf_segmenter import TensorflowArgumentSegmenter
                from segmenter.segmenter import RandomArgumentSegmenter

                st.session_state['segmenter_key'] = new_segmenter_key
                # segmenter = TensorflowArgumentSegmenter(segmenter_name, language)
                segmenter = RandomArgumentSegmenter(["MajorClaim", "Claim", "Premise"])
                st.session_state[new_segmenter_key] = segmenter
            if "segmenter_key" in st.session_state:
                st.info(f"Segmenter {st.session_state['segmenter_key']} Loaded")

    # Link Preditor
    if "link_predictor_key" in st.session_state:
        st.info(f"Link Predictor {st.session_state['link_predictor_key']} Loaded")
    else:
        st.error(f"Link Predictor not loaded")
    if "link_predictor_key" not in st.session_state and st.button("Load link predictor"):
        with st.spinner("Loading link predictor ..."):
            # Delete previous models
            if "link_predictor_key" in st.session_state and st.session_state["link_predictor_key"] != new_link_predictor_key:
                st.session_state.pop(st.session_state["link_predictor_key"])
                st.session_state.pop("link_predictor_key")
            if "link_predictor_key" not in st.session_state:
                # from link_prediction.tf_link_predictor import TensorflowLinkPredictor
                from link_prediction.link_predictor import RandomLinkPredictor

                st.session_state['link_predictor_key'] = new_link_predictor_key
                # link_predictor = TensorflowLinkPredictor(link_predictor_name, language)
                link_predictor = RandomLinkPredictor(["MajorClaim", "Claim", "Premise"], ["attacks", "supports"])
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

    text = None
    text = st.text_area("Input:")

    if text and st.button("Process input"):
        
        with st.spinner("Processing text ..."):
            result, brat_txt, brat_path = process_texts(
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

        if zipstr:
            st.download_button("Download annotations", zipstr, "file.zip")
elif input_format == "files":
    zip_file = None
    file = st.file_uploader("Upload file:", ["zip"], help="Upload zip file containing the files to analyze in .txt format.")
    if file is not None:
        zip_file = ZipFile(file)
        for info in zip_file.infolist():
            if info.is_dir():
                st.error(f"The zip file must contain only txt files. Directory {info.filename} found.")
            elif info.filename.split(".")[-1] != "txt":
                st.error(f"The zip file must contain only txt files. File {info.filename} is not txt.")
    else:
        st.error(f"File not uploaded.")

    zipstr = None
    if zip_file and st.button("Process files"):
        with st.spinner("Processing files ..."):
            brat_path = process_texts_console(corpus_name, language, zip_file)
            # brat_path = Path("/workspaces/argument-mining/streamlit_app/data/abstrct/brat")
            zipstr = create_zip(brat_path)

    if zipstr:
        st.download_button("Download annotations", zipstr, zip_file.filename)
        def copy_st_brat_to_server_brat(name, brat_path: Path):
            server_brat_path = Path(__file__, "../../brat/data/", name).resolve()
            
            if server_brat_path.exists():
                shutil.rmtree(server_brat_path)
            
            server_brat_path.mkdir(parents=True, exist_ok=True)

            for file in brat_path.iterdir():
                server_file = server_brat_path / file.name
                server_file.write_text(file.read_text())
        st.button("Copy to server brat file", on_click=copy_st_brat_to_server_brat, args=(zip_file.filename.split(".")[0], brat_path))


port = 8001
url = f"http://localhost:{port}"
brat_button = f'''
<a href={url}><button style="background-color:Gray;">Open brat</button></a>
'''
if is_brat_alive(port):
    st.markdown(brat_button, unsafe_allow_html=True)
else:
    if st.button("Launch brat"):
        start_brat(port)
        st.markdown(brat_button, unsafe_allow_html=True)