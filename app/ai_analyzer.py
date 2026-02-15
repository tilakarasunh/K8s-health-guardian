import json
import logging
import requests
from typing import Dict, Any

logger = logging.getLogger(__name__)

class AIAnalyzer:
    def __init__(self, endpoint: str, api_key: str):
        """Initialize Azure OpenAI client using REST API"""
        self.endpoint = endpoint.rstrip('/')
        self.api_key = api_key
        self.api_version = "2024-02-15-preview"
        self.deployment_name = "gpt-4o-mini"  # Make sure this matches your deployment
        
    def analyze_cluster_health(self, cluster_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze cluster data and generate insights using Azure OpenAI REST API"""
        
        # Prepare context for AI
        context = self._prepare_context(cluster_data)
        
        prompt = f"""You are an expert Kubernetes cluster administrator. Analyze this AKS cluster health data and provide:

1. Overall Health Score (0-100)
2. Top 3 Issues Detected (with severity: Critical/Warning/Info)
3. Predicted Problems (in next 24-48 hours)
4. Actionable Recommendations (specific kubectl commands or Azure portal actions)

Cluster Data:
{context}

Provide your analysis in JSON format:
{{
  "health_score": <number>,
  "summary": "<brief overall assessment>",
  "issues": [
    {{"severity": "<level>", "title": "<issue>", "description": "<details>"}}
  ],
  "predictions": [
    {{"timeframe": "<when>", "issue": "<what>", "probability": "<likelihood>"}}
  ],
  "recommendations": [
    {{"priority": "<high/medium/low>", "action": "<what to do>", "command": "<kubectl or az command>"}}
  ]
}}"""

        try:
            # Construct the REST API URL for Cognitive Services endpoint
            # Format: https://eastus.api.cognitive.microsoft.com/openai/deployments/{deployment-id}/chat/completions?api-version={api-version}
            url = f"{self.endpoint}/openai/deployments/{self.deployment_name}/chat/completions?api-version={self.api_version}"
            
            headers = {
                "Content-Type": "application/json",
                "api-key": self.api_key
            }
            
            payload = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a Kubernetes expert providing cluster health analysis. Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 2000,
                "top_p": 0.95,
                "frequency_penalty": 0,
                "presence_penalty": 0
            }
            
            logger.info(f"Calling Azure OpenAI API at: {url}")
            logger.info(f"Using deployment: {self.deployment_name}")
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            # Log response status
            logger.info(f"API Response Status: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"API Error Response: {response.text}")
                response.raise_for_status()
            
            result = response.json()
            analysis_text = result['choices'][0]['message']['content']
            
            logger.info(f"Received AI response, length: {len(analysis_text)} chars")
            
            # Extract JSON from response
            start = analysis_text.find('{')
            end = analysis_text.rfind('}') + 1
            
            if start >= 0 and end > start:
                analysis_json = json.loads(analysis_text[start:end])
                logger.info("Successfully parsed AI response")
                return analysis_json
            else:
                logger.warning("No JSON found in AI response, using fallback")
                return self._fallback_analysis(cluster_data)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
            return self._fallback_analysis(cluster_data)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI JSON response: {e}")
            logger.error(f"Raw response (first 500 chars): {analysis_text[:500]}")
            return self._fallback_analysis(cluster_data)
        except KeyError as e:
            logger.error(f"Unexpected response structure: {e}")
            logger.error(f"Response keys: {result.keys() if 'result' in locals() else 'N/A'}")
            return self._fallback_analysis(cluster_data)
        except Exception as e:
            logger.error(f"AI analysis failed: {e}", exc_info=True)
            return self._fallback_analysis(cluster_data)
    
    def _prepare_context(self, cluster_data: Dict[str, Any]) -> str:
        """Prepare concise context for AI"""
        context_parts = []
        
        # Pod summary
        pods = cluster_data.get('pods', {})
        context_parts.append(
            f"Pod Summary: {pods.get('total', 0)} total, "
            f"{pods.get('running', 0)} running, "
            f"{pods.get('failed', 0)} failed, "
            f"{pods.get('pending', 0)} pending"
        )
        
        # Failed pods
        failed_pods = cluster_data.get('failed_pods', [])
        context_parts.append(f"\nFailed Pods: {len(failed_pods)} pods in failed state")
        
        # Resource usage
        resource_usage = cluster_data.get('resource_usage', {})
        high_cpu = resource_usage.get('high_cpu_pods', [])
        high_mem = resource_usage.get('high_memory_pods', [])
        context_parts.append(
            f"High Resource Usage: {len(high_cpu)} pods with high CPU, "
            f"{len(high_mem)} pods with high memory"
        )
        
        # Events summary
        events = cluster_data.get('events', [])
        warning_events = [e for e in events if e.get('type') == 'Warning']
        normal_events = [e for e in events if e.get('type') == 'Normal']
        context_parts.append(f"\nRecent Events: {len(warning_events)} warnings, {len(normal_events)} normal")
        
        # Top events (limit to prevent token overflow)
        if events:
            context_parts.append("\nTop Recent Events:")
            for event in events[:5]:
                event_msg = event.get('message', '')[:100]
                context_parts.append(
                    f"  - [{event.get('type')}] {event.get('reason')}: {event_msg}"
                )
        
        # Failed pod details (limit to prevent token overflow)
        if failed_pods:
            context_parts.append("\nFailed Pod Details:")
            for pod in failed_pods[:3]:
                context_parts.append(
                    f"  - {pod.get('namespace')}/{pod.get('name')}: "
                    f"{pod.get('reason', 'Unknown')}"
                )
        
        return "\n".join(context_parts)
    
    def _fallback_analysis(self, cluster_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simple rule-based analysis if AI fails"""
        health_score = 100
        issues = []
        recommendations = []
        
        pods = cluster_data.get('pods', {})
        failed_pods = cluster_data.get('failed_pods', [])
        resource_usage = cluster_data.get('resource_usage', {})
        
        # Check for failed pods
        if pods.get('failed', 0) > 0:
            health_score -= 20
            issues.append({
                "severity": "Critical",
                "title": f"{pods.get('failed')} Failed Pods",
                "description": "Pods are in failed state and need investigation"
            })
            recommendations.append({
                "priority": "high",
                "action": "Investigate failed pods",
                "command": "kubectl get pods --all-namespaces --field-selector=status.phase=Failed"
            })
        
        # Check for high CPU usage
        high_cpu_pods = resource_usage.get('high_cpu_pods', [])
        if len(high_cpu_pods) > 0:
            health_score -= 10
            issues.append({
                "severity": "Warning",
                "title": "High CPU Usage Detected",
                "description": f"{len(high_cpu_pods)} pods using >500m CPU"
            })
            recommendations.append({
                "priority": "medium",
                "action": "Review pod resource limits",
                "command": "kubectl top pods --all-namespaces --sort-by=cpu"
            })
        
        # Check for high memory usage
        high_mem_pods = resource_usage.get('high_memory_pods', [])
        if len(high_mem_pods) > 0:
            health_score -= 10
            issues.append({
                "severity": "Warning",
                "title": "High Memory Usage Detected",
                "description": f"{len(high_mem_pods)} pods using >1Gi memory"
            })
        
        # Check for pending pods
        if pods.get('pending', 0) > 0:
            health_score -= 5
            issues.append({
                "severity": "Info",
                "title": f"{pods.get('pending')} Pods Pending",
                "description": "Pods waiting to be scheduled"
            })
        
        summary = "Cluster health analysis (AI unavailable - using rule-based fallback)"
        if health_score >= 90:
            summary = "Cluster is healthy with minor issues"
        elif health_score >= 70:
            summary = "Cluster has some issues requiring attention"
        else:
            summary = "Cluster has significant issues requiring immediate attention"
        
        return {
            "health_score": max(health_score, 0),
            "summary": summary,
            "issues": issues if issues else [{
                "severity": "Info",
                "title": "No Issues Detected",
                "description": "Cluster appears healthy"
            }],
            "predictions": [],
            "recommendations": recommendations if recommendations else [{
                "priority": "low",
                "action": "Continue monitoring",
                "command": "kubectl get pods --all-namespaces"
            }]
        }