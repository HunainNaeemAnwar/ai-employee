#!/bin/bash
# Ralph Wiggum Loop - Qwen CLI Implementation
#
# This is the ORIGINAL Ralph Wiggum pattern adapted for Qwen CLI.
# It uses a simple bash loop with completion detection and safety mechanisms.
#
# Usage:
#   ./ralph-loop.sh "Process all files in Needs_Action"
#   ./ralph-loop.sh "Migrate tests" --max-iterations 10 --completion-promise "DONE"
#   MAX_ITERATIONS=20 ./ralph-loop.sh "Add type hints" --vault ~/AI_Employee_Vault
#
# Environment Variables:
#   MAX_ITERATIONS     - Maximum loop iterations (default: 50)
#   LOG_DIR           - Directory for iteration logs (default: .ralph-logs)
#   COMPLETION_SIGNAL - Completion signal to detect (default: <promise>COMPLETE</promise>)

set -e

# Default values
MAX_ITERATIONS="${MAX_ITERATIONS:-10}"
COMPLETION_PROMISE="${COMPLETION_SIGNAL:-<promise>COMPLETE</promise>}"
VAULT_PATH="${VAULT_PATH:-.}"
PROMPT=""
ITERATION=0
TIMEOUT="${TIMEOUT:-120}"  # 2 minutes per iteration
NO_PROGRESS_COUNT=0
LAST_STATE_HASH=""

# Additional completion signals to detect
COMPLETION_SIGNALS=(
    "<promise>COMPLETE</promise>"
    "<promise>TASK_COMPLETE</promise>"
    "<status>TASK_COMPLETE</status>"
    "DONE"
    "TASK COMPLETE"
    "task complete"
)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --max-iterations)
            MAX_ITERATIONS="$2"
            shift 2
            ;;
        --completion-promise)
            COMPLETION_PROMISE="$2"
            shift 2
            ;;
        --vault)
            VAULT_PATH="$2"
            shift 2
            ;;
        --help|-h)
            echo "Ralph Wiggum Loop - Qwen CLI Implementation"
            echo ""
            echo "Usage:"
            echo "  $0 \"<prompt>\" [options]"
            echo ""
            echo "Options:"
            echo "  --max-iterations N    Maximum iterations (default: 50)"
            echo "  --completion-promise  String to detect for completion"
            echo "  --vault PATH          Path to Obsidian vault (default: .)"
            echo "  --help, -h            Show this help message"
            echo ""
            echo "Environment Variables:"
            echo "  MAX_ITERATIONS        Maximum loop iterations (default: 50)"
            echo "  LOG_DIR              Directory for logs (default: .ralph-logs)"
            echo "  COMPLETION_SIGNAL    Completion signal (default: <promise>COMPLETE</promise>)"
            echo ""
            echo "Examples:"
            echo "  $0 \"Process all emails in Needs_Action\""
            echo "  $0 \"Migrate tests\" --max-iterations 10 --completion-promise \"DONE\""
            echo "  MAX_ITERATIONS=20 $0 \"Add type hints\""
            exit 0
            ;;
        *)
            if [[ -z "$PROMPT" ]]; then
                PROMPT="$1"
            fi
            shift
            ;;
    esac
done

# Validate prompt
if [[ -z "$PROMPT" ]]; then
    echo -e "${RED}❌ ERROR: Prompt is required${NC}"
    echo "Usage: $0 \"<prompt>\" [options]"
    exit 1
fi

# Change to vault directory
cd "$VAULT_PATH"
VAULT_PATH="$(pwd)"

# Create directories
LOG_DIR="${LOG_DIR:-.ralph-logs}"
mkdir -p "$LOG_DIR"

# Create prompt file
PROMPT_FILE="$VAULT_PATH/PROMPT.md"
echo "$PROMPT" > "$PROMPT_FILE"

# Progress file
PROGRESS_FILE="$VAULT_PATH/progress.txt"

# State file for progress detection
STATE_FILE="$VAULT_PATH/SYSTEM/state/current_task.json"

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}🚀 RALPH WIGGUM LOOP - QWEN CLI${NC}"
echo -e "${BLUE}============================================================${NC}"
echo -e "📂 Vault: ${GREEN}$VAULT_PATH${NC}"
echo -e "📝 Prompt: ${YELLOW}${PROMPT:0:80}...${NC}"
echo -e "🎯 Max iterations: ${GREEN}$MAX_ITERATIONS${NC}"
echo -e "✅ Completion promise: ${GREEN}$COMPLETION_PROMISE${NC}"
echo -e "📁 Log directory: ${CYAN}$LOG_DIR${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the loop${NC}"
echo ""

# Trap Ctrl+C
trap 'echo -e "\n${RED}🛑 Interrupted by user${NC}"; exit 0' INT

# Function to hash state file
hash_state_file() {
    if [[ -f "$STATE_FILE" ]]; then
        md5sum "$STATE_FILE" 2>/dev/null | cut -d' ' -f1
    else
        echo ""
    fi
}

