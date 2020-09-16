#Global Raw Code and Latex Properties
####Code setup
CURVE_CONST_TRIGGER = "//Constant"
IGNORED_CONST_TRIGGER = "//Ignore"
COMMENT_TRIGGER = "//"
EMPTY_LINE = r''
FORMULA_START = "function("
FORMULA_END = "end function;"
RETURN = "return"
CHECK_ZERO = "if IsZero"
CHECK_AND = "and"
END_IF = "end if;"
CONSTANT_TABLE = "ccs"
SKIP_LINE = ["PolynomialRing", "Coeff"]
REMOVE_TRIGGER = ['//startIGNORE','//endIGNORE']
MUL_TO_ADD = ["i2"]
DEBUG_TRIGGER = "DEBUG"


EQUALS = ":="
MUL = "*"
SQUARE = "^2"
SUB = "-"
ADD = "+"
DIV2 = "/2"

####Variable generation
OPERANDS = ['=', ';', '+', '*', '(', ')', '^-1', '-', '^2', '/2']
NON_FORMULA_LINES_LEN2 = ["De", "re", "en", "if", "el"]

####Latex
PRIME = 'p'
MUL_VAR = 'M'
CONST_MUL_VAR = 'C'
IGNORED_MUL_VAR = None
SECOND_INPUT = "p"
FORMULA_WIDTH = "340pt"



#PARSING CLASSES
class Variables(object):
    def __init__(self, code):
        self.varDict = {}
        self.varSet = []

        mVars = []
        #goes through code and generates a list of non constant/ignored variables
        for line in code.lines:
            if line[:2] in  NON_FORMULA_LINES_LEN2:
                continue
            elif CONSTANT_TABLE in line and RETURN not in line:
                continue
            else:
                line = line.split(COMMENT_TRIGGER)[0].strip()
                for term in OPERANDS:
                    line = line.replace(term, ' ')
                allVars = line.split()
                for var in allVars:
                    if var in (code.curveConst + code.ignoredConst):
                        continue
                    elif var not in mVars:
                        mVars.append(var)
        
        #generates dictionary with all variables and cost types
        for var in mVars:
            self.varDict[var] = MUL_VAR
        for var in code.curveConst:
            self.varDict[var] = CONST_MUL_VAR
        for var in code.ignoredConst:
            self.varDict[var] = IGNORED_MUL_VAR
        
        self.varSet = mVars + code.curveConst + code.ignoredConst

    def mulType(self, codeVar):
        return self.varDict[codeVar]

    
