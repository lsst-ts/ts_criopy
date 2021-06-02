from PySide2.QtWidgets import QMessageBox
import asyncio


def setBoolLabel(label, trueText, falseText, value):
    text = falseText
    if value:
        text = trueText
    label.setText(text)


def setWarningLabel(label, value):
    setBoolLabel(label, "WARNING", "OK", value)


def setBoolLabelHighLow(label, value):
    setBoolLabel(label, "HIGH", "LOW", value)


def setBoolLabelOnOff(label, value):
    setBoolLabel(label, "ON", "OFF", value)


def setBoolLabelOpenClosed(label, value):
    setBoolLabel(label, "OPEN", "CLOSED", value)


def setBoolLabelYesNo(label, value):
    setBoolLabel(label, "YES", "NO", value)


def warning(parent, title, description):
    """Creates future with QMessageBox. Enables use of QMessageBox with asyncqt/asyncio. Mimics QMessageBox.warning behaviour - but QMessageBox cannot be used, as it blocks Qt loops from executing (as all modal dialogs does).

    Parameters
    ----------
    parent : `QtWidget`
        Parent widget.
    title : `str`
        Message window title.
    description : `str`
        Descrption of warning occured.
    """

    future = asyncio.Future()
    dialog = QMessageBox(parent)
    dialog.setWindowTitle(title)
    dialog.setText(description)
    dialog.setIcon(QMessageBox.Warning)
    dialog.finished.connect(lambda r: future.set_result(r))
    dialog.open()
    return future
