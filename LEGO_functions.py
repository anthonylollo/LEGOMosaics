import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import re

def jpg_to_df(image):
    """
    Convert .jpg PIL image into a DataFrame.
 
    Parameters
    ----------
    image : PIL.JpegImagePlugin.JpegImageFile
        Image to convert. 

    Return
    ------
    pandas.DataFrame
        Contains 5 columns pixel location x, y and 3 color channels.
    """
    width, height = image.size
    df = pd.DataFrame(np.vstack(np.array(image)[:,:,:3]), columns=('R', 'G', 'B'))

    # Associate the height and width for each pixel. 
    df['height'] = np.repeat(np.arange(height), width)
    df['width'] = np.tile(np.arange(width), height)
    return df


def df_to_image(df, rgb_cols):
    """
    Convert a dataframe with pixel location (height and width) and RGB information to an image.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame to convert.
    rgb_cols : list of str
        Column names of the three RGB columns

    Return
    ------
    PIL.Image.Image
    """
    # Ensure colors are uint8 
    df[rgb_cols] = df[rgb_cols].astype(np.uint8)
    data = np.reshape(df[rgb_cols].values, (df.height.max()+1, df.width.max()+1, 3))
    return Image.fromarray(data, 'RGB')


def pixelate(image, n_w, n_h):
    """
    Pixelate a larger image by rescaling it to a smaller image.

    Parameters
    ----------
    image : PIL.JpegImagePlugin.JpegImageFile
        Image to pixelate.
    n_w : int
        Resulting image width.
    n_h : int
        Resulting image height.

    Return
    ------
    PIL.JpegImagePlugin.JpegImageFile
        Pixelated image. 
    """
    image = image.resize((n_w, n_h), Image.ANTIALIAS)
    return image


def add_lego_colors(df, color_df):
    """
    Add lego color columns to DataFrame. 

    There are other ways to do this, but the colors are added based on the closest in Euclidean
    distance. Does not include Transparent, Metallic or Glow bricks and only uses the 2016 brick 
    palette. 

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with ['R', 'G', 'B'] columns to find the closest matching lego_color
    color_df : pandas.DataFrame
        DataFrame containing all lego colors.

    Return
    ------
    pd.DataFrame
        Contains 3 columns R_lego, G_lego, B_lego for the corrsponding lego brick. 
    """
    # Can't use uint8 for variance, numbers become too large. 
    df[['R', 'G', 'B']] = df[['R', 'G', 'B']].astype('int')

    # Determine which lego color is closest (Euclidean distance) to the image color.
    cmask = ((color_df.c_Palette2016==True) & (color_df.c_Transparent==False) 
             & (color_df.c_Glow==False) & (color_df.c_Metallic==False))
    for index, row in color_df[cmask].iterrows():
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


def legoize_larger_bricks(lego_df):
    """
    Create a lego brick image, using larger bricks. 

    Parameters
    ----------
    lego_df : pandas.DataFrame
        DataFrame containing lego brick color columns ['R_lego', 'G_lego', 'B_lego']
    """
    # Create the image for matplotlib
    image = df_to_image(lego_df, rgb_cols=['R_lego', 'G_lego', 'B_lego'])
    height, width = image.size

    fig, ax = plt.subplots(figsize=(10,10*height/width))
    _ = plt.imshow(image)
    height, width = image.size

    lego_df['group'] = np.NaN

    brick_list = [(2,4), (4,2), (2,2), (4,1), (1,4), (2,1), (1,2), (1,1)]
    for hgroup, wgroup in brick_list:
        for i in range(hgroup):
            for j in range(wgroup):
                remain= lego_df.group.isnull()
                if sum(remain) != 0:

                    # For plotting
                    groups = (lego_df[remain]
                              .groupby([(lego_df[remain].height+i)//hgroup, 
                                        (lego_df[remain].width+j)//wgroup])
                              .color.apply(lambda x: max(x.value_counts())).reset_index())
                    groups = groups[groups.color == (hgroup*wgroup)]

                    for index, row in groups.iterrows():
                        ax.add_patch(patches.Rectangle(
                            (wgroup*row.width-0.5-j, hgroup*row.height-0.5-i), 
                            wgroup, hgroup, fill=False, lw=0.7, color='black'))

                    # For removing from subsequent searches. 
                    df_groups = (lego_df[remain]
                                 .groupby([(lego_df[remain].height+i)//hgroup, 
                                           (lego_df[remain].width+j)//wgroup])
                                 .color.transform(lambda x: max(x.value_counts())))

                    lego_df.loc[lego_df.index.isin(
                        df_groups[df_groups == (hgroup*wgroup)].index), 
                            'group'] = (str(wgroup) + 'x' + str(hgroup))

    # Draw lego circles           
    for i in range(height):
        for j in range(width):
            circle1 = plt.Circle((i, j), 0.3, color='black', alpha=0.15)
            _ = ax.add_artist(circle1)

    _ = plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    _ = plt.tick_params(axis='y', which='both', left=False, right=False, labelleft=False)
    plt.show()