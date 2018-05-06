import pandas as pd
import numpy as np
from PIL import Image

def image_to_df(image):
    """ Read in an image and convert it to a dataframe 5 columns; pixel location
    and 3 color channels. Work with .jpg

    """
    width, height = image.size

    # Create df with RGB information
    df = pd.DataFrame(np.vstack(np.array(image)), columns=('R', 'G', 'B'))

    # Associate the height and width for each pixel. 
    df['height'] = np.repeat(np.arange(height), width)
    df['width'] = np.tile(np.arange(width), height)
    return df


def df_to_image(df, rgb_cols):
    """ Convers a dataframe with pixel location (height and width) and RGB
    information to an image

    """
    # Ensure colors are uint8 
    df[rgb_cols] = df[rgb_cols].astype(np.uint8)
    data = np.reshape(df[rgb_cols].values, (df.height.max()+1, df.width.max()+1, 3))
    return Image.fromarray(data, 'RGB')


def pixelate(image, n_w, n_h):
    """ Pixelates a larger image by rescaling it to a smaller image

    """
    image = image.resize((n_w, n_h), Image.ANTIALIAS)
    return image


def add_lego_colors(df, color_df):
    # Can't use uint8 for variance, numbers become too large. 
    df[['R', 'G', 'B']] = df[['R', 'G', 'B']].astype('int')

    # Determine which lego color is closest (Euclidean distance) to the image color.
    for index, row in color_df[color_df.c_Palette2016==True].iterrows():
        if index == color_df.index[0]:
            df['cvar_min'] = (df.R-row.R)**2 + (df.G-row.G)**2 + (df.B-row.B)**2
            df['R_lego'] = row.R
            df['G_lego'] = row.G
            df['B_lego'] = row.B
            df['color'] = row.Color
        else:
            df['cvar'] = (df.R-row.R)**2 + (df.G-row.G)**2 + (df.B-row.B)**2
            mask = df.cvar < df.cvar_min
            df.loc[mask, 'cvar_min'] = df.loc[mask, 'cvar']
            df.loc[mask, 'R_lego'] = row.R
            df.loc[mask, 'G_lego'] = row.G
            df.loc[mask, 'B_lego'] = row.B
            df.loc[mask, 'color'] = row.Color

    # Drop helper columns we no longer need
    df.drop(columns=['cvar', 'cvar_min'], inplace=True)
    return df