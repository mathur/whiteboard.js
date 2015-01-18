<?php
exec('n=/var/www/html/demo; mkdir $n; mkdir ${n}-img;' .
     'mv /var/www/html/files/IMG_*.jpg ${n}-img/;' .
     'PYTHONPATH=$PYTHONPATH:/usr/lib/python2.7/dist-packages ' .
     'python /root/whiteboardjs/python/jsonparserkinda.py $n ${n}-img/*');
?>
