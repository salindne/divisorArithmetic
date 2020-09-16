import glob
      

def read_data (filename):
    data_all = {}
    coef = 0.0
    with open (filename, "r") as f :
        lines = f.readlines()
        lines = lines[:len(lines)-2]
        random_seed = lines[2].split()[6]
        random_step = lines[2].split()[7]
        for line in lines[10:]:
            check = line.split()
            #print(check)
            exp = check[1]
            coef = float(check[2])/1000000
            data_all[exp] = []
            i = 3
            while i < len(check):
                data_all[exp].append(float(check[i])/coef)
                i = i + 1
    
    data_RAMADD = {}
    exp = 1
    while exp < 1024:
        exp = 2*exp
        data_RAMADD[str(exp)] = []
        relative_to = data_all[str(exp)][0]
        for algo in range(8) :
            data_RAMADD[str(exp)].append(float(((data_all[str(exp)][algo] - relative_to)*100)/relative_to))
    
    data_RAMDBL = {}
    exp = 1
    while exp < 1024:
        exp = 2*exp
        data_RAMDBL[str(exp)] = []
        relative_to = data_all[str(exp)][8]
        for algo in range(8,16) :
            data_RAMDBL[str(exp)].append(float(((data_all[str(exp)][algo] - relative_to)*100)/relative_to))

    data_SPLITADD = {}
    exp = 1
    while exp < 1024:
        exp = 2*exp
        data_SPLITADD[str(exp)] = []
        relative_to = data_all[str(exp)][16]
        for algo in range(16,21) :
            data_SPLITADD[str(exp)].append(float(((data_all[str(exp)][algo] - relative_to)*100)/relative_to))
    
    data_SPLITDBL = {}
    exp = 1
    while exp < 1024:
        exp = 2*exp
        data_SPLITDBL[str(exp)] = []
        relative_to = data_all[str(exp)][21]
        for algo in range(21, 26) :
            data_SPLITDBL[str(exp)].append(float(((data_all[str(exp)][algo] - relative_to)*100)/relative_to))
    
    return data_all, data_RAMADD, data_RAMDBL, data_SPLITADD, data_SPLITDBL, random_seed, random_step

def write_data(D1, D2, D3, D4, D5, filename, seed, step) :
    with open (filename, "w") as f :
        f.write ("# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n")
        f.write ("# Raw timings for genus 2 compared to previous best\n")
        f.write ("# Random generator seed: "+ seed + " and step: " + step + "\n")
        f.write ("# Naming convention: first digit: O= ours, P= previous\n")
        f.write ("#                   second digit: X= complete, L= Lange, G= Costello-Lauter, N= Costello-Lauter No Trades, E= Erickson, C= Cantor, G= Magma\n")
        f.write ("#                    third digit: A= addition, D= doubling\n")
        f.write ("#                   fourth digit: R= Ramified, S= Split\n")
        f.write ("# fld_bit\t OXAR\t OLAR\t PLAR\t OGAR\t PNAR\t PGAR\t PCAR\t MGAR\t OXDR\t OLDR\t PLDR\t OGDR\t PNDR\t PGDR\t PCDR\t MGDR\t OXAS\t OEAS\t PEAS\t PCAS\t MGAS\t OXDS\t OEDS\t PEDS\t PCDS\t MGDS\n")
        f.write ("# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n")

        exp = 1
        while exp < 1024:
            exp = 2*exp
            f.write (str(exp) + " ")
            for algo in range(0, len(D1[str(exp)])) :
                f.write (str("{:.2f}".format(D1[str(exp)][algo]))+" ")
            f.write ("\n")
        
        f.write("\n")
        f.write("\n")
        f.write ("# --------------------------------------------------------------------------------\n")
        f.write ("# Relative time for addition to our explicit OXAR, in percent\n")
        f.write ("# fld_bit\t OXAR\t OLAR\t PLAR\t OGAR\t PNAR\t PGAR\t PCAR\t MGAR\n")
        f.write ("# --------------------------------------------------------------------------------\n")

        exp = 1
        while exp < 1024:
            exp = 2*exp
            f.write ("#  " + str(exp) + "\t\t")
            for algo in range(0, len(D2[str(exp)])) :
                f.write (str("{:.2f}".format(D2[str(exp)][algo]))+"\t")
            f.write ("\n")

        f.write("\n")
        f.write ("# -------------------------------------------------------------------------------\n")
        f.write ("# Relative time for doubling to our explicit OXDR, in percent\n")
        f.write ("# fld_bit\t OXDR\t OLDR\t PLDR\t OGDR\t PNDR\t PGDR\t PCDR\t MGDR\n")
        f.write ("# -------------------------------------------------------------------------------\n")

        exp = 1
        while exp < 1024:
            exp = 2*exp
            f.write ("#  " + str(exp) + "\t\t")
            for algo in range(0, len(D3[str(exp)])) :
                f.write (str("{:.2f}".format(D3[str(exp)][algo]))+"\t")
            f.write ("\n")
        
        f.write("\n")
        f.write("\n")
        f.write ("# --------------------------------------------------------------------------------\n")
        f.write ("# Relative time for addition to our explicit OXAS, in percent\n")
        f.write ("# fld_bit\t OXAS\t OEAS\t PEAS\t PCAS\t MGAS\n")
        f.write ("# --------------------------------------------------------------------------------\n")

        exp = 1
        while exp < 1024:
            exp = 2*exp
            f.write ("#  " + str(exp) + "\t\t")
            for algo in range(0, len(D4[str(exp)])) :
                f.write (str("{:.2f}".format(D4[str(exp)][algo]))+"\t")
            f.write ("\n")

        f.write("\n")
        f.write ("# -------------------------------------------------------------------------------\n")
        f.write ("# Relative time for doubling to our explicit OXDS, in percent\n")
        f.write ("# fld_bit\t OXDS\t OEDS\t PEDS\t PCDS\t MGDS\n")
        f.write ("# -------------------------------------------------------------------------------\n")

        exp = 1
        while exp < 1024:
            exp = 2*exp
            f.write ("#  " + str(exp) + "\t\t")
            for algo in range(0, len(D5[str(exp)])) :
                f.write (str("{:.2f}".format(D5[str(exp)][algo]))+"\t")
            f.write ("\n")



if __name__ == "__main__" :
    for fin in glob.glob("outg2_complete.raw"):
        raw_data, peraddR, perdblR, peraddS, perdblS, seed, step = read_data (fin)
        fout = "poutg2_complete.raw"
        write_data (raw_data, peraddR, perdblR, peraddS, perdblS, fout,seed,step)

