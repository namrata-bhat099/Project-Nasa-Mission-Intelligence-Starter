# RAG Collection Query Validation Guide

## Overview
This guide explains how to validate that your ChromaDB collection is storing and retrieving relevant information correctly when queried with questions about NASA missions.

## Relevance Metrics

The validation system uses **ChromaDB's cosine distance** to measure result relevance:
- **Distance 0**: Perfect semantic match
- **Distance < 0.3**: Highly Relevant ✓✓
- **Distance 0.3-0.5**: Relevant ✓
- **Distance 0.5-0.7**: Somewhat Relevant ◐
- **Distance > 0.7**: Not Relevant ✗

Lower distances = better semantic match to your query.

---

## Query Categories & Examples

### 1. **Mission-Specific Queries**
Test if the system correctly identifies and retrieves information about specific missions.

**Good Test Queries:**
- "Tell me about Apollo 11 mission"
- "Apollo 11 launch date and time"
- "Apollo 11 astronauts Neil Armstrong Buzz Aldrin Michael Collins"
- "What happened in Apollo 13 oxygen tank"
- "Apollo 13 mission overview"
- "Challenger space shuttle mission"

**Expected Results:** Should return documents from Apollo 11, Apollo 13, or Challenger respectively with mission-specific content.

---

### 2. **Technical System Queries**
Test retrieval of technical specifications and system descriptions.

**Good Test Queries:**
- "Guidance platform and navigation computer"
- "Life support system oxygen CO2 management"
- "Fuel cells power generation"
- "Communication systems VHF radios"
- "Lunar module landing radar"
- "Reaction control system thrusters"
- "Saturn V rocket stages propulsion"
- "Thermal control heat shields"

**Expected Results:** Should return technical documentation with system details, specifications, and procedures.

---

### 3. **Mission Phase Queries**
Test retrieval of information about specific phases of the mission.

**Good Test Queries:**
- "Launch sequence countdown T minus procedures"
- "Ascent to orbit first stage second stage"
- "Translunar injection trajectory to moon"
- "Lunar orbit insertion around moon"
- "Lunar module descent procedures powered descent"
- "Landing on moon lunar surface touchdown"
- "Activities on lunar surface moonwalk experiments"
- "Re-entry landing splashdown recovery"

**Expected Results:** Should return timeline documents and phase-specific procedures.

---

### 4. **Event & Incident Queries**
Test retrieval of specific events or problems during missions.

**Good Test Queries:**
- "Oxygen tank heater short circuit explosion" (Apollo 13 specific)
- "Electrical power loss systems failure"
- "Communication issues transmission problems"
- "Equipment damage harm failure"
- "Abort emergency procedures safe return"
- "Manual procedures backup systems operations"
- "Navigation course correction maneuvers"
- "System failures redundancy backups"

**Expected Results:** Should return incident reports, transcripts describing the problem, and recovery procedures.

---

### 5. **Crew & Activity Queries**
Test retrieval of crew member activities and communications.

**Good Test Queries:**
- "Neil Armstrong first steps moon moonwalk"
- "Buzz Aldrin lunar module pilot moonwalk activities"
- "Michael Collins command module pilot orbit"
- "Jim Lovell Apollo 13 commander"
- "Crew communications mission control dialogue"
- "Astronauts training preparation procedures"
- "Crew activities tasks experiments moonwalk"

**Expected Results:** Should return transcripts and documents discussing crew activities, including direct quotes or descriptions of crew communications.

---

### 6. **Scientific Queries**
Test retrieval of scientific objectives and experimental data.

**Good Test Queries:**
- "Moon rocks lunar samples collection analysis"
- "Scientific instruments experiments ALSEP"
- "Seismic moonquakes seismic sensors"
- "Lunar geology rock formations composition"
- "Experiments conducted on moon surface"
- "Scientific data measurements experiments"

**Expected Results:** Should return documents about scientific objectives and experimental procedures.

---

### 7. **Flight Plan Queries**
Test retrieval of detailed procedures and timelines.

**Good Test Queries:**
- "Mission timeline schedule sequence"
- "Timeline hours minutes second stage ignition"
- "Flight path trajectory calculations"
- "Procedures step by step operations"
- "Checklist procedures verification steps"
- "Contingency plans backup procedures"
- "Abort modes emergency landing sites"

**Expected Results:** Should return flight plan documents with specific timelines and procedures.

---

## How to Use the Validation Tools

### Option 1: Using `test_chunking.py` with Command Line

Run comprehensive validation:
```bash
python test_chunking.py --chroma-dir ./chroma_db_openai --run-validation
```

Test a single query:
```bash
python test_chunking.py --chroma-dir ./chroma_db_openai --test-query "Tell me about Apollo 11"
```

Get collection statistics:
```bash
python test_chunking.py --chroma-dir ./chroma_db_openai --stats-only
```

