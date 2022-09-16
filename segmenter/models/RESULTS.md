# Resultados

Modelos para la segmentación de componentes argumentativas.

## Data

La carpeta data contiene subcarpetas con el corpus en el siguiente formato creado por el programa `segmenter_exporter.py`:

- [train, testa, testb].words.txt: En cada linea contiene una entrada con los tokens separados por espacios. Esta entrada puede ser segmentda en oraciones o párrafos en dependencia de lo que se necesite.
- [train, testa, testb].tags.txt: En cada linea contiene una entrada con las etiquetas de los tokens separados por espacios. Esta entrada puede ser segmentda en oraciones o párrafos en dependencia de lo que se necesite.
- vocab.[chars, tags, words].txt: En cada linea contiene los caracteres, tags y palabras como conjunto.

## Argument Segmentation

Contiene los modelos comparativos para la segmentación de componentes argumentativas.
Solamente hace falta cambiar la dirección del corpus para realizar el entrenamiento.

Entre las tareas que realiza se encuentran:

- Procesamiento del corpus
- Entrenamiento de modelos (LSTM-CRF, LSTM-DL-CRF, CNN-LSTM-CRF, CNN-LSTM-DL-CRF)
- Serializado de modelos
- Muestrado de gráficas de entrenamiento

## Argument Segmentation Metrics

Contiene los códigos necesarios para mostrar métricas acerca de los modelos.

## Experimentación

Se crearon dos versiones del modelo, uno entrenado con las etiquetas con los metadatos originales y otro con las etiquetas conteniendo solamente la asignación BIOES. El objetivo consistía en conocer si afectaba el resultado el hecho de tener información extra a la hora de segmentar las componentes.

El experimento anterior se realizó usando como conjunto de entrenamiento las oraciones y los textos de forma separada, para conocer cómo afecta la división del conjunto de entrenamiento al modelo.

### Resultados con metatags y oraciones

![Histograma](data/english_sentence/images/histogram_model_cnn_bilstm_crf.png)

Como se aprecia en las siguientes figuras se observa que muchos errores en los que incurre el modelo se trata de una mala clasificación en el tipo de metadato de la etiqueta, lo que en términos de segmentación no influye en el resultado final.

Errores en B-Claim | Errores en B-MajorClaim | Errores en B-Premise
:--:|:--:|:--:
![B-Claim](data/english_sentence/images/tag_B-Claim_model_cnn_bilstm_crf_mistakes.png) | ![B-MajorClaim](data/english_sentence/images/tag_B-MajorClaim_model_cnn_bilstm_crf_mistakes.png) | ![B-Premise](data/english_sentence/images/tag_B-Premise_model_cnn_bilstm_crf_mistakes.png)

Errores en I-Claim | Errores en I-MajorClaim | Errores en I-Premise
:--:|:--:|:--:
![I-Claim](data/english_sentence/images/tag_I-Claim_model_cnn_bilstm_crf_mistakes.png) | ![I-MajorClaim](data/english_sentence/images/tag_I-MajorClaim_model_cnn_bilstm_crf_mistakes.png) | ![I-Premise](data/english_sentence/images/tag_I-Premise_model_cnn_bilstm_crf_mistakes.png)

Errores en E-Claim | Errores en E-MajorClaim | Errores en E-Premise
:--:|:--:|:--:
![E-Claim](data/english_sentence/images/tag_E-Claim_model_cnn_bilstm_crf_mistakes.png) | ![E-MajorClaim](data/english_sentence/images/tag_E-MajorClaim_model_cnn_bilstm_crf_mistakes.png) | ![E-Premise](data/english_sentence/images/tag_E-Premise_model_cnn_bilstm_crf_mistakes.png)

Tomando solamente las anotaciones BIOES el modelo obtiene una precisión del 67% aproximadamente comparado con una precisión del 85% en su versión con meta tags.

Todas las tags | Solo BIOES tags
:--:|:--:
![Histograma](data/english_sentence/images/histogram_model_cnn_bilstm_crf.png) | ![Histograma solo BIOES](data/english_sentence/images/histogram_model_cnn_bilstm_crf_only_BIOES.png)