class Formula(object):
    def __init__(self, algName, inputVars, outputVars, formulaCode, variables):
        self.alg = algName
        self.input = inputVars
        self.output = outputVars
        self.variables = variables

        #terms is all variables and operands for parsing, starting with largest terms
        self.terms = OPERANDS+self.variables.varSet
        self.terms.sort(key = len)
        self.terms.reverse()

        self.lines = []
        self.count = 0
        self.degen = {}
        
        self.__parseCode(formulaCode)

    def __countLine(self, parsedLine):
        #get counts            
        S = 0
        M = 0
        C = 0
        A = 0
        i = 0

        #ignore leading negative sign
        if parsedLine[2] == SUB:
            A = A - 1

        while i < len(parsedLine):
            if parsedLine[i] == SQUARE:
                S = S + 1
            elif parsedLine[i] in [ADD,SUB,DIV2]:
                A = A + 1
            elif parsedLine[i] == MUL:
                
                ignoreFlag = False
                constFlag = False
                addFlag = False
                #check left:
                #if variable then possible constant
                #   if constant than constant mul
                #implicit else, normal mul
                if parsedLine[i-1] in self.variables.varSet:
                    if self.variables.mulType(parsedLine[i-1]) == CONST_MUL_VAR:
                        if parsedLine[i-1] in MUL_TO_ADD:
                            addFlag = True
                        else:
                            constFlag = True
                    elif self.variables.mulType(parsedLine[i-1]) == IGNORED_MUL_VAR:
                        ignoreFlag = True

                #check right:
                #if variable then possible constant
                #   if constant than constant mul
                #implicit else, normal mul
                if parsedLine[i+1] in self.variables.varSet:
                    if self.variables.mulType(parsedLine[i+1]) == CONST_MUL_VAR:
                        if parsedLine[i-1] in MUL_TO_ADD:
                            addFlag = True
                        else:
                            constFlag = True
                    elif self.variables.mulType(parsedLine[i+1]) == IGNORED_MUL_VAR:
                        ignoreFlag = True
                
                if constFlag:
                    C = C + 1
                elif addFlag:
                    A = A + 1
                elif not ignoreFlag:
                    M = M + 1     
            i = i + 1
        return M,S,A,C

        
    def __parseLine(self,line):
        line = line.split(COMMENT_TRIGGER)[0].strip()
        equation = line.split(EQUALS)
        if len(equation) != 2:
            print(equation)
        LHS = equation[0].strip()
        RHS = equation[1].replace(" ", "").replace(';','')
        
        #ignore leading negative sign
        leadingNeg = False
        if RHS[0] == "-":
            temp = RHS[1:]
            leadingNeg = True
        else:
            temp = RHS

        parsedLine = []
        #Traverse code line create parsed line
        while len(temp) > 0:
            for term in self.terms:
                if temp.startswith(term):
                    parsedLine.append(term)
                    temp = temp.replace(term,'',1)

        #bring back negative sign
        if leadingNeg:
            parsedLine.insert(0,'-')
        #bring back LHS
        parsedLine.insert(0,'=')
        parsedLine.insert(0,LHS)
        return parsedLine


    def __parseCode(self, codeLines):

        if CONSTANT_TABLE in self.input:
            self.input.remove(CONSTANT_TABLE)

        self.count = (0,0,0,0)
        degenCases = []
        degenLines = []
        degenCounts = []
        currentDegen = -1
        newLines = []
        
         

        for line in codeLines:
            noSkip = True
            for skip in SKIP_LINE:
                if skip in line:
                    noSkip = False

            if noSkip:
                if CONSTANT_TABLE in line and RETURN not in line:
                        self.input.append(line.split(EQUALS)[0].strip())

                elif CHECK_ZERO in line:
                    currentDegen = currentDegen + 1
                    if CHECK_AND in line:
                        andFlag = True
                        degenCases.append(line.split("(")[1].split(")")[0] + line.split("(")[2].split(")")[0])
                    else:
                        andFlag = False
                        degenCases.append(line.split("(")[1].split(")")[0])
                    degenLines.append([])
                    if currentDegen == 0:
                        degenCounts.append(self.count)
                        self.lines.append(degenCases[currentDegen])
                    else:
                        degenCounts.append(degenCounts[currentDegen - 1])
                        degenLines[currentDegen - 1].append(degenCases[currentDegen])

                elif currentDegen == -1:
                    parsedLine = self.__parseLine(line)
                    count =  self.__countLine(parsedLine)
                    self.lines.append((tuple(parsedLine), count))
                    self.count = tuple(map(sum,zip(self.count,count)))

                elif END_IF+COMMENT_TRIGGER+degenCases[currentDegen] in line:
                    if degenCases[currentDegen - 1] == degenCases[currentDegen]:
                        parent = "main"
                    else:
                        parent = degenCases[currentDegen - 1]
                    outputVar =  degenLines[currentDegen][-1].replace(';', '').replace(' ', '').split(',')
                    outputVar[0] = outputVar[0][-1]
                    del degenLines[currentDegen][-1]
                    self.degen[degenCases[currentDegen]] = (degenLines[currentDegen], outputVar, degenCounts[currentDegen], andFlag, parent)
                    del degenCases[currentDegen]
                    del degenLines[currentDegen]
                    del degenCounts[currentDegen]
                    currentDegen = currentDegen - 1

                elif RETURN in line:
                    degenLines[currentDegen].append(line)

                else:
                    parsedLine = self.__parseLine(line)
                    count =  self.__countLine(parsedLine)
                    degenLines[currentDegen].append((tuple(parsedLine), count))
                    degenCounts[currentDegen] = tuple(map(sum,zip(degenCounts[currentDegen], count)))              
    

    #Prints information about formula, for debuging
    def printFormula(self):
        print(self.alg + '\n')
        print('Input: = ' + str(self.input) + '\n')
        print('Output = ' + str(self.output) + '\n')
        print('Main Lines\n')
        for line in self.lines:
            print(line)
        print(self.count)
        print('\nDegens\n')
        for degen in self.degen.items():
            print('Degen name : ' + degen[0])
            print('Degen lines ')
            if degen[1][0] == []:
                print('[]')
            else:
                for line in degen[1][0]:
                    print(line)
            print('Degen output : ' + str(degen[1][1]))
            print(degen[1][2])
            print("and Flag: " + str(degen[1][3]))
            print("Parent: " + degen[1][4])
            print('\n')


