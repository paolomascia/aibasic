#!/bin/bash
# AIbasic Docker - Stop Script

set -e

echo "🛑 Stopping AIbasic Docker Environment..."
echo ""

docker-compose down

echo ""
echo "✅ All services stopped"
echo ""
echo "💡 To remove all data volumes, run:"
echo "   docker-compose down -v"
echo ""
echo "🚀 To start again, run:"
echo "   ./start.sh"
echo ""
