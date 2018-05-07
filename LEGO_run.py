import LEGO_functions as lego
import pandas as pd
from PIL import Image

def image_to_lego_colors(image_file, n_w=48, n_h=48):
    """ Convert a .jpg image into a pixelated version using only LEGO brick colors. 
    Output image is the same size as the original image

    Args:
      image_file: str
        File name of the file to convert into lego colors
      n_w: int, defaults to 48
        Wideness (in # of LEGO bricks) for the resulting image
      n_h: int, defaults to 48
        Height (in # of LEGO bricks) for the resulting image  

    """
    color_df = pd.read_csv('Colors/Lego_colors.csv')

    image = Image.open(image_file)
    pix = lego.pixelate(image, n_w, n_h)
    lego_df = lego.image_to_df(pix)
    lego_df = lego.add_lego_colors(lego_df, color_df)
    lego_image = lego.df_to_image(lego_df, rgb_cols=['R_lego', 'G_lego', 'B_lego'])

    return lego_image

def image_to_lego_bricks(image_file, n_w=48, n_h=48, plot_size=(10,10)):
    """ Convert a .jpg image into a bricked image. 

    Args:
      image_file: str
        File name of the file to convert into lego colors
      n_w: int, defaults to 48
        Wideness (in # of LEGO bricks) for the resulting image
      n_h: int, defaults to 48
        Height (in # of LEGO bricks) for the resulting image  

    """
    color_df = pd.read_csv('Colors/Lego_colors.csv')

    image = Image.open(image_file)
    pix = lego.pixelate(image, n_w, n_h)
    lego_df = lego.image_to_df(pix)
    lego_df = lego.add_lego_colors(lego_df, color_df)
    lego_image = lego.df_to_image(lego_df, rgb_cols=['R_lego', 'G_lego', 'B_lego'])
    lego.legoize(lego_image)


def image_to_large_lego_bricks(image_file, n_w=48, n_h=48, plot_size=(10,10)):
    """ Convert a .jpg image into a bricked image, with the ability to use 
    larger bricks.

    Args:
      image_file: str
        File name of the file to convert into lego colors
      n_w: int, defaults to 48
        Wideness (in # of LEGO bricks) for the resulting image
      n_h: int, defaults to 48
        Height (in # of LEGO bricks) for the resulting image  

    """
    color_df = pd.read_csv('Colors/Lego_colors.csv')

    image = Image.open(image_file)
    pix = lego.pixelate(image, n_w, n_h)
    lego_df = lego.image_to_df(pix)
    lego_df = lego.add_lego_colors(lego_df, color_df)
    lego.legoize_larger_bricks(lego_df)