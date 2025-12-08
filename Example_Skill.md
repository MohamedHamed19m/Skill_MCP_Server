# MCP Skills Server - Setup Guide & Examples

## Installation & Setup

### 1. Install Dependencies

```bash
pip install fastmcp pyyaml
```

### 2. Create Skills Directory

```bash
mkdir -p ~/.capl-skills/skills
```

### 3. Save the Server

Save the MCP server code as `capl_skills_server.py`

### 4. Create Example Skills

Create skill files in `~/.capl-skills/skills/` directory

---

## Example Skill Files

### Example 1: `arethil.md` - ARETHIL Library Expert

```markdown
---
name: capl-arethil
title: CAPL ARETHIL Library Expert
description: Expert knowledge of Vector CAPL ARETHIL library for automotive Ethernet testing including frame handling, initialization, and DLL integration
keywords: [arethil, ethernet, vector, capl, canoe, frame, dll]
version: 1.0.0
auto_activate: true
---

# CAPL ARETHIL Library Expert

You are an expert in Vector CAPL programming with deep knowledge of the ARETHIL library for automotive Ethernet testing.

## Core Functions

### ArEthil_Init()
Initializes the ARETHIL subsystem. Must be called before any other ARETHIL functions.

**Syntax:**
```capl
long ArEthil_Init(void);
```

**Returns:** 0 on success, error code otherwise

**Example:**
```capl
on start {
  long result;
  result = ArEthil_Init();
  if (result != 0) {
    write("ARETHIL initialization failed: %d", result);
  }
}
```

### ArEthil_SendFrame()
Sends an Ethernet frame via ARETHIL interface.

**Syntax:**
```capl
long ArEthil_SendFrame(dword frameId, byte data[], word length);
```

**Parameters:**
- `frameId`: Unique identifier for the frame
- `data`: Byte array containing frame payload
- `length`: Length of the data array

**Example:**
```capl
on key 'f' {
  byte frameData[64];
  long result;
  
  // Prepare frame data
  frameData[0] = 0x01;
  frameData[1] = 0x02;
  
  result = ArEthil_SendFrame(0x123, frameData, 2);
  if (result != 0) {
    write("Frame send failed: %d", result);
  }
}
```

### ArEthil_RegisterCallback()
Registers a callback function for frame reception.

**Syntax:**
```capl
long ArEthil_RegisterCallback(dword frameId, void (*callback)(byte[], word));
```

## Common Patterns

### Pattern 1: Basic Frame Transmission
```capl
variables {
  byte txBuffer[1500];
  msTimer sendTimer;
}

on start {
  // Initialize ARETHIL
  if (ArEthil_Init() != 0) {
    write("Init failed");
    return;
  }
  
  // Start periodic transmission
  setTimer(sendTimer, 100);
}

on timer sendTimer {
  // Prepare Ethernet frame
  txBuffer[0] = 0xAA; // Preamble
  txBuffer[1] = 0xBB;
  
  // Send frame
  ArEthil_SendFrame(0x100, txBuffer, 64);
  
  // Restart timer
  setTimer(sendTimer, 100);
}
```

### Pattern 2: Frame Reception with Callback
```capl
void OnFrameReceived(byte data[], word length) {
  write("Received frame: length=%d", length);
  // Process frame data
  for (int i = 0; i < length; i++) {
    write("  Byte[%d] = 0x%02X", i, data[i]);
  }
}

on start {
  ArEthil_Init();
  
  // Register callback for frame ID 0x200
  ArEthil_RegisterCallback(0x200, OnFrameReceived);
}
```

## Error Handling

Always check return values:
```capl
long result = ArEthil_SendFrame(frameId, data, len);
if (result != 0) {
  switch (result) {
    case -1: write("Invalid parameters"); break;
    case -2: write("Not initialized"); break;
    case -3: write("Hardware error"); break;
    default: write("Unknown error: %d", result);
  }
}
```

## DLL Integration

To use ARETHIL DLL functions:

1. Add DLL reference in CAPL browser
2. Import functions:
```capl
#pragma library("ArEthil.dll")

