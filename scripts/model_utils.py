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

import tensorflow as tf
def load_unet_with_mobilenet(input_shape=(256,256,3)):
    inputs = Input(shape=input_shape)
    x = build_augmentation_layer()(inputs) 
    base_model = MobileNetV2(input_tensor=x, include_top=False, weights="imagenet")
    skip_names = [
        'block_1_expand_relu',  # 128x128
        'block_3_expand_relu',  # 64x64
        'block_6_expand_relu',  # 32x32
        'block_13_expand_relu'  # 16x16
    ]
    skips = [base_model.get_layer(name).output for name in skip_names]

    x = base_model.output  # 16x16

    # Decoder
    for skip in reversed(skips):
        x = Conv2DTranspose(256, 3, strides=2, padding='same')(x)
        x = concatenate([x, skip])
        x = Conv2D(128, 3, padding='same', activation='relu')(x)

    # Final upsampling
    x = Conv2DTranspose(64, 3, strides=2, padding='same')(x)
    output = Conv2D(1, 1, activation='sigmoid')(x)

    return Model(inputs=base_model.input, outputs=output)


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
