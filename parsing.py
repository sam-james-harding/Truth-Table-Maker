from operator import or_, ne, and_, eq
import CombiParser as cp
from typing import Callable

# expr ::= xorExpr '+' expr | xorExpr 
# xorExpr ::= implExpr '^' xorExpr | implExpr
# implExpr ::= equivExpr '->' implExpr | equivExpr
# equivExpr ::= andExpr '<->' equivExpr | andExpr
# andExpr ::= notExpr '*' andExpr | notExpr
# notExpr ::= '-' term | term
# term ::= 'T' | 'F' | '(' expr ')' | variableName

expr, xorExpr, implExpr, equivExpr = cp.Parser(), cp.Parser(), cp.Parser(), cp.Parser()
andExpr, notExpr, term = cp.Parser(), cp.Parser(), cp.Parser()

variableName = cp.Parser()

def stringParser(string: str):
    charParsers = [(cp.charParser(char), True) for char in string]

    return cp.sequence(
        lambda *chars: "".join(chars),
        *charParsers
    )


class LogicExpr:
    LogicFunc = Callable[[dict[str, bool]], bool]

    def __init__(self, func: LogicFunc, varNames: list[str] = None):
        self.__func = func
        self.varNames = [] if varNames == None else varNames

    def __call__(self, values: dict[str, bool]):
        return self.__func(values)

    def __str__(self):
        if self.varNames == []:
            return "LogicExpr on no variables"
        else:
            return f"LogicExpr on the variables {self.varNames}"

    @staticmethod
    def Constant(val: bool):
        return LogicExpr(lambda _: val)

    @staticmethod
    def Variable(name: str):
        return LogicExpr(lambda vals: vals[name], [name])

    @staticmethod
    def CombineBinary(expr1: 'LogicExpr', expr2: 'LogicExpr', binFunc: Callable[[bool, bool], bool]):
        combinedVarNames = expr1.varNames + [name for name in expr2.varNames if name not in expr1.varNames]

        return LogicExpr(
            lambda vals: binFunc(expr1(vals), expr2(vals)), 
            combinedVarNames    
        ) 

    @staticmethod
    def parse(rawInput: str) -> 'LogicExpr':
        return expr.parse(rawInput)


def binaryOpParser(parser1: cp.Parser, parser2: cp.Parser, opString: str, binFunc: Callable) -> cp.Parser:
    return cp.sequence(
        lambda e1, e2: LogicExpr.CombineBinary(e1, e2, binFunc),
        (cp.whitespaceParser, False),
        (parser1, True),
        (cp.whitespaceParser, False),
        (stringParser(opString), False),
        (cp.whitespaceParser, False),
        (parser2, True),
        (cp.whitespaceParser, False)
    )


expr.setParser(
    cp.combine(
        binaryOpParser(xorExpr, expr, "+", or_),
        xorExpr
    )
)

xorExpr.setParser(
    cp.combine(
        binaryOpParser(implExpr, xorExpr, "^", ne),
        implExpr
    )
)

implExpr.setParser(
    cp.combine(
        binaryOpParser(equivExpr, implExpr, "->", lambda a, b: not a or b),
        equivExpr
    )
)

equivExpr.setParser(
    cp.combine(
        binaryOpParser(andExpr, equivExpr, "<->", eq),
        andExpr
    )
)

andExpr.setParser(
    cp.combine(
        binaryOpParser(notExpr, andExpr, "*", and_),
        notExpr
    )
)

notExpr.setParser(
    cp.combine(
        cp.sequence(
            lambda e: LogicExpr(lambda vals: not e(vals), e.varNames),
            (cp.charParser('-'), False),
            (cp.whitespaceParser, False),
            (term, True)
        ),
        term
    )
)

term.setParser(
    cp.combine(
        cp.sequence(
            lambda name: LogicExpr.Variable(name),
            (variableName, True)
        ),
        cp.sequence(
            lambda: LogicExpr.Constant(True),
            (cp.charParser('T'), False)
        ),
        cp.sequence(
            lambda: LogicExpr.Constant(False),
            (cp.charParser('F'), False)
        ),
        cp.sequence(
            lambda e: e,
            (cp.whitespaceParser, False),
            (cp.charParser('('), False),
            (expr, True),
            (cp.charParser(')'), False),
            (cp.whitespaceParser, False),
        )
    )
)

variableName.setParser(
    cp.parseWhere(
        lambda token: token not in ("T", "F"),
        cp.token
    )
)