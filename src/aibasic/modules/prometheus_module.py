"""
Prometheus Module for AIbasic

This module provides comprehensive Prometheus monitoring and observability capabilities.
It enables metric collection, exposition, and querying from Prometheus servers.

Features:
- Metric Types: Counter, Gauge, Histogram, Summary
- Metric Collection: Increment, set, observe, time operations
- Metric Exposition: HTTP endpoint for Prometheus scraping
- PromQL Queries: Query Prometheus server with PromQL
- Labels: Multi-dimensional metrics with labels
- Pushgateway: Push metrics to Prometheus Pushgateway
- Custom Collectors: Register custom metric collectors
- Metric Registry: Manage multiple metric registries

Author: AIbasic Team
License: MIT
"""

import threading
import time
import os
from typing import Optional, Dict, List, Any, Union
from prometheus_client import (
    Counter, Gauge, Histogram, Summary,
    CollectorRegistry, push_to_gateway, delete_from_gateway,
    start_http_server, generate_latest, REGISTRY
)
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily
from prometheus_api_client import PrometheusConnect
import requests
from .module_base import AIbasicModuleBase


class PrometheusModule(AIbasicModuleBase):
    """
    Prometheus module for monitoring and observability.

    Provides comprehensive Prometheus integration including:
    - Creating and managing metrics (Counter, Gauge, Histogram, Summary)
    - Exposing metrics via HTTP endpoint
    - Querying Prometheus server with PromQL
    - Pushing metrics to Pushgateway
    - Multi-dimensional labels
    """

    _instance = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls):
        """Singleton pattern - only one instance allowed."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize Prometheus module with configuration."""
        if self._initialized:
            return

        with self._lock:
            if self._initialized:
                return

            # Load configuration
            self._load_config()

            # Metric storage
            self._metrics = {}
            self._registry = CollectorRegistry() if self.use_custom_registry else REGISTRY

            # Prometheus client for queries
            self._prometheus_client = None

            # HTTP server for metric exposition
            self._http_server_started = False

            self._initialized = True

    def _load_config(self):
        """Load configuration from environment or config file."""
        # Prometheus server settings (for queries)
        self.prometheus_url = os.getenv('PROMETHEUS_URL', 'http://localhost:9090')
        self.prometheus_headers = {}

        # Metric exposition settings
        self.exposition_port = int(os.getenv('PROMETHEUS_EXPOSITION_PORT', '8000'))
        self.exposition_addr = os.getenv('PROMETHEUS_EXPOSITION_ADDR', '0.0.0.0')

        # Pushgateway settings
        self.pushgateway_url = os.getenv('PROMETHEUS_PUSHGATEWAY_URL', 'localhost:9091')
        self.pushgateway_job = os.getenv('PROMETHEUS_PUSHGATEWAY_JOB', 'aibasic')

        # Default metric settings
        self.default_namespace = os.getenv('PROMETHEUS_NAMESPACE', 'aibasic')
        self.default_subsystem = os.getenv('PROMETHEUS_SUBSYSTEM', '')

        # Registry settings
        self.use_custom_registry = os.getenv('PROMETHEUS_CUSTOM_REGISTRY', 'false').lower() == 'true'

        # Auto-start HTTP server
        self.auto_start_http = os.getenv('PROMETHEUS_AUTO_START_HTTP', 'false').lower() == 'true'

    @property
    def prometheus_client(self):
        """Get Prometheus API client (lazy-loaded)."""
        if self._prometheus_client is None:
            try:
                self._prometheus_client = PrometheusConnect(
                    url=self.prometheus_url,
                    headers=self.prometheus_headers,
                    disable_ssl=False
                )
            except Exception as e:
                raise RuntimeError(f"Failed to connect to Prometheus: {e}")
        return self._prometheus_client

    def _get_metric_name(self, name: str, namespace: Optional[str] = None,
                         subsystem: Optional[str] = None) -> str:
        """Build full metric name with namespace and subsystem."""
        parts = []
        if namespace or self.default_namespace:
            parts.append(namespace or self.default_namespace)
        if subsystem or self.default_subsystem:
            parts.append(subsystem or self.default_subsystem)
        parts.append(name)
        return '_'.join(parts)

    # ============================================================================
    # Metric Creation
    # ============================================================================

    def create_counter(self, name: str, description: str,
                      labels: Optional[List[str]] = None,
                      namespace: Optional[str] = None,
                      subsystem: Optional[str] = None) -> str:
        """
        Create a Counter metric.

        Args:
            name: Metric name
            description: Metric description
            labels: Label names for multi-dimensional metrics
            namespace: Metric namespace (default: from config)
            subsystem: Metric subsystem (default: from config)

        Returns:
            Metric identifier
        """
        try:
            metric_name = self._get_metric_name(name, namespace, subsystem)

            if metric_name in self._metrics:
                return metric_name

            counter = Counter(
                name=metric_name,
                documentation=description,
                labelnames=labels or [],
                registry=self._registry
            )

            self._metrics[metric_name] = {
                'type': 'counter',
                'metric': counter,
                'labels': labels or []
            }

            return metric_name
        except Exception as e:
            raise RuntimeError(f"Failed to create counter: {e}")

    def create_gauge(self, name: str, description: str,
                    labels: Optional[List[str]] = None,
                    namespace: Optional[str] = None,
                    subsystem: Optional[str] = None) -> str:
        """
        Create a Gauge metric.

        Args:
            name: Metric name
            description: Metric description
            labels: Label names for multi-dimensional metrics
            namespace: Metric namespace
            subsystem: Metric subsystem

        Returns:
            Metric identifier
        """
        try:
            metric_name = self._get_metric_name(name, namespace, subsystem)

            if metric_name in self._metrics:
                return metric_name

            gauge = Gauge(
                name=metric_name,
                documentation=description,
                labelnames=labels or [],
                registry=self._registry
            )

            self._metrics[metric_name] = {
                'type': 'gauge',
                'metric': gauge,
                'labels': labels or []
            }

            return metric_name
        except Exception as e:
            raise RuntimeError(f"Failed to create gauge: {e}")

    def create_histogram(self, name: str, description: str,
                        buckets: Optional[List[float]] = None,
                        labels: Optional[List[str]] = None,
                        namespace: Optional[str] = None,
                        subsystem: Optional[str] = None) -> str:
        """
        Create a Histogram metric.

        Args:
            name: Metric name
            description: Metric description
            buckets: Histogram buckets (default: [.005, .01, .025, .05, .075, .1, .25, .5, .75, 1.0, 2.5, 5.0, 7.5, 10.0, +Inf])
            labels: Label names
            namespace: Metric namespace
            subsystem: Metric subsystem

        Returns:
            Metric identifier
        """
        try:
            metric_name = self._get_metric_name(name, namespace, subsystem)

            if metric_name in self._metrics:
                return metric_name

            histogram = Histogram(
                name=metric_name,
                documentation=description,
                labelnames=labels or [],
                buckets=buckets or (.005, .01, .025, .05, .075, .1, .25, .5, .75, 1.0, 2.5, 5.0, 7.5, 10.0),
                registry=self._registry
            )

            self._metrics[metric_name] = {
                'type': 'histogram',
                'metric': histogram,
                'labels': labels or [],
                'buckets': buckets
            }

            return metric_name
        except Exception as e:
            raise RuntimeError(f"Failed to create histogram: {e}")

    def create_summary(self, name: str, description: str,
                      labels: Optional[List[str]] = None,
                      namespace: Optional[str] = None,
                      subsystem: Optional[str] = None) -> str:
        """
        Create a Summary metric.

        Args:
            name: Metric name
            description: Metric description
            labels: Label names
            namespace: Metric namespace
            subsystem: Metric subsystem

        Returns:
            Metric identifier
        """
        try:
            metric_name = self._get_metric_name(name, namespace, subsystem)

            if metric_name in self._metrics:
                return metric_name

            summary = Summary(
                name=metric_name,
                documentation=description,
                labelnames=labels or [],
                registry=self._registry
            )

            self._metrics[metric_name] = {
                'type': 'summary',
                'metric': summary,
                'labels': labels or []
            }

            return metric_name
        except Exception as e:
            raise RuntimeError(f"Failed to create summary: {e}")

    # ============================================================================
    # Metric Operations
    # ============================================================================

    def counter_inc(self, metric_name: str, value: float = 1.0,
                   labels: Optional[Dict[str, str]] = None):
        """
        Increment a counter.

        Args:
            metric_name: Counter name
            value: Increment value (default: 1.0)
            labels: Label values
        """
        try:
            if metric_name not in self._metrics:
                raise ValueError(f"Metric '{metric_name}' not found")

            metric_info = self._metrics[metric_name]
            if metric_info['type'] != 'counter':
                raise ValueError(f"Metric '{metric_name}' is not a counter")

            counter = metric_info['metric']

            if labels:
                counter.labels(**labels).inc(value)
            else:
                counter.inc(value)
        except Exception as e:
            raise RuntimeError(f"Failed to increment counter: {e}")

    def gauge_set(self, metric_name: str, value: float,
                 labels: Optional[Dict[str, str]] = None):
        """
        Set gauge value.

        Args:
            metric_name: Gauge name
            value: Gauge value
            labels: Label values
        """
        try:
            if metric_name not in self._metrics:
                raise ValueError(f"Metric '{metric_name}' not found")

            metric_info = self._metrics[metric_name]
            if metric_info['type'] != 'gauge':
                raise ValueError(f"Metric '{metric_name}' is not a gauge")

            gauge = metric_info['metric']

            if labels:
                gauge.labels(**labels).set(value)
            else:
                gauge.set(value)
        except Exception as e:
            raise RuntimeError(f"Failed to set gauge: {e}")

    def gauge_inc(self, metric_name: str, value: float = 1.0,
                 labels: Optional[Dict[str, str]] = None):
        """Increment gauge value."""
        try:
            if metric_name not in self._metrics:
                raise ValueError(f"Metric '{metric_name}' not found")

            metric_info = self._metrics[metric_name]
            if metric_info['type'] != 'gauge':
                raise ValueError(f"Metric '{metric_name}' is not a gauge")

            gauge = metric_info['metric']

            if labels:
                gauge.labels(**labels).inc(value)
            else:
                gauge.inc(value)
        except Exception as e:
            raise RuntimeError(f"Failed to increment gauge: {e}")

    def gauge_dec(self, metric_name: str, value: float = 1.0,
                 labels: Optional[Dict[str, str]] = None):
        """Decrement gauge value."""
        try:
            if metric_name not in self._metrics:
                raise ValueError(f"Metric '{metric_name}' not found")

            metric_info = self._metrics[metric_name]
            if metric_info['type'] != 'gauge':
                raise ValueError(f"Metric '{metric_name}' is not a gauge")

            gauge = metric_info['metric']

            if labels:
                gauge.labels(**labels).dec(value)
            else:
                gauge.dec(value)
        except Exception as e:
            raise RuntimeError(f"Failed to decrement gauge: {e}")

    def histogram_observe(self, metric_name: str, value: float,
                         labels: Optional[Dict[str, str]] = None):
        """
        Record observation in histogram.

        Args:
            metric_name: Histogram name
            value: Observed value
            labels: Label values
        """
        try:
            if metric_name not in self._metrics:
                raise ValueError(f"Metric '{metric_name}' not found")

            metric_info = self._metrics[metric_name]
            if metric_info['type'] != 'histogram':
                raise ValueError(f"Metric '{metric_name}' is not a histogram")

            histogram = metric_info['metric']

            if labels:
                histogram.labels(**labels).observe(value)
            else:
                histogram.observe(value)
        except Exception as e:
            raise RuntimeError(f"Failed to observe histogram: {e}")

    def summary_observe(self, metric_name: str, value: float,
                       labels: Optional[Dict[str, str]] = None):
        """
        Record observation in summary.

        Args:
            metric_name: Summary name
            value: Observed value
            labels: Label values
        """
        try:
            if metric_name not in self._metrics:
                raise ValueError(f"Metric '{metric_name}' not found")

            metric_info = self._metrics[metric_name]
            if metric_info['type'] != 'summary':
                raise ValueError(f"Metric '{metric_name}' is not a summary")

            summary = metric_info['metric']

            if labels:
                summary.labels(**labels).observe(value)
            else:
                summary.observe(value)
        except Exception as e:
            raise RuntimeError(f"Failed to observe summary: {e}")

    def histogram_time(self, metric_name: str, labels: Optional[Dict[str, str]] = None):
        """
        Get context manager for timing code blocks.

        Args:
            metric_name: Histogram name
            labels: Label values

        Returns:
            Context manager for timing
        """
        if metric_name not in self._metrics:
            raise ValueError(f"Metric '{metric_name}' not found")

        metric_info = self._metrics[metric_name]
        if metric_info['type'] != 'histogram':
            raise ValueError(f"Metric '{metric_name}' is not a histogram")

        histogram = metric_info['metric']

        if labels:
            return histogram.labels(**labels).time()
        else:
            return histogram.time()

    # ============================================================================
    # Metric Exposition
    # ============================================================================

    def start_http_server(self, port: Optional[int] = None, addr: Optional[str] = None):
        """
        Start HTTP server to expose metrics for Prometheus scraping.

        Args:
            port: HTTP port (default: from config)
            addr: Bind address (default: from config)
        """
        try:
            if self._http_server_started:
                return

            port = port or self.exposition_port
            addr = addr or self.exposition_addr

            start_http_server(port, addr, registry=self._registry)
            self._http_server_started = True
        except Exception as e:
            raise RuntimeError(f"Failed to start HTTP server: {e}")

    def get_metrics(self) -> bytes:
        """
        Get current metrics in Prometheus exposition format.

        Returns:
            Metrics in text format
        """
        try:
            return generate_latest(self._registry)
        except Exception as e:
            raise RuntimeError(f"Failed to generate metrics: {e}")

    # ============================================================================
    # Pushgateway Operations
    # ============================================================================

    def push_to_gateway(self, job: Optional[str] = None,
                       grouping_key: Optional[Dict[str, str]] = None,
                       gateway_url: Optional[str] = None):
        """
        Push metrics to Prometheus Pushgateway.

        Args:
            job: Job name (default: from config)
            grouping_key: Additional grouping labels
            gateway_url: Pushgateway URL (default: from config)
        """
        try:
            job = job or self.pushgateway_job
            gateway_url = gateway_url or self.pushgateway_url

            push_to_gateway(
                gateway=gateway_url,
                job=job,
                registry=self._registry,
                grouping_key=grouping_key
            )
        except Exception as e:
            raise RuntimeError(f"Failed to push to gateway: {e}")

    def delete_from_gateway(self, job: Optional[str] = None,
                           grouping_key: Optional[Dict[str, str]] = None,
                           gateway_url: Optional[str] = None):
        """
        Delete metrics from Pushgateway.

        Args:
            job: Job name
            grouping_key: Grouping labels
            gateway_url: Pushgateway URL
        """
        try:
            job = job or self.pushgateway_job
            gateway_url = gateway_url or self.pushgateway_url

            delete_from_gateway(
                gateway=gateway_url,
                job=job,
                grouping_key=grouping_key
            )
        except Exception as e:
            raise RuntimeError(f"Failed to delete from gateway: {e}")

    # ============================================================================
    # PromQL Queries
    # ============================================================================

    def query(self, promql: str) -> List[Dict[str, Any]]:
        """
        Execute instant PromQL query.

        Args:
            promql: PromQL query string

        Returns:
            Query results
        """
        try:
            result = self.prometheus_client.custom_query(query=promql)
            return result
        except Exception as e:
            raise RuntimeError(f"Query failed: {e}")

    def query_range(self, promql: str, start_time: Union[str, float],
                   end_time: Union[str, float], step: str) -> List[Dict[str, Any]]:
        """
        Execute range PromQL query.

        Args:
            promql: PromQL query string
            start_time: Start time (timestamp or RFC3339)
            end_time: End time (timestamp or RFC3339)
            step: Query resolution step width

        Returns:
            Query results
        """
        try:
            result = self.prometheus_client.custom_query_range(
                query=promql,
                start_time=start_time,
                end_time=end_time,
                step=step
            )
            return result
        except Exception as e:
            raise RuntimeError(f"Range query failed: {e}")

    def get_metric_range_data(self, metric_name: str,
                             label_config: Optional[Dict[str, str]] = None,
                             start_time: Optional[Union[str, float]] = None,
                             end_time: Optional[Union[str, float]] = None,
                             step: str = '1m') -> List[Dict[str, Any]]:
        """
        Get range data for specific metric.

        Args:
            metric_name: Metric name
            label_config: Label matchers
            start_time: Start time
            end_time: End time
            step: Query step

        Returns:
            Metric data
        """
        try:
            result = self.prometheus_client.get_metric_range_data(
                metric_name=metric_name,
                label_config=label_config,
                start_time=start_time,
                end_time=end_time,
                step=step
            )
            return result
        except Exception as e:
            raise RuntimeError(f"Failed to get metric range data: {e}")

    def get_current_metric_value(self, metric_name: str,
                                 label_config: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        Get current value of metric.

        Args:
            metric_name: Metric name
            label_config: Label matchers

        Returns:
            Current metric values
        """
        try:
            result = self.prometheus_client.get_current_metric_value(
                metric_name=metric_name,
                label_config=label_config
            )
            return result
        except Exception as e:
            raise RuntimeError(f"Failed to get current metric value: {e}")

    # ============================================================================
    # Utility Methods
    # ============================================================================

    def list_metrics(self) -> List[str]:
        """List all registered metrics."""
        return list(self._metrics.keys())

    def get_metric_info(self, metric_name: str) -> Dict[str, Any]:
        """
        Get metric information.

        Args:
            metric_name: Metric name

        Returns:
            Metric information
        """
        if metric_name not in self._metrics:
            raise ValueError(f"Metric '{metric_name}' not found")

        info = self._metrics[metric_name].copy()
        info.pop('metric')  # Don't expose internal metric object
        return info

    def metric_exists(self, metric_name: str) -> bool:
        """Check if metric exists."""
        return metric_name in self._metrics

    def get_registry(self):
        """Get the metric registry."""
        return self._registry

    # ============================================================================
    # Module Metadata
    # ============================================================================

    @classmethod
    def get_metadata(cls):
        """Get module metadata for compiler prompt generation."""
        from aibasic.modules.module_base import ModuleMetadata
        return ModuleMetadata(
            name="Prometheus",
            task_type="prometheus",
            description="Prometheus monitoring and observability with metric collection (Counter, Gauge, Histogram, Summary), HTTP exposition, PromQL queries, Pushgateway support, and multi-dimensional labels",
            version="1.0.0",
            keywords=["prometheus", "monitoring", "metrics", "observability", "counter", "gauge", "histogram", "summary", "promql", "pushgateway", "labels", "scraping", "time-series", "alerting"],
            dependencies=["prometheus-client>=0.14.0", "prometheus-api-client>=0.5.0"]
        )

    @classmethod
    def get_usage_notes(cls):
        """Get usage notes and best practices."""
        return [
            "Module uses singleton pattern - one instance per application",
            "Supports four metric types: Counter (monotonic), Gauge (up/down), Histogram (distributions), Summary (quantiles)",
            "Metrics can have multi-dimensional labels for flexible querying",
            "Counter metrics only increase - never use for values that can decrease",
            "Gauge metrics can go up and down - use for current values like temperature, memory usage",
            "Histogram metrics track distributions with configurable buckets - use for request durations, response sizes",
            "Summary metrics calculate quantiles - similar to histograms but computed on client side",
            "Metric names automatically prefixed with namespace and subsystem if configured",
            "Configure PROMETHEUS_NAMESPACE to prefix all metrics with application namespace",
            "Configure PROMETHEUS_SUBSYSTEM for additional metric categorization",
            "HTTP server exposes metrics on /metrics endpoint for Prometheus scraping",
            "Start HTTP server with start_http_server() or set PROMETHEUS_AUTO_START_HTTP=true",
            "Default exposition port is 8000, configure with PROMETHEUS_EXPOSITION_PORT",
            "Pushgateway allows pushing metrics from short-lived jobs or batch jobs",
            "Use custom registry (PROMETHEUS_CUSTOM_REGISTRY=true) to isolate metrics from global registry",
            "PromQL queries require PROMETHEUS_URL pointing to Prometheus server",
            "Instant queries with query() return current metric values",
            "Range queries with query_range() return time-series data over time period",
            "Labels must be declared at metric creation time - cannot add new labels later",
            "Label values should have low cardinality to avoid high memory usage",
            "Histogram buckets should be chosen based on expected value distribution",
            "Use histogram_time() context manager for automatic duration tracking",
            "Metric names must match regex [a-zA-Z_:][a-zA-Z0-9_:]* according to Prometheus conventions",
            "Label names must match regex [a-zA-Z_][a-zA-Z0-9_]* (no colons in labels)",
        ]

    @classmethod
    def get_methods_info(cls):
        """Get information about available methods."""
        from aibasic.modules.module_base import MethodInfo
        return [
            MethodInfo(
                name="create_counter",
                description="Create a Counter metric that only increases (monotonic)",
                parameters={
                    "name": "str - Metric name (without namespace/subsystem prefix)",
                    "description": "str - Metric description for documentation",
                    "labels": "list[str] (optional) - Label names for multi-dimensional metrics",
                    "namespace": "str (optional) - Override default namespace",
                    "subsystem": "str (optional) - Override default subsystem"
                },
                returns="str - Full metric identifier (name with namespace/subsystem)",
                examples=[
                    'prometheus create_counter name "requests_total" description "Total HTTP requests"',
                    'prometheus create_counter name "errors" description "Error count" labels ["method", "status"]',
                    'prometheus create_counter name "jobs_completed" description "Completed jobs" namespace "batch" subsystem "processing"'
                ]
            ),
            MethodInfo(
                name="create_gauge",
                description="Create a Gauge metric that can increase or decrease",
                parameters={
                    "name": "str - Metric name",
                    "description": "str - Metric description",
                    "labels": "list[str] (optional) - Label names",
                    "namespace": "str (optional) - Override namespace",
                    "subsystem": "str (optional) - Override subsystem"
                },
                returns="str - Metric identifier",
                examples=[
                    'prometheus create_gauge name "temperature" description "Current temperature in Celsius"',
                    'prometheus create_gauge name "memory_usage" description "Memory usage in bytes" labels ["host", "process"]',
                    'prometheus create_gauge name "queue_size" description "Current queue depth"'
                ]
            ),
            MethodInfo(
                name="create_histogram",
                description="Create a Histogram metric for tracking distributions",
                parameters={
                    "name": "str - Metric name",
                    "description": "str - Metric description",
                    "buckets": "list[float] (optional) - Histogram bucket boundaries (default: [.005, .01, .025, .05, .075, .1, .25, .5, .75, 1.0, 2.5, 5.0, 7.5, 10.0])",
                    "labels": "list[str] (optional) - Label names",
                    "namespace": "str (optional) - Override namespace",
                    "subsystem": "str (optional) - Override subsystem"
                },
                returns="str - Metric identifier",
                examples=[
                    'prometheus create_histogram name "request_duration_seconds" description "HTTP request duration"',
                    'prometheus create_histogram name "response_size_bytes" description "Response size" buckets [100, 1000, 10000, 100000]',
                    'prometheus create_histogram name "query_duration" description "Query time" labels ["database", "query_type"]'
                ]
            ),
            MethodInfo(
                name="create_summary",
                description="Create a Summary metric for calculating quantiles",
                parameters={
                    "name": "str - Metric name",
                    "description": "str - Metric description",
                    "labels": "list[str] (optional) - Label names",
                    "namespace": "str (optional) - Override namespace",
                    "subsystem": "str (optional) - Override subsystem"
                },
                returns="str - Metric identifier",
                examples=[
                    'prometheus create_summary name "request_latency" description "Request latency in seconds"',
                    'prometheus create_summary name "batch_size" description "Batch processing size" labels ["job_type"]'
                ]
            ),
            MethodInfo(
                name="counter_inc",
                description="Increment a Counter metric",
                parameters={
                    "metric_name": "str - Counter identifier returned from create_counter",
                    "value": "float (optional) - Increment amount (default: 1.0)",
                    "labels": "dict[str, str] (optional) - Label values matching declared label names"
                },
                returns="None",
                examples=[
                    'prometheus counter_inc metric_name "aibasic_requests_total"',
                    'prometheus counter_inc metric_name "aibasic_requests_total" value 5',
                    'prometheus counter_inc metric_name "aibasic_errors" labels {"method": "GET", "status": "500"}'
                ]
            ),
            MethodInfo(
                name="gauge_set",
                description="Set Gauge metric to specific value",
                parameters={
                    "metric_name": "str - Gauge identifier",
                    "value": "float - New gauge value",
                    "labels": "dict[str, str] (optional) - Label values"
                },
                returns="None",
                examples=[
                    'prometheus gauge_set metric_name "aibasic_temperature" value 23.5',
                    'prometheus gauge_set metric_name "aibasic_memory_usage" value 1024000000 labels {"host": "server1", "process": "worker"}'
                ]
            ),
            MethodInfo(
                name="gauge_inc",
                description="Increment Gauge metric",
                parameters={
                    "metric_name": "str - Gauge identifier",
                    "value": "float (optional) - Increment amount (default: 1.0)",
                    "labels": "dict[str, str] (optional) - Label values"
                },
                returns="None",
                examples=[
                    'prometheus gauge_inc metric_name "aibasic_active_connections"',
                    'prometheus gauge_inc metric_name "aibasic_queue_size" value 10'
                ]
            ),
            MethodInfo(
                name="gauge_dec",
                description="Decrement Gauge metric",
                parameters={
                    "metric_name": "str - Gauge identifier",
                    "value": "float (optional) - Decrement amount (default: 1.0)",
                    "labels": "dict[str, str] (optional) - Label values"
                },
                returns="None",
                examples=[
                    'prometheus gauge_dec metric_name "aibasic_active_connections"',
                    'prometheus gauge_dec metric_name "aibasic_queue_size" value 5'
                ]
            ),
            MethodInfo(
                name="histogram_observe",
                description="Record observation in Histogram metric",
                parameters={
                    "metric_name": "str - Histogram identifier",
                    "value": "float - Observed value",
                    "labels": "dict[str, str] (optional) - Label values"
                },
                returns="None",
                examples=[
                    'prometheus histogram_observe metric_name "aibasic_request_duration_seconds" value 0.235',
                    'prometheus histogram_observe metric_name "aibasic_response_size_bytes" value 4096',
                    'prometheus histogram_observe metric_name "aibasic_query_duration" value 0.142 labels {"database": "users", "query_type": "select"}'
                ]
            ),
            MethodInfo(
                name="summary_observe",
                description="Record observation in Summary metric",
                parameters={
                    "metric_name": "str - Summary identifier",
                    "value": "float - Observed value",
                    "labels": "dict[str, str] (optional) - Label values"
                },
                returns="None",
                examples=[
                    'prometheus summary_observe metric_name "aibasic_request_latency" value 0.125',
                    'prometheus summary_observe metric_name "aibasic_batch_size" value 500 labels {"job_type": "import"}'
                ]
            ),
            MethodInfo(
                name="start_http_server",
                description="Start HTTP server to expose metrics for Prometheus scraping",
                parameters={
                    "port": "int (optional) - HTTP port (default: from PROMETHEUS_EXPOSITION_PORT or 8000)",
                    "addr": "str (optional) - Bind address (default: from PROMETHEUS_EXPOSITION_ADDR or 0.0.0.0)"
                },
                returns="None",
                examples=[
                    'prometheus start_http_server',
                    'prometheus start_http_server port 9090',
                    'prometheus start_http_server port 8080 addr "127.0.0.1"'
                ]
            ),
            MethodInfo(
                name="get_metrics",
                description="Get current metrics in Prometheus text exposition format",
                parameters={},
                returns="bytes - Metrics in Prometheus text format",
                examples=[
                    'prometheus get_metrics'
                ]
            ),
            MethodInfo(
                name="push_to_gateway",
                description="Push metrics to Prometheus Pushgateway for batch/short-lived jobs",
                parameters={
                    "job": "str (optional) - Job name (default: from PROMETHEUS_PUSHGATEWAY_JOB or 'aibasic')",
                    "grouping_key": "dict[str, str] (optional) - Additional grouping labels",
                    "gateway_url": "str (optional) - Pushgateway URL (default: from PROMETHEUS_PUSHGATEWAY_URL or 'localhost:9091')"
                },
                returns="None",
                examples=[
                    'prometheus push_to_gateway',
                    'prometheus push_to_gateway job "batch_import"',
                    'prometheus push_to_gateway job "backup" grouping_key {"instance": "server1"}',
                    'prometheus push_to_gateway job "ETL" gateway_url "pushgateway.example.com:9091"'
                ]
            ),
            MethodInfo(
                name="delete_from_gateway",
                description="Delete metrics from Prometheus Pushgateway",
                parameters={
                    "job": "str (optional) - Job name",
                    "grouping_key": "dict[str, str] (optional) - Grouping labels",
                    "gateway_url": "str (optional) - Pushgateway URL"
                },
                returns="None",
                examples=[
                    'prometheus delete_from_gateway job "batch_import"',
                    'prometheus delete_from_gateway job "backup" grouping_key {"instance": "server1"}'
                ]
            ),
            MethodInfo(
                name="query",
                description="Execute instant PromQL query against Prometheus server",
                parameters={
                    "promql": "str - PromQL query expression"
                },
                returns="list[dict] - Query results with metric labels and values",
                examples=[
                    'prometheus query promql "up"',
                    'prometheus query promql "rate(http_requests_total[5m])"',
                    'prometheus query promql "sum(rate(requests_total[1m])) by (method)"',
                    'prometheus query promql "avg_over_time(cpu_usage[1h])"'
                ]
            ),
            MethodInfo(
                name="query_range",
                description="Execute range PromQL query to get time-series data",
                parameters={
                    "promql": "str - PromQL query expression",
                    "start_time": "str|float - Start time (Unix timestamp or RFC3339 string)",
                    "end_time": "str|float - End time (Unix timestamp or RFC3339 string)",
                    "step": "str - Query resolution step width (e.g., '15s', '1m', '1h')"
                },
                returns="list[dict] - Time-series results with timestamps and values",
                examples=[
                    'prometheus query_range promql "cpu_usage" start_time "2024-01-01T00:00:00Z" end_time "2024-01-01T23:59:59Z" step "1m"',
                    'prometheus query_range promql "rate(requests_total[5m])" start_time 1704067200 end_time 1704153600 step "15s"'
                ]
            ),
            MethodInfo(
                name="get_metric_range_data",
                description="Get time-series data for specific metric with optional label filtering",
                parameters={
                    "metric_name": "str - Metric name to query",
                    "label_config": "dict[str, str] (optional) - Label matchers for filtering",
                    "start_time": "str|float (optional) - Start time",
                    "end_time": "str|float (optional) - End time",
                    "step": "str (optional) - Query step (default: '1m')"
                },
                returns="list[dict] - Metric time-series data",
                examples=[
                    'prometheus get_metric_range_data metric_name "cpu_usage"',
                    'prometheus get_metric_range_data metric_name "http_requests_total" label_config {"method": "GET", "status": "200"}',
                    'prometheus get_metric_range_data metric_name "memory_usage" start_time 1704067200 end_time 1704153600 step "5m"'
                ]
            ),
            MethodInfo(
                name="get_current_metric_value",
                description="Get current (latest) value of specific metric",
                parameters={
                    "metric_name": "str - Metric name",
                    "label_config": "dict[str, str] (optional) - Label matchers"
                },
                returns="list[dict] - Current metric values",
                examples=[
                    'prometheus get_current_metric_value metric_name "up"',
                    'prometheus get_current_metric_value metric_name "cpu_usage" label_config {"instance": "server1"}'
                ]
            ),
            MethodInfo(
                name="list_metrics",
                description="List all registered metric names",
                parameters={},
                returns="list[str] - Metric names",
                examples=[
                    'prometheus list_metrics'
                ]
            ),
            MethodInfo(
                name="get_metric_info",
                description="Get information about specific metric",
                parameters={
                    "metric_name": "str - Metric identifier"
                },
                returns="dict - Metric info with type, labels, buckets (for histogram)",
                examples=[
                    'prometheus get_metric_info metric_name "aibasic_requests_total"'
                ]
            ),
            MethodInfo(
                name="metric_exists",
                description="Check if metric exists",
                parameters={
                    "metric_name": "str - Metric identifier"
                },
                returns="bool - True if metric exists",
                examples=[
                    'prometheus metric_exists metric_name "aibasic_requests_total"'
                ]
            )
        ]

    @classmethod
    def get_examples(cls):
        """Get example AIbasic code snippets."""
        return [
            '''// Basic counter usage
prometheus = new prometheus
prometheus create_counter name "requests_total" description "Total requests"
prometheus counter_inc metric_name "aibasic_requests_total"
prometheus counter_inc metric_name "aibasic_requests_total" value 5''',

            '''// Counter with labels
prometheus = new prometheus
prometheus create_counter name "http_requests" description "HTTP requests by method and status" labels ["method", "status"]
prometheus counter_inc metric_name "aibasic_http_requests" labels {"method": "GET", "status": "200"}
prometheus counter_inc metric_name "aibasic_http_requests" labels {"method": "POST", "status": "201"}
prometheus counter_inc metric_name "aibasic_http_requests" labels {"method": "GET", "status": "500"}''',

            '''// Gauge for tracking current values
prometheus = new prometheus
prometheus create_gauge name "temperature" description "Current temperature" labels ["location"]
prometheus gauge_set metric_name "aibasic_temperature" value 23.5 labels {"location": "server_room"}
prometheus gauge_set metric_name "aibasic_temperature" value 18.2 labels {"location": "outdoor"}''',

            '''// Gauge increment/decrement
prometheus = new prometheus
prometheus create_gauge name "active_connections" description "Active connections"
prometheus gauge_inc metric_name "aibasic_active_connections"
prometheus gauge_inc metric_name "aibasic_active_connections" value 5
prometheus gauge_dec metric_name "aibasic_active_connections" value 2''',

            '''// Histogram for request durations
prometheus = new prometheus
prometheus create_histogram name "request_duration_seconds" description "HTTP request duration" labels ["endpoint"]
prometheus histogram_observe metric_name "aibasic_request_duration_seconds" value 0.123 labels {"endpoint": "/api/users"}
prometheus histogram_observe metric_name "aibasic_request_duration_seconds" value 0.456 labels {"endpoint": "/api/orders"}
prometheus histogram_observe metric_name "aibasic_request_duration_seconds" value 0.089 labels {"endpoint": "/api/users"}''',

            '''// Histogram with custom buckets
prometheus = new prometheus
buckets = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
prometheus create_histogram name "query_duration" description "Database query duration" buckets buckets
prometheus histogram_observe metric_name "aibasic_query_duration" value 0.234
prometheus histogram_observe metric_name "aibasic_query_duration" value 1.567
prometheus histogram_observe metric_name "aibasic_query_duration" value 0.089''',

            '''// Summary metric
prometheus = new prometheus
prometheus create_summary name "request_latency" description "Request latency" labels ["service"]
prometheus summary_observe metric_name "aibasic_request_latency" value 0.125 labels {"service": "api"}
prometheus summary_observe metric_name "aibasic_request_latency" value 0.234 labels {"service": "api"}
prometheus summary_observe metric_name "aibasic_request_latency" value 0.156 labels {"service": "database"}''',

            '''// Start HTTP server for scraping
prometheus = new prometheus
prometheus create_counter name "app_starts" description "Application starts"
prometheus counter_inc metric_name "aibasic_app_starts"
prometheus start_http_server port 8000
// Metrics now available at http://localhost:8000/metrics''',

            '''// Expose metrics without HTTP server
prometheus = new prometheus
prometheus create_gauge name "status" description "Application status"
prometheus gauge_set metric_name "aibasic_status" value 1
metrics_data = prometheus get_metrics
print metrics_data''',

            '''// Push to Pushgateway (for batch jobs)
prometheus = new prometheus
prometheus create_counter name "batch_processed" description "Batch records processed"
prometheus counter_inc metric_name "aibasic_batch_processed" value 1000
prometheus push_to_gateway job "nightly_import"''',

            '''// Push with grouping key
prometheus = new prometheus
prometheus create_gauge name "backup_size" description "Backup size in bytes"
prometheus gauge_set metric_name "aibasic_backup_size" value 1024000000
prometheus push_to_gateway job "backup" grouping_key {"instance": "db-server-1", "backup_type": "full"}''',

            '''// Delete metrics from Pushgateway
prometheus = new prometheus
prometheus delete_from_gateway job "batch_import"
prometheus delete_from_gateway job "backup" grouping_key {"instance": "db-server-1"}''',

            '''// Query Prometheus server (instant query)
prometheus = new prometheus
result = prometheus query promql "up"
print result
result = prometheus query promql "rate(http_requests_total[5m])"
print result''',

            '''// Advanced PromQL queries
prometheus = new prometheus
// Query request rate by method
result = prometheus query promql "sum(rate(http_requests_total[1m])) by (method)"
print result
// Query CPU usage average
result = prometheus query promql "avg_over_time(cpu_usage[1h])"
print result
// Query 95th percentile latency
result = prometheus query promql "histogram_quantile(0.95, rate(request_duration_seconds_bucket[5m]))"
print result''',

            '''// Range query for time-series data
prometheus = new prometheus
result = prometheus query_range promql "cpu_usage" start_time "2024-01-01T00:00:00Z" end_time "2024-01-01T23:59:59Z" step "1m"
foreach data in result {
    print data
}''',

            '''// Get specific metric range data
prometheus = new prometheus
result = prometheus get_metric_range_data metric_name "http_requests_total" label_config {"method": "GET"} step "5m"
foreach data in result {
    print data
}''',

            '''// Get current metric value
prometheus = new prometheus
result = prometheus get_current_metric_value metric_name "up"
print result
result = prometheus get_current_metric_value metric_name "cpu_usage" label_config {"instance": "server1"}
print result''',

            '''// Complete monitoring example
prometheus = new prometheus

// Create metrics
prometheus create_counter name "requests_total" description "Total requests" labels ["method", "status"]
prometheus create_histogram name "request_duration_seconds" description "Request duration" labels ["endpoint"]
prometheus create_gauge name "active_users" description "Currently active users"

// Track request
prometheus counter_inc metric_name "aibasic_requests_total" labels {"method": "GET", "status": "200"}
prometheus histogram_observe metric_name "aibasic_request_duration_seconds" value 0.234 labels {"endpoint": "/api/users"}
prometheus gauge_set metric_name "aibasic_active_users" value 42

// Expose metrics
prometheus start_http_server port 8000''',

            '''// Metric management
prometheus = new prometheus
prometheus create_counter name "events" description "Events counter"

// Check if metric exists
exists = prometheus metric_exists metric_name "aibasic_events"
print exists

// Get metric info
info = prometheus get_metric_info metric_name "aibasic_events"
print info

// List all metrics
metrics = prometheus list_metrics
foreach metric in metrics {
    print metric
}''',

            '''// Custom namespace and subsystem
prometheus = new prometheus
prometheus create_counter name "operations" description "Operations count" namespace "myapp" subsystem "api"
// Creates metric: myapp_api_operations
prometheus counter_inc metric_name "myapp_api_operations"''',

            '''// Multi-dimensional metrics with labels
prometheus = new prometheus
prometheus create_counter name "orders" description "Order count" labels ["region", "product_type", "status"]

prometheus counter_inc metric_name "aibasic_orders" labels {"region": "us-east", "product_type": "electronics", "status": "completed"}
prometheus counter_inc metric_name "aibasic_orders" labels {"region": "eu-west", "product_type": "books", "status": "pending"}
prometheus counter_inc metric_name "aibasic_orders" labels {"region": "us-west", "product_type": "electronics", "status": "completed"}''',

            '''// Error tracking with metrics
prometheus = new prometheus
prometheus create_counter name "errors_total" description "Total errors" labels ["error_type", "severity"]
prometheus create_gauge name "error_rate" description "Current error rate"

try {
    // Some operation that might fail
} catch error {
    prometheus counter_inc metric_name "aibasic_errors_total" labels {"error_type": "connection", "severity": "high"}
    prometheus gauge_set metric_name "aibasic_error_rate" value 0.05
}''',

            '''// Application lifecycle metrics
prometheus = new prometheus

// Application startup
prometheus create_counter name "app_starts_total" description "Application starts"
prometheus create_gauge name "app_info" description "Application information" labels ["version", "environment"]

prometheus counter_inc metric_name "aibasic_app_starts_total"
prometheus gauge_set metric_name "aibasic_app_info" value 1 labels {"version": "1.0.0", "environment": "production"}

// Expose metrics
prometheus start_http_server

// Application shutdown
prometheus gauge_set metric_name "aibasic_app_info" value 0''',

            '''// Query and analyze metrics
prometheus = new prometheus

// Get current values
uptime = prometheus get_current_metric_value metric_name "process_uptime_seconds"
print "Uptime: " + uptime

// Query request rate
rate = prometheus query promql "rate(http_requests_total[5m])"
print "Request rate: " + rate

// Query error percentage
error_pct = prometheus query promql "rate(http_requests_total{status=~\"5..\"}[5m]) / rate(http_requests_total[5m]) * 100"
print "Error percentage: " + error_pct'''
        ]
