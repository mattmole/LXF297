START=`date -d "Oct 14 2022 20:47:00" +%s`
END=`date -d "Oct 14 2022 21:47:00" +%s`
# Times can also be specified using the AT-style descriptors, such as -1d for one day in the past

rrdtool graph dloadSpeed.png \
          --font DEFAULT:16: \
          --start $START \
          --end $END \
          -w 1280 \
          -h 720 \
          -t "Download Speed" \
          -v "B/s" \
          --slope-mode \
          DEF:m1_num=targetSample.rrd:dloadSpeed:AVERAGE \
          DEF:m1_max=targetSample.rrd:dloadSpeed:MAX \
          DEF:m1_min=targetSample.rrd:dloadSpeed:MIN \
          CDEF:maxMB=m1_max,1048576,/ \
          CDEF:minMB=m1_min,1048576,/ \
          LINE3:m1_num#FF0000:Avg \
          "GPRINT:maxMB:MAX:Max %6.2lf MB/s" \
          "GPRINT:minMB:MIN:Min %6.2lf MB/s"

rrdtool graph cpuTemp.png \
          --font DEFAULT:16: \
          --start $START \
          --end $END \
          -w 1280 \
          -h 720 \
          -t "CPU Temp" \
          -v "Degrees C" \
          --upper-limit 44 \
          --lower-limit 33 \
          --left-axis-format %6.1lf \
          --rigid \
          --slope-mode \
          DEF:m1_num=targetSample.rrd:cpuTemp:AVERAGE \
          DEF:m1_max=targetSample.rrd:cpuTemp:MAX \
          DEF:m1_min=targetSample.rrd:cpuTemp:MIN \
          CDEF:maxMB=m1_max,1048576,/ \
          CDEF:minMB=m1_min,1048576,/ \
          LINE3:m1_num#FF0000:Avg \
          "GPRINT:m1_max:MAX:Max %6.2lf C" \
          "GPRINT:m1_min:MIN:Min %6.2lf C"