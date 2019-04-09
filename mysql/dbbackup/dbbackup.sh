#!/bin/bash
#use condfig
#dbbackup.sh dbname
#dbbackup.sh all

SHELL_FOLDER=$(dirname $(readlink -f "$0"))
source ${SHELL_FOLDER}/dbbackup.conf

RETVAL=0
let processNumber=$processNumber-1
OPTIONS="-h$host -u$user -p$pwd -P$port --single-transaction --triggers --log-error=${DBPATH}/backup_error.dat --opt -R -K -E"
DMin=`date +%Y%m%d_%H%M`
DHour=$(date +%Y%m%d%H)
my_mysqlclinet=$(which mysql)
db_list=`$my_mysqlclinet -h$host -u$user -p$pwd -P$port -s -e "show databases"|egrep -v "information_schema|performance_schema|test|sys|undolog"`

function echo_y (){
    # Color yellow: ok
    [ $# -ne 1 ] && return 1
    echo -e "\033[33m$1\033[0m"
}

function echo_r (){
    # Color red: Error, Failed
    [ $# -ne 1 ] && return 1
    echo -e "\033[31m$1\033[0m"
}

function my_try_dir(){
    [ -d $1 ] || mkdir -p "$1"
}

function cleanbackup()
{
    find ${DBPATH}/[0-9]* -type d -mtime +7|xargs rm -rf
}

function myfiletime(){
    local timestamp=`date +%s`
    local mytime=$2
    local my_file=$1
    local filetimestamp=`stat -c %Y $my_file`
    if [ -f $filepath ];
    then
        local timecha=$[ $timestamp - $filetimestamp ]
        if [ $timecha -gt $mytime ];then
            echo_y "no error"
            echo "$my_file当前时间大于文件最后修改时间$timecha 秒"
        else
            echo_r "happen error"
            echo "$my_file当前时间小于等于文件最后修改时间$timecha 秒"
            echo_r "有错误生成，备份也许失败"
            RETVAL=1
        fi
    else
        echo "文件不存在或者您输入的路径有误"
        RETVAL=1
    fi
}

function dbbackup_action()
{
    my_try_dir "${DBPATH}/${DHour}"
#   [ -d ${DBPATH}/${DHour} ] || mkdir -p ${DBPATH}/${DHour}
    echo "$DMin Start backup $1" >> ${DBPATH}/backup_log.dat
    #/usr/bin/mysqldump $OPTIONS $1 > ${DBPATH}/${DHour}/$1_$DMin.sql
    if [ -n "$2" ];then
        my_try_dir "${DBPATH}/${DHour}/$1"
#        [ -d ${DBPATH}/${DHour}/$1 ] || mkdir -p ${DBPATH}/${DHour}/$1
        /usr/bin/mysqldump $OPTIONS $1 $2 |gzip > ${DBPATH}/${DHour}/$1/$1_$2_$DMin.gz
    else
        /usr/bin/mysqldump $OPTIONS $1 |gzip > ${DBPATH}/${DHour}/$1_$DMin.gz
    fi
}

function many_processA()
{
    local mynum=$(($RANDOM%50+10000))
    local myaction=dbbackup_action
    case $1 in
        manydb)
            local mydb_list=$db_list
            ;;
        *)
            local my_sin_db=$1
            local mytable_list=`$my_mysqlclinet -h$host -P$port -u$user -p$pwd $my_sin_db -s -e "show tables"`
            ;;
    esac
    trap "exec 999>&-;exec 999<&-;exit 0" 2
    mkfifo testfifo999
    exec 999<>testfifo999
    rm -rf testfifo999
    for((fifon=1;fifon<=$processNumber;fifon++))
    do
        echo >&999
    done
    if [ -n "$mydb_list" ];then
        local myxxlist=$mydb_list
    else
        local myxxlist=$mytable_list
    fi
    for dby in $myxxlist
    do
        read -u999
        {
            if [ -n "$my_sin_db" ];then
                $myaction $my_sin_db $dby
            else
                $myaction $dby
            fi
        echo >&999
        }&
    done
    wait
    exec 999>&-
    exec 999<&-
}

function my_main(){
case $1 in
       all|ALL)
            while true;
            do
                case $1 in
                    all|ALL)
                        many_processA manydb
                        myfiletime ${DBPATH}/backup_error.dat 60
                        break
                        ;;
                    *) 
                        RETVAL=1
                        exit $RETVAL
                        ;;
                esac
			done
       ;;
       *)
           if [[ "$db_list" =~ "$1" ]] && [ -n "$1" ];then
            many_processA $1
            myfiletime ${DBPATH}/backup_error.dat 60
           else
            echo 'error'
           fi
       ;;
      esac 
}


cleanbackup
my_main "$@"
exit $RETVAL