// Declare external functions
extern long ArEthil_CustomFunction(dword param);
```

## Best Practices

1. **Always initialize** before use
2. **Check return values** for all ARETHIL calls
3. **Use proper buffer sizes** (max 1500 bytes for Ethernet)
4. **Clean up resources** on test end
5. **Handle errors gracefully** with appropriate messages

## Performance Tips

- Reuse buffers instead of allocating new ones
- Use timers for periodic transmission
- Avoid blocking operations in callbacks
- Monitor frame rate to prevent overload
```

---

### Example 2: `test-framework.md` - Test Framework Expert

```markdown
---
name: capl-test-framework
title: CAPL Test Framework Expert
description: Expert in CAPL test case design, TestWaitFor functions, test sequencing, and CANoe test automation patterns
keywords: [test, testcase, testwaitfor, testmodule, automation, verification]
version: 1.0.0
auto_activate: true
---

# CAPL Test Framework Expert

Expert guidance on creating robust CAPL test cases with proper sequencing, verification, and reporting.

## TestWaitFor Functions

### TestWaitForSignalMatch()
Wait for a signal to match a specific value.

**Syntax:**
```capl
long TestWaitForSignalMatch(char signalName[], dword value, dword timeout_ms);
```

**Example:**
```capl
testcase TC_CheckEngineSpeed() {
  long result;
  
  // Wait for EngineSpeed to reach 2000 RPM within 5 seconds
  result = TestWaitForSignalMatch("EngineSpeed", 2000, 5000);
  
  if (result == 1) {
    TestStepPass("Engine speed reached target");
  } else {
    TestStepFail("Timeout waiting for engine speed");
  }
}
```

### TestWaitForSignalInRange()
Wait for a signal to be within a range.

**Syntax:**
```capl
long TestWaitForSignalInRange(char signalName[], dword min, dword max, dword timeout_ms);
```

**Example:**
```capl
testcase TC_TemperatureRange() {
  // Wait for temperature between 20-25°C
  if (TestWaitForSignalInRange("CoolantTemp", 20, 25, 10000)) {
    TestStepPass("Temperature in range");
  } else {
    TestStepFail("Temperature out of range");
  }
}
```

## Test Case Structure

### Complete Test Case Template
```capl
testcase TC_ExampleTest() {
  // 1. Setup
  TestStep("Setup", "Initialize test environment");
  // Reset system
  ResetECU();
  wait(500);
  
  // 2. Preconditions
  TestStep("Preconditions", "Verify initial conditions");
  if (GetSignalValue("IgnitionState") != 1) {
    TestStepFail("Ignition must be ON");
    return;
  }
  TestStepPass("Preconditions met");
  
  // 3. Test execution
  TestStep("Execution", "Perform test actions");
  SendCANMessage(0x123, data);
  
  // 4. Verification
  TestStep("Verification", "Check results");
  if (TestWaitForSignalMatch("ResponseReceived", 1, 2000)) {
    TestStepPass("Response received");
  } else {
    TestStepFail("No response");
  }
  
  // 5. Cleanup
  TestStep("Cleanup", "Reset to initial state");
  // Cleanup code
}
```

## Test Modules

### Organizing Multiple Test Cases
```capl
testmodule TM_BrakingSystem {
  
  // Module setup (runs once before all tests)
  testsetup() {
    write("=== Braking System Tests ===");
    InitializeTestEnvironment();
  }
  
  // Test case 1
  testcase TC_EmergencyBraking() {
    // Test implementation
  }
  
  // Test case 2
  testcase TC_ABSActivation() {
    // Test implementation
  }
  
  // Module cleanup (runs once after all tests)
  testcleanup() {
    write("=== Tests Complete ===");
    RestoreNormalOperation();
  }
}
```

## Verification Patterns

### Pattern 1: Signal Verification with Timeout
```capl
long VerifySignal(char signal[], dword expectedValue, dword timeout) {
  long startTime = timeNow();
  
  while ((timeNow() - startTime) < timeout) {
    if (GetSignalValue(signal) == expectedValue) {
      return 1; // Success
    }
    wait(10); // Check every 10ms
  }
  
  return 0; // Timeout
}

