#ADD_RAM  2
#NUC_RAM  3
#MGA_RAM  4
#DBL_RAM  5
#NUD_RAM  6
#MGD_RAM  7
#ADD_pSPL 8
#NUC_pSPL 9
#MGA_pSPL 10
#DBL_pSPL 11
#NUD_pSPL 12
#MGD_pSPL 13
#ADD_nSPL 14
#NUC_nSPL 15
#DBL_nSPL 16
#NUD_nSPL 17

set key top left
set xlabel 'genus'
set ylabel 'time (in ms)'
set xrange [2:50]
set xtics 2,2,50

set terminal pdf

do for [size in "2 4 8 16 32 64 128 256 512 1024"] {
   N = int(size)
   gmin = 2
   gmax = 50

   curves(N) = sprintf("Addition algorithms / %d-bit field", N)
   set title curves(N)
   filename(N) = sprintf("add_pos_neg_split_%d.pdf", N)
   set output filename(N)

   plot[gmin:gmax] 'pout'.N.'.raw' using 1:15 with linespoints ps 0.75 title 'NUCOMP / split / neg. basis',\
     	'pout'.N.'.raw' using 1:9 with linespoints ps 0.75 title 'NUCOMP / split / pos. basis'
   
   curves(N)  = sprintf("Doubling algorithms / %d-bit field", N)
    set title curves(N)
    filename(N) = sprintf("dbl_pos_neg_split_%d.pdf", N)
    set output filename(N)

    plot[gmin:gmax] 'pout'.N.'.raw' using 1:17 with linespoints ps 0.75 title 'NUDUPL /split / neg. basis',\
     	'pout'.N.'.raw' using 1:12 with linespoints ps 0.75 title 'NUDUPL / split / pos. basis',\


   curves(N) = sprintf("Addition algorithms / %d-bit field", N)
   set title curves(N)
   filename(N) = sprintf("add_%d.pdf", N)
   set output filename(N)

   plot[gmin:gmax] 'pout'.N.'.raw' using 1:4 with linespoints ps 0.75 title 'Magma / ramified',\
      'pout'.N.'.raw' using 1:10 with linespoints ps 0.75 title 'Magma / split',\
      'pout'.N.'.raw' using 1:2 with linespoints ps 0.75 title 'Cantor / ramified',\
      'pout'.N.'.raw' using 1:14 with linespoints ps 0.75 title 'Cantor / split / neg. basis',\
      'pout'.N.'.raw' using 1:3 with linespoints linestyle 8 ps 0.75 title 'NUCOMP / ramified',\
     	'pout'.N.'.raw' using 1:15 with linespoints ps 0.75 title 'NUCOMP / split / neg. basis'
     	

    curves(N)  = sprintf("Doubling algorithms / %d-bit field", N)
    set title curves(N)
    filename(N) = sprintf("dbl_%d.pdf", N)
    set output filename(N)

    plot[gmin:gmax] 'pout'.N.'.raw' using 1:7 with linespoints ps 0.75 title 'Magma / ramified',\
      'pout'.N.'.raw' using 1:13 with linespoints ps 0.75 title 'Magma / split',\
      'pout'.N.'.raw' using 1:5 with linespoints ps 0.75 title 'Cantor / ramified',\
      'pout'.N.'.raw' using 1:16 with linespoints ps 0.75 title 'Cantor / split / neg. basis',\
      'pout'.N.'.raw' using 1:6 with linespoints linestyle 8 ps 0.75 title 'NUDUPL / ramified',\
      'pout'.N.'.raw' using 1:17 with linespoints ps 0.75 title 'NUDUPL /split / neg. basis'

   gmax = 10
   curves(N) = sprintf("Addition algorithms / %d-bit field", N)
   set title curves(N)
   filename(N) = sprintf("add_lowg_%d.pdf", N)
   set output filename(N)

   plot[gmin:gmax] 'pout'.N.'.raw' using 1:15 with linespoints ps 0.75 title 'NUCOMP / split / neg. basis',\
     	'pout'.N.'.raw' using 1:14 with linespoints ps 0.75 title 'Cantor / split / neg. basis',\
      'pout'.N.'.raw' using 1:10 with linespoints ps 0.75 title 'Magma / split'
   
   curves(N)  = sprintf("Doubling algorithms / %d-bit field", N)
    set title curves(N)
    filename(N) = sprintf("dbl_lowg_%d.pdf", N)
    set output filename(N)

    plot[gmin:gmax] 'pout'.N.'.raw' using 1:17 with linespoints ps 0.75 title 'NUDUPL /split / neg. basis',\
     	'pout'.N.'.raw' using 1:16 with linespoints ps 0.75 title 'Cantor / split / neg. basis',\
      'pout'.N.'.raw' using 1:13 with linespoints ps 0.75 title 'Magma / split'
      
}


do for [size in "32"] {
   N = int(size)
   gmin = 2
   gmax = 50

   curves(N) = sprintf("Addition algorithms / %d-bit field", N)
   set title curves(N)
   filename(N) = sprintf("add_y_%d.pdf", N)
   set output filename(N)
   set yrange [0:3]
   set key at -2.5, 2.9
   plot[gmin:gmax] 'pout'.N.'.raw' using 1:4 with linespoints ps 0.75 title 'Magma / ramified',\
      'pout'.N.'.raw' using 1:10 with linespoints ps 0.75 title 'Magma / split',\
      'pout'.N.'.raw' using 1:2 with linespoints ps 0.75 title 'Cantor / ramified',\
      'pout'.N.'.raw' using 1:14 with linespoints ps 0.75 title 'Cantor / split / neg. basis',\
      'pout'.N.'.raw' using 1:3 with linespoints linestyle 8 ps 0.75 title 'NUCOMP / ramified',\
     	'pout'.N.'.raw' using 1:15 with linespoints ps 0.75 title 'NUCOMP / split / neg. basis'
     	

    curves(N)  = sprintf("Doubling algorithms / %d-bit field", N)
    set title curves(N)
    filename(N) = sprintf("dbl_y_%d.pdf", N)
    set output filename(N)
    set yrange [0:3]
    set key at -2.5, 2.9
    plot[gmin:gmax] 'pout'.N.'.raw' using 1:7 with linespoints ps 0.75 title 'Magma / ramified',\
      'pout'.N.'.raw' using 1:13 with linespoints ps 0.75 title 'Magma / split',\
      'pout'.N.'.raw' using 1:5 with linespoints ps 0.75 title 'Cantor / ramified',\
      'pout'.N.'.raw' using 1:16 with linespoints ps 0.75 title 'Cantor / split / neg. basis',\
      'pout'.N.'.raw' using 1:6 with linespoints linestyle 8 ps 0.75 title 'NUDUPL / ramified',\
      'pout'.N.'.raw' using 1:17 with linespoints ps 0.75 title 'NUDUPL /split / neg. basis'
}