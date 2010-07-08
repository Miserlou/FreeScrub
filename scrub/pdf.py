from pyPdf import PdfFileWriter, PdfFileReader

from sys import argv

#arguments: argv1[1] is old pdf, argv[2] is new pdf

output = PdfFileWriter()
input = PdfFileReader(file(argv[1], "rb"))

for i in range(0, input1.getNumPages()):
    output.addPage(input1.getPage(i))

outputStream = file(argv[2], "wb")
output.write(outputStream)
outputStream.flush()
outputStream.close()


