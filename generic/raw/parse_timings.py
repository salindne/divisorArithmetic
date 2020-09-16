import glob
import re

       

def read_data (filename):
    data = {}
    coef = 0.0
    with open (filename, "r") as f :
        lines = f.readlines()
        coef = float(lines[4].split()[2])/1000
        random_seed = lines[3].split()[6]
        random_step = lines[3].split()[7]

        for line in lines[7:]:
            check = line.split()
            genus = check[0]
            data[genus] = []
            data[genus].append(float(check[1])/coef)
            data[genus].append(float(check[2])/coef)
            data[genus].append(float(check[3])/coef)
            data[genus].append(float(check[4])/coef)
            data[genus].append(float(check[5])/coef)
            data[genus].append(float(check[6])/coef)
            data[genus].append(float(check[7])/coef)
            data[genus].append(float(check[8])/coef)
            data[genus].append(float(check[9])/coef)
            data[genus].append(float(check[10])/coef)
            data[genus].append(float(check[11])/coef)
            data[genus].append(float(check[12])/coef)
            data[genus].append(float(check[13])/coef)
            data[genus].append(float(check[14])/coef)
            data[genus].append(float(check[15])/coef)
            data[genus].append(float(check[16])/coef)
    return data, random_seed, random_step

def write_data(D, fieldsize, filename, seed, step) :
    with open (filename, "w") as f :
        
        f.write ("# ------------------------------------------------------------------------------\n")
        f.write ("# Raw timings for " + fieldsize + "-bit fields\n")
        f.write ("# genus ADD_ram, NUC_ram, MGA_ram, DBL_ram, NUD_ram, MGD_ram, ADD_pspl, NUC_pspl, MGA_pspl, DBL_pspl, NUD_pspl, MGD_pspl, ADD_nspl, NUC_nspl, DBL_nspl, NUD_nspl\n")
        f.write ("# Random generator seed: " + seed + " and step: " + step + "\n")
        f.write ("# ------------------------------------------------------------------------------\n")

        for g in range(2, 51):
            f.write (str(g) + " ")
            for algo in range(0, 16) :
                f.write (str("{:.4f}".format(D[str(g)][algo]))+" ")
            f.write ("\n")


if __name__ == "__main__" :
    for fin in glob.glob("out*.raw"):
        raw_data,seed,step = read_data (fin)
        n = re.match (r'out(\d+).raw', fin).group(1)
        fout = "pout" + str(n) + ".raw"
        write_data (raw_data, n, fout,seed,step)

