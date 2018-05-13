import LEGO_functions as lego
import pandas as pd
from PIL import Image


def image_to_lego_bricks(image_file, n_w=48):
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
    width, height = image.size
    pix = lego.pixelate(image, n_w, int(n_w*height/width))
    lego_df = lego.image_to_df(pix)
    lego_df = lego.add_lego_colors(lego_df, color_df)
    lego.legoize_larger_bricks(lego_df)
