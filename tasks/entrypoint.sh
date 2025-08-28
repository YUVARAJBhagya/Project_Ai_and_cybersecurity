#!/bin/bash

# Entrypoint script for A4S Evaluation Service
# Supports multiple modes: server, worker, or combined

set -e

# Function to construct Redis URL
construct_redis_url() {
    local redis_host="${REDIS_HOST:-localhost}"
    local redis_port="${REDIS_PORT:-6379}"
    local redis_ssl="${REDIS_SSL:-false}"
    local redis_auth_enabled="${REDIS_AUTH_ENABLED:-false}"
    
    if [ "$redis_ssl" = "true" ]; then
        local protocol="rediss"
    else
        local protocol="redis"
    fi
    
    if [ "$redis_auth_enabled" = "true" ] && [ -n "$REDIS_AUTH_TOKEN" ]; then
        export REDIS_BACKEND_URL="${protocol}://:${REDIS_AUTH_TOKEN}@${redis_host}:${redis_port}/0"
    else
        export REDIS_BACKEND_URL="${protocol}://${redis_host}:${redis_port}/0"
    fi
}

# Function to construct RabbitMQ URL
construct_mq_url() {
    local mq_username="${MQ_USERNAME:-guest}"
    local mq_use_ssl="${MQ_USE_SSL:-false}"
    
    if [ "$mq_use_ssl" = "true" ] && [ -n "$MQ_AMQPS_ENDPOINT" ]; then
        local endpoint="$MQ_AMQPS_ENDPOINT"
        local protocol="amqps"
        local port="5671"
    else
        local endpoint="${MQ_AMQP_ENDPOINT:-amqp://localhost:5672}"
        local protocol="amqp"
        local port="5672"
    fi
    
    # Extract host from endpoint
    local mq_host=$(echo "$endpoint" | sed -E 's/^[a-z]+:\/\/([^:\/]+).*/\1/')
    
    if [ -n "$MQ_PASSWORD" ]; then
        export CELERY_BROKER_URL="${protocol}://${mq_username}:${MQ_PASSWORD}@${mq_host}:${port}//"
    else
        export CELERY_BROKER_URL="${protocol}://${mq_username}@${mq_host}:${port}//"
    fi
}

# Function to wait for dependencies
wait_for_dependencies() {
    # Wait for Redis
    if [ -n "$REDIS_HOST" ]; then
        echo "Waiting for Redis at $REDIS_HOST:${REDIS_PORT:-6379}..."
        timeout 30 bash -c "until nc -z $REDIS_HOST ${REDIS_PORT:-6379}; do sleep 1; done" || {
            echo "Redis not reachable at $REDIS_HOST:${REDIS_PORT:-6379}"
        }
    fi
    
    # Wait for RabbitMQ
    local mq_host=$(echo "${MQ_AMQP_ENDPOINT:-localhost}" | sed -E 's/^[a-z]+:\/\/([^:\/]+).*/\1/')
    if [ -n "$mq_host" ]; then
        echo "Waiting for RabbitMQ at $mq_host..."
        timeout 30 bash -c "until nc -z $mq_host 5672; do sleep 1; done" || {
            echo "RabbitMQ not reachable at $mq_host:5672"
        }
    fi
}

# Function to start FastAPI server
start_server() {
    echo "Starting FastAPI evaluation server..."
    exec uvicorn a4s_eval.main:app --host 0.0.0.0 --port 8001
}

# Function to start Celery worker
start_worker() {
    echo "Starting Celery worker..."
    exec celery -A a4s_eval.celery_worker worker --loglevel=info --concurrency=1 --hostname=worker@%h
}

# Function to start both server and worker
start_combined() {
    echo "Starting combined server and worker..."
    
    # Start Celery worker in background
    echo "Starting Celery worker in background..."
    celery -A a4s_eval.celery_worker worker --loglevel=info --concurrency=1 --hostname=worker@%h &
    
    # Wait a moment for worker to start
    sleep 5
    
    # Start FastAPI server in foreground
    echo "Starting FastAPI server..."
    exec uvicorn a4s_eval.main:app --host 0.0.0.0 --port 8001
}

# Main function
main() {
    # Construct connection URLs
    construct_redis_url
    construct_mq_url
    
    # Wait for dependencies
    wait_for_dependencies
    
    # Start based on mode
    case "${1:-server}" in
        "server")
            start_server
            ;;
        "worker")
            start_worker
            ;;
        "combined")
            start_combined
            ;;
    esac
}

# Execute main function with all arguments
main "$@"
