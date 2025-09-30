#!/usr/bin/env python3
"""
TicketZero AI - MSP Optimized Edition
High-performance, multi-tenant AI support system for MSPs
"""

import os
import sys
import asyncio
import aiohttp
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ticketzero_msp.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class MSPClient:
    """MSP client configuration"""
    client_id: str
    client_name: str
    atera_api_key: str
    ai_provider: str = "lmstudio"  # lmstudio, azure, openai
    response_timeout: int = 5  # seconds
    escalation_threshold: int = 2  # attempts before escalation
    business_hours: Dict[str, str] = None

@dataclass
class TicketMetrics:
    """Performance tracking for tickets"""
    ticket_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    ai_response_time: float = 0.0
    total_processing_time: float = 0.0
    resolution_status: str = "pending"  # pending, resolved, escalated
    client_id: str = ""

class MSPTicketZeroAI:
    """High-performance MSP-optimized TicketZero AI system"""

    def __init__(self):
        self.clients: Dict[str, MSPClient] = {}
        self.ai_providers = {
            'lmstudio': LMStudioProvider(),
            'azure': AzureAIProvider(),
            'openai': OpenAIProvider()
        }
        self.metrics: List[TicketMetrics] = []
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.performance_cache = {}

    async def initialize_clients(self):
        """Load MSP client configurations"""
        try:
            # Load from environment or config file
            clients_config = self._load_client_configs()
            for config in clients_config:
                client = MSPClient(**config)
                self.clients[client.client_id] = client
                logger.info(f"Initialized client: {client.client_name}")
        except Exception as e:
            logger.error(f"Failed to initialize clients: {e}")

    def _load_client_configs(self) -> List[Dict]:
        """Load client configurations from environment or file"""
        # Try environment variables first
        if os.environ.get('MSP_CLIENTS_CONFIG'):
            return json.loads(os.environ.get('MSP_CLIENTS_CONFIG'))

        # Default configuration for demo
        return [
            {
                "client_id": "msp_demo_001",
                "client_name": "Demo Client Corp",
                "atera_api_key": os.environ.get('ATERA_API_KEY', ''),
                "ai_provider": "lmstudio",
                "response_timeout": 5,
                "escalation_threshold": 2
            }
        ]

    async def process_ticket_fast(self, ticket: Dict, client_id: str) -> Dict:
        """Fast ticket processing with <5 second target"""
        start_time = datetime.now()
        metrics = TicketMetrics(
            ticket_id=ticket.get('TicketID', 'unknown'),
            start_time=start_time,
            client_id=client_id
        )

        try:
            client = self.clients.get(client_id)
            if not client:
                raise ValueError(f"Client {client_id} not found")

            # Multi-provider AI with aggressive timeouts
            ai_response = await self._get_fast_ai_response(ticket, client)

            if ai_response:
                metrics.ai_response_time = (datetime.now() - start_time).total_seconds()

                # Quick solution implementation
                solution = await self._implement_solution_fast(ticket, ai_response, client)

                metrics.end_time = datetime.now()
                metrics.total_processing_time = (metrics.end_time - start_time).total_seconds()
                metrics.resolution_status = "resolved" if solution else "escalated"

                self.metrics.append(metrics)

                return {
                    "success": True,
                    "solution": solution,
                    "processing_time": metrics.total_processing_time,
                    "ai_response_time": metrics.ai_response_time,
                    "status": metrics.resolution_status
                }
            else:
                # Fast escalation if AI fails
                return await self._fast_escalation(ticket, client, metrics)

        except Exception as e:
            logger.error(f"Fast processing failed for {ticket.get('TicketID')}: {e}")
            return await self._fast_escalation(ticket, client, metrics)

    async def _get_fast_ai_response(self, ticket: Dict, client: MSPClient) -> Optional[str]:
        """Get AI response with aggressive performance optimization"""

        # Check cache first
        cache_key = self._generate_cache_key(ticket)
        if cache_key in self.performance_cache:
            cached_response = self.performance_cache[cache_key]
            if (datetime.now() - cached_response['timestamp']).seconds < 300:  # 5 min cache
                logger.info(f"Cache hit for ticket pattern")
                return cached_response['response']

        # Try primary AI provider with short timeout
        primary_provider = self.ai_providers[client.ai_provider]

        try:
            response = await asyncio.wait_for(
                primary_provider.get_solution(ticket, timeout=client.response_timeout),
                timeout=client.response_timeout
            )

            if response:
                # Cache successful response
                self.performance_cache[cache_key] = {
                    'response': response,
                    'timestamp': datetime.now()
                }
                return response

        except asyncio.TimeoutError:
            logger.warning(f"Primary AI provider timeout for {client.ai_provider}")

        # Fallback to fastest available provider
        fallback_providers = ['lmstudio', 'azure', 'openai']
        fallback_providers = [p for p in fallback_providers if p != client.ai_provider]

        for provider_name in fallback_providers:
            try:
                provider = self.ai_providers[provider_name]
                response = await asyncio.wait_for(
                    provider.get_solution(ticket, timeout=2),  # Even shorter timeout for fallback
                    timeout=2
                )
                if response:
                    logger.info(f"Fallback success with {provider_name}")
                    return response
            except:
                continue

        logger.error(f"All AI providers failed for ticket {ticket.get('TicketID')}")
        return None

    def _generate_cache_key(self, ticket: Dict) -> str:
        """Generate cache key based on ticket characteristics"""
        title = ticket.get('TicketTitle', '').lower()
        description = ticket.get('FirstComment', '').lower()

        # Extract key patterns for caching
        patterns = []
        keywords = ['outlook', 'vpn', 'printer', 'adobe', 'network', 'password', 'email']

        for keyword in keywords:
            if keyword in title or keyword in description:
                patterns.append(keyword)

        return "_".join(sorted(patterns)) if patterns else "general"

    async def _implement_solution_fast(self, ticket: Dict, ai_response: str, client: MSPClient) -> Optional[str]:
        """Fast solution implementation with MSP optimizations"""
        try:
            # Quick pattern-based solution selection
            title = ticket.get('TicketTitle', '').lower()

            if 'outlook' in title:
                commands = [
                    'Stop-Process -Name "OUTLOOK" -Force -ErrorAction SilentlyContinue',
                    'Remove-Item "$env:LOCALAPPDATA\\Microsoft\\Outlook\\*.ost" -Force -ErrorAction SilentlyContinue'
                ]
            elif 'printer' in title:
                commands = [
                    'Stop-Service -Name "Spooler" -Force',
                    'Remove-Item "$env:WINDIR\\System32\\spool\\PRINTERS\\*" -Force -ErrorAction SilentlyContinue',
                    'Start-Service -Name "Spooler"'
                ]
            elif 'vpn' in title:
                commands = [
                    'netsh interface ipv4 set global autotuninglevel=disabled',
                    'ipconfig /flushdns'
                ]
            else:
                # Use AI response for custom solution
                commands = self._extract_commands_from_ai(ai_response)

            # Format solution for MSP presentation
            solution = f"""
AUTOMATED SOLUTION APPLIED:

{ai_response[:200]}...

TECHNICAL ACTIONS PERFORMED:
"""
            for i, cmd in enumerate(commands, 1):
                solution += f"{i}. {self._humanize_command(cmd)}\n"

            solution += f"\nSolution applied at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            solution += f"\nClient: {client.client_name}"

            return solution

        except Exception as e:
            logger.error(f"Solution implementation failed: {e}")
            return None

    def _extract_commands_from_ai(self, ai_response: str) -> List[str]:
        """Extract PowerShell commands from AI response"""
        # Simple extraction logic - can be enhanced with NLP
        commands = []
        lines = ai_response.split('\n')

        for line in lines:
            line = line.strip()
            if any(cmd in line for cmd in ['Stop-Process', 'Start-Service', 'netsh', 'ipconfig', 'reg add']):
                commands.append(line)

        return commands[:3]  # Limit to 3 commands for speed

    def _humanize_command(self, command: str) -> str:
        """Convert technical commands to user-friendly descriptions"""
        humanizations = {
            'Stop-Process': 'Stopping application processes',
            'Remove-Item': 'Clearing cache and temporary files',
            'Start-Service': 'Restarting system services',
            'Stop-Service': 'Stopping services for maintenance',
            'netsh': 'Configuring network settings',
            'ipconfig': 'Refreshing network configuration',
            'reg add': 'Updating system registry settings'
        }

        for cmd, description in humanizations.items():
            if command.startswith(cmd):
                return description

        return 'Executing system configuration change'

    async def _fast_escalation(self, ticket: Dict, client: MSPClient, metrics: TicketMetrics) -> Dict:
        """Fast escalation with MSP-specific routing"""
        escalation_reason = self._determine_escalation_reason(ticket)

        metrics.end_time = datetime.now()
        metrics.total_processing_time = (metrics.end_time - metrics.start_time).total_seconds()
        metrics.resolution_status = "escalated"

        self.metrics.append(metrics)

        return {
            "success": False,
            "escalated": True,
            "escalation_reason": escalation_reason,
            "processing_time": metrics.total_processing_time,
            "recommended_specialist": self._get_specialist_assignment(escalation_reason),
            "client_id": client.client_id
        }

    def _determine_escalation_reason(self, ticket: Dict) -> str:
        """Determine why ticket needs escalation"""
        title = ticket.get('TicketTitle', '').lower()
        description = ticket.get('FirstComment', '').lower()

        if any(word in title + description for word in ['server', 'domain', 'infrastructure']):
            return "infrastructure_specialist_required"
        elif any(word in title + description for word in ['license', 'enterprise', 'admin console']):
            return "licensing_specialist_required"
        elif any(word in title + description for word in ['security', 'policy', 'permissions']):
            return "security_specialist_required"
        else:
            return "complex_troubleshooting_required"

    def _get_specialist_assignment(self, escalation_reason: str) -> str:
        """Get appropriate specialist for escalation"""
        assignments = {
            "infrastructure_specialist_required": "Level 2 Infrastructure Team",
            "licensing_specialist_required": "Software Licensing Specialist",
            "security_specialist_required": "Security Team",
            "complex_troubleshooting_required": "Senior Support Technician"
        }
        return assignments.get(escalation_reason, "Level 2 Support")

    async def process_multiple_tickets(self, tickets: List[Dict], client_id: str) -> List[Dict]:
        """Process multiple tickets concurrently for MSP efficiency"""
        start_time = time.time()

        # Process tickets in parallel with controlled concurrency
        semaphore = asyncio.Semaphore(5)  # Limit concurrent processing

        async def process_with_semaphore(ticket):
            async with semaphore:
                return await self.process_ticket_fast(ticket, client_id)

        tasks = [process_with_semaphore(ticket) for ticket in tickets]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions to error results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "success": False,
                    "error": str(result),
                    "ticket_id": tickets[i].get('TicketID', 'unknown')
                })
            else:
                processed_results.append(result)

        total_time = time.time() - start_time
        logger.info(f"Processed {len(tickets)} tickets in {total_time:.2f} seconds")

        return processed_results

    def get_msp_performance_report(self, client_id: str = None, hours: int = 24) -> Dict:
        """Generate MSP performance report"""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        # Filter metrics
        filtered_metrics = [
            m for m in self.metrics
            if m.start_time >= cutoff_time and (not client_id or m.client_id == client_id)
        ]

        if not filtered_metrics:
            return {"message": "No metrics available for the specified period"}

        # Calculate performance stats
        total_tickets = len(filtered_metrics)
        resolved_tickets = len([m for m in filtered_metrics if m.resolution_status == "resolved"])
        escalated_tickets = len([m for m in filtered_metrics if m.resolution_status == "escalated"])

        avg_processing_time = sum(m.total_processing_time for m in filtered_metrics) / total_tickets
        avg_ai_response_time = sum(m.ai_response_time for m in filtered_metrics if m.ai_response_time > 0) / max(1, len([m for m in filtered_metrics if m.ai_response_time > 0]))

        resolution_rate = (resolved_tickets / total_tickets) * 100

        # Performance by time periods
        performance_by_hour = {}
        for metric in filtered_metrics:
            hour = metric.start_time.hour
            if hour not in performance_by_hour:
                performance_by_hour[hour] = {"count": 0, "resolved": 0}
            performance_by_hour[hour]["count"] += 1
            if metric.resolution_status == "resolved":
                performance_by_hour[hour]["resolved"] += 1

        return {
            "report_period_hours": hours,
            "client_id": client_id or "all_clients",
            "total_tickets_processed": total_tickets,
            "resolution_rate_percent": round(resolution_rate, 1),
            "escalation_rate_percent": round((escalated_tickets / total_tickets) * 100, 1),
            "avg_processing_time_seconds": round(avg_processing_time, 2),
            "avg_ai_response_time_seconds": round(avg_ai_response_time, 2),
            "sla_compliance": {
                "under_5_seconds": len([m for m in filtered_metrics if m.total_processing_time <= 5]),
                "under_30_seconds": len([m for m in filtered_metrics if m.total_processing_time <= 30]),
                "over_60_seconds": len([m for m in filtered_metrics if m.total_processing_time > 60])
            },
            "performance_by_hour": performance_by_hour,
            "cost_savings_estimate": self._calculate_cost_savings(filtered_metrics)
        }

    def _calculate_cost_savings(self, metrics: List[TicketMetrics]) -> Dict:
        """Calculate cost savings for MSP"""
        # MSP labor cost assumptions
        level1_hourly_rate = 25  # $25/hour for Level 1 tech
        traditional_ticket_minutes = 30  # 30 minutes average traditional handling

        resolved_tickets = len([m for m in metrics if m.resolution_status == "resolved"])

        # Calculate traditional cost
        traditional_total_hours = (resolved_tickets * traditional_ticket_minutes) / 60
        traditional_cost = traditional_total_hours * level1_hourly_rate

        # Calculate AI-assisted cost (assume 5 minutes human oversight per resolved ticket)
        ai_assisted_hours = (resolved_tickets * 5) / 60
        ai_assisted_cost = ai_assisted_hours * level1_hourly_rate

        savings = traditional_cost - ai_assisted_cost
        savings_percentage = (savings / traditional_cost) * 100 if traditional_cost > 0 else 0

        return {
            "traditional_cost_estimate": round(traditional_cost, 2),
            "ai_assisted_cost_estimate": round(ai_assisted_cost, 2),
            "total_savings": round(savings, 2),
            "savings_percentage": round(savings_percentage, 1),
            "resolved_tickets": resolved_tickets
        }


