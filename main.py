from parsing import LogicExpr, expr

import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QPushButton, QLineEdit, QTableWidgetItem, QMessageBox
from PyQt5 import uic

def generateTruthTable(inputNames: list[str], rule: LogicExpr) -> list[list[bool]]:
    nInputs = len(inputNames)
    nRows = 2**nInputs

    array = [[None for _ in range(nInputs+1)] for _ in range(nRows)]

    for colN in range(nInputs):
        blockSize = 2**(nInputs-1-colN)

        currentIdx = 0
        currentState = True

        while currentIdx < nRows:
            for _ in range(blockSize):
                array[currentIdx][colN] = currentState
                currentIdx += 1
            currentState = not currentState

    for rowN in range(nRows):
        inputs = dict(zip(inputNames, array[rowN][:-1]))
        array[rowN][nInputs] = rule(inputs)

    return array

class TruthTableApp(QMainWindow):

    PARSE_ERROR_MESSAGE = "Could not parse logic expression"

    def __init__(self):
        super().__init__()

        self.initUI()

        self.generate_button.clicked.connect(self.generateTable)

    def initUI(self):
        uic.loadUi("truth_table_generator.ui", self)

        self.logic_expr_input: QLineEdit
        self.generate_button: QPushButton
        self.truth_table: QTableWidget

        self.show()

    def generateTable(self):
        rawExpression = self.logic_expr_input.text()
        
        try:
            logicExpr = LogicExpr.parse(rawExpression)
        except ValueError:
            self.showParseError()
            return

        inputNames = list(logicExpr.varNames)
        headers = inputNames + ["Output"]

        truthTableData = generateTruthTable(inputNames, logicExpr)   
        self.fillTable(headers, truthTableData)     

    def fillTable(self, headers: list[str], contents: list[list[str]]):
        self.truth_table.clear()

        self.truth_table.setColumnCount(len(headers))
        self.truth_table.setRowCount(len(contents))

        self.truth_table.setHorizontalHeaderLabels(headers)

        for rowN, row in enumerate(contents):
            for colN, value in enumerate(row):
                self.truth_table.setItem(
                    rowN, colN, QTableWidgetItem(str(value))
                )

    def showParseError(self):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setText(self.PARSE_ERROR_MESSAGE)
        msg.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = TruthTableApp()
    sys.exit(app.exec_())