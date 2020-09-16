#OXA  2
#OSA  3
#PSA  4
#PRA  5
#PCA  6
#MGA  7

#OXD  8
#OSD  9
#PSD  10
#RSD  11
#PCD  12
#MGD  13


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
set title sprintf("Genus 3 Split Addition algorithms")
set output sprintf("g3_G1_ADD.pdf")
plot[gmin:gmax] 'poutg3_complete.raw' using 1:2 with linespoints ps 0.75 title 'All explicit',\
   'poutg3_complete.raw' using 1:3 with linespoints ps 0.75 title 'Sutherland/Rad Explicit',



#set yrange [0:75]
set title sprintf("Genus 3 Split Doubling algorithms")
set output sprintf("g3_G1_DBL.pdf")
plot[gmin:gmax] 'poutg3_complete.raw' using 1:8 with linespoints ps 0.75 title 'All explicit',\
   'poutg3_complete.raw' using 1:9 with linespoints ps 0.75 title 'Sutherland/Rad explicit',




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
   
set yrange [0:175]
set title sprintf("Genus 3 Split Doubling algorithms")
set output sprintf("g3_G2_DBL.pdf")
plot[gmin:gmax] 'poutg3_complete.raw' using 1:13 with linespoints ps 0.75 title 'Magma',\
   'poutg3_complete.raw' using 1:12 with linespoints ps 0.75 title 'Cantor/ our',\
   'poutg3_complete.raw' using 1:11 with linespoints ps 0.75 title 'Rad',\
   'poutg3_complete.raw' using 1:10 with linespoints ps 0.75 title 'Sutherland',\
   'poutg3_complete.raw' using 1:8 with linespoints ps 0.75 title 'Explicit / our',

set yrange [0:150]
set title sprintf("Genus 3 Split Addition algorithms")
set output sprintf("g3_G2_ADD.pdf")
plot[gmin:gmax] 'poutg3_complete.raw' using 1:7 with linespoints ps 0.75 title 'Magma',\
   'poutg3_complete.raw' using 1:6 with linespoints ps 0.75 title 'Cantor/ our',\
   'poutg3_complete.raw' using 1:5 with linespoints ps 0.75 title 'Rad',\
   'poutg3_complete.raw' using 1:4 with linespoints ps 0.75 title 'Sutherland',\
   'poutg3_complete.raw' using 1:2 with linespoints ps 0.75 title 'Explicit / our',

