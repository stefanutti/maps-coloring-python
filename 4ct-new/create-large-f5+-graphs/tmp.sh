#!/bin/bash
#
# This script check all servers of the GVT suite
#
################################################

function mysql {

    #######
    # Mysql
    #######
    running_tmp=`ps ww -ef | grep "mysqld" | grep -v grep | awk '{print $2}'`
    if [ "$1" = "status" ]; then
        if [ "$running_tmp" = "" ]; then
            echo "mysqld (external)   - NOT running"
            return 0
        else
            echo "mysqld (external)   - Running     - $running_tmp"
            return $running_tmp
        fi
    elif [ "$1" = "start" ]; then
        echo "mysqld (External service. Cannot be started from here)"
    elif [ "$1" = "stop" ]; then
        echo "mysqld (External service. Cannot be stopped from here)"
    fi
}

function activemq {

    ##########
    # Activemq
    ##########
    running_tmp=`ps ww -ef | grep "java.*activemq" | grep -v grep | awk '{print $2}'`
    if [ "$1" = "status" ]; then
        if [ "$running_tmp" = "" ]; then
            echo "activemq            - NOT running"
            return 0
        else
            echo "activemq            - Running     - $running_tmp"
            return $running_tmp
        fi
    elif [ "$1" = "start" ]; then
        cd ~/gvt/jms-domain/gvt-jms-*1/activemq/bin
        ./activemq start
        cd -
    elif [ "$1" = "stop" ]; then
        echo "Starting activemq"
        echo "Shutting down activemq"
        cd ~/gvt/jms-domain/gvt-jms-*1/activemq/bin
        ./activemq stop
        cd -
    fi
}

function zookeeper {

    ###########
    # Zookeeper
    ###########
    running_tmp=`ps ww -ef | grep "java.*org.apache.zookeeper.server.quorum.QuorumPeerMain" | grep -v grep | awk '{print $2}'`
    if [ "$1" = "status" ]; then
        if [ "$running_tmp" = "" ]; then
            echo "zookeeper           - NOT running"
            return 0
        else
            echo "zookeeper           - Running     - $running_tmp"
            return $running_tmp
        fi
    elif [ "$1" = "start" ]; then
        cd ~/gvt/kafka-domain/gvt-kafka-*1/kafka
        bin/zookeeper-server-start.sh -daemon config/zookeeper.properties
        cd -
    elif [ "$1" = "stop" ]; then
        cd ~/gvt/kafka-domain/gvt-kafka-*1/kafka
        bin/zookeeper-server-stop.sh
        cd -
    fi
}

function kafka {

    #######
    # Kafka
    #######
    running_tmp=`ps ww -ef | grep "java.*kafka.Kafka" | grep -v grep | awk '{print $2}'`
    if [ "$1" = "status" ]; then
        if [ "$running_tmp" = "" ]; then
            echo "kafka               - NOT running"
            return 0
        else
            echo "kafka               - Running     - $running_tmp"
            return $running_tmp
        fi
    elif [ "$1" = "start" ]; then
        cd ~/gvt/kafka-domain/gvt-kafka-*1/kafka
        bin/kafka-server-start.sh -daemon config/server.properties
        cd -
    elif [ "$1" = "stop" ]; then
        cd ~/gvt/kafka-domain/gvt-kafka-*1/kafka
        bin/kafka-server-stop.sh
        cd -
    fi
}

function file-simulator {

    ################
    # File Simulator
    ################
    running_tmp=`ps ww -ef | grep "python files-generator.py" | grep -v grep | awk '{print $2}'`
    if [ "$1" = "status" ]; then
        if [ "$running_tmp" = "" ]; then
            echo "files-generator     - NOT running"
            return 0
        else
            echo "files-generator     - Running     - $running_tmp"
            return $running_tmp
        fi
    elif [ "$1" = "start" ]; then
        echo "files-generator.py (External service. Cannot be started from here. Do it manually)"
    elif [ "$1" = "stop" ]; then
        echo "files-generator.py (External service. Cannot be stopped from here. Do it manually)"
    fi
}

