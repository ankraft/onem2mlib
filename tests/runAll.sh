#!/bin/sh
starttime=`date +%s`

python3 test_session.py
python3 test_cse.py
python3 test_ae.py
python3 test_container.py
python3 test_contentInstance.py
python3 test_group.py
python3 test_accessControlPolicy.py
python3 test_discovery.py

endtime=`date +%s`

runtime=$((endtime-starttime))

echo "\n\rExecution time: " $runtime seconds