testcase TC_VerifyExample() {
  if (VerifySignal("Status", 0x01, 3000)) {
    TestStepPass("Signal verified");
  } else {
    TestStepFail("Verification failed");
  }
}
```

### Pattern 2: Multiple Condition Verification
```capl
testcase TC_MultiCondition() {
  long allPassed = 1;
  
  TestStep("Check Condition 1", "Verify ignition");
  if (!TestWaitForSignalMatch("Ignition", 1, 1000)) {
    TestStepFail("Ignition check failed");
    allPassed = 0;
  }
  
  TestStep("Check Condition 2", "Verify voltage");
  if (!TestWaitForSignalInRange("BatteryVoltage", 12, 14, 1000)) {
    TestStepFail("Voltage check failed");
    allPassed = 0;
  }
  
  if (allPassed) {
    TestStepPass("All conditions met");
  }
}
```

## Best Practices

1. **Use descriptive test names** - TC_CheckEngineStartupSequence vs TC_Test1
2. **Include proper logging** - Use TestStep() for clarity
3. **Set realistic timeouts** - Don't use arbitrary large values
4. **Clean up after tests** - Reset state for next test
5. **Use helper functions** - Reduce code duplication
6. **Document expected behavior** - Clear test descriptions
7. **Handle edge cases** - Test both success and failure paths

## Common Patterns

### Sequential Test Execution
```capl
testmodule TM_Sequence {
  testcase TC_Step1() {
    // First step
    if (success) {
      TestSetNextTestCase("TC_Step2");
    }
  }
  
  testcase TC_Step2() {
    // Second step
    if (success) {
      TestSetNextTestCase("TC_Step3");
    }
  }
  
  testcase TC_Step3() {
    // Final step
  }
}
```

### Parameterized Testing
```capl
void RunSpeedTest(dword targetSpeed, char testName[]) {
  TestStep(testName, "Testing speed: %d RPM", targetSpeed);
  
  SetEngineSpeed(targetSpeed);
  
  if (TestWaitForSignalMatch("ActualSpeed", targetSpeed, 5000)) {
    TestStepPass("Speed reached");
  } else {
    TestStepFail("Speed not reached");
  }
}

testcase TC_SpeedTests() {
  RunSpeedTest(1000, "Idle Speed");
  RunSpeedTest(3000, "Cruising Speed");
  RunSpeedTest(5000, "High Speed");
}
```
```

---

### Example 3: `database.md` - Database Expert

```markdown
---
name: capl-database
title: CAPL Database Integration Expert
description: Expert in CAPL database access, CAN database management, signal and message definitions, and DBC file handling
keywords: [database, dbc, signal, message, can, attribute]
version: 1.0.0
auto_activate: true
---

# CAPL Database Expert

Expert guidance on working with CAN databases in CAPL, including signal access, message handling, and database attributes.

## Signal Access

### Reading Signal Values
```capl
// Method 1: Direct signal access
variables {
  message EngineData msg;
}

on message EngineData {
  double rpm = this.EngineSpeed;
  double temp = this.CoolantTemp;
  
  write("RPM: %.0f, Temp: %.1f°C", rpm, temp);
}

// Method 2: Using $ operator
on message 0x123 {
  double speed = $EngineData::EngineSpeed;
  write("Speed: %.0f", speed);
}

// Method 3: GetSignal function
on timer checkTimer {
  double value = GetSignal("EngineSpeed");
  write("Current speed: %.0f", value);
}
```

### Writing Signal Values
```capl
on key 'v' {
  message EngineCommand cmd;
  
  // Set signal values
  cmd.TargetSpeed = 3000;
  cmd.EnableCruiseControl = 1;
  
  // Send message
  output(cmd);
}

// Or using PutSignal
on key 'p' {
  PutSignal("TargetSpeed", 3000);
  SendMessage(EngineCommand);
}
```

## Message Handling

### Sending CAN Messages
```capl
on key 's' {
  message BrakeCommand cmd;
  
  // Configure message
  cmd.dir = TX;  // Transmission direction
  cmd.dlc = 8;   // Data length code
  
  // Set signal values
  cmd.BrakePressure = 50;
  cmd.ABSActive = 0;
  
  // Send
  output(cmd);
}
```

### Message Reception Patterns
```capl
// Pattern 1: Specific message handler
on message EngineData {
  write("Engine RPM: %.0f", this.EngineSpeed);
}

