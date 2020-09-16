#OXAR  2
#OLAR  3
#PLAR  4
#OGAR  5
#PNAR  6
#PGAR  7
#PCAR  8
#MGAR  9

#OXDR  10
#OLDR  11
#PLDR  12
#OGDR  13
#PNDR  14
#PGDR  15
#PCDR  16
#MGDR  17

#OXAS  18
#OEAS  19
#PEAS  20
#PCAS  21
#MGAS  22

#OXDS  23
#OEDS  24
#PEDS  25
#PCDS  26
#MGDS  27

#GROUP 1

set key top center
set xlabel 'field size in bits'
set ylabel 'time (in {/Symbol m}s)'
set xrange [2:32]
set xtics (2,4,8,16,32)
set logscale x 2
set terminal pdf
gmin = 2
gmax = 32

#set yrange [0:65]
set title sprintf("Genus 2 Ramified Addition algorithms")
set output sprintf("g2_G1_RAM_ADD.pdf")
plot[gmin:gmax] 'poutg2_complete.raw' using 1:2 with linespoints ps 0.75 title 'All explicit',\
   'poutg2_complete.raw' using 1:5 with linespoints ps 0.75 title 'Costello-Lauter explicit',\
   'poutg2_complete.raw' using 1:3 with linespoints ps 0.75 title 'Lange explicit',

   
   
#set yrange [0:75]
set title sprintf("Genus 2 Ramfiied Doubling algorithms")
set output sprintf("g2_G1_RAM_DBL.pdf")
plot[gmin:gmax] 'poutg2_complete.raw' using 1:10 with linespoints ps 0.75 title 'All explicit',\
   'poutg2_complete.raw' using 1:13 with linespoints ps 0.75 title 'Costello-Lauter explicit',\
   'poutg2_complete.raw' using 1:11 with linespoints ps 0.75 title 'Lange explicit',


#set yrange [0:65]
set title sprintf("Genus 2 Split Addition algorithms")
set output sprintf("g2_G1_SPL_ADD.pdf")
plot[gmin:gmax] 'poutg2_complete.raw' using 1:18 with linespoints ps 0.75 title 'All explicit',\
   'poutg2_complete.raw' using 1:19 with linespoints ps 0.75 title 'Erickson explicit',



#set yrange [0:75]
set title sprintf("Genus 2 Split Doubling algorithms")
set output sprintf("g2_G1_SPL_DBL.pdf")
plot[gmin:gmax] 'poutg2_complete.raw' using 1:23 with linespoints ps 0.75 title 'All explicit',\
   'poutg2_complete.raw' using 1:24 with linespoints ps 0.75 title 'Erickson explicit',




set key top left
set xlabel 'field size in bits'
set ylabel 'time (in {/Symbol m}s)'
set xrange [2:1024]
set xtics (2,4,8,16,32,64,128,256,512,1024)
set logscale x 2
set terminal pdf
#set yrange [0:65]
gmin = 2
gmax = 1024

#GROUP 2

set yrange [0:65]
set title sprintf("Genus 2 Ramified Doubling algorithms")
set output sprintf("g2_G2_RAM_DBL.pdf")
plot[gmin:gmax] 'poutg2_complete.raw' using 1:17 with linespoints ps 0.75 title 'Magma',\
   'poutg2_complete.raw' using 1:16 with linespoints ps 0.75 title 'Cantor/ our',\
   'poutg2_complete.raw' using 1:15 with linespoints ps 0.75 title 'Costello-Lauter / trades',\
   'poutg2_complete.raw' using 1:14 with linespoints ps 0.75 title 'Costello-Lauter / no trades',\
   'poutg2_complete.raw' using 1:12 with linespoints ps 0.75 title 'Lange',\
   'poutg2_complete.raw' using 1:10 with linespoints ps 0.75 title 'Explicit/ our',

set yrange [0:55]
set title sprintf("Genus 2 Ramified Doubling algorithms")
set output sprintf("g2_G2_RAM_ADD.pdf")
plot[gmin:gmax] 'poutg2_complete.raw' using 1:9 with linespoints ps 0.75 title 'Magma',\
   'poutg2_complete.raw' using 1:8 with linespoints ps 0.75 title 'Cantor/ our',\
   'poutg2_complete.raw' using 1:7 with linespoints ps 0.75 title 'Costello-Lauter / trades',\
   'poutg2_complete.raw' using 1:6 with linespoints ps 0.75 title 'Costello-Lauter / no trades',\
   'poutg2_complete.raw' using 1:4 with linespoints ps 0.75 title 'Lange',\
   'poutg2_complete.raw' using 1:2 with linespoints ps 0.75 title 'Explicit/ our',
   

#GROUP 3
   
set yrange [0:70]
set title sprintf("Genus 2 Split Doubling algorithms")
set output sprintf("g2_G3_SPL_DBL.pdf")
plot[gmin:gmax] 'poutg2_complete.raw' using 1:27 with linespoints ps 0.75 title 'Magma',\
   'poutg2_complete.raw' using 1:26 with linespoints ps 0.75 title 'Cantor/ our',\
   'poutg2_complete.raw' using 1:25 with linespoints ps 0.75 title 'Erickson',\
   'poutg2_complete.raw' using 1:23 with linespoints ps 0.75 title 'Explicit / our',

set yrange [0:60]
set title sprintf("Genus 2 Split Addition algorithms")
set output sprintf("g2_G3_SPL_ADD.pdf")
plot[gmin:gmax] 'poutg2_complete.raw' using 1:22 with linespoints ps 0.75 title 'Magma',\
   'poutg2_complete.raw' using 1:21 with linespoints ps 0.75 title 'Cantor/ our',\
   'poutg2_complete.raw' using 1:20 with linespoints ps 0.75 title 'Erickson',\
   'poutg2_complete.raw' using 1:18 with linespoints ps 0.75 title 'Explicit / our',


#GROUP 4

set yrange [0:65]
set title sprintf("Genus 2 Doubling algorithms")
set output sprintf("g2_G4_DBL.pdf")
plot[gmin:gmax] 'poutg2_complete.raw' using 1:23 with linespoints ps 0.75 title 'Split',\
   'poutg2_complete.raw' using 1:10 with linespoints ps 0.75 title 'Ramified',

set yrange [0:55]
set title sprintf("Genus 2 Addition algorithms")
set output sprintf("g2_G4_ADD.pdf")
plot[gmin:gmax] 'poutg2_complete.raw' using 1:18 with linespoints ps 0.75 title 'Split',\
   'poutg2_complete.raw' using 1:2 with linespoints ps 0.75 title 'Ramified',

set yrange [0:65]
set title sprintf("Genus 2 algorithms")
set output sprintf("g2_G4.pdf")
plot[gmin:gmax] 'poutg2_complete.raw' using 1:23 with linespoints ps 0.75 title 'Double/ split',\
   'poutg2_complete.raw' using 1:10 with linespoints ps 0.75 title 'Double/ Ramified',\
   'poutg2_complete.raw' using 1:18 with linespoints ps 0.75 title 'Add/ split',\
   'poutg2_complete.raw' using 1:2 with linespoints ps 0.75 title 'Add/ ramified',