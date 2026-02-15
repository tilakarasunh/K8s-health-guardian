import os
import logging
from datetime import datetime, timedelta
from k8s_monitor import KubernetesMonitor
from ai_analyzer import AIAnalyzer
from report_generator import ReportGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main execution function for daily health check"""
    logger.info("Starting AKS Health Guardian...")
    
    # Initialize components
    k8s_monitor = KubernetesMonitor()
    ai_analyzer = AIAnalyzer(
        endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
        api_key=os.getenv('AZURE_OPENAI_API_KEY')
    )
    report_gen = ReportGenerator()
    
    # Collect cluster data
    logger.info("Collecting cluster metrics...")
    cluster_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'pods': k8s_monitor.get_pod_status(),
        'nodes': k8s_monitor.get_node_metrics(),
        'events': k8s_monitor.get_recent_events(hours=24),
        'resource_usage': k8s_monitor.get_resource_usage(),
        'failed_pods': k8s_monitor.get_failed_pods()
    }
    
    # Analyze with AI
    logger.info("Analyzing data with Azure OpenAI...")
    analysis = ai_analyzer.analyze_cluster_health(cluster_data)
    
    # Generate report
    logger.info("Generating health report...")
    report = report_gen.create_report(cluster_data, analysis)
    
    # Send report
    logger.info("Sending report via email...")
    report_gen.send_email(
        report=report,
        recipients=os.getenv('REPORT_RECIPIENTS').split(',')
    )
    
    logger.info("Health check completed successfully!")

if __name__ == "__main__":
    main()