// Pattern 2: Message ID handler
on message 0x123 {
  write("Received message 0x123");
}

// Pattern 3: Wildcard handler with filter
on message * {
  if (this.id >= 0x100 && this.id <= 0x1FF) {
    write("Received message in range: 0x%X", this.id);
  }
}
```

## Database Attributes

### Reading Attributes
```capl
on start {
  char attrValue[256];
  long numValue;
  
  // Get message attribute
  GetMessageAttribute(EngineData, "GenMsgCycleTime", numValue);
  write("Cycle time: %d ms", numValue);
  
  // Get signal attribute
  GetSignalAttribute("EngineSpeed", "GenSigStartValue", numValue);
  write("Start value: %d", numValue);
  
  // Get string attribute
  GetDBAttribute("DatabaseName", attrValue);
  write("Database: %s", attrValue);
}
```

### Common Attributes
- **GenMsgCycleTime**: Message cycle time (ms)
- **GenSigStartValue**: Signal initial value
- **GenSigSendType**: Signal send type (cyclic/event)
- **GenMsgDelayTime**: Message delay time
- **Unit**: Signal unit (e.g., "rpm", "°C")
- **Min/Max**: Signal min/max values

## Signal Value Tables

### Using Value Tables
```capl
on message GearPosition {
  char gearName[32];
  long gearValue = this.CurrentGear;
  
  // Get value table entry
  GetValueTableEntry("GearPositions", gearValue, gearName);
  write("Current gear: %s (%d)", gearName, gearValue);
}

// Value table definition in DBC:
// VAL_ 100 CurrentGear 0 "Park" 1 "Reverse" 2 "Neutral" 
//                       3 "Drive" 4 "Sport" ;
```

## Advanced Patterns

### Pattern 1: Database-Driven Configuration
```capl
variables {
  long messageCycleTimes[100];
  long messageCount = 0;
}

on start {
  char msgName[64];
  long cycleTime;
  
  // Load all message cycle times
  for (long id = 0; id < 0x7FF; id++) {
    if (GetMessageName(id, msgName) == 0) {
      GetMessageAttribute(msgName, "GenMsgCycleTime", cycleTime);
      messageCycleTimes[messageCount++] = cycleTime;
      write("Message 0x%X (%s): %d ms", id, msgName, cycleTime);
    }
  }
}
```

### Pattern 2: Signal Monitoring with Ranges
```capl
void CheckSignalRange(char signalName[], double min, double max) {
  double value = GetSignal(signalName);
  double dbMin, dbMax;
  
  // Get range from database
  GetSignalAttribute(signalName, "Min", dbMin);
  GetSignalAttribute(signalName, "Max", dbMax);
  
  if (value < dbMin || value > dbMax) {
    write("WARNING: %s out of range: %.2f (valid: %.2f-%.2f)",
          signalName, value, dbMin, dbMax);
  }
}

on message EngineData {
  CheckSignalRange("EngineSpeed", 0, 8000);
  CheckSignalRange("CoolantTemp", -40, 150);
}
```

### Pattern 3: Dynamic Message Generation
```capl
void SendDatabaseMessage(char msgName[], byte data[]) {
  long msgId;
  message * msg;
  
  // Get message ID from name
  GetMessageId(msgName, msgId);
  
  // Create message dynamically
  msg = CreateMessage(msgId);
  msg.dlc = 8;
  memcpy(msg.byte(), data, 8);
  
  output(msg);
}

on key 'g' {
  byte payload[8] = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08};
  SendDatabaseMessage("EngineCommand", payload);
}
```

## Best Practices

1. **Use symbolic names** - Reference signals by name, not raw values
2. **Check database availability** - Verify database is loaded before access
3. **Handle missing signals gracefully** - Check return values
4. **Use appropriate data types** - Match signal types (physical vs. raw)
5. **Leverage value tables** - Use for enum-like signal values
6. **Cache attribute values** - Don't read repeatedly in loops
7. **Document dependencies** - Note which DBC file is required

## Common Errors & Solutions

### Error: Signal not found
```capl
// Problem: Typo in signal name
double speed = $EngineData::EnginSpeed; // Wrong!