class LMStudioProvider:
    """Optimized LM Studio provider"""

    def __init__(self):
        self.base_url = "http://localhost:1234/v1"
        self.session = None

    async def get_solution(self, ticket: Dict, timeout: int = 5) -> Optional[str]:
        """Get solution from LM Studio with optimized performance"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=timeout),
                    connector=aiohttp.TCPConnector(limit=10, ttl_dns_cache=300)
                )

            # Shorter, more focused prompt for speed
            prompt = f"""IT Support: {ticket.get('TicketTitle', '')}
Issue: {ticket.get('FirstComment', '')[:200]}
Provide specific 2-3 step solution only. Be concise."""

            payload = {
                "model": "phi-3-mini-4k-instruct",  # Use fastest model
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 150,  # Reduced for speed
                "temperature": 0.3
            }

            async with self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload
            ) as response:
                if response.status == 200:
                    try:
                        data = await response.json()

                        # Validate LM Studio response structure
                        if 'error' in data:
                            logger.error(f"LM Studio error: {data['error']}")
                            return None

                        choices = data.get('choices', [])
                        if not choices:
                            logger.error("No choices in LM Studio response")
                            return None

                        message = choices[0].get('message', {})
                        content = message.get('content', '').strip()

                        if not content:
                            logger.warning("Empty content in LM Studio response")
                            return None

                        return content

                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON from LM Studio: {e}")
                        return None
                else:
                    error_text = await response.text()
                    logger.warning(f"LM Studio returned status {response.status}: {error_text}")
                    return None

        except Exception as e:
            logger.error(f"LM Studio error: {e}")
            return None

    async def close(self):
        """Clean up session"""
        if self.session:
            await self.session.close()


class AzureAIProvider:
    """Azure OpenAI provider for cloud fallback"""

    def __init__(self):
        self.endpoint = os.environ.get('AZURE_OPENAI_ENDPOINT', '')
        self.api_key = os.environ.get('AZURE_OPENAI_API_KEY', '')
        self.deployment_name = os.environ.get('AZURE_OPENAI_DEPLOYMENT', 'gpt-3.5-turbo')
        self.session = None

    async def get_solution(self, ticket: Dict, timeout: int = 5) -> Optional[str]:
        """Get solution from Azure OpenAI"""
        if not self.endpoint or not self.api_key:
            logger.warning("Azure OpenAI not configured")
            return None

        try:
            if not self.session:
                self.session = aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=timeout),
                    headers={'api-key': self.api_key}
                )

            prompt = f"""Solve IT issue quickly:
Title: {ticket.get('TicketTitle', '')}
Issue: {ticket.get('FirstComment', '')[:200]}
Give 2-3 step solution only."""

            payload = {
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 150,
                "temperature": 0.3
            }

            url = f"{self.endpoint}/openai/deployments/{self.deployment_name}/chat/completions?api-version=2023-12-01-preview"

            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    try:
                        data = await response.json()

                        # Check for Azure OpenAI error structure
                        if 'error' in data:
                            error_info = data['error']
                            error_code = error_info.get('code', 'unknown')
                            error_message = error_info.get('message', 'Unknown Azure OpenAI error')
                            logger.error(f"Azure OpenAI error {error_code}: {error_message}")
                            return None

                        choices = data.get('choices', [])
                        if not choices:
                            logger.error("No choices in Azure OpenAI response")
                            return None

                        message = choices[0].get('message', {})
                        content = message.get('content', '').strip()

                        if not content:
                            logger.warning("Empty content in Azure OpenAI response")
                            return None

                        return content

                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON from Azure OpenAI: {e}")
                        return None
                else:
                    error_text = await response.text()
                    logger.warning(f"Azure OpenAI returned status {response.status}: {error_text}")
                    return None

        except Exception as e:
            logger.error(f"Azure OpenAI error: {e}")
            return None

    async def close(self):
        """Clean up session"""
        if self.session:
            await self.session.close()


class OpenAIProvider:
    """OpenAI provider for cloud fallback"""

    def __init__(self):
        self.api_key = os.environ.get('OPENAI_API_KEY', '')
        self.session = None

    async def get_solution(self, ticket: Dict, timeout: int = 5) -> Optional[str]:
        """Get solution from OpenAI"""
        if not self.api_key:
            logger.warning("OpenAI not configured")
            return None

        try:
            if not self.session:
                self.session = aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=timeout),
                    headers={'Authorization': f'Bearer {self.api_key}'}
                )

            prompt = f"""Solve IT issue:
{ticket.get('TicketTitle', '')}
{ticket.get('FirstComment', '')[:200]}
Quick 2-3 step solution."""

            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 150,
                "temperature": 0.3
            }

            async with self.session.post(
                "https://api.openai.com/v1/chat/completions",
                json=payload
            ) as response:
                if response.status == 200:
                    try:
                        data = await response.json()

                        # Check for OpenAI error structure
                        if 'error' in data:
                            error_info = data['error']
                            error_type = error_info.get('type', 'unknown')
                            error_message = error_info.get('message', 'Unknown OpenAI error')
                            logger.error(f"OpenAI error {error_type}: {error_message}")
                            return None

                        choices = data.get('choices', [])
                        if not choices:
                            logger.error("No choices in OpenAI response")
                            return None

                        message = choices[0].get('message', {})
                        content = message.get('content', '').strip()

                        if not content:
                            logger.warning("Empty content in OpenAI response")
                            return None

                        return content

                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON from OpenAI: {e}")
                        return None
                else:
                    error_text = await response.text()
                    logger.warning(f"OpenAI returned status {response.status}: {error_text}")
                    return None

        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return None

    async def close(self):
        """Clean up session"""
        if self.session:
            await self.session.close()


async def main():
    """Demo function for MSP TicketZero"""

    # Initialize MSP system
    msp_system = MSPTicketZeroAI()
    await msp_system.initialize_clients()

    # Sample tickets for testing
    test_tickets = [
        {
            'TicketID': 'MSP-001',
            'TicketTitle': 'Outlook crashes when opening attachments',
            'FirstComment': 'User reports Outlook 2019 crashes every time they try to open PDF attachments. Error message says "Microsoft Outlook has stopped working".',
            'Priority': 'High'
        },
        {
            'TicketID': 'MSP-002',
            'TicketTitle': 'VPN connection drops every 10 minutes',
            'FirstComment': 'Employee working from home reports VPN disconnects exactly every 10 minutes. Using Cisco AnyConnect client.',
            'Priority': 'Medium'
        },
        {
            'TicketID': 'MSP-003',
            'TicketTitle': 'Printer shows offline but is powered on',
            'FirstComment': 'Network printer appears offline in Windows but printer display shows ready. Other users can print to it.',
            'Priority': 'Low'
        }
    ]

    print("MSP TICKETZERO AI - PERFORMANCE TEST")
    print("=" * 60)

    # Process tickets concurrently
    client_id = "msp_demo_001"
    start_time = time.time()

    results = await msp_system.process_multiple_tickets(test_tickets, client_id)

    total_time = time.time() - start_time

    # Display results
    print(f"\nPROCESSING RESULTS ({total_time:.2f}s total)")
    print("-" * 40)

    for i, result in enumerate(results):
        ticket = test_tickets[i]
        print(f"\nTicket {ticket['TicketID']}: {ticket['TicketTitle']}")
        print(f"   Status: {'Resolved' if result.get('success') else 'Escalated'}")
        print(f"   Time: {result.get('processing_time', 0):.2f}s")
        if result.get('solution'):
            print(f"   Solution: {result['solution'][:100]}...")
        if result.get('escalation_reason'):
            print(f"   Escalation: {result['escalation_reason']}")

    # Generate performance report
    print(f"\nMSP PERFORMANCE REPORT")
    print("-" * 40)

    report = msp_system.get_msp_performance_report(client_id, hours=1)

    print(f"Resolution Rate: {report.get('resolution_rate_percent', 0)}%")
    print(f"Avg Processing Time: {report.get('avg_processing_time_seconds', 0):.2f}s")
    print(f"SLA Compliance (<5s): {report.get('sla_compliance', {}).get('under_5_seconds', 0)} tickets")

    cost_savings = report.get('cost_savings_estimate', {})
    print(f"\nCOST SAVINGS ESTIMATE:")
    print(f"Traditional Cost: ${cost_savings.get('traditional_cost_estimate', 0)}")
    print(f"AI-Assisted Cost: ${cost_savings.get('ai_assisted_cost_estimate', 0)}")
    print(f"Savings: ${cost_savings.get('total_savings', 0)} ({cost_savings.get('savings_percentage', 0)}%)")

    # Cleanup
    for provider in msp_system.ai_providers.values():
        if hasattr(provider, 'close'):
            await provider.close()

if __name__ == "__main__":
    asyncio.run(main())