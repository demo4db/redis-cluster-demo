# Redis-cluster基于kopf结合helm的实现
## 功能列表
- redis cluster模式创建，删除，集群自平衡自愈
- todo


## 调试和使用
1. 创建crd
```shell
alias k=kubectl
k apply  -f  crd.yml
```
2. 调试operator
```shell
pip3 install asyncio  kubernetes kopf
kopf run redis.py --verbose
```
3. 创建cr
```shell
k apply  -f  redis.yml
```


将基于cr的内容创建Redis集群
4. 查看集群

```
[root@worker01 kopf]# k get po | grep redis
redis-redis-cluster-0             1/1     Running   2          7h
redis-redis-cluster-1             1/1     Running   2          7h
redis-redis-cluster-2             1/1     Running   1          7h
redis-redis-cluster-3             1/1     Running   2          7h
redis-redis-cluster-4             1/1     Running   2          7h
redis-redis-cluster-5             1/1     Running   1          7h
```