# Function to check completion signals
check_completion() {
    local output="$1"
    
    # Check custom completion promise
    if [[ -n "$COMPLETION_PROMISE" && "$output" == *"$COMPLETION_PROMISE"* ]]; then
        echo "$COMPLETION_PROMISE"
        return 0
    fi
    
    # Check standard completion signals
    for SIGNAL in "${COMPLETION_SIGNALS[@]}"; do
        if [[ "$output" == *"$SIGNAL"* ]]; then
            echo "$SIGNAL"
            return 0
        fi
    done
    
    return 1
}

# Main loop - THE RALPH WIGGUM PATTERN
# Core pattern: while :; do cat PROMPT.md | qwen; done
# With stop hook behavior via completion detection

while [[ $ITERATION -lt $MAX_ITERATIONS ]]; do
    ITERATION=$((ITERATION + 1))
    ITER_START_TIME=$(date +%s)
    
    echo -e "${BLUE}============================================================${NC}"
    echo -e "${BLUE}🔄 RALPH LOOP - Iteration ${ITERATION}/${MAX_ITERATIONS}${NC}"
    echo -e "${BLUE}============================================================${NC}"
    echo ""
    
    # Capture state hash before iteration
    STATE_HASH_BEFORE=$(hash_state_file)
    
    # Run Qwen CLI with the prompt
    # Capture output to check for completion signals
    OUTPUT_FILE="$LOG_DIR/iteration-$ITERATION.txt"
    
    # Run Qwen with prompt
    set +e
    OUTPUT=$(cat "$PROMPT_FILE" | qwen -i -o text 2>&1) || EXIT_CODE=$?
    set -e
    
    # Save output to log file
    echo "$OUTPUT" > "$OUTPUT_FILE"
    
    # Calculate iteration time
    ITER_END_TIME=$(date +%s)
    ITER_DURATION=$((ITER_END_TIME - ITER_START_TIME))
    
    # Show output preview
    if [[ -n "$OUTPUT" ]]; then
        OUTPUT_LEN=${#OUTPUT}
        echo -e "${CYAN}📄 Qwen output (${OUTPUT_LEN} chars, ${ITER_DURATION}s):${NC}"
        
        if [[ $OUTPUT_LEN -gt 500 ]]; then
            echo "${OUTPUT:0:500}..."
        else
            echo "$OUTPUT"
        fi
        echo ""
    fi
    
    # Check for completion signals
    COMPLETION_FOUND=$(check_completion "$OUTPUT") || COMPLETION_FOUND=""
    
    if [[ -n "$COMPLETION_FOUND" ]]; then
        echo -e "${GREEN}✅ COMPLETION SIGNAL DETECTED: '$COMPLETION_FOUND'${NC}"
        echo ""
        echo -e "${GREEN}============================================================${NC}"
        echo -e "${GREEN}✅ RALPH LOOP COMPLETED SUCCESSFULLY${NC}"
        echo -e "${GREEN}   Iterations: ${ITERATION}${NC}"
        echo -e "${GREEN}   Total time: ${ITER_DURATION}s${NC}"
        echo -e "${GREEN}============================================================${NC}"
        
        # Update progress
        echo "Iteration $ITERATION completed at $(date) - COMPLETED" >> "$PROGRESS_FILE"
        
        exit 0
    fi
    
    # Check for progress (state file changed)
    STATE_HASH_AFTER=$(hash_state_file)
    
    if [[ "$STATE_HASH_AFTER" == "$STATE_HASH_BEFORE" && -z "$OUTPUT" ]]; then
        NO_PROGRESS_COUNT=$((NO_PROGRESS_COUNT + 1))
        echo -e "${YELLOW}⚠️  No progress detected ($NO_PROGRESS_COUNT/3)${NC}"
        echo -e "${YELLOW}   (State file unchanged and no output)${NC}"
        
        if [[ $NO_PROGRESS_COUNT -ge 3 ]]; then
            echo ""
            echo -e "${RED}❌ Exiting: No progress for 3 consecutive iterations${NC}"
            echo ""
            echo "Iteration $ITERATION - NO PROGRESS" >> "$PROGRESS_FILE"
            exit 1
        fi
    else
        NO_PROGRESS_COUNT=0
    fi
    
    # Update progress tracking
    echo "Iteration $ITERATION completed at $(date)" >> "$PROGRESS_FILE"
    
    # Stop hook behavior: continue if not complete
    echo ""
    echo -e "${YELLOW}🔄 Stop hook activated - task not complete, continuing...${NC}"
    echo -e "${YELLOW}   (Qwen tried to exit, but completion not detected)${NC}"
    echo ""
    
    EXIT_CODE=0  # Reset for next iteration
done

# Max iterations reached
echo ""
echo -e "${RED}============================================================${NC}"
echo -e "${RED}⚠️  MAX ITERATIONS REACHED (${MAX_ITERATIONS})${NC}"
echo -e "${RED}============================================================${NC}"
echo ""
echo -e "${YELLOW}The task may not be complete. Consider:${NC}"
echo -e "  1. Increasing MAX_ITERATIONS (e.g., MAX_ITERATIONS=100 $0 ...)"
echo -e "  2. Breaking the task into smaller steps"
echo -e "  3. Checking for errors in the output above"
echo -e "  4. Checking logs in: $LOG_DIR/"
echo ""

# Check logs
if [[ -f "$OUTPUT_FILE" ]]; then
    echo -e "${CYAN}Last iteration output saved to: $OUTPUT_FILE${NC}"
fi

exit 1