class Code(object):
    def __init__(self, codeLines):
        self.lines = []
        self.curveConst = []
        self.ignoredConst = []        
        self.__setupCode(codeLines)
        self.__remove()

        self.variables = Variables(self)
        
        self.formulas = []
        self.__createFormulas()
        

    #Removes comments, blank lines.
    #Initiates curve constants and ignored constants
    def __setupCode(self, codeLines):
        cleanCode = []
        for line in codeLines:
            line = line.strip()
            if line[:len(CURVE_CONST_TRIGGER)] == CURVE_CONST_TRIGGER:
                self.curveConst = line.split()[1].split(',')
            elif line[:len(IGNORED_CONST_TRIGGER)] == IGNORED_CONST_TRIGGER:
                self.ignoredConst =line.split()[1].split(',')
            elif line[:len(COMMENT_TRIGGER)] == COMMENT_TRIGGER:
                continue
            elif line == EMPTY_LINE:
                continue
            elif DEBUG_TRIGGER in line:
                continue
            else:
                cleanCode.append(line)
        self.lines = cleanCode


    #Creates list of formula objects
    def __createFormulas(self):
        collectAlg = False
        currentAlg = None
        algLines = []
        inputVar = []
        outputVar = []
        for line in self.lines:
            
            if FORMULA_START in line:
                collectAlg = True
                currentAlg = line.split(EQUALS)[0][3:].strip()
                inputVar = line.split('(')[1].split(')')[0].split(',')
            elif FORMULA_END in line and collectAlg:
                outputVar = algLines[-1].split('return')[1].replace(' ', '').replace(';', '').replace('[','').replace(']','').split(',')
                del algLines[-1]
                
                self.formulas.append(Formula(currentAlg, inputVar, outputVar, algLines, self.variables))
                collectAlg = False
                currentAlg = None
                algLines = []
                inputVar = []
                outputVar = []
            elif collectAlg:
                algLines.append(line)
    
    #Remove code within if statements that are not wanted in tables, 
    #Removes line with trigger start/end and everything in between
    def __remove(self):
        remove = False
        newCode = []
        for line in self.lines:
            if REMOVE_TRIGGER[0] in line:
                remove = True
            elif REMOVE_TRIGGER[1] in line and remove:
                remove = False
            elif remove:
                continue
            else:
                newCode.append(line)
        self.lines = newCode
    
    def getFormula(self, algName):
        for formula in self.formulas:
            if formula.alg == algName:
                return formula
    
    #Prints cost summary of formulas
    def printCosts(self):
        for formula in self.formulas:
            if len(formula.alg) == 8 :
                print(formula.alg + str(formula.count) )
            else:
                print(formula.alg + '\t' + str(formula.count) )


