#!/bin/bash

# 检查是否提供了参数
if [ $# -eq 0 ]; then
    echo "请提供参数"
    exit 1
fi

if [ $# -eq 1 ]; then
    echo "请提供充足参数"
    exit 1
fi

# 根据第一个参数执行不同操作
case $1 in
    mysql)
        echo "正在查看mysql服务"
	case $2 in
            start)
                echo "正在启动mysql服务"
                systemctl start mysqld
                ;;
            status)
                echo "正在查看mysql服务状态"
                systemctl status mysqld
                ;;
            stop)
                echo "正在停止mysql服务"
                systemctl stop mysqld
                ;;
            restart)
                echo "重启正在启动mysql服务"
                systemctl restart mysqld
                ;;
            *)
                echo ""未知参数，可用参数: start,stop,restart,stop""
                ;;
        esac
        # 这里可以添加启动服务的实际命令，例如：systemctl start some_service
        ;;
    redis)
        echo "正在进行redis服务"
	case $2 in
            start)
                echo "正在启动redis服务"
                /usr/local/bin/redis/redis-server /usr/local/bin/redis/redis.conf
                ;;
            stop)
                echo "正在停止mysql服务"
                /usr/local/bin/redis/redis-cli -a password  shutdown
                ;;
            *)
                echo "未知参数，可用参数: start,stop"
                ;;
        esac
        # 这里可以添加停止服务的实际命令，例如：systemctl stop some_service
        ;;
    nginx)
        echo "正在进行nginxg服务"
	case $2 in
            start)
                echo "正在启动nginx服务"
                systemctl start nginx
                ;;
            status)
                echo "正在查看nginx服务状态"
                systemctl status nginx
                ;;
            stop)
                echo "正在停止nginx服务"
                systemctl stop nginx
                ;;
            restart)
                echo "重启正在启动nginx服务"
                systemctl restart nginx
                ;;
            *)
                echo ""未知参数，可用参数: start,stop,restart,stop""
                ;;
        esac
        # 这里可以添加重启服务的实际命令，例如：systemctl restart some_service
        ;;
    *)
        echo "未知参数，可用参数: mysql, nginx, redis"
        ;;
esac
