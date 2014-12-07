"""Builds a PDF that contains an index of all the cover art."""


from os.path import basename, join, splitext
from sys import argv


def main(output_file_name):
    A4_WIDTH_IN_POINTS = 595
    A4_HEIGHT_IN_POINTS = 842
    POINTS_PER_INCH = 72

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
        lines.append("showpage")

        output_file.write("\n".join(lines))


if __name__ == "__main__":
    if len(argv) != 2:
        raise Exception("Script expects a single argument that represents the output file name")

    main(argv[1])