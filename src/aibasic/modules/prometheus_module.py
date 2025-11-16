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


class PrometheusModule:
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
