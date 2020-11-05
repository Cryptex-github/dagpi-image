import textwrap

from PIL import ImageDraw, Image, ImageFont

from app.image.decorators import executor
from app.image.PILManip import pil

__all__ = ("retromeme_gen", )


class Meme:
    def __init__(self, text, image: Image):
        self.image = image
        self.meme_path = None
        self.tmp_path = None
        self.text = text
        self.filetype = "png"
        self.font_path = "app/image/assets/impact.ttf"

    def store_image(self):
        return self.image

    def find_longest_line(self, text):
        longest_width = 0
        longest_line = ""
        for line in text:
            width = self.draw.textsize(
                line, font=ImageFont.truetype(self.font_path, 20)
            )[0]
            if width > longest_width:
                longest_width = width
                longest_line = line

        return longest_line

    def get_font_measures(self, text, font_size, ratio):
        measures = {}
        measures["font"] = ImageFont.truetype(self.font_path, size=font_size)
        measures["width"] = self.draw.textsize(text, font=measures["font"])[0]
        measures["ratio"] = measures["width"] / float(self.image.width)
        measures["ratio_diff"] = abs(ratio - measures["ratio"])

        return measures

    def optimize_font(self, text):
        """Fuckin' magnets how do they work"""
        font_min_size = 12
        font_max_size = 150
        font_size_range = range(font_min_size, font_max_size + 1)

        longest_text_line = self.find_longest_line(text)

        # set min/max ratio of font width to image width
        min_ratio = 0.7
        max_ratio = 0.9
        perfect_ratio = min_ratio + (max_ratio - min_ratio) / 2
        ratio = 0

        while (ratio < min_ratio or ratio > max_ratio) and \
              (len(font_size_range) > 2):
            measures = {
                "top": self.get_font_measures(
                    text=longest_text_line,
                    font_size=font_size_range[-1],
                    ratio=perfect_ratio,
                ),
                "low": self.get_font_measures(
                    text=longest_text_line,
                    font_size=font_size_range[0],
                    ratio=perfect_ratio,
                ),
            }

            half_index = len(font_size_range) // 2
            if measures["top"]["ratio_diff"] < measures["low"]["ratio_diff"]:
                closer = "top"
                font_size_range = font_size_range[int(half_index): -1]
            else:
                closer = "low"
                font_size_range = font_size_range[0:half_index]

            ratio = measures[closer]["ratio"]
            font = measures[closer]["font"]

        width = self.draw.textsize(longest_text_line, font=font)[0]

        return font, width

    def set_text_wrapping(self, text_length):
        if text_length <= 32:
            wrapping = 32
        elif text_length > 100:
            wrapping = 10 + text_length // 3
        elif text_length > 32:
            wrapping = 5 + text_length // 2
        return int(wrapping)

    def prepare_text(self, text):
        if not text:
            return "", 0
        if type(text) == list:
            text = text[0]
        wrapping = self.set_text_wrapping(len(text))
        text = text.strip().upper()
        text = textwrap.wrap(text, wrapping)
        font, text_width = self.optimize_font(text)

        text = "\n".join(text)

        return text, text_width, font

    def draw_text(self, xy, text, font):
        x = xy[0]
        y = xy[1]

        o = 1

        xys = (
            (x + o, y),
            (x - o, y),
            (x + o, y + o),
            (x - o, y - o),
            (x - o, y + o),
            (x, y - o),
            (x, y + o),
        )

        for xy in xys:
            self.draw.multiline_text(
                xy, text, fill="black", font=font, align="center")

        self.draw.multiline_text(
            (x, y), text, fill="white", font=font, align="center")

    def draw_meme(self):
        self.draw = ImageDraw.Draw(self.image)

        margin_xy = (0, self.image.height / 18)

        text_top = self.text.split("|")[0]
        if text_top:
            text_top, text_top_width, top_font = self.prepare_text(text_top)
            top_xy = (
                ((self.image.width - text_top_width) / 2),
                (margin_xy[1]))
            self.draw_text(top_xy, text_top, top_font)

        text_bottom = self.text.split("|")[1:]
        if text_bottom:
            text_bottom, text_bottom_width, bottom_font = self.prepare_text(
                text_bottom)
            bottom_xy = [
                ((self.image.width - text_bottom_width) / 2),
                (self.image.height - bottom_font.getsize(text_bottom)[1] * 
                 len(text_bottom.split("\n")) - margin_xy[1]), ]
            self.draw_text(bottom_xy, text_bottom, bottom_font)

    def make_meme(self):
        if self.image:
            self.draw_meme()
            im = self.store_image()
            return im
        else:
            return False


@executor
@pil
def retromeme_gen(image, text: str):
    mem = Meme(text, image)
    return mem.make_meme()
