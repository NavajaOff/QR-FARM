#!/bin/bash
# Script helper para builds estables de Docker
# Deshabilita BuildKit para evitar timeouts de auth.docker.io

set -e

echo "🔧 Deshabilitando BuildKit para builds más estables..."
export DOCKER_BUILDKIT=0
export COMPOSE_DOCKER_CLI_BUILD=0

echo "📦 Construyendo servicios..."
docker compose build "$@"

echo "✅ Build completado exitosamente"
