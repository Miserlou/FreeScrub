from pyPdf import PdfFileWriter, PdfFileReader
import os
import shutil

# This is very crude - it should be getting the images in the PDF and scrubbing
# them as well.

if __name__ == "__main__":
    import sys
def scrub(file_in, file_out):
    """
    Scrubs the pdf file_in, returns results to file_out
    """

    file(file_out, 'rb+').close()

    output = PdfFileWriter()
    input = PdfFileReader(file(file_in, 'rb'))

    for i in range(0, input.getNumPages()):
        output.addPage(input.getPage(i))

    #Not proud of this, but pyPDF complains otherwise
    temp_path = file_out + ".CLEAN"
    outputStream = file(temp_path, 'wb')
    output.write(outputStream)
    outputStream.flush()
    outputStream.close()
    os.remove(file_out)
    shutil.move(temp_path, file_out)


__all__ = [scrub]
