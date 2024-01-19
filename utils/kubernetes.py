from kubernetes import client, config

from utils.config import config as cfg
from utils.logger import log

class K8sProvider:
    driver=None
    def __init__(self, *kwargs):
        self.namespace = cfg.whoami.getEnvVar("CM_MANAGER_K8S_NAMESPACE")
        self.service_account = cfg.whoami.getEnvVar("CM_MANAGER_K8S_SA")
        self.deployment_name = cfg.whoami.getEnvVar("CM_MANAGER_K8S_DEPLOY_NAME")
        log.debug(action="[K8sProvider]", message="Trying K8s local connection...")
        local=False
        try:
            config.load_kube_config()
            local=True
            log.debug(action="[K8sProvider]", message="K8s local connection success")
        except Exception as e:
            print(e)
            log.error(action="[K8sProvider]", message="Unable to load local K8s driver")

        if not local:
            try:
                log.debug(action="[K8sProvider]", message="Trying K8s inCluster connection...")
                config.load_incluster_config()
                log.debug(action="[K8sProvider]", message="K8s inCluster connection success")
            except:
                log.error(action="[K8sProvider]", message="Unable to load K8s inCluster driver")
        self.driver = client.BatchV1Api()
    
    def get_deployment_version(self):
        driver = client.AppsV1Api()
        deployment_info = driver.read_namespaced_deployment(self.deployment_name, self.namespace)

        container = deployment_info.spec.template.spec.containers[0]
        image_version = container.image.split(":")[1].split("@")[0]

        return image_version
    
    def get_total_jobs(self):
        jobs = self.driver.list_namespaced_job(self.namespace)
        active_jobs = [job for job in jobs.items if job.status.succeeded is None]
        return len(active_jobs)

    def create_job_object(self, engine_id, engine_k8s_settings, scan_id, app_id, client_id, extra_fields):
        log.debug(action="[create_job_object]", message="Starting job creation with parameters (engine_id: %s, engine_k8s_settings: %s, scan_id: %s, app_id: %s, extra_fields: %s)" % (engine_id, engine_k8s_settings, scan_id, app_id, extra_fields))
        job_name='appsec-engine-'+engine_id+'-'+str(scan_id)

        # Create container
        container = client.V1Container(
            name=job_name,
            image=engine_k8s_settings['image'],
            image_pull_policy='IfNotPresent',
            command=[ "python3", "main.py", str(scan_id) ],
            resources=client.V1ResourceRequirements(
                requests=engine_k8s_settings['requests'],
                limits=engine_k8s_settings['limits']
            )
        )
        
        # Add environment  variables
        if container.env is None: container.env = []
   
        env_vars = [ 
            client.V1EnvVar(name="DB_ENGINE_REQ_TIMEOUT",        value=str(cfg.settings.get("DB_ENGINE_REQ_TIMEOUT"))),
            client.V1EnvVar(name="DB_ENGINE_MANAGER_URL",        value=cfg.settings.get("DB_ENGINE_MANAGER_URL")),
            client.V1EnvVar(name="CM_ENGINE_NAME",               value=engine_id),
            client.V1EnvVar(name="CM_ENGINE_JOB_NAME",           value=job_name),
            client.V1EnvVar(name="CM_LOG_FORMAT",                value=cfg.whoami.getEnvVar("CM_LOG_FORMAT")),
            client.V1EnvVar(name="CM_LOG_LEVEL",                 value=cfg.whoami.getEnvVar("CM_LOG_LEVEL")),
            client.V1EnvVar(name="SECRET_MANAGER_CLIENT_ID",     value_from=client.V1EnvVarSource(secret_key_ref=client.V1SecretKeySelector(name="manager-secrets", key="manager-id-appsec"))),
            client.V1EnvVar(name="SECRET_MANAGER_SECRET",        value_from=client.V1EnvVarSource(secret_key_ref=client.V1SecretKeySelector(name="manager-secrets", key="manager-pass-appsec"))),
            client.V1EnvVar(name="SECRET_MANAGER_SHARED_SECRET", value_from=client.V1EnvVarSource(secret_key_ref=client.V1SecretKeySelector(name="manager-secrets", key="manager-shared-secret-appsec"))),
            client.V1EnvVar(name="SECRET_GIT_USER",              value_from=client.V1EnvVarSource(secret_key_ref=client.V1SecretKeySelector(name="manager-secrets", key="git-user-manager-appsec"))),
            client.V1EnvVar(name="SECRET_GIT_PASSWORD",          value_from=client.V1EnvVarSource(secret_key_ref=client.V1SecretKeySelector(name="manager-secrets", key="git-pass-manager-appsec")))
        ]

        try:
            if "custom_secrets" in engine_k8s_settings and len(engine_k8s_settings["custom_secrets"]) > 0:
                for secret in engine_k8s_settings["custom_secrets"]:
                    env_vars.append(client.V1EnvVar(name=secret["secret_name"], 
                                        value_from=client.V1EnvVarSource(secret_key_ref=client.V1SecretKeySelector(name=secret["k8s_secret"], key=secret["k8s_secret_key"]))))
        except: pass

        for env_var in env_vars: container.env.append(env_var) 

        # Create pod spec section
        pod_spec = client.V1PodSpec(
            restart_policy='Never', 
            containers=[container],
            image_pull_secrets=[client.V1LocalObjectReference(name="regcred")],
            service_account_name=self.service_account
        )

        # Create and configurate pod section
        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels={'scan': str(scan_id), 'engine': engine_id, 'client': client_id}), 
            spec=pod_spec
        )

        # Create the specification of job
        spec = client.V1JobSpec(
            template=template,
            ttl_seconds_after_finished=10
        )

        # Create metadata for job
        metadata = client.V1ObjectMeta(name=job_name, namespace=self.namespace)

        # Instantiate the job object
        job = client.V1Job(api_version='batch/v1', kind='Job', metadata=metadata, spec=spec)
        
        return job

    def create_job(self, engine_id, engine_k8s_settings, scan_id, app_id, client_id, extra_fields):
        job=self.create_job_object(engine_id, engine_k8s_settings, scan_id, app_id, client_id, extra_fields)
        api_response = self.driver.create_namespaced_job(body=job, namespace=self.namespace)

    def delete_job(self, job_name):
        api_response = self.driver.delete_namespaced_job(
        name=job_name,
        namespace=self.namespace,
        body=client.V1DeleteOptions(
            propagation_policy='Foreground',
            grace_period_seconds=0))
