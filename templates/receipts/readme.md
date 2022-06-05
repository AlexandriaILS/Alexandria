# Receipts

This directory is the HTML used to render the four types of receipts that Alexandria produces. If you want to modify the receipts for your installation, just modify these files and restart the server.

## Process

Because this is a web-based application, receipts are only supported through the Electron companion application for Alexandria. When a receipt needs to be generated, we:

* get the HTML file for the appropriate receipt
* render the HTML file with the appropriate information
* return the receipt to the webpage
* Electron app detects receipt on the page
* prints directly to receipt printer

The HTML files render to the [OFSC's ReceiptLine](https://github.com/receiptline/receiptline) format, and receipts built using this specification (with some **important caveats**) can be used with Alexandria. You can build (or check) receipt templates with the Django templating removed at [ReceiptLine's Designer website](https://receiptline.github.io/designer/).

## Important caveats

There are several issues that, at the time of this writing, I don't have answers for. They are:

* Centering text only works if the line is 22 characters or longer (and trailing / leading spaces are stripped out, so you can't pad). A centered line that is 21 characters long will left justify and I don't know why. The current method for getting around this issue is to left or right justify all lines.
* ASCII art lines built into ReceiptLine do not render properly on my Epson TM-T88V -- they might work for you, but they definitely don't work for me. This is not an issue with ReceiptLine but something between ReceiptLine and my printer.
* Make sure that the rendered HTML is not wider than the capabilities of your printers. Alexandria defaults to a 42 line receipt, but if you're working with a printer with fewer columns then you will need to manually make sure that the templates are appropriate for your column width.

## Future work

Eventually it would be nice to give folks a way to create / edit receipts inside the UI, but until the graphical issues listed under caveats are resolved then hardcoding the receipts is the most futureproof method.