# LATEX GENERATION CLASSES
class Table(object):
    def __init__(self, formula, width, ignoreVar):
        self.formula = formula
        self.tableWidth = width
        self.latex = []

        #Formats divisor input
        noConstInput = [x for x in formula.input if x not in ignoreVar]
        d2Input = filter(lambda x: SECOND_INPUT in x, noConstInput)
        d1Input = [x for x in noConstInput if x not in set(d2Input)]

        tex1Input = "D = ["
        for variable in d1Input:
            if tex1Input == "D = [":
                tex1Input = tex1Input + self.var(variable)
            else:
                tex1Input = tex1Input + "," + self.var(variable)
        tex1Input = tex1Input + "], "
        tex2Input = ''

        if 'ADD' in formula.alg:
            tex2Input = "D' = ["
            for variable in d2Input:
                if tex2Input == "D' = [":
                    tex2Input = tex2Input + self.var(variable)
                else:
                    tex2Input = tex2Input + "," + self.var(variable)
            tex2Input = tex2Input + "]"
        divisorInput = tex1Input + tex2Input

        #Sets Up Table Latex
        self.latex.append('\\begin{tabular}{|c|cr|c|c|c|c|}' + '\n')
        self.latex.append('\\hline'+ '\n')
        self.latex.append('\\multicolumn{7}{|c|}{\\bf{'+formula.alg+'}} \\TS \\\\'+ '\n')
        self.latex.append('\\hline'+ '\n')
        self.latex.append('\\bf{IN:} &\\multicolumn{2}{|c|}{$'+divisorInput+'$}' + '\n')
        self.latex.append('\\TS & M & \\hspace{1pt}S\\hspace{1pt} & A & \\hspace{1pt}C\\hspace{1pt} \\\\' + '\n')
        self.latex.append('\\hline'+ '\n')


        lineLength = 0
        count = (0,0,0,0)
        dSpecial = []
        special = []

        caseCount = 1
        dCaseCount = 1
        latex = '\\multicolumn{3}{|R{' + FORMULA_WIDTH + '}|}{ \n'
        for line in formula.lines:
            
            if type(line) is str:
                M,S,A,C = self.prepLineCount(count)            
                latex = latex + '} & ' + M + ' & ' + S + ' & ' + A + ' & ' + C + '\\\\' + '\n'
                self.latex.append(latex)
                lineLength = 0
                count = (0,0,0,0)
                
                if line == "d":
                    dSpecial.append((line,dCaseCount))
                    self.latex.append('\\multicolumn{3}{|l|}{ \n \\bf{If $' + self.var(line) + ' = 0$ go to Special GCD Case ' + str(caseCount) + ', else:} } &  &  &  & \\\\' + '\n')
                else:
                    special.append((line,caseCount))
                    self.latex.append('\\multicolumn{3}{|l|}{ \n \\bf{If $' + self.var(line) + ' = 0$ go to Special Output Case ' + str(caseCount) + ', else:} } &  &  &  & \\\\' + '\n')
                    caseCount += 1

                latex = '\\multicolumn{3}{|R{' + FORMULA_WIDTH + '}|}{ \n'

            else:
                if lineLength + self.length(line) > self.tableWidth:
                    M,S,A,C = self.prepLineCount(count)            
                    latex = latex + '} & ' + M + ' & ' + S + ' & ' + A + ' & ' + C + '\\\\' + '\n'
                    self.latex.append(latex)
                    lineLength = 0
                    count = (0,0,0,0)
                    latex = '\\multicolumn{3}{|R{' + FORMULA_WIDTH + '}|}{ \n'

                latex = latex + '$'
                for term in line[0]:
                    if term in OPERANDS:
                        latex = latex + self.operand(term)
                    else:
                        latex = latex + self.var(term)
                latex = latex + '$;\\hspace{4pt}\n'
                lineLength = lineLength + self.length(line)
                count = tuple(map(sum,zip(count,line[1])))

                if line == formula.lines[-1]:
                    M,S,A,C = self.prepLineCount(count)            
                    latex = latex + '} & ' + M + ' & ' + S + ' & ' + A + ' & ' + C + '\\\\' + '\n'
                    self.latex.append(latex)


        M,S,A,C = self.prepLineCount(formula.count)
        self.latex.append('\\hline'+ '\n')
        
        out = "["
        for variable in formula.output[1:]:                        
            if out == "[":
                out = out + self.var(variable)
            else:
                out = out + "," + self.var(variable)
        out = out + "]"

        if 'ADD' in formula.alg:
            self.latex.append('\\bf{OUT:} & \\hspace*{65pt} $D + D\' = D\'\' = '+out+'$'+ '\n')
        else:
            self.latex.append('\\bf{OUT:} & \\hspace*{65pt} $2D = D\'\' = '+out+'$'+ '\n')
        self.latex.append('\\TS & Total: & ' + M + ' & ' + S + ' & ' + A + ' & ' + C + ' \\\\'+ '\n')
        self.latex.append('\\hline'+ '\n')
        self.latex.append('\\hline'+ '\n')
        
        #Special Output Cases first
        for spCase in special:
            self.recurseSpecial(spCase, "Output")
            
        #Special GCD Cases after
        for spCase in dSpecial:
            self.recurseSpecial(spCase, "GCD")
            
        self.latex.append('\\end{tabular}' + '\n\n\n')


    def recurseSpecial(self, case, caseType):
        self.latex.append('\\multicolumn{3}{|c|}{Special '+ caseType +' Case ' + str(case[1])+': $' + self.var(case[0])+' = 0$} \\TS & M & \\hspace{1pt}S\\hspace{1pt} & A & \\hspace{1pt}C\\hspace{1pt} \\\\' + '\n')

        if self.formula.degen[case[0]][0] != []:
            self.latex.append('\\hline'+ '\n')
        


        lineLength = 0
        count = (0,0,0,0)
        special = []
        caseCount = 1

        latex = '\\multicolumn{3}{|R{' + FORMULA_WIDTH + '}|}{ \n'
        for line in self.formula.degen[case[0]][0]:
            
            if type(line) is str:
                M,S,A,C = self.prepLineCount(count)            
                latex = latex + '} & ' + M + ' & ' + S + ' & ' + A + ' & ' + C + '\\\\' + '\n'
                self.latex.append(latex)
                lineLength = 0
                count = (0,0,0,0)

                special.append((line,str(case[1])+'.'+str(caseCount)))
                self.latex.append('\\multicolumn{3}{|l|}{ \n \\bf{If $' + self.var(line) + ' = 0$ go to Special '+ caseType +' Case ' + str(case[1])+'.'+str(caseCount) + ', else:} } &  &  &  & \\\\' + '\n')
                caseCount += 1
                latex = '\\multicolumn{3}{|R{' + FORMULA_WIDTH + '}|}{ \n'

            else:
                if lineLength + self.length(line) > self.tableWidth:
                    M,S,A,C = self.prepLineCount(count)            
                    latex = latex + '} & ' + M + ' & ' + S + ' & ' + A + ' & ' + C + '\\\\' + '\n'
                    self.latex.append(latex)
                    lineLength = 0
                    count = (0,0,0,0)
                    latex = '\\multicolumn{3}{|R{' + FORMULA_WIDTH + '}|}{ \n'

                latex = latex + '$'
                for term in line[0]:
                    if term in OPERANDS:
                        latex = latex + self.operand(term)
                    else:
                        latex = latex + self.var(term)
                latex = latex + '$;\\hspace{4pt}\n'
                lineLength = lineLength + self.length(line)
                count = tuple(map(sum,zip(count,line[1])))

                if line == self.formula.degen[case[0]][0][-1]:
                    M,S,A,C = self.prepLineCount(count)            
                    latex = latex + '} & ' + M + ' & ' + S + ' & ' + A + ' & ' + C + '\\\\' + '\n'
                    self.latex.append(latex)

        M,S,A,C = self.prepLineCount(self.formula.degen[case[0]][2])
        self.latex.append('\\hline'+ '\n')
        
        out = "["
        for variable in self.formula.degen[case[0]][1][1:]:                        
            if out == "[":
                out = out + self.var(variable)
            else:
                out = out + "," + self.var(variable)
        out = out + "]"

        if 'ADD' in self.formula.alg:
            self.latex.append('\\bf{OUT:} & \\hspace*{65pt} $D + D\' = D\'\' = '+out+'$'+ '\n')
        else:
            self.latex.append('\\bf{OUT:} & \\hspace*{65pt} $2D = D\'\' = '+out+'$'+ '\n')
        self.latex.append('\\TS & Total: & ' + M + ' & ' + S + ' & ' + A + ' & ' + C + ' \\\\'+ '\n')
        self.latex.append('\\hline'+ '\n')
        self.latex.append('\\hline'+ '\n')

        for spCase in special:
            self.recurseSpecial(spCase, caseType)


    #Eyeballin it
    def length(self, line):
        length = 0
        for term in line[0]:
            if term in ["^-1", "^2"]:
                length = length + 1
            elif term in ["+", "-", "="]:
                length = length + 2
            elif 'p' in term:
                length = length + 2
            else:
                length = length + len(term)
        return length +3

    def prepLineCount(self, count):
        if count[0] == 0:
            M = ''
        else:
            M = str(count[0])
        if count[1] == 0:
            S = ''
        else:
            S = str(count[1])
        if count[2] == 0:
            A = ''
        else:
            A = str(count[2])
        if count[3] == 0:
            C = ''
        else:
            C = str(count[3])
        return M,S,A,C

    def var(self, codeVar):
        prevDigit = False
        latex = ''
        if codeVar.isdigit():
            return codeVar
        for char in codeVar:
            if char == PRIME:
                prevDigit = False
                j = len(latex)
                if 'prime' == latex[j-6:j-1]:
                    latex = latex[:j-1] + '\\prime' + latex[j-1:]
                else:
                    latex = latex + '^{\\prime}'
            elif char.isalpha():
                prevDigit = False
                latex = latex + char
            elif char.isdigit():
                if not prevDigit:
                    latex = latex + '_{' + char + '}'
                else:
                    latex = latex.rstrip('}') + char + '}'
                prevDigit = True
        return latex

    def operand(self, codeOp):
        if codeOp[0] == '^':
            return '{}^{'+codeOp[1:]+'}'
        elif codeOp == '*':
            return ' \cdot '
        else:
            return codeOp

      
