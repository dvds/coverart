"""Builds a PDF that contains an index of all the cover art."""


from glob import glob
from os.path import basename, dirname, join, splitext
from PIL import Image
from sys import argv


class ImageData(object):
    POINTS_PER_INCH = 72.0

    def __init__(self, file):
        self.__file = file

        image = Image.open(self.__file)
        if image.mode != "RGB":
            raise Exception("Only supports RGB images at present.")
        else:
            self.bits_per_component = 8

        self.width = image.size[0]
        self.height = image.size[1]

        if "dpi" in image.info:
            self.__horizontal_dpi = image.info["dpi"][0]
            self.__vertical_dpi = image.info["dpi"][1]
        else:
            self.__horizontal_dpi = self.POINTS_PER_INCH
            self.__vertical_dpi = self.POINTS_PER_INCH

    def get_name(self):
        return splitext(basename(self.__file))[0]

    def get_print_width_in_points(self):
        return int(round(self.width * self.POINTS_PER_INCH / self.__horizontal_dpi))

    def get_print_height_in_points(self):
        return int(round(self.height * self.POINTS_PER_INCH / self.__vertical_dpi))

    def get_pixel_data(self):
        lines = []

        image = Image.open(self.__file)

        line = []
        for y in range(0, self.height):
            for x in range(0, self.width):
                r, g, b = image.getpixel((x, y))
                if len(line) == 64:
                    lines.append(" ".join(line))
                    line = []
                line.append("{0:02x}{1:02x}{2:02x}".format(r, g, b))

        lines.append(" ".join(line))

        return "\n".join(lines)


class TileData(object):
    def __init__(self, new_page, origin_x, origin_y, width, height, image_data, font_size):
        self.__new_page = new_page
        self.__origin_x = origin_x
        self.__origin_y = origin_y
        self.__width = width
        self.__height = height
        self.__image_data = image_data
        self.__font_size = font_size

    def __calculate_image_position_within_tile(self):
        available_image_height = self.__height - (2 * self.__font_size)

        if self.__image_data.get_print_width_in_points() <= self.__width and self.__image_data.get_print_height_in_points() <= available_image_height:
            # image will print entirely inside the tile
            image_width = self.__image_data.get_print_width_in_points()
            image_height = self.__image_data.get_print_height_in_points()

        else:
            # image needs to be scaled
            tile_width_height_scale_factor = self.__width * 1.0 / self.__height
            image_width_height_scale_factor = self.__image_data.get_print_width_in_points() * 1.0 / self.__image_data.get_print_height_in_points()
            if tile_width_height_scale_factor < image_width_height_scale_factor:
                # image is more tall than wide
                image_width = self.__width
                image_height = available_image_height * tile_width_height_scale_factor / image_width_height_scale_factor
            else:
                # image is more wide than tall
                image_width = self.__width * image_width_height_scale_factor / tile_width_height_scale_factor
                image_height = available_image_height

        return self.__origin_x + (self.__width / 2.0) - (image_width / 2.0), self.__origin_y + (available_image_height / 2.0) - (image_height / 2.0), image_width, image_height

    def get_postscript(self):
        lines = []

        if self.__new_page:
            lines.append("showpage")

        # draw name
        lines.append("/Helvetica findfont {0} scalefont setfont".format(self.__font_size))
        lines.append("{0} {1} moveto".format((self.__origin_x + (self.__width / 2.0)), (self.__origin_y + self.__height - self.__font_size)))
        lines.append("({0}) dup stringwidth pop 2 div neg 0 rmoveto show".format(self.__image_data.get_name()))
        lines.append("")

        # draw image
        image_origin_x, image_origin_y, image_width, image_height = self.__calculate_image_position_within_tile()
        lines.append("gsave")
        lines.append("{0} {1} translate".format(image_origin_x, image_origin_y))
        lines.append("{0} {1} scale".format(image_width, image_height))
        lines.append("{0} {1} {2} [{0} 0 0 -{1} 0 {1}]".format(self.__image_data.width, self.__image_data.height, self.__image_data.bits_per_component))
        lines.append("{<")
        lines.append(self.__image_data.get_pixel_data())
        lines.append(">}")
        lines.append("false 3 colorimage")
        lines.append("grestore")
        lines.append("")

        return "\n".join(lines)


def __generate_tile_data(page_width, page_height, page_margin, columns, rows, image_files):
    tiles_per_page = columns * rows

    tile_counter = 0
    for image_file in image_files:
        if tile_counter % tiles_per_page == 0:
            new_page = True
        else:
            new_page = False

        tile_spacer_size = page_margin / 2.0

        tile_width = (page_width - (2 * page_margin) - ((columns - 1) * tile_spacer_size)) / (columns * 1.0)
        tile_column_ordinal = tile_counter % columns
        tile_origin_x = page_margin + (tile_column_ordinal * (tile_width + tile_spacer_size))

        tile_height = (page_height - (2 * page_margin) - ((rows - 1) * tile_spacer_size)) / (rows * 1.0)
        tile_row_ordinal = (tile_counter % (columns * rows)) / columns
        tile_origin_y = page_height - page_margin - tile_height - (tile_row_ordinal * (tile_height + tile_spacer_size))

        image_data = ImageData(image_file)

        font_size = page_margin / 8.0

        yield TileData(new_page, tile_origin_x, tile_origin_y, tile_width, tile_height, image_data, font_size)

        tile_counter += 1


def main(output_file_name):
    A4_WIDTH_IN_POINTS = 595
    A4_HEIGHT_IN_POINTS = 842
    POINTS_PER_INCH = 72
    TILE_COLUMNS = 2
    TILE_ROWS = 3

    jpg_files = glob(join(dirname(output_file_name), "..", "*.jpg"))
    jpg_files.sort()

    with open(output_file_name, "w") as output_file:

        lines = []
        lines.append("%!PS")
        lines.append("")
        lines.append("<< /PageSize [{0} {1}] >> setpagedevice".format(A4_WIDTH_IN_POINTS, A4_HEIGHT_IN_POINTS))
        lines.append("")
        lines.append("/Helvetica findfont {0} scalefont setfont".format(POINTS_PER_INCH))
        lines.append("{0} {1} moveto".format(A4_WIDTH_IN_POINTS / 2.0, (A4_HEIGHT_IN_POINTS * 2 / 3.0) - (POINTS_PER_INCH / 2)))
        lines.append("({0}) dup stringwidth pop 2 div neg 0 rmoveto show".format(splitext(basename(output_file_name))[0]))
        lines.append("")

        for tile_data in __generate_tile_data(A4_WIDTH_IN_POINTS, A4_HEIGHT_IN_POINTS, POINTS_PER_INCH, TILE_COLUMNS, TILE_ROWS, jpg_files):
            lines.append(tile_data.get_postscript())

        lines.append("showpage")

        output_file.write("\n".join(lines))


if __name__ == "__main__":
    if len(argv) != 2:
        raise Exception("Script expects a single argument that represents the output file name")

    main(argv[1])