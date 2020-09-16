import os, signal, sys
from subprocess import Popen
from time import sleep

#fieldType = arb, ch2, nch2
#curveType = ramified, split
#genus     = integer greater than 1
#tagDigit  = (DBL_DEBUG digits, ADD_DEBUG digits)
class FileInfo(object):
    def __init__(self,fieldType, curveType, genus):
        self.PATH = "../g" + genus + "/" + curveType + "Model/" + "negReduced/"
        self.GEN = "genFiles/" + fieldType + "_" + curveType + "G" + genus + "_WB_gen.mag"
        self.ADD = "g" + genus + "Formulas/" + fieldType + "_" + curveType + "G" + genus + "_ADD.mag"
        self.DBL = "g" + genus + "Formulas/" + fieldType + "_" + curveType + "G" + genus + "_DBL.mag"
        self.UTL = "g" + genus + "Formulas/" + fieldType + "_" + curveType + "G" + genus + "_UTL.mag"
        self.LOG = "logs/" + fieldType + "_" + curveType + "G" + genus + "_log.txt"
        self.OUT = "testerFiles/" + fieldType + "_" + curveType + "G" + str(genus) + "_whiteBox_tester.mag"
        self.GENUS = genus
        self.FIELD = fieldType;    
        
        if curveType == "split":
            self.split = True
        else:
            self.split = False

        self.dblNum = 0
        #Counts DBL cases
        f = open(self.PATH + self.DBL, "r")        
        raw = f.readlines()

        for line in raw:
            if "DBL_DEBUG" in line:
                self.dblNum = self.dblNum + 1
        f.close()
        self.dblTag = "{0:0=" + str(len(str(self.dblNum))) + "d}"


        self.addNum = 0
        #Counts ADD cases
        f = open(self.PATH + self.ADD, "r")        
        raw = f.readlines()

        for line in raw:
            if "ADD_DEBUG" in line:
                self.addNum = self.addNum + 1
        f.close()
        self.addTag = "{0:0=" + str(len(str(self.addNum))) + "d}"    



class CaseGen(object):
    def __init__(self, fileInfo):
        self.file = fileInfo
        self.secondInterval = 10
        
        

    def generateCases(self, DBLCases=[], ADDCases=[]):
        cases = {}

        if DBLCases == []:
            i = 0
            while i < self.file.dblNum:
                DBLCases.append("DBL" + self.file.dblTag.format(i))
                i = i+1

        
        if ADDCases == []:
            i = 0
            while i < self.file.addNum:
                ADDCases.append("ADD" + self.file.addTag.format(i))
                i = i+1


        #Reset log file to empty
        f = open(self.file.LOG, "w+")
        f.truncate(0)                               
        f.close() 

        #Start process for magma asynchronously
        magmaProcess = Popen(["magma", self.file.GEN])
        sleep(1)

        #Magma annoyingly takes a variable amount of time to load
        loadingMagma = True
        while loadingMagma:
            sleep(1)
            os.kill(magmaProcess.pid, signal.SIGSTOP) #pauses process
            f = open(self.file.LOG, "r")

            if f.readline().strip() == "Loaded ...":
                print("Loaded ...")
                loadingMagma = False

            f.close()    
            os.kill(magmaProcess.pid, signal.SIGCONT)   #resumes process

        #Keep while loop going until all cases are hit
        testing = True
        while testing:
            sleep(self.secondInterval) #delay for 10 sec intervals
            os.kill(magmaProcess.pid, signal.SIGSTOP) #pauses process
            
            #Open log file, seconds of accumulated trial cases
            f = open(self.file.LOG, "r+")        
            raw = f.readlines()
            processingCase = False
            current = []

            for line in raw:
                if "failed" in line:
                    magmaProcess.terminate()
                    print("Testing Failed!!!\n")
                    testing = False
                if "@B" in line:
                    processingCase = True
                elif processingCase and "@E" in line:
                    processingCase = False
                    if current[0] in ADDCases:
                        if self.file.split:
                            cases[current[0]] = (current[1],[current[2],current[3],current[4],current[5]],[current[6].replace(' ','').replace('<','').replace('>','').split(','),current[7].replace(' ','').replace('<','').replace('>','').split(',')],current[8])
                        else:
                            cases[current[0]] = (current[1],[current[2],current[3]],[current[4].replace(' ','').replace('<','').replace('>','').split(','),current[5].replace(' ','').replace('<','').replace('>','').split(',')],current[6])
                        ADDCases.remove(current[0])
                    elif current[0] in DBLCases:
                        
                        if self.file.split:
                            cases[current[0]] = (current[1],[current[2],current[3],current[4],current[5]],[current[6].replace(' ','').replace('<','').replace('>','').split(',')],current[8])
                        else:
                            
                            cases[current[0]] = (current[1],[current[2],current[3]],[current[4].replace(' ','').replace('<','').replace('>','').split(',')],current[6])
                        DBLCases.remove(current[0])
                    current = []
                elif processingCase:
                    current.append(line.strip())
                else:
                    continue

            print(DBLCases)
            print(ADDCases)
            f.truncate(0)
            f.close()


            if len(DBLCases) == 0 and len(ADDCases) == 0:          
                magmaProcess.terminate()
                print("Testing complete. All cases computed. \n")
                testing = False
            else:
                os.kill(magmaProcess.pid, signal.SIGCONT)   #Resumes process

        os.remove(self.file.LOG)
        return cases     
    
    def getDBLNum(self):
        return self.dblNum
    
    def getADDNum(self):
        return self.addNum


