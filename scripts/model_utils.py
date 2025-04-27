# scripts/model_utils.py
# ------------------------------------------------------------------
# FUNCIONES ÚTILES PARA EL MODELO
# ------------------------------------------------------------------

import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras import Input, Model
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Conv2D, Conv2DTranspose, UpSampling2D, concatenate,Input
from tensorflow.keras.layers.experimental import preprocessing


def build_augmentation_layer():
    return preprocessing.RandomFlip(mode="horizontal_and_vertical")

def load_unet_with_mobilenet(input_shape=(256,256,4)):
    # Input y augment+proyección 4→3
    inputs = Input(shape=input_shape)
    x = build_augmentation_layer()(inputs)
    x = Conv2D(3, (1,1), padding='same', activation='relu', name='proj_4to3')(x)
    
    # Backbone puro
    backbone = MobileNetV2(input_shape=(256,256,3),
                           include_top=False,
                           weights='imagenet')
    
    # Creamos un sub-modelo que devuelva los skips + la salida
    skip_layer_names = [
        'block_1_expand_relu',   # 128×128
        'block_3_expand_relu',   # 64×64
        'block_6_expand_relu',   # 32×32
        'block_13_expand_relu'   # 16×16
    ]
    skip_outputs = [backbone.get_layer(name).output for name in skip_layer_names]
    down_outputs = skip_outputs + [backbone.output]
    down_model = Model(inputs=backbone.input, outputs=down_outputs)
    down_model.trainable = False
    
    # Aplicamos el sub-modelo al tensor proyectado
    skips = down_model(x)[:-1]
    x = down_model(x)[-1]
    
    # Decoder (UNet clásico)
    for skip in reversed(skips):
        x = Conv2DTranspose(256, 3, strides=2, padding='same')(x)
        x = concatenate([x, skip])
        x = Conv2D(128, 3, padding='same', activation='relu')(x)
    
    # Upsample final y salida
    x = Conv2DTranspose(64, 3, strides=2, padding='same')(x)
    output = Conv2D(1, 1, activation='sigmoid')(x)
    
    return Model(inputs=inputs, outputs=output)


def build_augmentation_layer():
    return tf.keras.Sequential([
        preprocessing.RandomFlip(mode="horizontal_and_vertical"),
        preprocessing.RandomRotation(factor=0.2),
        preprocessing.RandomContrast(factor=0.1)
    ])

def dice_loss(y_true, y_pred, smooth=1e-6):
    intersection = tf.reduce_sum(y_true * y_pred)
    return 1 - (2. * intersection + smooth) / (tf.reduce_sum(y_true) + tf.reduce_sum(y_pred) + smooth)

def predict_mask(image_path, model):
    img = tf.io.read_file(image_path)
    img = tf.image.decode_png(img, channels=3)
    img = tf.image.resize(img, (256, 256))
    img = tf.cast(img, tf.float32) / 255.0  
    prediction = model.predict(tf.expand_dims(img, axis=0))
    return prediction.squeeze()
