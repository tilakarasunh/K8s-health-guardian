from kubernetes import client, config
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class KubernetesMonitor:
    def __init__(self):
        """Initialize Kubernetes client"""
        try:
            config.load_incluster_config()  # Running inside cluster
        except:
            config.load_kube_config()  # Running locally
        
        self.v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.metrics = client.CustomObjectsApi()
    
    def get_pod_status(self):
        """Get status of all pods"""
        pods = self.v1.list_pod_for_all_namespaces()
        
        pod_summary = {
            'total': 0,
            'running': 0,
            'pending': 0,
            'failed': 0,
            'unknown': 0,
            'details': []
        }
        
        for pod in pods.items:
            pod_summary['total'] += 1
            status = pod.status.phase.lower()
            pod_summary[status] = pod_summary.get(status, 0) + 1
            
            pod_summary['details'].append({
                'name': pod.metadata.name,
                'namespace': pod.metadata.namespace,
                'status': pod.status.phase,
                'restarts': sum(cs.restart_count for cs in pod.status.container_statuses or []),
                'age': (datetime.now(pod.metadata.creation_timestamp.tzinfo) - 
                       pod.metadata.creation_timestamp).days
            })
        
        return pod_summary
    
    def get_node_metrics(self):
        """Get node resource metrics"""
        nodes = self.v1.list_node()
        node_data = []
        
        for node in nodes.items:
            allocatable = node.status.allocatable
            capacity = node.status.capacity
            
            node_data.append({
                'name': node.metadata.name,
                'cpu_capacity': capacity.get('cpu'),
                'memory_capacity': capacity.get('memory'),
                'cpu_allocatable': allocatable.get('cpu'),
                'memory_allocatable': allocatable.get('memory'),
                'conditions': [
                    {'type': c.type, 'status': c.status} 
                    for c in node.status.conditions
                ]
            })
        
        return node_data
    
    def get_recent_events(self, hours=24):
        """Get cluster events from last N hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        events = self.v1.list_event_for_all_namespaces()
        
        recent_events = []
        for event in events.items:
            if event.last_timestamp and event.last_timestamp.replace(tzinfo=None) > cutoff_time:
                recent_events.append({
                    'type': event.type,
                    'reason': event.reason,
                    'message': event.message,
                    'object': f"{event.involved_object.kind}/{event.involved_object.name}",
                    'namespace': event.metadata.namespace,
                    'count': event.count,
                    'timestamp': event.last_timestamp.isoformat()
                })
        
        return sorted(recent_events, key=lambda x: x['timestamp'], reverse=True)[:50]
    
    def get_resource_usage(self):
        """Get current resource usage via metrics API"""
        try:
            pods_metrics = self.metrics.list_cluster_custom_object(
                group="metrics.k8s.io",
                version="v1beta1",
                plural="pods"
            )
            
            usage_summary = {
                'total_cpu_usage': 0,
                'total_memory_usage': 0,
                'pod_count': 0,
                'high_cpu_pods': [],
                'high_memory_pods': []
            }
            
            for pod in pods_metrics.get('items', []):
                for container in pod.get('containers', []):
                    cpu = container['usage'].get('cpu', '0')
                    memory = container['usage'].get('memory', '0')
                    
                    # Parse CPU (nanocores to millicores)
                    cpu_value = int(cpu.replace('n', '')) / 1_000_000 if 'n' in cpu else 0
                    # Parse memory (Ki to Mi)
                    mem_value = int(memory.replace('Ki', '')) / 1024 if 'Ki' in memory else 0
                    
                    usage_summary['total_cpu_usage'] += cpu_value
                    usage_summary['total_memory_usage'] += mem_value
                    usage_summary['pod_count'] += 1
                    
                    # Flag high usage
                    if cpu_value > 500:  # >500m CPU
                        usage_summary['high_cpu_pods'].append({
                            'pod': pod['metadata']['name'],
                            'namespace': pod['metadata']['namespace'],
                            'cpu_millicores': round(cpu_value, 2)
                        })
                    
                    if mem_value > 1024:  # >1Gi memory
                        usage_summary['high_memory_pods'].append({
                            'pod': pod['metadata']['name'],
                            'namespace': pod['metadata']['namespace'],
                            'memory_mi': round(mem_value, 2)
                        })
            
            return usage_summary
        except Exception as e:
            logger.error(f"Error fetching metrics: {e}")
            return {'error': str(e)}
    
    def get_failed_pods(self):
        """Get details of failed or problematic pods"""
        pods = self.v1.list_pod_for_all_namespaces()
        failed = []
        
        for pod in pods.items:
            if pod.status.phase in ['Failed', 'Unknown']:
                failed.append({
                    'name': pod.metadata.name,
                    'namespace': pod.metadata.namespace,
                    'status': pod.status.phase,
                    'reason': pod.status.reason or 'Unknown',
                    'message': pod.status.message or 'No message',
                    'container_statuses': [
                        {
                            'name': cs.name,
                            'ready': cs.ready,
                            'restart_count': cs.restart_count,
                            'state': str(cs.state)
                        }
                        for cs in (pod.status.container_statuses or [])
                    ]
                })
        
        return failed