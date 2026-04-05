#!/bin/bash
# Social Media Manager Plugin Regression Test Suite
# Runs against a live Agent Zero container with the plugin installed.
#
# Usage:
#   ./regression_test.sh                    # Test against default (a0-verify-active on port 50088)
#   ./regression_test.sh <container> <port> # Test against specific container
#
# Requires: docker, python3 (for JSON parsing)

CONTAINER="${1:-a0-verify-active}"
PORT="${2:-50088}"
BASE_URL="http://localhost:${PORT}"

PASSED=0
FAILED=0
SKIPPED=0
ERRORS=""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

pass() {
    PASSED=$((PASSED + 1))
    echo -e "  ${GREEN}PASS${NC} $1"
}

fail() {
    FAILED=$((FAILED + 1))
    ERRORS="${ERRORS}\n  - $1: $2"
    echo -e "  ${RED}FAIL${NC} $1 — $2"
}

skip() {
    SKIPPED=$((SKIPPED + 1))
    echo -e "  ${YELLOW}SKIP${NC} $1 — $2"
}

section() {
    echo ""
    echo -e "${CYAN}━━━ $1 ━━━${NC}"
}

# Helper: acquire CSRF token + session cookie from the container
CSRF_TOKEN=""
setup_csrf() {
    if [ -z "$CSRF_TOKEN" ]; then
        CSRF_TOKEN=$(docker exec "$CONTAINER" bash -c '
            curl -s -c /tmp/test_cookies.txt \
                -H "Origin: http://localhost" \
                "http://localhost/api/csrf_token" 2>/dev/null
        ' | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))" 2>/dev/null)
    fi
}

# Helper: curl the container's internal API (with CSRF token)
api() {
    local endpoint="$1"
    local data="${2:-}"
    setup_csrf
    if [ -n "$data" ]; then
        docker exec "$CONTAINER" curl -s -X POST "http://localhost/api/plugins/social_manager/${endpoint}" \
            -H "Content-Type: application/json" \
            -H "Origin: http://localhost" \
            -H "X-CSRF-Token: ${CSRF_TOKEN}" \
            -b /tmp/test_cookies.txt \
            -d "$data" 2>/dev/null
    else
        docker exec "$CONTAINER" curl -s "http://localhost/api/plugins/social_manager/${endpoint}" \
            -H "Origin: http://localhost" \
            -H "X-CSRF-Token: ${CSRF_TOKEN}" \
            -b /tmp/test_cookies.txt 2>/dev/null
    fi
}

# Helper: run Python inside the container
pyexec() {
    docker exec "$CONTAINER" bash -c "cd /a0 && PYTHONPATH=/a0 PYTHONWARNINGS=ignore /opt/venv-a0/bin/python3 -c \"$1\"" 2>&1
}

# Helper: check file exists inside container
container_file_exists() {
    docker exec "$CONTAINER" test -f "$1" 2>/dev/null
}

# Helper: check directory exists inside container
container_dir_exists() {
    docker exec "$CONTAINER" test -d "$1" 2>/dev/null
}

echo "========================================"
echo " Social Media Manager Regression Tests"
echo "========================================"
echo "Container: $CONTAINER"
echo "Port:      $PORT"
echo "Date:      $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

########################################
section "1. Container & Service Health"
########################################

# T1.1 Container running
if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
    pass "T1.1 Container '$CONTAINER' is running"
else
    fail "T1.1 Container '$CONTAINER' is not running" "Start it first"
    echo ""
    echo -e "${RED}FATAL: Container not running. Cannot proceed.${NC}"
    exit 1
fi

# T1.2 HTTP reachable
HTTP_STATUS=$(docker exec "$CONTAINER" curl -s -o /dev/null -w '%{http_code}' "http://localhost/" 2>/dev/null)
if [ "$HTTP_STATUS" = "200" ] || [ "$HTTP_STATUS" = "302" ]; then
    pass "T1.2 HTTP reachable (status: $HTTP_STATUS)"
else
    fail "T1.2 HTTP not reachable" "Got status: $HTTP_STATUS"
fi

# T1.3 Python venv
if docker exec "$CONTAINER" test -x /opt/venv-a0/bin/python 2>/dev/null; then
    pass "T1.3 Python venv available"
else
    fail "T1.3 Python venv not found" "/opt/venv-a0/bin/python missing"
fi

########################################
section "2. Plugin Installation"
########################################

PLUGIN_DIR="/a0/plugins/social_manager"
USR_DIR="/a0/usr/plugins/social_manager"

# T2.1 Plugin directory
if container_dir_exists "$PLUGIN_DIR" || container_dir_exists "$USR_DIR"; then
    pass "T2.1 Plugin directory exists"
else
    fail "T2.1 Plugin directory missing" "Neither $PLUGIN_DIR nor $USR_DIR"
fi

# T2.2 plugin.yaml
if container_file_exists "$PLUGIN_DIR/plugin.yaml" || container_file_exists "$USR_DIR/plugin.yaml"; then
    pass "T2.2 plugin.yaml exists"
else
    fail "T2.2 plugin.yaml missing" ""
fi

# T2.3 plugin.yaml name field
NAME_CHECK=$(pyexec "
import yaml
for p in ['$PLUGIN_DIR/plugin.yaml', '$USR_DIR/plugin.yaml']:
    try:
        d = yaml.safe_load(open(p))
        print(d.get('name', ''))
        break
    except: pass
")
if [ "$NAME_CHECK" = "social_manager" ]; then
    pass "T2.3 plugin.yaml name = 'social_manager'"
else
    fail "T2.3 plugin.yaml name field" "Expected 'social_manager', got '$NAME_CHECK'"
fi

# T2.4 Toggle file
if container_file_exists "$PLUGIN_DIR/.toggle-1" || container_file_exists "$USR_DIR/.toggle-1"; then
    pass "T2.4 .toggle-1 exists (plugin enabled)"
else
    fail "T2.4 .toggle-1 missing" "Plugin not enabled"
fi

# T2.5 Data directory
if container_dir_exists "$PLUGIN_DIR/data" || container_dir_exists "$USR_DIR/data"; then
    pass "T2.5 data/ directory exists"
else
    skip "T2.5 data/ directory" "Created on first use"
fi

########################################
section "3. Python Imports — Helpers"
########################################

# T3.1 content_adapter
RESULT=$(pyexec "from usr.plugins.social_manager.helpers.content_adapter import adapt_for_platform, split_for_threads, generate_platform_variants, preview_adaptations; print('ok')")
if [ "$RESULT" = "ok" ]; then
    pass "T3.1 content_adapter imports (adapt_for_platform, split_for_threads, generate_platform_variants, preview_adaptations)"
else
    fail "T3.1 content_adapter import" "$RESULT"
fi

# T3.2 social_manager_client
RESULT=$(pyexec "from usr.plugins.social_manager.helpers.social_manager_client import PLATFORMS, get_available_platforms, get_ready_platforms, resolve_platform_list, get_social_manager_config; print('ok')")
if [ "$RESULT" = "ok" ]; then
    pass "T3.2 social_manager_client imports (PLATFORMS, get_available_platforms, get_ready_platforms, resolve_platform_list)"
else
    fail "T3.2 social_manager_client import" "$RESULT"
fi

# T3.3 sanitize
RESULT=$(pyexec "from usr.plugins.social_manager.helpers.sanitize import validate_platform_list, format_cross_post_result, format_platform_status, format_schedule_entry; print('ok')")
if [ "$RESULT" = "ok" ]; then
    pass "T3.3 sanitize imports (validate_platform_list, format_cross_post_result, format_platform_status, format_schedule_entry)"
else
    fail "T3.3 sanitize import" "$RESULT"
fi

########################################
section "4. Content Adapter Unit Tests"
########################################

# T4.1 adapt_for_platform truncates long text
RESULT=$(pyexec "
from usr.plugins.social_manager.helpers.content_adapter import adapt_for_platform
text = 'A' * 500
result = adapt_for_platform(text, 'x', 280)
assert len(result) <= 280, f'Too long: {len(result)}'
assert result.endswith('\u2026'), f'No ellipsis: {result[-5:]}'
print('ok')
")
if [ "$RESULT" = "ok" ]; then
    pass "T4.1 adapt_for_platform truncates to char limit with ellipsis"
else
    fail "T4.1 Content adaptation truncation" "$RESULT"
fi

# T4.2 adapt_for_platform preserves short text
RESULT=$(pyexec "
from usr.plugins.social_manager.helpers.content_adapter import adapt_for_platform
text = 'Hello world'
result = adapt_for_platform(text, 'bluesky', 300)
assert result == text, f'Changed: {repr(result)}'
print('ok')
")
if [ "$RESULT" = "ok" ]; then
    pass "T4.2 Short text preserved unchanged"
else
    fail "T4.2 Short text preservation" "$RESULT"
fi

# T4.3 adapt_for_platform handles empty text
RESULT=$(pyexec "
from usr.plugins.social_manager.helpers.content_adapter import adapt_for_platform
result = adapt_for_platform('', 'x', 280)
assert result == '', f'Expected empty, got: {repr(result)}'
print('ok')
")
if [ "$RESULT" = "ok" ]; then
    pass "T4.3 Empty text returns empty"
else
    fail "T4.3 Empty text handling" "$RESULT"
fi

# T4.4 Per-platform char limits: X=280, Bluesky=300, Threads=500, LinkedIn=3000
RESULT=$(pyexec "
from usr.plugins.social_manager.helpers.content_adapter import adapt_for_platform
text = 'A' * 1000
for platform, limit in [('x', 280), ('bluesky', 300), ('threads', 500), ('linkedin', 3000)]:
    result = adapt_for_platform(text, platform, limit)
    assert len(result) <= limit, f'{platform}: {len(result)} > {limit}'
print('ok')
")
if [ "$RESULT" = "ok" ]; then
    pass "T4.4 Per-platform char limits enforced (x=280, bluesky=300, threads=500, linkedin=3000)"
else
    fail "T4.4 Per-platform char limits" "$RESULT"
fi

# T4.5 split_for_threads splits long text
RESULT=$(pyexec "
from usr.plugins.social_manager.helpers.content_adapter import split_for_threads
text = ' '.join(['word'] * 200)
chunks = split_for_threads(text, 280)
assert len(chunks) > 1, f'Expected >1 chunks, got {len(chunks)}'
for chunk in chunks:
    assert len(chunk) <= 280, f'Chunk too long: {len(chunk)}'
print('ok')
")
if [ "$RESULT" = "ok" ]; then
    pass "T4.5 split_for_threads splits long text into chunks <= limit"
else
    fail "T4.5 Thread splitting" "$RESULT"
fi

# T4.6 split_for_threads returns single item for short text
RESULT=$(pyexec "
from usr.plugins.social_manager.helpers.content_adapter import split_for_threads
chunks = split_for_threads('Short', 280)
assert len(chunks) == 1, f'Expected 1 chunk, got {len(chunks)}'
print('ok')
")
if [ "$RESULT" = "ok" ]; then
    pass "T4.6 Short text not split"
else
    fail "T4.6 Short text split check" "$RESULT"
fi

# T4.7 generate_platform_variants returns dict with platform keys
RESULT=$(pyexec "
from usr.plugins.social_manager.helpers.content_adapter import generate_platform_variants
platforms = [
    {'platform': 'x', 'char_limit': 280, 'supports_images': True, 'supports_video': True},
    {'platform': 'bluesky', 'char_limit': 300, 'supports_images': True, 'supports_video': False},
]
result = generate_platform_variants('Hello world', platforms)
assert isinstance(result, dict), f'Not a dict: {type(result)}'
assert 'x' in result and 'bluesky' in result, f'Missing keys: {result.keys()}'
print('ok')
")
if [ "$RESULT" = "ok" ]; then
    pass "T4.7 generate_platform_variants returns correct platform dict"
else
    fail "T4.7 Platform variants" "$RESULT"
fi

# T4.8 preview_adaptations returns truncation warnings
RESULT=$(pyexec "
from usr.plugins.social_manager.helpers.content_adapter import preview_adaptations
text = 'A' * 500
platforms = [{'platform': 'x', 'char_limit': 280, 'supports_images': True, 'supports_video': True}]
result = preview_adaptations(text, platforms)
assert len(result) == 1
assert result[0]['truncated'] == True
assert len(result[0]['warnings']) > 0
assert result[0]['adapted_length'] <= 280
print('ok')
")
if [ "$RESULT" = "ok" ]; then
    pass "T4.8 preview_adaptations generates truncation warnings"
else
    fail "T4.8 Preview truncation warnings" "$RESULT"
fi

# T4.9 preview_adaptations — no warnings for short text on long-limit platform
RESULT=$(pyexec "
from usr.plugins.social_manager.helpers.content_adapter import preview_adaptations
text = 'Short post'
platforms = [{'platform': 'reddit', 'char_limit': 40000, 'supports_images': True, 'supports_video': True}]
result = preview_adaptations(text, platforms)
assert result[0]['truncated'] == False
assert not any('truncat' in w.lower() for w in result[0]['warnings'])
print('ok')
")
if [ "$RESULT" = "ok" ]; then
    pass "T4.9 No truncation warnings for short text on Reddit"
else
    fail "T4.9 Short text no warnings" "$RESULT"
fi

########################################
section "5. Sanitize / Validation Unit Tests"
########################################

# T5.1 validate_platform_list accepts "all"
RESULT=$(pyexec "
from usr.plugins.social_manager.helpers.sanitize import validate_platform_list
ok, err, parsed = validate_platform_list('all')
assert ok and not err, f'ok={ok}, err={err}'
print('ok')
")
if [ "$RESULT" = "ok" ]; then
    pass "T5.1 validate_platform_list accepts 'all'"
else
    fail "T5.1 Validate 'all'" "$RESULT"
fi

# T5.2 validate_platform_list rejects unknown platform
RESULT=$(pyexec "
from usr.plugins.social_manager.helpers.sanitize import validate_platform_list
ok, err, parsed = validate_platform_list('fakebook,x')
assert not ok, f'Should have failed'
assert 'fakebook' in err, f'Error should mention fakebook: {err}'
print('ok')
")
if [ "$RESULT" = "ok" ]; then
    pass "T5.2 validate_platform_list rejects unknown platform"
else
    fail "T5.2 Validate unknown platform" "$RESULT"
fi

# T5.3 validate_platform_list accepts valid comma-separated list
RESULT=$(pyexec "
from usr.plugins.social_manager.helpers.sanitize import validate_platform_list
ok, err, parsed = validate_platform_list('bluesky,x,linkedin')
assert ok and not err, f'ok={ok}, err={err}'
assert parsed == ['bluesky', 'x', 'linkedin'], f'parsed={parsed}'
print('ok')
")
if [ "$RESULT" = "ok" ]; then
    pass "T5.3 validate_platform_list accepts valid list"
else
    fail "T5.3 Validate valid list" "$RESULT"
fi

# T5.4 format_cross_post_result formats success/failure
RESULT=$(pyexec "
from usr.plugins.social_manager.helpers.sanitize import format_cross_post_result
results = [
    {'platform': 'x', 'success': True, 'message': 'Posted'},
    {'platform': 'bluesky', 'success': False, 'message': 'Auth failed'},
]
out = format_cross_post_result(results)
assert 'OK' in out and 'FAIL' in out, f'Missing markers: {out[:200]}'
assert '1 succeeded' in out and '1 failed' in out, f'Missing counts: {out[:200]}'
print('ok')
")
if [ "$RESULT" = "ok" ]; then
    pass "T5.4 format_cross_post_result output correct"
else
    fail "T5.4 Cross-post result formatting" "$RESULT"
fi

# T5.5 format_platform_status produces table
RESULT=$(pyexec "
from usr.plugins.social_manager.helpers.sanitize import format_platform_status
platforms = [
    {'platform': 'x', 'installed': True, 'enabled': True, 'configured': True, 'ready': True},
    {'platform': 'bluesky', 'installed': True, 'enabled': False, 'configured': False, 'ready': False},
]
out = format_platform_status(platforms)
assert 'Platform Status' in out, f'Missing header: {out[:200]}'
assert '1/2' in out, f'Missing count: {out[:200]}'
print('ok')
")
if [ "$RESULT" = "ok" ]; then
    pass "T5.5 format_platform_status output correct"
else
    fail "T5.5 Platform status formatting" "$RESULT"
fi

########################################
section "6. Platform Registry"
########################################

# T6.1 PLATFORMS dict has 10 entries
RESULT=$(pyexec "
from usr.plugins.social_manager.helpers.social_manager_client import PLATFORMS
assert len(PLATFORMS) == 10, f'Expected 10, got {len(PLATFORMS)}'
print('ok')
")
if [ "$RESULT" = "ok" ]; then
    pass "T6.1 PLATFORMS registry has 10 entries"
else
    fail "T6.1 PLATFORMS count" "$RESULT"
fi

# T6.2 Each platform has required keys
RESULT=$(pyexec "
from usr.plugins.social_manager.helpers.social_manager_client import PLATFORMS
required = {'plugin', 'post_tool', 'char_limit', 'supports_images', 'supports_video'}
errors = []
for name, info in PLATFORMS.items():
    missing = required - set(info.keys())
    if missing:
        errors.append(f'{name}: missing {missing}')
assert not errors, '; '.join(errors)
print('ok')
")
if [ "$RESULT" = "ok" ]; then
    pass "T6.2 All platforms have required keys"
else
    fail "T6.2 Platform registry keys" "$RESULT"
fi

# T6.3 Char limits are positive integers
RESULT=$(pyexec "
from usr.plugins.social_manager.helpers.social_manager_client import PLATFORMS
for name, info in PLATFORMS.items():
    assert isinstance(info['char_limit'], int) and info['char_limit'] > 0, f'{name}: invalid limit {info[\"char_limit\"]}'
print('ok')
")
if [ "$RESULT" = "ok" ]; then
    pass "T6.3 All char_limits are positive integers"
else
    fail "T6.3 Char limit validation" "$RESULT"
fi

# T6.4 Expected platforms present
RESULT=$(pyexec "
from usr.plugins.social_manager.helpers.social_manager_client import PLATFORMS
expected = {'bluesky', 'x', 'reddit', 'facebook', 'threads', 'instagram', 'linkedin', 'youtube', 'pinterest', 'tiktok'}
actual = set(PLATFORMS.keys())
assert actual == expected, f'Mismatch: missing={expected-actual}, extra={actual-expected}'
print('ok')
")
if [ "$RESULT" = "ok" ]; then
    pass "T6.4 All 10 expected platforms present"
else
    fail "T6.4 Expected platforms" "$RESULT"
fi

########################################
section "7. API Endpoints"
########################################

# T7.1 Test API responds with platform data
TEST_RESP=$(api "social_manager_test" '{}')
TEST_OK=$(echo "$TEST_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print('ok' if 'total_platforms' in d else 'FAIL')" 2>/dev/null)
if [ "$TEST_OK" = "ok" ]; then
    pass "T7.1 social_manager_test API responds with platform data"
else
    fail "T7.1 Test API response" "$TEST_RESP"
fi

# T7.2 Test API returns 10 platforms
PLATFORM_CT=$(echo "$TEST_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('total_platforms',0))" 2>/dev/null)
if [ "$PLATFORM_CT" = "10" ]; then
    pass "T7.2 Test API reports 10 total platforms"
else
    fail "T7.2 Platform count in API" "Expected 10, got $PLATFORM_CT"
fi

# T7.3 Config API GET responds
CONFIG_RESP=$(api "social_manager_config_api" '')
CONFIG_OK=$(echo "$CONFIG_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print('ok' if 'error' not in d else d.get('error'))" 2>/dev/null)
if [ "$CONFIG_OK" = "ok" ]; then
    pass "T7.3 Config API GET responds"
else
    fail "T7.3 Config API GET" "$CONFIG_OK"
fi

# T7.4 Config API SET + GET roundtrip
SAVE_RESP=$(api "social_manager_config_api" '{"action":"set","config":{"adapt_content":false,"schedule":{"timezone":"US/Eastern"}}}')
SAVE_OK=$(echo "$SAVE_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print('ok' if d.get('ok') else d.get('error','FAIL'))" 2>/dev/null)
if [ "$SAVE_OK" = "ok" ]; then
    pass "T7.4a Config API SET succeeds"
else
    fail "T7.4a Config API SET" "$SAVE_OK"
fi

READ_RESP=$(api "social_manager_config_api" '')
READ_CHECK=$(echo "$READ_RESP" | python3 -c "
import sys,json
d=json.load(sys.stdin)
ok = d.get('adapt_content') == False and d.get('schedule',{}).get('timezone') == 'US/Eastern'
print('ok' if ok else f'FAIL: {d}')
" 2>/dev/null)
if [ "$READ_CHECK" = "ok" ]; then
    pass "T7.4b Config API roundtrip verified"
else
    fail "T7.4b Config API roundtrip" "$READ_CHECK"
fi

# T7.5 CSRF enforcement
CSRF_CHECK=$(docker exec "$CONTAINER" curl -s -X POST "http://localhost/api/plugins/social_manager/social_manager_test" \
    -H "Content-Type: application/json" \
    -d '{}' 2>/dev/null)
if echo "$CSRF_CHECK" | grep -qi "403\|forbidden\|csrf\|error"; then
    pass "T7.5 CSRF enforcement (no-token request blocked)"
else
    fail "T7.5 CSRF enforcement" "Request without CSRF token was not rejected"
fi

########################################
section "8. Tool Imports"
########################################

TOOLS=(
    "social_manager_post:SocialManagerPost"
    "social_manager_status:SocialManagerStatus"
    "social_manager_analytics:SocialManagerAnalytics"
    "social_manager_schedule:SocialManagerSchedule"
    "social_manager_adapt:SocialManagerAdapt"
)

for tool_spec in "${TOOLS[@]}"; do
    IFS=':' read -r tool_file tool_class <<< "$tool_spec"
    RESULT=$(pyexec "from usr.plugins.social_manager.tools.${tool_file} import ${tool_class}; print('ok')")
    if [ "$RESULT" = "ok" ]; then
        pass "T8 Tool: ${tool_class}"
    else
        fail "T8 Tool: ${tool_class}" "$RESULT"
    fi
done

########################################
section "9. Prompt Files"
########################################

PROMPTS=(
    "agent.system.tool_group.md"
    "agent.system.tool.social_manager_post.md"
    "agent.system.tool.social_manager_status.md"
    "agent.system.tool.social_manager_analytics.md"
    "agent.system.tool.social_manager_schedule.md"
    "agent.system.tool.social_manager_adapt.md"
)

for prompt in "${PROMPTS[@]}"; do
    if container_file_exists "$PLUGIN_DIR/prompts/$prompt" || container_file_exists "$USR_DIR/prompts/$prompt"; then
        pass "T9 Prompt: $prompt"
    else
        fail "T9 Prompt: $prompt" "File missing"
    fi
done

########################################
section "10. Skills"
########################################

SKILLS=("social-manager-campaign" "social-manager-monitor" "social-manager-publish")

for skill in "${SKILLS[@]}"; do
    if container_file_exists "$PLUGIN_DIR/skills/$skill/SKILL.md" || container_file_exists "$USR_DIR/skills/$skill/SKILL.md"; then
        pass "T10 Skill: $skill/SKILL.md"
    else
        fail "T10 Skill: $skill/SKILL.md" "File missing"
    fi
done

########################################
section "11. WebUI Integrity"
########################################

# T11.1 main.html exists
if container_file_exists "$PLUGIN_DIR/webui/main.html" || container_file_exists "$USR_DIR/webui/main.html"; then
    pass "T11.1 webui/main.html exists"
else
    fail "T11.1 webui/main.html" "File missing"
fi

# T11.2 config.html exists
if container_file_exists "$PLUGIN_DIR/webui/config.html" || container_file_exists "$USR_DIR/webui/config.html"; then
    pass "T11.2 webui/config.html exists"
else
    fail "T11.2 webui/config.html" "File missing"
fi

# T11.3 WebUI uses data-sm= attributes (not bare IDs)
SM_ATTR=$(pyexec "
content = ''
import os
for base in ['$PLUGIN_DIR', '$USR_DIR']:
    p = os.path.join(base, 'webui', 'main.html')
    if os.path.exists(p):
        content = open(p).read()
        break
count = content.count('data-sm=')
print(count)
" 2>/dev/null)
if [ -n "$SM_ATTR" ] && [ "$SM_ATTR" -gt 0 ] 2>/dev/null; then
    pass "T11.3 WebUI uses data-sm= attributes ($SM_ATTR found)"
else
    fail "T11.3 WebUI data-sm= attributes" "Expected data-sm= attributes"
fi

# T11.4 WebUI uses globalThis.fetchApi
RESULT=$(pyexec "
import os
content = ''
for base in ['$PLUGIN_DIR', '$USR_DIR']:
    p = os.path.join(base, 'webui', 'main.html')
    if os.path.exists(p):
        content = open(p).read()
        break
print('ok' if 'globalThis.fetchApi' in content else 'FAIL')
" 2>/dev/null)
if [ "$RESULT" = "ok" ]; then
    pass "T11.4 WebUI uses globalThis.fetchApi"
else
    fail "T11.4 fetchApi usage" "$RESULT"
fi

# T11.5 WebUI brand color #6366F1
RESULT=$(pyexec "
import os
content = ''
for base in ['$PLUGIN_DIR', '$USR_DIR']:
    p = os.path.join(base, 'webui', 'main.html')
    if os.path.exists(p):
        content = open(p).read()
        break
print('ok' if '#6366F1' in content else 'FAIL')
" 2>/dev/null)
if [ "$RESULT" = "ok" ]; then
    pass "T11.5 WebUI brand color #6366F1"
else
    fail "T11.5 Brand color" "$RESULT"
fi

# T11.6 config.html uses data-sm= prefix
RESULT=$(pyexec "
import os
content = ''
for base in ['$PLUGIN_DIR', '$USR_DIR']:
    p = os.path.join(base, 'webui', 'config.html')
    if os.path.exists(p):
        content = open(p).read()
        break
has_sm = 'data-sm=' in content
print('ok' if has_sm else 'FAIL')
" 2>/dev/null)
if [ "$RESULT" = "ok" ]; then
    pass "T11.6 config.html uses data-sm= prefix"
else
    fail "T11.6 Config UI prefix" "$RESULT"
fi

########################################
section "12. Documentation"
########################################

DOCS=("README.md" "docs/README.md" "docs/QUICKSTART.md" "docs/SETUP.md" "docs/DEVELOPMENT.md")

for doc in "${DOCS[@]}"; do
    if container_file_exists "$PLUGIN_DIR/$doc" || container_file_exists "$USR_DIR/$doc"; then
        pass "T12 Doc: $doc"
    else
        fail "T12 Doc: $doc" "File missing"
    fi
done

########################################
section "13. Default Config"
########################################

# T13.1 default_config.yaml is valid YAML
RESULT=$(pyexec "
import yaml
for p in ['$PLUGIN_DIR/default_config.yaml', '$USR_DIR/default_config.yaml']:
    try:
        d = yaml.safe_load(open(p))
        print('ok' if isinstance(d, dict) else 'FAIL: not dict')
        break
    except FileNotFoundError:
        continue
    except Exception as e:
        print(f'FAIL: {e}')
        break
")
if [ "$RESULT" = "ok" ]; then
    pass "T13.1 default_config.yaml is valid YAML"
else
    fail "T13.1 Default config YAML" "$RESULT"
fi

# T13.2 default_config has expected keys
RESULT=$(pyexec "
import yaml
for p in ['$PLUGIN_DIR/default_config.yaml', '$USR_DIR/default_config.yaml']:
    try:
        d = yaml.safe_load(open(p))
        required = {'default_platforms', 'adapt_content', 'content_preferences', 'schedule'}
        missing = required - set(d.keys())
        print('ok' if not missing else f'FAIL: missing {missing}')
        break
    except FileNotFoundError:
        continue
")
if [ "$RESULT" = "ok" ]; then
    pass "T13.2 Default config has all required keys"
else
    fail "T13.2 Default config keys" "$RESULT"
fi

########################################
section "14. Security"
########################################

# T14.1 API handlers require CSRF
RESULT=$(pyexec "
from usr.plugins.social_manager.api.social_manager_test import SocialManagerTest
from usr.plugins.social_manager.api.social_manager_config_api import SocialManagerConfigApi
assert SocialManagerTest.requires_csrf() == True, 'social_manager_test CSRF not required'
assert SocialManagerConfigApi.requires_csrf() == True, 'config_api CSRF not required'
print('ok')
")
if [ "$RESULT" = "ok" ]; then
    pass "T14.1 Both API handlers require CSRF"
else
    fail "T14.1 CSRF enforcement in handlers" "$RESULT"
fi

# T14.2 No hardcoded secrets in source
RESULT=$(docker exec "$CONTAINER" bash -c "
    for base in '$PLUGIN_DIR' '$USR_DIR'; do
        if [ -d \"\$base\" ]; then
            grep -rl 'api_key\|api_secret\|password\|token.*=' \"\$base/helpers/\" \"\$base/tools/\" \"\$base/api/\" 2>/dev/null | grep -v __pycache__ | grep -v '.pyc' || true
        fi
    done
" 2>/dev/null)
if [ -z "$RESULT" ]; then
    pass "T14.2 No hardcoded secrets in source files"
else
    fail "T14.2 Potential secrets found" "$RESULT"
fi

# T14.3 .gitignore excludes sensitive paths
RESULT=$(pyexec "
import os
content = ''
for base in ['$PLUGIN_DIR', '$USR_DIR']:
    p = os.path.join(base, '.gitignore')
    if os.path.exists(p):
        content = open(p).read()
        break
checks = ['data/', 'config.json', '__pycache__/', '.env']
missing = [c for c in checks if c not in content]
print('ok' if not missing else f'FAIL: missing {missing}')
" 2>/dev/null)
if [ "$RESULT" = "ok" ]; then
    pass "T14.3 .gitignore excludes sensitive paths"
else
    fail "T14.3 .gitignore coverage" "$RESULT"
fi

########################################
# Summary
########################################

TOTAL=$((PASSED + FAILED + SKIPPED))
echo ""
echo "========================================"
echo " Results: $PASSED passed, $FAILED failed, $SKIPPED skipped (total: $TOTAL)"
echo "========================================"

if [ $FAILED -gt 0 ]; then
    echo -e "\n${RED}Failed tests:${NC}$ERRORS"
    echo ""
    exit 1
else
    echo -e "\n${GREEN}All tests passed!${NC}"
    exit 0
fi