function karaf {

    #######
    # Karaf
    #######
    running_tmp=`ps ww -ef | grep "karaf server" | grep -v grep | awk '{print $2}'`
    if [ "$1" = "status" ]; then
        if [ "$running_tmp" = "" ]; then
            echo "karaf (GV ESB)      - NOT running"
            return 0
        else
            echo "karaf (GV ESB)      - Running     - $running_tmp"
            return $running_tmp
        fi
    elif [ "$1" = "start" ]; then
        cd ~/gvt/esb-domain/gvt-esb-*1/karaf/bin
        ./start
        cd -
    elif [ "$1" = "stop" ]; then
        cd ~/gvt/esb-domain/gvt-esb-*1/karaf/bin
        ./stop
        cd -
    fi
}

echo Machine: `hostname`
echo ""

if [[ ($# -eq 0) || (("$1" != "status") && ("$1" != "start") && ("$1" != "stop")) ]]; then
    echo "Error: Wrong parameters"
    echo "Usage; $0 <status|start|stop> [<mysql|activemq|zookeeper|kafka|karaf>]"
    exit -1
fi

if [[ ($# -eq 2) && (("$2" != "mysql") && ("$2" != "activemq") && ("$2" != "zookeeper") && ("$2" != "kafka")  && ("$2" != "karaf")) ]]; then
    echo "Error: Wrong parameters"
    echo "Usage; $0 <status|start|stop> [<mysql|activemq|zookeeper|kafka|karaf>]"
    exit -1
fi

if [ $# -eq 1 ]; then
    sw="all"
else
    sw=$2
fi

if [ "$1" = "status" ]; then
    case $sw in
        ("mysql") mysql "$1" ;;
        ("activemq") activemq "$1" ;;
        ("zookeeper") zookeeper "$1" ;;
        ("kafka") kafka "$1" ;;
        ("karaf") karaf "$1" ;;
        ("all")
            mysql "$1"
            activemq "$1"
            zookeeper "$1"
            kafka "$1"
            karaf "$1"
            file-simulator "$1"
            ;;
    esac
elif [ "$1" = "start" ]; then
    case $sw in
        ("mysql") mysql "$1" ;;
        ("activemq") activemq "$1" ;;
        ("zookeeper") zookeeper "$1" ;;
        ("kafka") kafka "$1" ;;
        ("karaf") karaf "$1" ;;
        ("all")
            echo "Starting mysql"
            mysql "$1"
            echo "Sleeps 2 secs ..."; sleep 2

            echo "Starting activemq"
            activemq "$1"
            echo "Sleeps 2 secs ..."; sleep 2

            echo "Starting zookeeper"
            zookeeper "$1"
            echo "Sleeps 2 secs ..."; sleep 2

            echo "Starting kafka"
            kafka "$1"
            echo "Sleeps 2 secs ..."; sleep 2

            echo "Starting karaf"
            karaf "$1"
            echo "Sleeps 2 secs ..."; sleep 2
            ;;
    esac
elif [ "$1" = "stop" ]; then
    case $sw in
        ("karaf") karaf "$1" ;;
        ("kafka") kafka "$1" ;;
        ("zookeeper") zookeeper "$1" ;;
        ("activemq") activemq "$1" ;;
        ("mysql") mysql "$1" ;;
        ("all")
            echo "Shutting down activemq"
            karaf "$1"
            echo "Sleeps 4 secs ..."; sleep 4

            echo "Shutting down kafka"
            kafka "$1"
            echo "Sleeps 4 secs ..."; sleep 4

            echo "Shutting down zookeeper"
            zookeeper "$1"
            echo "Sleeps 4 secs ..."; sleep 4

            echo "Shutting down activemq"
            activemq "$1"
            echo "Sleeps 4 secs ..."; sleep 4

            echo "Shutting down mysql"
            mysql "$1"
            echo "Sleeps 4 secs ..."; sleep 4
            ;;
    esac
fi
~   