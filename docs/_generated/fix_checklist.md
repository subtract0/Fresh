# 🛠️ Broken Windows Fix Checklist

## 📊 Summary
- **Total Failing Tests**: 19
- **Critical Issues**: Invalid OpenAI model `gpt-5`, missing Firebase credentials
- **System Status**: Autonomous loop blocked by safety checks

---

## 🔥 **Category A: Configuration Errors (CRITICAL - Fix First)**

### A1. Invalid OpenAI Model Configuration ⚡ HIGH PRIORITY
- [ ] **12 Mother Agent Tests**: All failing with `gpt-5` model (doesn't exist)
  - TestMotherAgent.test_run_with_basic_parameters
  - TestMotherAgent.test_run_spawns_appropriate_agent_type  
  - TestMotherAgent.test_run_with_test_generation_task
  - TestMotherAgent.test_run_with_architecture_task
  - TestMotherAgent.test_memory_persistence_on_spawn
  - TestMotherAgent.test_spawn_request_tracking
  - TestMotherAgent.test_model_selection
  - TestMotherAgent.test_output_type_validation
  - TestMotherAgent.test_integration_with_father_agent
  - TestMotherAgent.test_spawn_history_limit
  - TestMotherAgent.test_concurrent_spawn_safety
  - TestMotherAgent.test_get_spawn_statistics

**Root Cause**: Code references `gpt-5` which doesn't exist. OpenAI timeout issues.
**Fix Required**: Update model configuration to use valid models (`gpt-4o`, `gpt-4-turbo`)

### A2. Missing Firebase Credentials
- [ ] **5 Firestore Tests**: All falling back to in-memory mode
  - TestFirestoreCrossSession.test_memory_persists_across_sessions
  - TestFirestoreCrossSession.test_learning_patterns_persist  
  - TestFirestoreCrossSession.test_agent_memory_accumulation
  - TestFirestoreCrossSession.test_memory_search_across_sessions
  - TestFirestoreCrossSession.test_memory_consolidation_cross_session

**Root Cause**: Missing `./firebase-credentials.json` file
**Fix Required**: Either add credentials or make tests skip gracefully

---

## 🧪 **Category C: Logic/Implementation Regressions** 

### C1. CLI Data Structure Errors
- [ ] **test_assist_scan_json**: KeyError: 'comment' in scan result parsing
  - **File**: `tests/test_cli_assist_scan.py:40`
  - **Root Cause**: Expected data structure mismatch in CLI scan output

### C2. Repository Scanner Logic
- [ ] **TestRepoScanner.test_find_todos_in_files**: TODO detection failing
  - **File**: `tests/test_repo_scanner.py:54`  
  - **Root Cause**: TODO pattern matching not working as expected

---

## 🏗️ **Impact Analysis**

### Autonomous Loop Blockage
```
WARNING: Skipping unsafe improvement: issue_-2247194437160625315
  error: Changes would break existing tests
  warning: Repository has uncommitted changes
Result: 30,224 opportunities, 0/0 successful improvements
```

**Cause**: Safety system correctly blocking all changes because tests are failing.

---

## 🎯 **Fix Priority Order**

1. **🔴 URGENT**: Fix OpenAI model configuration (blocks 12 tests)
2. **🟡 MEDIUM**: Handle Firebase credentials gracefully (5 tests) 
3. **🟢 LOW**: Fix CLI scan data structure (1 test)
4. **🟢 LOW**: Fix TODO scanner logic (1 test)

---

## ✅ **Completion Criteria** 

- [ ] All 19 tests pass
- [ ] Autonomous loop runs without safety blocks
- [ ] System can make improvements autonomously
- [ ] CI pipeline green
- [ ] Documentation updated

---

## 📝 **Notes**
- Tests use 5s timeout - need to optimize for faster execution
- Some tests have thread safety issues in concurrent execution
- Need to verify if `claude-2` model is valid or should be replaced

**Generated**: $(date)
**Branch**: fix/broken-windows
**Status**: 🔴 CRITICAL REPAIRS NEEDED