class Latex(object):
    def __init__(self, code, width, outFileName):
        open(outFileName + ".tex", 'w').close()
        for formula in code.formulas:
            with open(outFileName + ".tex", "a") as out:
                out.writelines(Table(formula, width, set(code.curveConst + code.ignoredConst)).latex)
    

    


####MAIN#####
#G2#
#Ramified Formulas
'''
ramArbDBL = Code(open('../g2/ramifiedModel/g2Formulas/arb_ramifiedG2_DBL.mag', 'r'))
#ramArbDBL.getFormula('1DBL').printFormula()
#ramArbDBL.getFormula('2DBL').printFormula()
#Latex(ramArbDBL,70,"ram_arb_DBL")

ramArbADD = Code(open('../g2/ramifiedModel/g2Formulas/arb_ramifiedG2_ADD.mag', 'r'))
#ramArbADD.getFormula('1ADD').printFormula()
#ramArbADD.getFormula('12ADD').printFormula()
#ramArbADD.getFormula('2ADD').printFormula()
#Latex(ramArbADD,58,"ram_arb_ADD")

ramCh2DBL = Code(open('../g2/ramifiedModel/g2Formulas/ch2_ramifiedG2_DBL.mag', 'r'))
#ramCh2DBL.getFormula('1DBL').printFormula()
#ramCh2DBL.getFormula('2DBL').printFormula()
#Latex(ramCh2DBL,24,"ram_ch2_DBL")

ramCh2ADD = Code(open('../g2/ramifiedModel/g2Formulas/ch2_ramifiedG2_ADD.mag', 'r'))
#ramCh2ADD.getFormula('1ADD').printFormula()
#ramCh2ADD.getFormula('12ADD').printFormula()
#ramCh2ADD.getFormula('2ADD').printFormula()
#Latex(ramCh2ADD,24,"ram_ch2_ADD")

ramNch2DBL = Code(open('../g2/ramifiedModel/g2Formulas/nch2_ramifiedG2_DBL.mag', 'r'))
#ramNch2DBL.getFormula('1DBL').printFormula()
#ramNch2DBL.getFormula('2DBL').printFormula()
#Latex(ramNch2DBL,24,"ram_nch2_DBL")

ramNch2ADD = Code(open('../g2/ramifiedModel/g2Formulas/nch2_ramifiedG2_ADD.mag', 'r'))
#ramNch2ADD.getFormula('1ADD').printFormula()
#ramNch2ADD.getFormula('12ADD').printFormula()
#ramNch2ADD.getFormula('2ADD').printFormula()
#Latex(ramNch2ADD,24,"ram_nch2_ADD")



#Split Formulas
splitArbPRE = Code(open('../g2/splitModel/g2Formulas/arb_splitG2_UTL.mag', 'r'))
#splitArbPRE.getFormula('compute').printFormula()

splitArbDBL = Code(open('../g2/splitModel/g2Formulas/arb_splitG2_DBL.mag', 'r'))
#splitArbDBL.getFormula('1DBLDWN').printFormula()
#splitArbDBL.getFormula('1DBLUP').printFormula()
#splitArbDBL.getFormula('2DBL').printFormula()

splitArbADD = Code(open('../g2/splitModel/g2Formulas/arb_splitG2_ADD.mag', 'r'))
#splitArbADD.getFormula('01ADDDWN').printFormula()
#splitArbADD.getFormula('01ADDUP').printFormula()
#splitArbADD.getFormula('02ADDDWN').printFormula()
#splitArbADD.getFormula('02ADDUP').printFormula()
#splitArbADD.getFormula('1ADD').printFormula()
#splitArbADD.getFormula('1ADDDWN').printFormula()
#splitArbADD.getFormula('1ADDUP').printFormula()
#splitArbADD.getFormula('12ADD').printFormula()
#splitArbADD.getFormula('12ADDUP').printFormula()
#splitArbADD.getFormula('2ADD').printFormula()

splitCh2PRE = Code(open('../g2/splitModel/g2Formulas/ch2_splitG2_UTL.mag', 'r'))
#splitCh2PRE.getFormula('compute').printFormula()

splitCh2DBL = Code(open('../g2/splitModel/g2Formulas/ch2_splitG2_DBL.mag', 'r'))
#splitCh2DBL.getFormula('1DBLDWN').printFormula()
#splitCh2DBL.getFormula('1DBLUP').printFormula()
#splitCh2DBL.getFormula('2DBL').printFormula()

splitCh2ADD = Code(open('../g2/splitModel/g2Formulas/ch2_splitG2_ADD.mag', 'r'))
#splitCh2ADD.getFormula('01ADDDWN').printFormula()
#splitCh2ADD.getFormula('01ADDUP').printFormula()
#splitCh2ADD.getFormula('02ADDDWN').printFormula()
#splitCh2ADD.getFormula('02ADDUP').printFormula()
#splitCh2ADD.getFormula('1ADD').printFormula()
#splitCh2ADD.getFormula('1ADDDWN').printFormula()
#splitCh2ADD.getFormula('1ADDUP').printFormula()
#splitCh2ADD.getFormula('12ADD').printFormula()
#splitCh2ADD.getFormula('12ADDUP').printFormula()
#splitCh2ADD.getFormula('2ADD').printFormula()

splitNch2PRE = Code(open('../g2/splitModel/g2Formulas/nch2_splitG2_UTL.mag', 'r'))
#splitCh2PRE.getFormula('compute').printFormula()

splitNch2DBL = Code(open('../g2/splitModel/g2Formulas/nch2_splitG2_DBL.mag', 'r'))
#splitNch2DBL.getFormula('1DBLDWN').printFormula()
#splitNch2DBL.getFormula('1DBLUP').printFormula()
#splitNch2DBL.getFormula('2DBL').printFormula()

splitNch2ADD = Code(open('../g2/splitModel/g2Formulas/nch2_splitG2_ADD.mag', 'r'))
#splitNch2ADD.getFormula('01ADDDWN').printFormula()
#splitNch2ADD.getFormula('01ADDUP').printFormula()
#splitNch2ADD.getFormula('02ADDDWN').printFormula()
#splitNch2ADD.getFormula('02ADDUP').printFormula()
#splitNch2ADD.getFormula('1ADD').printFormula()
#splitNch2ADD.getFormula('1ADDDWN').printFormula()
#splitNch2ADD.getFormula('1ADDUP').printFormula()
#splitNch2ADD.getFormula('12ADD').printFormula()
#splitNch2ADD.getFormula('12ADDUP').printFormula()
#splitNch2ADD.getFormula('2ADD').printFormula()


#print('Arb')
#splitArbDBL.printCosts()
#splitArbADD.printCosts()
#print('\nNch2')
#splitNch2DBL.printCosts()
#splitNch2ADD.printCosts()
#print('\nCh2')
#splitCh2DBL.printCosts()
#splitCh2ADD.printCosts()

#Generate Tables
#Latex(splitArbPRE,60,"split_PRE")
#Latex(ramArbDBL,58,"ram_DBL")
#Latex(ramArbADD,60,"ram_ADD")

'''

