from operator import or_, ne, and_
import CombiParser as cp
from typing import Callable

# expr ::= xorExpr '|' expr | xorExpr 
# xorExpr ::= andExpr '^' xorExpr | andExpr
# andExpr ::= notExpr '&' andExpr | notExpr
# notExpr ::= '-' term | term
# term ::= 'T' | 'F' | '(' expr ')'

expr, xorExpr, andExpr, notExpr, term = cp.Parser(), cp.Parser(), cp.Parser(), cp.Parser(), cp.Parser()

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
        # remove all spaces
        preprocessed = "".join([c for c in rawInput if not c.isspace()])

        return expr.parse(preprocessed)

expr.setParser(
    cp.combine(
        cp.sequence(
            lambda e1, e2: LogicExpr.CombineBinary(e1, e2, or_),
            (xorExpr, True),
            (cp.charParser('|'), False),
            (expr, True)
        ),
        xorExpr
    )
)

xorExpr.setParser(
    cp.combine(
        cp.sequence(
            lambda e1, e2: LogicExpr.CombineBinary(e1, e2, ne),
            (andExpr, True),
            (cp.charParser('^'), False),
            (xorExpr, True)
        ),
        andExpr
    )
)

andExpr.setParser(
    cp.combine(
        cp.sequence(
            lambda e1, e2: LogicExpr.CombineBinary(e1, e2, and_),
            (notExpr, True),
            (cp.charParser('&'), False),
            (andExpr, True)
        ),
        notExpr
    )
)

notExpr.setParser(
    cp.combine(
        cp.sequence(
            lambda e: LogicExpr(lambda vals: not e(vals), e.varNames),
            (cp.charParser('-'), False),
            (term, True)
        ),
        term
    )
)

term.setParser(
    cp.combine(
        cp.sequence(
            lambda name: LogicExpr.Variable(name),
            (cp.parseIf(lambda c: c.isalpha() and c not in ("T", "F")), True)
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
            (cp.charParser('('), False),
            (expr, True),
            (cp.charParser(')'), False)
        )
    )
)