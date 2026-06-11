# Quick Reference: Test Queries for RAG Validation

Use these queries directly with your validation tools. Copy and paste them or use as command-line arguments.

---

## 🚀 MISSION-SPECIFIC QUERIES

### Apollo 11
```
"Tell me about Apollo 11 mission"
"Apollo 11 launch date and time"
"Apollo 11 astronauts Neil Armstrong Buzz Aldrin Michael Collins"
"Apollo 11 moonwalk lunar surface activities"
"Apollo 11 command module lunar module systems"
```

### Apollo 13
```
"Apollo 13 mission overview"
"What happened in Apollo 13 oxygen tank"
"Apollo 13 oxygen tank heater short circuit explosion"
"Apollo 13 crisis recovery return to Earth safely"
"Jim Lovell Fred Haise Jack Swigert Apollo 13"
```

### Challenger
```
"Challenger space shuttle mission"
"Challenger mission audio transcript"
"Challenger flight details"

---

## ⚙️ TECHNICAL SYSTEM QUERIES

### Power & Propulsion
```
"Fuel cells power generation electrical system"
"Saturn V rocket stages propulsion engines"
"Reaction control system thrusters attitude control"
"Battery power systems backup power"
"Propulsion main engine steering"
```

### Life Support & Environmental
```
"Life support system oxygen CO2 management"
"Cabin pressure environmental control systems"
"Thermal control heat shields radiation protection"
"Water management cooling systems"
```

### Navigation & Guidance
```
"Guidance platform and navigation computer"
"Inertial measurement unit IMU guidance system"
"Landing radar descent guidance"
"Navigation procedures star sighting"
"Course correction maneuvers trajectory"
```

### Communication & Sensors
```
"Communication systems VHF radios antennas"
"Telemetry systems data transmission"
"Radar systems detection ranging"
"Instrumentation sensors monitoring"
```

### Spacecraft Structures
```
"Lunar module landing legs structure"
"Command service module structure heat shield"
"Docking mechanism rendezvous procedures"
"Hatch procedures equipment access"
```

---

## 📋 MISSION PHASE QUERIES

### Launch & Ascent
```
"Launch sequence countdown T minus procedures"
"First stage ignition booster separation"
"Second stage ignition third stage trans-lunar injection"
"Ascent to orbit staging procedures"
```

### In-Space Operations
```
"Translunar injection trajectory to moon"
"Lunar orbit insertion around moon"
"Spacecraft maneuvering attitude control"
"Navigation update mid-course correction"
```

### Lunar Operations
```
"Lunar module descent procedures powered descent"
"Landing on moon lunar surface touchdown"
"Landing site preparation surface operations"
"Lunar surface activities moonwalk experiments"
"Ascent from lunar surface rejoin command module"
```

### Return Operations
```
"Return trajectory Earth orbit insertion"
"Re-entry procedures atmospheric entry"
"Landing splashdown recovery procedures"
"Post-landing procedures crew recovery"
```

---

## 🚨 INCIDENT & EVENT QUERIES

### Problems & Failures
```
"Oxygen tank heater short circuit explosion"
"Electrical power loss systems failure"
"Communication issues transmission problems"
"Equipment damage harm failure"
"System failures redundancy backups"
"Navigation problems attitude control issues"
```

### Emergency Response
```
"Abort emergency procedures safe return"
"Manual procedures backup systems operations"
"Contingency plans crisis management"
"Emergency response procedures recovery"
"Life support emergency procedures"
```

### Specific Incidents
```
"Apollo 13 crisis details"
"Apollo 13 oxygen tank malfunction"
"Electrical failure power system"
"Fuel cell malfunction backup procedures"
```

---

## 👨‍🚀 CREW & ACTIVITIES QUERIES

### Astronaut Names & Activities
```
"Neil Armstrong first steps moon moonwalk"
"Buzz Aldrin lunar module pilot moonwalk activities"
"Michael Collins command module pilot orbit"
"Jim Lovell Apollo 13 commander"
"Fred Haise Apollo 13 lunar module pilot"
"Jack Swigert Apollo 13 command module pilot"
```

### Crew Operations
```
"Crew communications mission control dialogue"
"Astronauts training preparation procedures"
"Crew procedures checklist operations"
"Crew activities tasks experiments"
"Crew rest periods sleep schedules"
```

### Mission Control Interactions
```
"Mission control Houston communications"
"Telemetry data transmission monitoring"
"Flight director procedures management"
"Ground control operations support"
```

---

## 🔬 SCIENTIFIC & EXPERIMENT QUERIES

### Lunar Samples & Analysis
```
"Moon rocks lunar samples collection analysis"
"Sample collection procedures techniques"
"Rock analysis composition measurements"
"Soil samples regolith studies"
```

### Experiments & Instruments
```
"Scientific instruments experiments ALSEP"
"Seismic monitoring moonquakes seismic sensors"
"Lunar geology rock formations composition"
"Experiments conducted on moon surface"
"Scientific data measurements experiments"
"Passive seismic experiment instrumentation"
```

### Scientific Objectives
```
"Scientific objectives Apollo missions"
"Lunar surface observations documentation"
"Geological surveys mapping procedures"
"Data collection analysis procedures"
```

---

## 📊 FLIGHT PLAN & PROCEDURE QUERIES

### Timeline & Scheduling
```
"Mission timeline schedule sequence"
"Timeline hours minutes second stage ignition"
"Translunar coast timeline procedures"
"Lunar surface timeline activities"
"Timeline return procedures Earth arrival"
```

### Detailed Procedures
```
"Procedures step by step operations"
"Flight plan procedures checklist"
"Launch procedures countdown sequence"
"Docking procedures rendezvous techniques"
"Landing procedures descent sequence"
```

### Plans & Contingencies
```
"Flight path trajectory calculations"
"Contingency plans backup procedures"
"Abort modes emergency landing sites"
"Alternate procedures backup systems"
"Emergency procedures crisis response"
```

---

## 💡 ADVANCED QUERIES (Multi-Concept)

### Cross-Mission Comparisons
```
"Apollo 11 vs Apollo 13 mission differences"
"Life support systems Apollo 11 and Apollo 13 comparison"
"Launch procedures Apollo missions"
```

### Specific Technical Scenarios
```
"How Apollo 13 overcame oxygen tank crisis"
"Abort procedures and contingency planning"
"Manual procedures during system failures"
"Emergency protocols spacecraft systems"
```

### Integrated Mission Knowledge
```
"What training did astronauts receive"
"How were emergencies handled on moon"
"What scientific experiments were conducted"
"How did mission control support the missions"
"What systems proved critical during emergencies"
```

---

## 📝 USAGE EXAMPLES

### Using `test_chunking.py`
```bash
# Single query
python test_chunking.py --test-query "Tell me about Apollo 11"