### Resultados sin metatags y oraciones

![Histograma](data/english_sentence_no_meta_tags/images/histogram_model_cnn_bilstm_crf.png)

Errores en B | Errores en I
:--:|:--:
![B](data/english_sentence_no_meta_tags/images/tag_B_model_cnn_bilstm_crf_mistakes.png) | ![I](data/english_sentence_no_meta_tags/images/tag_I_model_cnn_bilstm_crf_mistakes.png)

Errores en E | Errores en O
:--:|:--:
![E](data/english_sentence_no_meta_tags/images/tag_E_model_cnn_bilstm_crf_mistakes.png) | ![O](data/english_sentence_no_meta_tags/images/tag_O_model_cnn_bilstm_crf_mistakes.png)

El modelo tiene una precisión del 90% al igual que su contraparte con metatags. Esto supone que el cambio de anotación no trae grandes cambios en el resultado final del problema.

### Resultados con metatags y párrafos

![Histograma](data/english_paragraph/images/histogram_model_cnn_bilstm_crf.png)

Como se aprecia en las siguientes figuras se observa que muchos errores en los que incurre el modelo se trata de una mala clasificación en el tipo de metadato de la etiqueta, lo que en términos de segmentación no influye en el resultado final.

Errores en B-Claim | Errores en B-MajorClaim | Errores en B-Premise
:--:|:--:|:--:
![B-Claim](data/english_paragraph/images/tag_B-Claim_model_cnn_bilstm_crf_mistakes.png) | ![B-MajorClaim](data/english_paragraph/images/tag_B-MajorClaim_model_cnn_bilstm_crf_mistakes.png) | ![B-Premise](data/english_paragraph/images/tag_B-Premise_model_cnn_bilstm_crf_mistakes.png)

Errores en I-Claim | Errores en I-MajorClaim | Errores en I-Premise
:--:|:--:|:--:
![I-Claim](data/english_paragraph/images/tag_I-Claim_model_cnn_bilstm_crf_mistakes.png) | ![I-MajorClaim](data/english_paragraph/images/tag_I-MajorClaim_model_cnn_bilstm_crf_mistakes.png) | ![I-Premise](data/english_paragraph/images/tag_I-Premise_model_cnn_bilstm_crf_mistakes.png)

Errores en E-Claim | Errores en E-MajorClaim | Errores en E-Premise
:--:|:--:|:--:
![E-Claim](data/english_paragraph/images/tag_E-Claim_model_cnn_bilstm_crf_mistakes.png) | ![E-MajorClaim](data/english_paragraph/images/tag_E-MajorClaim_model_cnn_bilstm_crf_mistakes.png) | ![E-Premise](data/english_paragraph/images/tag_E-Premise_model_cnn_bilstm_crf_mistakes.png)

Tomando solamente las anotaciones BIOES el modelo obtiene una precisión del 90% aproximadamente comparado con una precisión del 76% en su versión con meta tags.

Todas las tags | Solo BIOES tags
:--:|:--:
![Histograma](data/english_paragraph/images/histogram_model_cnn_bilstm_crf.png) | ![Histograma solo BIOES](data/english_paragraph/images/histogram_model_cnn_bilstm_crf_only_BIOES.png)

### Resultados sin metatags y párrafos

![Histograma](data/english_paragraph_no_meta_tags/images/histogram_model_cnn_bilstm_crf.png)

Errores en B | Errores en I
:--:|:--:
![B](data/english_paragraph_no_meta_tags/images/tag_B_model_cnn_bilstm_crf_mistakes.png) | ![I](data/english_paragraph_no_meta_tags/images/tag_I_model_cnn_bilstm_crf_mistakes.png)

Errores en E | Errores en O
:--:|:--:
![E](data/english_paragraph_no_meta_tags/images/tag_E_model_cnn_bilstm_crf_mistakes.png) | ![O](data/english_paragraph_no_meta_tags/images/tag_O_model_cnn_bilstm_crf_mistakes.png)

El modelo tiene una precisión del 90% al igual que su contraparte con metatags. Esto supone que el cambio de anotación no trae grandes cambios en el resultado final del problema.