// Solution: Use correct name
double speed = $EngineData::EngineSpeed; // Correct

// Or check if signal exists
if (SignalExists("EngineSpeed")) {
  double speed = GetSignal("EngineSpeed");
}
```

### Error: Database not loaded
```capl
on preStart {
  if (!IsDatabaseLoaded("MyDatabase.dbc")) {
    write("ERROR: Database not loaded!");
    stop();
  }
}
```
```

---

## Configuration File

Create `~/.capl-skills/config.json`:

```json
{
  "skills_directory": "~/.capl-skills/skills",
  "auto_scan_on_startup": true,
  "default_auto_activate": true,
  "max_concurrent_skills": 5
}
```

---

## Running the Server

### Method 1: Direct Execution
```bash
python capl_skills_server.py
```

### Method 2: As MCP Server with Claude Desktop

Add to Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on Mac):

```json
{
  "mcpServers": {
    "capl-skills": {
      "command": "python",
      "args": ["/path/to/capl_skills_server.py"]
    }
  }
}
```

### Method 3: With Gemini CLI (requires MCP support)

```bash
# Start the server
python capl_skills_server.py

# In another terminal, connect Gemini CLI to the MCP server
# (Configuration depends on Gemini CLI's MCP integration)
```

---

## Usage Examples

### Example 1: List Available Skills
```
User: List my CAPL skills

Assistant calls: list_skills()
Response shows: capl-arethil, capl-test-framework, capl-database
```

### Example 2: Automatic Skill Discovery
```
User: How do I send an ARETHIL Ethernet frame?

Assistant calls: find_relevant_skills(query="send ARETHIL Ethernet frame", auto_activate=True)
System loads: capl-arethil skill
Assistant responds with: Detailed ARETHIL frame sending code
```

### Example 3: Search Within Skills
```
User: Find information about TestWaitFor functions

Assistant calls: search_skill_content(search_query="TestWaitFor")
System searches all skills and returns relevant snippets
```

### Example 4: Manual Skill Management
```
User: Load the test framework skill

Assistant calls: activate_skill(skill_name="capl-test-framework")
Assistant: "Test framework knowledge loaded. Ready to help with test cases!"

User: I'm done with testing, now working on database

Assistant calls: deactivate_skill(skill_name="capl-test-framework")
Assistant calls: activate_skill(skill_name="capl-database")
```

---

## Creating Your Own Skills

### Skill Template

```markdown
---
name: your-skill-name
title: Human Readable Title
description: Brief description of what this skill provides (used for relevance matching)
keywords: [keyword1, keyword2, keyword3]
version: 1.0.0
auto_activate: true
---

# Skill Content Title

Your detailed skill content goes here. Include:

## Sections
- Code examples
- Best practices
- Common patterns
- Error handling
- Troubleshooting

## Code Examples
```capl
// Example code
```

## Best Practices
1. Practice one
2. Practice two
```

### Tips for Writing Good Skills

1. **Good descriptions** - Make them specific and keyword-rich for better relevance matching
2. **Comprehensive keywords** - Include variations and related terms
3. **Structured content** - Use headers and sections for clarity
4. **Code examples** - Include working, tested code
5. **Best practices** - Share proven patterns
6. **Error handling** - Document common issues and solutions
7. **Keep focused** - One skill per domain/library

---

## Troubleshooting

### Skills not found
```bash
# Verify directory exists
ls ~/.capl-skills/skills/

# Rescan directory
# Use reload_skills_directory() tool
```

### YAML parsing errors
- Check frontmatter format (must start/end with ---)
- Verify YAML syntax (use a YAML validator)
- Ensure proper indentation

### Skills not activating automatically
- Check `auto_activate` in frontmatter
- Verify keywords match your queries
- Use `find_relevant_skills()` to debug relevance scores

---

## Next Steps

1. Create your CAPL skill files
2. Test the server with sample queries
3. Refine keywords based on usage
4. Add more skills as needed
5. Share skills with your team!