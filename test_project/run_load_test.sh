#!/bin/bash

set -e  # Exit immediately if a command fails

echo "🚀 Starts load test..."
locust -f test_project/books/locustfile.py --headless -u 100 -r 5 --run-time 1m --csv results --html load_tests/report.html