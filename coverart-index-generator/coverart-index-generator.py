"""Builds a PDF that contains an index of all the cover art."""


from glob import glob
from os.path import basename, join, splitext
from sys import argv


class TileData(object):
    def __init__(self, new_page, origin_x, origin_y, width, height, font_size, name):
        self.__new_page = new_page
        self.__origin_x = origin_x
        self.__origin_y = origin_y
        self.__width = width
        self.__height = height
        self.__font_size = font_size
        self.__name = name

    def get_postscript(self):
        lines = []

        if self.__new_page:
            lines.append("showpage")

        # draw bounding box
        lines.append("newpath")
        lines.append("{0} {1} moveto".format(self.__origin_x, self.__origin_y))
        lines.append("{0} {1} lineto".format(self.__origin_x + self.__width, self.__origin_y))
        lines.append("{0} {1} lineto".format(self.__origin_x + self.__width, self.__origin_y + self.__height))
        lines.append("{0} {1} lineto".format(self.__origin_x, self.__origin_y + self.__height))
        lines.append("{0} {1} lineto".format(self.__origin_x, self.__origin_y))
        lines.append("closepath")
        lines.append("0.1 setlinewidth")
        lines.append("stroke")
        lines.append("")

        # draw name
        lines.append("/Helvetica findfont {0} scalefont setfont".format(self.__font_size))
        lines.append("{0} {1} moveto".format((self.__origin_x + (self.__width / 2.0)), (self.__origin_y + self.__height - self.__font_size)))
        lines.append("({0}) dup stringwidth pop 2 div neg 0 rmoveto show".format(self.__name))
        lines.append("")

        # draw delimiting line
        lines.append("newpath")
        lines.append("{0} {1} moveto".format(self.__origin_x, self.__origin_y + self.__height - (2 * self.__font_size)))
        lines.append("{0} {1} lineto".format(self.__origin_x + self.__width, self.__origin_y + self.__height - (2 * self.__font_size)))
        lines.append("closepath")
        lines.append("0.1 setlinewidth")
        lines.append("stroke")
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

        font_size = page_margin / 8.0

        yield TileData(new_page, tile_origin_x, tile_origin_y, tile_width, tile_height, font_size, splitext(basename(image_file))[0])

        tile_counter += 1


def main(output_file_name):
    A4_WIDTH_IN_POINTS = 595
    A4_HEIGHT_IN_POINTS = 842
    POINTS_PER_INCH = 72
    TILE_COLUMNS = 2
    TILE_ROWS = 3

    jpg_files = glob(join("..", "*.jpg"))
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