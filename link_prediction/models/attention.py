import tensorflow as tf
from tensorflow import keras
from keras import layers
import keras.backend as K

def build_attention(sequence_size, embedding_dim, input_query, input_keys, input_values):
    input_query = layers.Input(shape=(sequence_size, embedding_dim))
    
    input_keys = layers.Input(shape=(sequence_size, embedding_dim))
    
    input_values = layers.Input(shape=(sequence_size, embedding_dim))
    
    
    def apply_keys_transform(keys_layers):

        linear_key = layers.Dense(
            units=embedding_dim
        )

        keys_transformed = layers.TimeDistributed(linear_key)(keys_layers)
        return linear_key, keys_transformed
    
    def apply_query_transform(to_query_layer):
        query = layers.GlobalAveragePooling1D()(to_query_layer)

        query = layers.Dense(
            units=embedding_dim
        )(query)
        
        return query
    
    def apply_attention_function(keys, query):
        """
        additive soft attention
        """

        repeated_querys = layers.RepeatVector(sequence_size)(query)
        
        energy_layer = layers.Add()([keys, repeated_querys])
        
        energy_layer = layers.Activation(
            activation='relu'
        )(energy_layer)
        
        vector_layer = layers.Dense(
            units=1,
            kernel_initializer='he_normal'
        )
        
        energy_layer = layers.TimeDistributed(vector_layer)(energy_layer)
        
        return energy_layer
        
    
    keys = apply_keys_transform(input_keys)
    values = apply_keys_transform(input_values)
    query = apply_query_transform(input_query)
    energy = apply_attention_function(keys, query)
    attention = layers

## Attention from repo https://arxiv.org/abs/2102.12227

def create_mutiply_negative_elements_fn():
    """
    Creates multiply the tensor for a set of very negative numbers
    :return: the tensor mutiplied for  -1e9
    """
    def func(x):
        n = x * (-1e9)
        return n

    func.__name__ = "mutiply_negative_elements_"
    return func

def create_padding_mask_fn():
    """
    Given a padded tensor, provides a mask with padded elements set to 1
    :return: a tensor whose elements are 1 in correspondence of the padding elements
    """
    def func(x, axis=-1):
        zeros = tf.equal(x, 0)
        zeros = tf.cast(zeros, dtype='float32')
        return zeros

    func.__name__ = "create_padding_mask_"
    return func

def create_sum_fn(axis):
    """
    Sum a tensor along an axis
    :param axis: axis along which to sum
    :return:
    """
    def func(x):
        return K.sum(x, axis=axis)

    func.__name__ = "sumalong_" + str(axis)
    return func

def apply_attention(source_input, target_input, prev_source_layer, prev_target_layer, source_layers, target_layers, embedding_size, index):
    
    # create keys using dense layer
    source_linearity = layers.Dense(units=embedding_size,
                             name=f'att_linearity_K_source_{index}')
    source_keys = layers.TimeDistributed(source_linearity, name=f'att_K_source_{index}')(source_layers)
    target_linearity = layers.Dense(units=embedding_size,
                             name=f'att_linearity_K_target_{index}')
    target_keys = layers.TimeDistributed(target_linearity, name=f'att_K_target_{index}')(target_layers)

    # create query elements doing average and then multiplication
    source_avg = layers.GlobalAveragePooling1D(name=f"avg_query_source_{index}")(source_layers)
    target_avg = layers.GlobalAveragePooling1D(name=f"avg_query_target_{index}")(target_layers)

    # Original code. Problems when saving the model
    # source_query = source_linearity(target_avg)
    # target_query = source_linearity(source_avg)
    
    # Code added to fix the problem.
    querys_linear_source = layers.Dense(
        units=embedding_size,
        name=f'att_linearity_query_source_{index}')
    querys_linear_target = layers.Dense(
        units=embedding_size,
        name=f'att_linearity_query_target_{index}')
    
    source_query = querys_linear_source(target_avg)
    target_query = querys_linear_target(source_avg)
    
    time_shape = (source_keys.shape)[1]
    space_shape = (source_keys.shape)[2]

    # repeat the query and sum
    source_query = layers.RepeatVector(time_shape, name=f'repeat_query_source_{index}')(source_query)
    target_query = layers.RepeatVector(time_shape, name=f'repeat_query_target_{index}')(target_query)
    source_score = layers.Add(name=f'att_addition_source_{index}')([source_query, source_keys])
    target_score = layers.Add(name=f'att_addition_target_{index}')([target_query, target_keys])

    # activation and dot product with importance vector
    target_score = layers.Activation(activation='relu', name=f'att_activation_target_{index}')(target_score)
    source_score = layers.Activation(activation='relu', name=f'att_activation_source_{index}')(source_score)
    imp_v_target = layers.Dense(units=1,
                         kernel_initializer='he_normal',
                         name=f'importance_vector_target_{index}')
    target_score = layers.TimeDistributed(imp_v_target, name=f'att_scores_target_{index}')(target_score)
    imp_v_source = layers.Dense(units=1,
                         kernel_initializer='he_normal',
                         name=f'importance_vector_source_{index}')
    source_score = layers.TimeDistributed(imp_v_source, name=f'att_scores_source_{index}')(source_score)

    # application of mask: padding layer are associated to very negative scores to improve softmax
    source_score = layers.Flatten(name=f'att_scores_flat_source_{index}')(source_score)
    target_score = layers.Flatten(name=f'att_scores_flat_target_{index}')(target_score)
    maskLayer = layers.Lambda(create_padding_mask_fn(), name=f'masking')
    negativeLayer = layers.Lambda(create_mutiply_negative_elements_fn(), name=f'negative_mul')
    mask_source = maskLayer(source_input)
    mask_target = maskLayer(target_input)
    neg_source = negativeLayer(mask_source)
    neg_target = negativeLayer(mask_target)
    source_score = layers.Add(name=f'att_masked_addition_source_{index}')([neg_source, source_score])
    target_score = layers.Add(name=f'att_masked_addition_target_{index}')([neg_target, target_score])

    # softmax application
    source_weight = layers.Activation(activation='softmax', name=f'att_weights_source_{index}')(source_score)
    target_weight = layers.Activation(activation='softmax', name=f'att_weights_target_{index}')(target_score)

    # weighted sum
    source_weight = layers.Reshape(target_shape=(source_weight.shape[-1], 1), name=f'att_weights_reshape_source_{index}')(
        source_weight)
    target_weight = layers.Reshape(target_shape=(target_weight.shape[-1], 1), name=f'att_weights_reshape_target_{index}')(
        target_weight)
    source_weighted = layers.Multiply(name=f'att_multiply_source_{index}')([source_weight, prev_source_layer])
    target_weighted = layers.Multiply(name=f'att_multiply_target_{index}')([target_weight, prev_target_layer])
    source_layers = layers.Lambda(create_sum_fn(1), name=f'att_cv_source_{index}')(source_weighted)
    target_layers = layers.Lambda(create_sum_fn(1), name=f'att_cv_target_{index}')(target_weighted)
    
    return source_layers, target_layers