#G3#
#splitArbPRE = Code(open('../g3/splitModel/g3Formulas/arb_splitG3_UTL.mag', 'r'))
#splitArbPRE.getFormula('compute').printFormula()

splitArbDBL = Code(open('../g3/splitModel/g3Formulas/arb_splitG3_DBL.mag', 'r'))
#splitArbDBL.getFormula('1DBL').printFormula()
#splitArbDBL.getFormula('1DBLDWN').printFormula()
#splitArbDBL.getFormula('1DBLUP2').printFormula()
#splitArbDBL.getFormula('2DBL').printFormula()
#splitArbDBL.getFormula('2DBLUP2').printFormula()
#splitArbDBL.getFormula('3DBL').printFormula()

splitArbADD = Code(open('../g3/splitModel/g3Formulas/arb_splitG3_ADD.mag', 'r'))
#splitArbADD.getFormula('01ADDDWN').printFormula()
#splitArbADD.getFormula('01ADDUP2').printFormula()
#splitArbADD.getFormula('02ADDDWN').printFormula()
#splitArbADD.getFormula('02ADDUP').printFormula()
#splitArbADD.getFormula('1ADD').printFormula()
#splitArbADD.getFormula('1ADDDWN').printFormula()
#splitArbADD.getFormula('1ADDUP').printFormula()
#splitArbADD.getFormula('12ADD').printFormula()
#splitArbADD.getFormula('12ADDUP').printFormula()
#splitArbADD.getFormula('2ADD').printFormula()

