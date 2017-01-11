#!/bin/sh
RETURN_STATUS=0
mytime=`date`

rebootMessage=


echo Dell Inc. Auto-Generated Sample Bundle Execution Script
logFile="$LOGFILE"
if [ -z "$LOGFILE" ]; then logFile=/tmp/apply_components.log; fi
touch "$logFile" 2>/dev/null
if [ ! $? == 0 ]; then logFile=/tmp/apply_components.log; else ln -sf $logFile ./apply_components.log > /dev/null 2>&1; fi
echo Start time: $mytime | tee -a $logFile
REEBOOTSTDMESSAGE="Note: Some update requires machine reboot. Please reboot the machine and re-run the script if there are failed updates because of dependency..."
ExecuteDup()
{
   index=$1
        count=$2
        DUP=$3
        Options=
        force=$4
        dependency=$5
        reboot=$6

        if [ ! -z "$force" ];then
                Options="-f"
        fi
        echo [$index/$count] - Executing $DUP | tee -a $logFile
        sh "$DUP" -q $Options | tee -a $logFile
        DUP_STATUS=${PIPESTATUS[0]}
        if [ ! -z "$reboot" ];then
                echo "Note: $DUP update requires machine reboot ..."
                rebootMessage=$REEBOOTSTDMESSAGE
        fi
        if [ ${DUP_STATUS} -eq 1 ];
        then
                RETURN_STATUS=1
        fi
        if [ ${DUP_STATUS} -eq 9 ];
        then
                RETURN_STATUS=1
        fi
        if [ ${DUP_STATUS} -eq 127 ];
        then
                RETURN_STATUS=1
        fi
        return $RETURN_STATUS
}