class Magma(object):
    def __init__(self, fileInfo, cases):
        self.file = fileInfo
        self.magma = []
        self.cases = cases
        self.generateCode()
        self.makeFile()
        

    def generateCase(self, case):
        g = int(self.file.GENUS)

        self.magma.append('FF := GF(' + case[1][0] + ');\n')
        self.magma.append('R<x>:=PolynomialRing(FF);\n')
        self.magma.append('f:= R! ' + case[1][1][0] + ';\n')
        self.magma.append('h:= R! ' + case[1][1][1] + ';\n')

        if self.file.split:
            self.magma.append('V:= R! ' + case[1][1][2] + ';\n')
            self.magma.append('Vn:= -V - h;\n')
            self.magma.append('ccs:= Precompute(f,h,' + case[1][0] + ');\n')
            self.magma.append('\n')

            
            returned = 'un' + str(g)
            polyU = 'un' + str(g) +'*x^' + str(g)
            #if (g % 2) == 1:
            polyV = 'Coeff(Vn,' + str(g+1) + ')*x^' + str(g+1) + ' + Coeff(Vn,' + str(g) + ')*x^' + str(g)
            #else:
            #    polyV = 'Coeff(V,' + str(g+1) + ')*x^' + str(g+1) + ' + Coeff(V,' + str(g) + ')*x^' + str(g)
                
            

            i= g - 1
            while i >= 0:
                returned = returned + ',un' + str(i)
                polyU = polyU + ' + un' + str(i) +'*x^' + str(i)
                i = i-1
            
            i= g - 1
            while i >= 0:
                returned = returned + ',vn' + str(i)
                polyV = polyV + ' + vn' + str(i) +'*x^' + str(i)
                i = i-1




            if 'DBL' in case[0]:
                self.magma.append('U1 := R! ' + case[1][2][0][0] + ';\n')
                self.magma.append('V1 := R! ' + case[1][2][0][1] + ';\n')
                self.magma.append('N1 := ' + case[1][2][0][3] + ';\n')
                self.magma.append('D1 := <U1, V1, ExactQuotient(f - V1*(V1 + h),U1), N1>;\n')
                self.magma.append(returned + ',nN := DBL(U1,V1,N1,ccs);\n')
                self.magma.append('nU:= R! ' + polyU + ';\n')
                self.magma.append('nV:= R! ' + polyV + ';\n')

                #if (g % 2) == 1:
                self.magma.append('Cantor:= Double_SPLIT_NEG(D1,f,h,Vn,'+ str(g) +');\n')
                #else:
                #    self.magma.append('Cantor:= Double_SPLIT_NEG(D1,f,h,V,2);\n')

                self.magma.append('assert <nU, nV, ExactQuotient(f - nV*(nV + h),nU), nN> eq Cantor;\n\n')

                

            else:
                self.magma.append('U1 := R! ' + case[1][2][0][0] + ';\n')
                self.magma.append('V1 := R! ' + case[1][2][0][1] + ';\n')
                self.magma.append('N1 := ' + case[1][2][0][3] + ';\n')
                self.magma.append('U2 := R! ' + case[1][2][1][0] + ';\n')
                self.magma.append('V2 := R! ' + case[1][2][1][1] + ';\n')
                self.magma.append('N2 := ' + case[1][2][1][3] + ';\n')
                self.magma.append('D1 := <U1, V1, ExactQuotient(f - V1*(V1 + h),U1), N1>;\n')

                self.magma.append('D2 := <U2, V2, ExactQuotient(f - V2*(V2 + h),U2), N2>;\n')

                self.magma.append(returned + ', nN := ADD(U1,V1,N1,U2,V2,N2,ccs);\n')
                self.magma.append('nU:= R! ' + polyU + ';\n')
                self.magma.append('nV:= R! ' + polyV + ';\n')
                
                #if (g % 2) == 1:
                self.magma.append('Cantor:= Add_SPLIT_NEG(D1,D2,f,h,Vn,'+ str(g) +');\n')
                #else:    
                #    self.magma.append('Cantor:= Add_SPLIT_NEG(D1,D2,f,h,V,2);\n')

                self.magma.append('assert <nU,nV,ExactQuotient(f - nV*(nV + h),nU), nN> eq Cantor;\n\n')



        else:
            self.magma.append('C:= HyperellipticCurve(f,h);\n')
            self.magma.append('J:= Jacobian(C);\n')
            self.magma.append('\n')
            
            returned = 'un' + str(g)
            polyU = 'un' + str(g) +'*x^' +str(g)

            i = g - 1
            while i >= 0:
                returned = returned + ',un' + str(i)
                polyU = polyU + ' + un' + str(i) +'*x^' + str(i)
                i = i-1
            
            i = g - 1
            polyV = 'vn' + str(i) +'*x^' + str(i)
            returned = returned + ',vn' + str(i)

            i = i-1
            while i >= 0:
                returned = returned + ',vn' + str(i)
                polyV = polyV + ' + vn' + str(i) +'*x^' + str(i)
                i = i-1




            if 'DBL' in case[0]:
                self.magma.append('U1 := R!' + case[1][2][0][0] + ';\n')
                self.magma.append('V1 := R!' + case[1][2][0][1] + ';\n')
                self.magma.append('D1 := J![U1,V1];\n')

                if self.file.FIELD == "nch2":
                    self.magma.append(returned + ' := DBL(U1,V1,f);\n')
                else:
                    self.magma.append(returned + ' := DBL(U1,V1,f,h);\n')

                self.magma.append('nU:= R! ' + polyU + ';\n')
                self.magma.append('nV:= R! ' + polyV + ';\n')
                self.magma.append('Cantor:= 2*D1;\n')
                self.magma.append('assert (' + polyU + ') eq Cantor[1] and (' + polyV + ') eq Cantor[2];\n')
                self.magma.append('\n\n')
                

            else:
                self.magma.append('U1 := R!' + case[1][2][0][0] + ';\n')
                self.magma.append('V1 := R!' + case[1][2][0][1] + ';\n')
                self.magma.append('U2 := R!' + case[1][2][1][0] + ';\n')
                self.magma.append('V2 := R!' + case[1][2][1][1] + ';\n')
                self.magma.append('D1 := J![U1,V1];\n')
                self.magma.append('D2 := J![U2,V2];\n')

                if self.file.FIELD == "nch2":
                    self.magma.append(returned + ' := ADD(U1,V1,U2,V2,f);\n')
                else:
                    self.magma.append(returned + ' := ADD(U1,V1,U2,V2,f,h);\n')
                
                self.magma.append('nU:= R! ' + polyU + ';\n')
                self.magma.append('nV:= R! ' + polyV + ';\n')
                self.magma.append('Cantor:= D1 + D2;\n')
                self.magma.append('assert (' + polyU + ') eq Cantor[1] and (' + polyV + ') eq Cantor[2];\n')
                self.magma.append('\n\n')


    def generateCode(self):
        self.magma.append('ADD_DEBUG := true;\n')
        self.magma.append('DBL_DEBUG := true;\n')

        if self.file.split:
            self.magma.append('UTL_DEBUG := false;\n')
            self.magma.append('load "reduced_basis_arithmetic.mag";\n')
            self.magma.append('load "' + self.file.UTL + '";\n')
        else:
            self.magma.append('load "ramifiedUtilities.mag";\n')

        self.magma.append('load "' + self.file.DBL + '";\n')
        self.magma.append('load "' + self.file.ADD + '";\n')
        self.magma.append('"";' + '\n\n')

        totalCases = 0
        for case in self.cases.items():
            totalCases = totalCases + 1
            self.generateCase(case)

        self.magma.append('"\nTotal Cases: ' + str(totalCases) +'";\n')
        self.magma.append("quit;")
        



    def makeFile(self):
        with open(self.file.OUT, 'w+') as out:
            out.writelines(self.magma)



#MAIN
        

#Instantiate case generation object
fileInfo = FileInfo("nch2","split","2")
gen = CaseGen(fileInfo)

#Generate cases
cases = gen.generateCases()

#Create Magma file
Magma(fileInfo, cases)