# Run comprehensive tests
python test_chunking.py --run-validation
```

### Using `validate_rag_collection.py`
```bash
# Custom query
python validate_rag_collection.py --query "Oxygen tank heater explosion Apollo 13"

# Category tests
python validate_rag_collection.py --category missions
python validate_rag_collection.py --category technical
python validate_rag_collection.py --category incidents
python validate_rag_collection.py --category crew
```

---

## ✅ EXPECTED RESULTS

### Highly Relevant (Distance < 0.3)
- Mission-specific queries return documents from that mission
- Technical queries return system documentation with specifications
- Crew queries return transcripts/documents with crew activities

### Relevant (Distance 0.3-0.5)
- General mission queries return overview documents
- Phase queries return timeline-adjacent information
- Incident queries return general system information

### Warning Signs (Distance > 0.7)
- Mission queries return generic space information
- Technical queries return unrelated mission phases
- Specific event queries return different events

---

## 🎯 QUERY TIPS

✓ **DO:**
- Include specific mission names (Apollo 11, Apollo 13)
- Use technical terms from documents (translunar, powered descent)
- Reference specific people (Neil Armstrong, Jim Lovell)
- Mention specific events (oxygen tank explosion)
- Use multiple related keywords

✗ **DON'T:**
- Use vague terms ("space", "rockets")
- Ask about topics outside mission scope
- Use overly long queries (> 20 words)
- Mix unrelated concepts in one query
- Expect exact phrase matching

---

## 🔍 TROUBLESHOOTING QUERIES

If you're getting poor results:

**Try these diagnostic queries:**
```
"Apollo 11" - Should return Apollo 11 documents only
"Apollo 13" - Should return Apollo 13 documents only
"Challenger" - Should return Challenger documents only
"Armstrong" - Should return Neil Armstrong references
"Lovell" - Should return Jim Lovell references
"oxygen" - Should return oxygen system references
"descent" - Should return descent procedure references
```

**If diagnostic queries fail:**
- Collection may be empty → verify data was loaded
- Documents may be poorly chunked → adjust chunk size
- Metadata may be missing → check extraction functions
