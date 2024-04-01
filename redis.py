import kopf
import subprocess
import yaml
import asyncio
import logging



def check_and_recover_helm_release(app_name,namespace):
    # 检查 Helm Release 是否存在，如果不存在则重新创建
    helm_check_command = f"helm status {app_name}"
    helm_check_process = subprocess.Popen(helm_check_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, _ = helm_check_process.communicate()

    if "STATUS: deployed" not in stdout.decode():
        logging.warn(f"{app_name} Not exits,Will Recreate {app_name}  Helm Release")
        # 误删的情况
        # 调用已定义的 handle_create 函数来重新创建 Helm Release
        body = {'metadata': {'name': app_name, 'namespace': namespace}}
        handle_create(body=body, namespace=namespace)
    
    else:
        logging.info(f"Helm Release for app {app_name} is still active")

# 守护进程，用于监视并恢复被删除的 Helm Release
@kopf.daemon('RedisCluster')
async def helm_release_monitor(**kwargs):
    while True:
        app_name = kwargs['body']['metadata']['name']
        namespace = kwargs['body']['metadata']['namespace']
        check_and_recover_helm_release(app_name,namespace)
        await asyncio.sleep(3)

@kopf.on.create('RedisCluster')
def handle_create(body,namespace,**kwargs):
    app_name = body['metadata']['name']
    chart_name = "redis-cluster"
    release_name = f"{app_name}"
    # 解析 CR 中的字段值
    cr_fields = body.get('spec', {})
    field1_value = cr_fields.get('usePassword', 'false')
    field2_value = cr_fields.get('password', '')

    # 构建 Helm values 文件内容
    values = {
        'field1': field1_value,
        'field2': field2_value
    }
    values_yaml = yaml.dump(values, default_flow_style=False)

    # 将 values 写入临时文件
    with open('/tmp/values.yaml', 'w') as f:
        f.write(values_yaml)

    # 构建 Helm 命令
    helm_command = f"helm upgrade {release_name} {chart_name} -f /tmp/values.yaml --install --namespace {namespace}"

    # 执行 Helm 安装应用的命令
    result = subprocess.run(helm_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if result.returncode == 0:
        logging.info(f"APP  {app_name} deploy successed")
    else:
        logging.info(f"APP {app_name} deployed failed：{result.stderr}")





@kopf.on.delete('RedisCluster')
def handle_delete(body, **kwargs):
    app_name = body['metadata']['name']
    release_name = f"{app_name}"

    # 删除 Helm Release
    helm_delete_command = f"helm uninstall {release_name}"
    subprocess.run(helm_delete_command, shell=True)

    logging.info(f"Deleted {app_name}  Helm Release")