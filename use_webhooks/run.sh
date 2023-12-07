# /usr/bin/env bash

echo ""
echo "💻 Backend API: http://localhost:8000"
echo "📋 Next steps:"
echo "   1. Visit http://localhost:3000 in your browser, and create a new link.";\

RUN_TARGETS="backend_$BACKEND frontend"

docker compose \
    -f docker-compose.yml \
    up --build --remove-orphans $RUN_TARGETS