### Option 2: Using `validate_rag_collection.py` (Dedicated Validation Tool)

Run all category tests:
```bash
python validate_rag_collection.py --chroma-dir ./chroma_db_openai
```

Test specific category:
```bash
python validate_rag_collection.py --category missions
python validate_rag_collection.py --category technical
python validate_rag_collection.py --category incidents
python validate_rag_collection.py --category crew
python validate_rag_collection.py --category science
```

Run a custom query:
```bash
python validate_rag_collection.py --query "What happened during the Apollo 13 crisis?"
```

---

## What Makes a Good Test Query?

✓ **Good queries include:**
- Specific mission names (Apollo 11, Apollo 13, Challenger)
- System/component names (oxygen tank, guidance computer, fuel cells)
- Technical terms used in the documents (translunar, powered descent, module)
- Astronaut names (Neil Armstrong, Buzz Aldrin, Jim Lovell)
- Specific events or problems (oxygen tank explosion, re-entry procedures)
- Document types (transcript, flight plan, technical specifications)

✗ **Avoid vague queries:**
- "Tell me about space" (too generic)
- "What is NASA?" (not specific to missions)
- "How does gravity work?" (outside scope of documents)
- "When was space exploration invented?" (too broad)

---

## Interpreting Results

### Ideal Results (Highly Relevant ✓✓)
```
Query: "Apollo 11 moonwalk Neil Armstrong"
Distance: 0.15
Status: HIGHLY_RELEVANT
Result: Document excerpt about Neil Armstrong's moonwalk on Apollo 11
```

### Good Results (Relevant ✓)
```
Query: "Guidance computer navigation system"
Distance: 0.35
Status: RELEVANT
Result: Document about Apollo guidance computer with technical details
```

### Problematic Results (Not Relevant ✗)
```
Query: "Apollo 13 oxygen tank explosion"
Distance: 0.85
Status: NOT_RELEVANT
Issue: Returns documents about general systems but not the incident
Action: May indicate incomplete chunking or missing search terms
```

---

## Validation Workflow

1. **Start with Collection Stats**
   ```bash
   python test_chunking.py --stats-only
   ```
   Check total documents and mission breakdown

2. **Test Mission-Specific Queries**
   ```bash
   python validate_rag_collection.py --category missions
   ```
   Verify each mission's data is retrievable

3. **Test Technical Queries**
   ```bash
   python validate_rag_collection.py --category technical
   ```
   Ensure system specifications are well-indexed

4. **Test Events/Incidents**
   ```bash
   python validate_rag_collection.py --category incidents
   ```
   Verify crisis situations are documented

5. **Run Custom Queries**
   ```bash
   python validate_rag_collection.py --query "Your specific question"
   ```
   Test domain-specific questions

6. **Run Full Validation**
   ```bash
   python validate_rag_collection.py
   ```
   Get overall collection quality score

---

## Success Criteria

Your collection is **well-validated** when:
- ✓ > 80% of queries return Highly Relevant or Relevant results
- ✓ All mission-specific queries retrieve correct mission documents
- ✓ Technical queries return system documentation
- ✓ Incident queries return problem descriptions and solutions
- ✓ Crew queries return crew-related activities and communications
- ✓ Average distance scores < 0.5 across most queries

---

## Troubleshooting

### **Problem: All queries return high distances (>0.7)**
- **Cause**: Chunks may be too small/large
- **Solution**: Adjust `--chunk-size` (try 500-1000)

### **Problem: Mission-specific queries return wrong mission**
- **Cause**: Documents not properly tagged in metadata
- **Solution**: Verify mission extraction logic in `extract_mission_from_path()`

### **Problem: Technical queries return generic documents**
- **Cause**: Insufficient term density in chunks
- **Solution**: Try queries with more specific technical terms

### **Problem: No results returned**
- **Cause**: Collection may be empty
- **Solution**: Verify data was processed: `python test_chunking.py --chroma-dir ./chroma_db_openai --data-path ./data_text`

---

## Example: Complete Validation Run

```bash
# Step 1: Process data if not already done
python test_chunking.py --data-path ./data_text --chroma-dir ./chroma_db_openai

# Step 2: Check collection stats
python test_chunking.py --stats-only --chroma-dir ./chroma_db_openai

# Step 3: Run comprehensive validation
python validate_rag_collection.py --chroma-dir ./chroma_db_openai

# Step 4: Test specific mission
python validate_rag_collection.py --category missions

# Step 5: Test custom question
python validate_rag_collection.py --query "Tell me about Apollo 11 moonwalk"
```

---

## Notes

- The validation system evaluates **semantic similarity**, not exact keyword matching
- Results are ranked by relevance (distance score)
- Each query typically returns top 5 most relevant results
- Check logs in `validation.log` for detailed results
- Distance scores are relative—compare across similar queries
