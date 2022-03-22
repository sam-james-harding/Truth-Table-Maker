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

    def __init__(self):
        super().__init__()

        self.initUI()

        self.logic_expr_input: QLineEdit
        self.generate_button: QPushButton
        self.truth_table: QTableWidget

        self.generate_button.clicked.connect(self.generateTable)

    def initUI(self):
        uic.loadUi("truth_table_generator.ui", self)
        self.show()

    def generateTable(self):
        rawExpression = self.logic_expr_input.text()
        
        try:
            logicExpr = LogicExpr.parse(rawExpression)
        except:
            self.showParseError()
            return

        inputNames = list(logicExpr.varNames)

        truthTableData = generateTruthTable(inputNames, logicExpr)   

        self.fillTable(inputNames + ["Output"], truthTableData)     

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
        msg.setText("Could not parse logic expression")
        msg.exec()


'''
testExpr = "X&Y"

test = expr.parse(preprocess(testExpr))

print(preprocess(testExpr))
print(test)
print(test({"Y": True, "X": True}))
'''

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = TruthTableApp()
    sys.exit(app.exec_())