#splitCh2PRE = Code(open('../g2/splitModel/g2Formulas/ch2_splitG2_UTL.mag', 'r'))
#splitCh2PRE.getFormula('compute').printFormula()

splitCh2DBL = Code(open('../g3/splitModel/g3Formulas/ch2_splitG3_DBL.mag', 'r'))
#splitCh2DBL.getFormula('1DBLDWN').printFormula()
#splitCh2DBL.getFormula('1DBLUP').printFormula()
#splitCh2DBL.getFormula('2DBL').printFormula()

splitCh2ADD = Code(open('../g3/splitModel/g3Formulas/ch2_splitG3_ADD.mag', 'r'))
#splitCh2ADD.getFormula('01ADDDWN').printFormula()
#splitCh2ADD.getFormula('01ADDUP2').printFormula()
#splitCh2ADD.getFormula('02ADDDWN').printFormula()
#splitCh2ADD.getFormula('02ADDUP').printFormula()
#splitCh2ADD.getFormula('1ADD').printFormula()
#splitCh2ADD.getFormula('1ADDDWN').printFormula()
#splitCh2ADD.getFormula('1ADDUP').printFormula()
#splitCh2ADD.getFormula('12ADD').printFormula()
#splitCh2ADD.getFormula('12ADDUP').printFormula()
#splitCh2ADD.getFormula('2ADD').printFormula()

