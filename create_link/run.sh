# /usr/bin/env bash

echo ""
echo "💻 Backend API: http://localhost:8000"
echo "📋 Next steps:"
if [ "$FRONTEND" = "web" ]; then\
    echo "   1. Visit http://localhost:3000 in your browser, and create a new link.";\
elif [ "$FRONTEND" = "ios" ]; then\
    echo "   1. Open the iOS frontend Xcode project: 'create_link/frontend/ios/Create Link.xcodeproj'";\
    echo "   2. Build and run the project in the Simulator.";\
    echo "   3. Create a new link with the Simulator.";\
elif [ "$FRONTEND" = "android" ]; then\
    echo "   1. TODO";\
elif [ "$FRONTEND" = "react_native" ]; then\
    echo "   1. TODO";\
fi

RUN_TARGETS="backend_$BACKEND"
if [ "$FRONTEND" = "web" ]; then\
    RUN_TARGETS="$RUN_TARGETS frontend_web"
fi

docker compose \
    -f docker-compose.yml \
    up --build --remove-orphans $RUN_TARGETS
