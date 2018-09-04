from keras.layers import Conv2D
from keras.layers import Add
from keras.layers import Activation
from keras.layers import BatchNormalization

import keras
from distutils.version import StrictVersion

if  StrictVersion(keras.__version__) < StrictVersion('2.2.2'):
    from .layers import UpSampling2D
else:
    from keras.layers import UpSampling2D

def Conv(n_filters, kernel_size, activation='relu', use_batchnorm=False, **kwargs):
    """Extension of Conv2aaD layer with batchnorm"""
    def layer(input_tensor):

        x = Conv2D(n_filters, kernel_size, use_bias=not(use_batchnorm), **kwargs)(input_tensor)
        if use_batchnorm:
            x = BatchNormalization()(x)
        x = Activation(activation)(x)

        return x
    return layer


def pyramid_block(pyramid_filters=256, segmentation_filters=128, upsample_rate=2,
                  use_batchnorm=False):
    """
    Pyramid block according to:
        http://presentations.cocodataset.org/COCO17-Stuff-FAIR.pdf

    This block generate `M` and `P` blocks.

    Args:
        pyramid_filters: integer, filters in `M` block of top-down FPN branch
        segmentation_filters: integer, number of filters in segmentation head,
            basically filters in convolution layers between `M` and `P` blocks
        upsample_rate: integer, uspsample rate for `M` block of top-down FPN branch
        use_batchnorm: bool, include batchnorm in convolution blocks

    Returns:
        Pyramid block function (as Keras layers functional API)
    """
    def layer(c, m=None):

        x = Conv2D(pyramid_filters, (1, 1))(c)

        if m is not None:
            up = UpSampling2D((upsample_rate, upsample_rate))(m)
            x = Add()([x, up])

        # segmentation head
        p = Conv(segmentation_filters, (3, 3), padding='same', use_batchnorm=use_batchnorm)(x)
        p = Conv(segmentation_filters, (3, 3), padding='same', use_batchnorm=use_batchnorm)(p)
        m = x

        return m, p
    return layer