#splitNch2PRE = Code(open('../g2/splitModel/g2Formulas/nch2_splitG2_UTL.mag', 'r'))
#splitCh2PRE.getFormula('compute').printFormula()

splitNch2DBL = Code(open('../g3/splitModel/g3Formulas/nch2_splitG3_DBL.mag', 'r'))
#splitNch2DBL.getFormula('1DBLDWN').printFormula()
#splitNch2DBL.getFormula('1DBLUP').printFormula()
#splitNch2DBL.getFormula('2DBL').printFormula()

splitNch2ADD = Code(open('../g3/splitModel/g3Formulas/nch2_splitG3_ADD.mag', 'r'))
#splitNch2ADD.getFormula('01ADDDWN').printFormula()
#splitNch2ADD.getFormula('01ADDUP').printFormula()
#splitNch2ADD.getFormula('02ADDDWN').printFormula()
#splitNch2ADD.getFormula('02ADDUP').printFormula()
#splitNch2ADD.getFormula('1ADD').printFormula()
#splitNch2ADD.getFormula('1ADDDWN').printFormula()
#splitNch2ADD.getFormula('1ADDUP').printFormula()
#splitNch2ADD.getFormula('12ADD').printFormula()
#splitNch2ADD.getFormula('12ADDUP').printFormula()
#splitNch2ADD.getFormula('2ADD').printFormula()

#print('Arb')
#splitArbDBL.printCosts()
#splitArbADD.printCosts()
print('\nNch2')
splitNch2DBL.printCosts()
splitNch2ADD.printCosts()
print('\nCh2')
splitCh2DBL.printCosts()
splitCh2ADD.printCosts()

#Generate Tables
#Latex(splitArbPRE,60,"split_PRE")
#Latex(ramArbDBL,58,"ram_DBL")
#Latex(ramArbADD,60,"ram_ADD")
