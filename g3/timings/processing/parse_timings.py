import glob
      

def read_data (filename):
    data_all = {}
    coef = 0.0
    with open (filename, "r") as f :
        lines = f.readlines()
        lines = lines[:len(lines)-2]
        random_seed = lines[2].split()[6]
        random_step = lines[2].split()[7]
        for line in lines[9:]:
            check = line.split()
            #print(check)
            exp = check[1]
            coef = float(check[2])/1000000
            data_all[exp] = []
            i = 3
            while i < len(check):
                data_all[exp].append(float(check[i])/coef)
                i = i + 1

    data_SPLITADD = {}
    exp = 1
    while exp < 1024:
        exp = 2*exp
        data_SPLITADD[str(exp)] = []
        relative_to = data_all[str(exp)][0]
        for algo in range(0,6) :
            data_SPLITADD[str(exp)].append(float(((data_all[str(exp)][algo] - relative_to)*100)/relative_to))
    
    data_SPLITDBL = {}
    exp = 1
    while exp < 1024:
        exp = 2*exp
        data_SPLITDBL[str(exp)] = []
        relative_to = data_all[str(exp)][6]
        for algo in range(6, 12) :
            data_SPLITDBL[str(exp)].append(float(((data_all[str(exp)][algo] - relative_to)*100)/relative_to))
    
    return data_all, data_SPLITADD, data_SPLITDBL, random_seed, random_step

def write_data(D1, D2, D3, filename, seed, step) :
    with open (filename, "w") as f :
        f.write ("# --------------------------------------------------------------------------------------------------------\n")
        f.write ("# Raw timings for genus 3 compared to previous best\n")
        f.write ("# Random generator seed: "+ seed + " and step: " + step + "\n")
        f.write ("# Naming convention: first digit: O= ours, P= previous\n")
        f.write ("#                   second digit: X= complete, R= Rad, S= Sutherland, C= Cantor, G= Magma\n")
        f.write ("#                    third digit: A= addition, D= doubling\n")
        f.write ("# fld_bit\t OXA\t OSA\t PSA\t PRA\t PCA\t MGA\t OXD\t OSD\t PSD\t PRD\t PCD\t MGD\n")
        f.write ("# --------------------------------------------------------------------------------------------------------\n")

        exp = 1
        while exp < 1024:
            exp = 2*exp
            f.write (str(exp) + " ")
            for algo in range(0, len(D1[str(exp)])) :
                f.write (str("{:.2f}".format(D1[str(exp)][algo]))+" ")
            f.write ("\n")
        
        f.write("\n")
        f.write("\n")
        f.write ("# ------------------------------------------------------------\n")
        f.write ("# Relative time for addition to our explicit OXA, in percent\n")
        f.write ("# fld_bit\t OXA\t OSA\t PSA\t PRA\t PCA\t MGA\n")
        f.write ("# ------------------------------------------------------------\n")

        exp = 1
        while exp < 1024:
            exp = 2*exp
            f.write ("#  " + str(exp) + "\t\t")
            for algo in range(0, len(D2[str(exp)])) :
                f.write (str("{:.2f}".format(D2[str(exp)][algo]))+"\t")
            f.write ("\n")

        f.write("\n")
        f.write ("# ------------------------------------------------------------\n")
        f.write ("# Relative time for doubling to our explicit OXD, in percent\n")
        f.write ("# fld_bit\t OXD\t OSD\t PSD\t PRD\t PCD\t MGD\n")
        f.write ("# ------------------------------------------------------------\n")

        exp = 1
        while exp < 1024:
            exp = 2*exp
            f.write ("#  " + str(exp) + "\t\t")
            for algo in range(0, len(D3[str(exp)])) :
                f.write (str("{:.2f}".format(D3[str(exp)][algo]))+"\t")
            f.write ("\n")
        



if __name__ == "__main__" :
    for fin in glob.glob("outg3_complete.raw"):
        raw_data, peraddS, perdblS, seed, step = read_data (fin)
        fout = "poutg3_complete.raw"
        write_data (raw_data, peraddS, perdblS, fout,seed,step)

