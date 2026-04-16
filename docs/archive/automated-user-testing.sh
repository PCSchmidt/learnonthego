#!/bin/bash
# Automated User Testing Script for Multi-Provider AI
# Tests critical user journeys and validates cost optimization

set -e

echo "🧪 Starting automated user testing for Multi-Provider AI..."

# Configuration
BACKEND_URL="${BACKEND_URL:-https://learnonthego-production.up.railway.app}"
FRONTEND_URL="${FRONTEND_URL:-https://learnonthego-bice.vercel.app}"
TEST_EMAIL="test-$(date +%s)@example.com"
TEST_PASSWORD="TestPass123!"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Helper functions
success() { echo -e "${GREEN}✅ $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; }
warning() { echo -e "${YELLOW}⚠️ $1${NC}"; }
info() { echo -e "${BLUE}ℹ️ $1${NC}"; }

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0
TOTAL_TESTS=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo ""
    info "Test $TOTAL_TESTS: $test_name"
    
    if eval "$test_command"; then
        success "PASSED: $test_name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        error "FAILED: $test_name"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Test 1: System Health Check
test_system_health() {
    # Backend health
    if ! curl -f --silent --max-time 10 "$BACKEND_URL/health" > /dev/null; then
        return 1
    fi
    
    # Frontend accessibility
    if ! curl -f --silent --max-time 10 "$FRONTEND_URL" > /dev/null; then
        return 1
    fi
    
    return 0
}

# Test 2: User Registration
test_user_registration() {
    local response
    response=$(curl -s -X POST "$BACKEND_URL/api/auth/register" \
        -H "Content-Type: application/json" \
        -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\",\"confirm_password\":\"$TEST_PASSWORD\",\"full_name\":\"Test User\"}")
    
    if echo "$response" | grep -q "access_token"; then
        # Extract token for later tests
        ACCESS_TOKEN=$(echo "$response" | grep -o '"access_token":"[^"]*"' | sed 's/"access_token":"//' | sed 's/"//')
        return 0
    fi
    
    return 1
}

# Test 3: Multi-Provider Dashboard Access
test_dashboard_access() {
    local response
    response=$(curl -s -H "Authorization: Bearer $ACCESS_TOKEN" "$BACKEND_URL/api/multi-provider/dashboard")
    
    if echo "$response" | grep -q "provider_status"; then
        return 0
    fi
    
    return 1
}

# Test 4: Provider Status Monitoring
test_provider_status() {
    local response
    response=$(curl -s -H "Authorization: Bearer $ACCESS_TOKEN" "$BACKEND_URL/api/multi-provider/provider-status")
    
    # Check if response contains provider data
    if echo "$response" | grep -q "provider" && echo "$response" | grep -q "status"; then
        # Count providers
        local provider_count
        provider_count=$(echo "$response" | grep -o '"provider"' | wc -l)
        
        if [ "$provider_count" -ge 5 ]; then  # Should have at least 5 providers
            info "Found $provider_count AI providers"
            return 0
        fi
    fi
    
    return 1
}

# Test 5: Cost Analysis Functionality
test_cost_analysis() {
    local response
    response=$(curl -s -X POST "$BACKEND_URL/api/multi-provider/analyze-costs" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $ACCESS_TOKEN" \
        -d '{"topic":"Introduction to Machine Learning","duration":15,"difficulty":"beginner","quality_tier":"standard"}')
    
    # Check for cost analysis data
    if echo "$response" | grep -q "recommended_providers" && echo "$response" | grep -q "potential_savings"; then
        # Extract savings information
        local savings
        savings=$(echo "$response" | grep -o '"potential_savings":[0-9.]*' | sed 's/"potential_savings"://')
        
        if [ "$savings" ] && (( $(echo "$savings >= 0" | bc -l) )); then
            info "Cost analysis shows potential savings: \$${savings}"
            return 0
        fi
    fi
    
    return 1
}

# Test 6: Provider Recommendations
test_provider_recommendations() {
    local response
    response=$(curl -s -X POST "$BACKEND_URL/api/multi-provider/recommend-providers" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $ACCESS_TOKEN" \
        -d '{"topic":"Advanced React Native Development","duration":30,"difficulty":"advanced","quality_tier":"premium"}')
    
    # Check for recommendation data
    if echo "$response" | grep -q "llm_provider" && echo "$response" | grep -q "tts_provider"; then
        # Extract recommended providers
        local llm_provider
        local tts_provider
        llm_provider=$(echo "$response" | grep -o '"llm_provider":"[^"]*"' | head -1 | sed 's/"llm_provider":"//' | sed 's/"//')
        tts_provider=$(echo "$response" | grep -o '"tts_provider":"[^"]*"' | head -1 | sed 's/"tts_provider":"//' | sed 's/"//')
        
        info "Recommended LLM: $llm_provider, TTS: $tts_provider"
        return 0
    fi
    
    return 1
}

# Test 7: Cost Estimation
test_cost_estimation() {
    local response
    response=$(curl -s -X POST "$BACKEND_URL/api/multi-provider/estimate-cost" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $ACCESS_TOKEN" \
        -d '{"topic":"Quick JavaScript Tutorial","duration":10}')
    
    # Check for cost estimation
    if echo "$response" | grep -q "estimated_cost"; then
        local cost
        cost=$(echo "$response" | grep -o '"estimated_cost":[0-9.]*' | sed 's/"estimated_cost"://')
        
        if [ "$cost" ] && (( $(echo "$cost >= 0" | bc -l) )); then
            info "Estimated cost: \$${cost}"
            return 0
        fi
    fi
    
    return 1
}

# Test 8: User Preferences Management
test_user_preferences() {
    # Get current preferences
    local get_response
    get_response=$(curl -s -H "Authorization: Bearer $ACCESS_TOKEN" "$BACKEND_URL/api/multi-provider/user-preferences")
    
    if echo "$get_response" | grep -q "preferred_quality_tier"; then
        # Update preferences
        local update_response
        update_response=$(curl -s -X PUT "$BACKEND_URL/api/multi-provider/user-preferences" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $ACCESS_TOKEN" \
            -d '{"preferred_quality_tier":"premium","auto_optimize_costs":true,"max_cost_per_lecture":1.0}')
        
        if echo "$update_response" | grep -q "preferred_quality_tier"; then
            return 0
        fi
    fi
    
    return 1
}

# Test 9: Performance Benchmarking
test_performance() {
    local start_time
    local end_time
    local response_time
    
    # Test API response time
    start_time=$(date +%s%N)
    curl -f --silent --max-time 30 "$BACKEND_URL/api/multi-provider/provider-status" \
        -H "Authorization: Bearer $ACCESS_TOKEN" > /dev/null
    end_time=$(date +%s%N)
    
    response_time=$(( (end_time - start_time) / 1000000 ))  # Convert to milliseconds
    
    info "Provider status API response time: ${response_time}ms"
    
    # Should respond within 5 seconds (5000ms)
    if [ "$response_time" -lt 5000 ]; then
        return 0
    fi
    
    return 1
}

# Test 10: Error Handling
test_error_handling() {
    # Test invalid authentication
    local response
    response=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "Authorization: Bearer invalid_token" \
        "$BACKEND_URL/api/multi-provider/dashboard")
    
    if [ "$response" = "401" ]; then
        # Test invalid cost analysis data
        response=$(curl -s -o /dev/null -w "%{http_code}" \
            -X POST "$BACKEND_URL/api/multi-provider/analyze-costs" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $ACCESS_TOKEN" \
            -d '{"invalid":"data"}')
        
        if [ "$response" = "422" ]; then  # Validation error
            return 0
        fi
    fi
    
    return 1
}

# Run all tests
echo "🚀 Starting comprehensive user testing suite..."
echo "Backend URL: $BACKEND_URL"
echo "Frontend URL: $FRONTEND_URL"
echo ""

run_test "System Health Check" "test_system_health"
run_test "User Registration" "test_user_registration"
run_test "Multi-Provider Dashboard Access" "test_dashboard_access"
run_test "Provider Status Monitoring" "test_provider_status"
run_test "Cost Analysis Functionality" "test_cost_analysis"
run_test "Provider Recommendations" "test_provider_recommendations"
run_test "Cost Estimation" "test_cost_estimation"
run_test "User Preferences Management" "test_user_preferences"
run_test "Performance Benchmarking" "test_performance"
run_test "Error Handling" "test_error_handling"

# Performance monitoring
echo ""
info "Running extended performance monitoring..."

# Monitor API endpoints
endpoints=(
    "/health"
    "/api/multi-provider/provider-status"
    "/api/auth/me"
)

for endpoint in "${endpoints[@]}"; do
    start_time=$(date +%s%N)
    
    if [ "$endpoint" = "/health" ]; then
        curl -f --silent --max-time 10 "$BACKEND_URL$endpoint" > /dev/null
    else
        curl -f --silent --max-time 10 "$BACKEND_URL$endpoint" \
            -H "Authorization: Bearer $ACCESS_TOKEN" > /dev/null
    fi
    
    end_time=$(date +%s%N)
    response_time=$(( (end_time - start_time) / 1000000 ))
    
    info "$endpoint response time: ${response_time}ms"
done

# Test Summary
echo ""
echo "📊 Test Results Summary"
echo "======================"
echo "Total Tests: $TOTAL_TESTS"
echo "Passed: $TESTS_PASSED"
echo "Failed: $TESTS_FAILED"
echo "Success Rate: $(( TESTS_PASSED * 100 / TOTAL_TESTS ))%"

if [ $TESTS_FAILED -eq 0 ]; then
    echo ""
    success "🎉 ALL TESTS PASSED!"
    echo ""
    info "Multi-Provider AI system is ready for production users!"
    echo ""
    echo "Key Features Validated:"
    echo "✅ User authentication and registration"
    echo "✅ Multi-provider AI dashboard"
    echo "✅ Real-time cost analysis"
    echo "✅ Provider recommendations"
    echo "✅ Cost optimization engine"
    echo "✅ User preferences management"
    echo "✅ Performance benchmarks met"
    echo "✅ Error handling robustness"
    echo ""
    echo "🚀 Ready to launch beta testing program!"
    exit 0
else
    echo ""
    error "Some tests failed. Please review and fix issues before production launch."
    echo ""
    echo "Failed tests need attention:"
    echo "- Check backend logs for detailed error information"
    echo "- Verify database connectivity and migrations"
    echo "- Ensure all environment variables are properly set"
    echo "- Test individual API endpoints manually"
    exit 1
fi
