# Practical Examples: Running Validations

This document shows real examples of how to run validations and interpret the results.

---

## Example 1: Quick Check with simple_validator.py

### Command
```bash
python simple_validator.py --query "Tell me about Apollo 11"
```

### Expected Output
```
================================================================================
QUESTION: Tell me about Apollo 11
================================================================================
Results found: 5
Average distance: 0.23

[Result #1] HIGHLY_RELEVANT ✓✓
Distance: 0.12
Source: a11transcript_pao | Mission: apollo_11
Category: public_affairs_officer | Chunk: 1
Text: Apollo 11 Spacecraft Commentary July 16-24,1969 MANNED SPACECRAFT CENTER...

[Result #2] HIGHLY_RELEVANT ✓✓
Distance: 0.18
Source: a11transcript_tec | Mission: apollo_11
Category: technical | Chunk: 5
Text: APOLLO 11 - SPACECRAFT COMMENTARY Technical procedures and system checks...

[Result #3] RELEVANT ✓
Distance: 0.35
Source: Apollo_11_Flight_Plan | Mission: apollo_11
Category: flight_plan | Chunk: 12
Text: Mission timeline and procedures for Apollo 11 spacecraft...

[Result #4] RELEVANT ✓
Distance: 0.42
Source: a11transcript_cm | Mission: apollo_11
Category: command_module | Chunk: 8
Text: Command module operations and procedures...

[Result #5] SOMEWHAT_RELEVANT ◐
Distance: 0.58
Source: NASA_NTRS_Archive | Mission: apollo_11
Category: technical_report | Chunk: 3
Text: Technical specifications and mission overview documentation...
```

**Interpretation:**
- ✓ Excellent! All 5 results are from Apollo 11 (correct mission)
- ✓ Top 3 results are highly relevant (distance < 0.3)
- ✓ Average distance is low (0.23), indicating strong semantic match
- ✓ Results cover different document types (transcripts, flight plan, technical)

---

## Example 2: Testing with validate_rag_collection.py

### Command
```bash
python validate_rag_collection.py --category missions
```

### Expected Output
```
================================================================================
TESTING: Mission Queries
================================================================================

[apollo_11_overview]
Query: Tell me about Apollo 11 mission
Status: SUCCESS
Relevance: HIGHLY_RELEVANT ✓✓
Results: 5
Avg Distance: 0.2134
Top Distances: [0.1234, 0.1856, 0.2456]
Source: a11transcript_pao
Mission: apollo_11
Preview: Apollo 11 Spacecraft Commentary July 16-24,1969...
--------------------------------------------------------------------------------

[apollo_11_launch]
Query: Apollo 11 launch date and time
Status: SUCCESS
Relevance: RELEVANT ✓
Results: 5
Avg Distance: 0.3845
Top Distances: [0.2123, 0.3456, 0.4567]
Source: a11transcript_pao
Mission: apollo_11
Preview: This is Apollo/Saturn Launch Control T minus 1 hour...
--------------------------------------------------------------------------------

[apollo_13_overview]
Query: Apollo 13 mission overview
Status: SUCCESS
Relevance: HIGHLY_RELEVANT ✓✓
Results: 5
Avg Distance: 0.2234
Top Distances: [0.1567, 0.2123, 0.2890]
Source: AS13_PAO_textract_full_text
Mission: apollo_13
Preview: Apollo 13 mission details and overview...
--------------------------------------------------------------------------------

[apollo_13_problem]
Query: What happened in Apollo 13 oxygen tank
Status: SUCCESS
Relevance: HIGHLY_RELEVANT ✓✓
Results: 5
Avg Distance: 0.1834
Top Distances: [0.0912, 0.1456, 0.1998]
Source: AS13_CM_textract_full_text
Mission: apollo_13
Preview: Oxygen tank heater short circuit and electrical problems...
--------------------------------------------------------------------------------

[challenger_overview]
Query: Challenger space shuttle mission
Status: SUCCESS
Relevance: RELEVANT ✓
Results: 5
Avg Distance: 0.4123
Top Distances: [0.2345, 0.3890, 0.4567]
Source: 107-AAG_STS-51L_Mission_Audio_transcript
Mission: challenger
Preview: Mission audio transcript for Challenger mission...
--------------------------------------------------------------------------------
```

**Interpretation:**
- ✓ All queries returned results (no empty results)
- ✓ Most queries are highly relevant (distance < 0.3)
- ✓ Results are correctly categorized by mission
- ✓ Apollo 13 oxygen tank query had especially low distance (0.18), showing excellent match
- ✓ This category scores well for validation

---

## Example 3: Running Full Validation

### Command
```bash
python validate_rag_collection.py
```

### Expected Output (Summary Section)
```
================================================================================
VALIDATION SUMMARY
================================================================================

Total Tests: 80
Highly Relevant: 58
Relevant: 14
Somewhat Relevant: 6
Not Relevant: 2
Success Rate (Highly + Relevant): 90.0%
```

**Interpretation:**
- ✓ 80 test queries across all categories
- ✓ 58 (72.5%) are highly relevant - excellent!
- ✓ 14 (17.5%) are relevant - good coverage
- ✓ Only 2 (2.5%) are not relevant - minimal poor results
- ✓ **90% success rate exceeds 80% threshold** ✓

---

## Example 4: Testing Technical Queries

### Command
```bash
python validate_rag_collection.py --category technical
```

### Key Queries & Expected Results

#### Query: "Guidance system navigation computer"
```
Status: SUCCESS
Relevance: HIGHLY_RELEVANT ✓✓
Results: 5
Top Distance: 0.14
Source: a11transcript_tec
Preview: Apollo Guidance Computer (AGC) procedures for navigation...
```
✓ Excellent - Returns technical specifications

#### Query: "Life support system oxygen management"
```
Status: SUCCESS
Relevance: RELEVANT ✓
Results: 5
Top Distance: 0.42
Source: AS13_TEC_textract_full_text
Preview: Life support systems and CO2 scrubbing procedures...
```
✓ Good - Returns system documentation (slightly higher distance due to technical terminology)

#### Query: "Fuel cells power generation"
```
Status: SUCCESS
Relevance: HIGHLY_RELEVANT ✓✓
Results: 5
Top Distance: 0.18
Source: a11transcript_tec
Preview: Fuel cell specifications and power system operations...
```
✓ Excellent - Specific technical terms match well

**Interpretation:**
- ✓ Technical queries retrieve system documentation
- ✓ Distance scores are reasonable (0.14-0.42 range)
- ✓ Results come from technical transcript sources
- ✓ Category performs well for RAG system

---

## Example 5: Testing Incident Queries

### Command
```bash
python validate_rag_collection.py --category incidents
```

### Key Query

#### Query: "Oxygen tank heater short circuit explosion"
```
Status: SUCCESS
Relevance: HIGHLY_RELEVANT ✓✓
Results: 5
Avg Distance: 0.19
Top Distances: [0.09, 0.15, 0.22]
Source: AS13_CM_textract_full_text
Mission: apollo_13

[Result #1] 
Distance: 0.09
Text: "Oxygen tank Number 2 heater failure causing electrical short circuit which led to 
       the explosion and subsequent power loss..."

[Result #2]
Distance: 0.15  
Text: "The damage to oxygen tank systems forced Apollo 13 to abort lunar landing and 
       return to Earth using contingency procedures..."

[Result #3]
Distance: 0.22
Text: "Emergency procedures and response to the oxygen system failure were critical to 
       bringing the crew safely home..."
```

**Interpretation:**
- ✓ Very low distances (0.09 - 0.22) - Excellent semantic match!
- ✓ All results directly address the oxygen tank incident
- ✓ Results show problem, impact, and resolution
- ✓ This is exactly what a RAG system should return for critical incidents

---

## Example 6: Single Custom Query

### Command
```bash
python validate_rag_collection.py --query "How did astronauts prepare for moonwalk"
```

### Output
```
QUESTION: How did astronauts prepare for moonwalk
Status: SUCCESS
Relevance: RELEVANT ✓
Results: 5
Avg Distance: 0.38

Results:
[1] Distance: 0.25 | Source: a11transcript_pao
    "Astronauts trained extensively for lunar surface operations including...
     suit procedures, equipment deployment, and sample collection..."

[2] Distance: 0.35 | Source: Apollo_11_Flight_Plan
    "Moonwalk procedures and checklist items for surface operations..."

[3] Distance: 0.42 | Source: a11transcript_tec
    "EVA (Extravehicular Activity) procedures and timeline..."

[4] Distance: 0.48 | Source: NASA_NTRS_Archive
    "Training schedules and preparation activities for Apollo missions..."

[5] Distance: 0.55 | Source: AS13_PAO
    "Lunar surface procedures and equipment specifications..."
```

**Interpretation:**
- ✓ Results returned (no empty results)
- ✓ Average distance 0.38 - Good relevance
- ✓ Top result has distance 0.25 - Highly relevant
- ✓ Results cover training, procedures, and timeline
- ✓ Custom query works well with collection

---

## Example 7: Problematic Results (What to Watch For)

### Problematic Query Example 1
```
Query: "Oxygen tank problem"
Relevance: SOMEWHAT_RELEVANT ◐
Results: 5
Avg Distance: 0.62

Results:
[1] Distance: 0.45 | Source: a11transcript_pao
    "Oxygen levels in cabin maintained..."

[2] Distance: 0.67 | Source: AS13_TEC
    "General life support system specifications..."

[3] Distance: 0.78 | Source: Apollo_11_Flight_Plan
    "Oxygen management procedures..."

⚠️ Average distance 0.62 is higher than ideal
✓ Solution: Use more specific query: "Apollo 13 oxygen tank heater failure"
```

### Problematic Query Example 2
```
Query: "Tell me about rockets"
Status: NO_RESULTS

Issues: Query too generic
✓ Solution: Try more specific: "Saturn V rocket stages and propulsion systems"
```

### Problematic Query Example 3
```
Query: "What is the meaning of life?"
Status: NO_RESULTS

Issues: Question outside scope of documents
✓ This is expected - collection is for NASA missions only
```

---

## Example 8: Batch Validation with simple_validator.py

### Command
```bash
python simple_validator.py --test-set missions_101
```

### Output
```
Running test set: missions_101
Queries: 3

================================================================================
QUESTION: Tell me about Apollo 11
================================================================================
Results found: 5
Average distance: 0.21
[Result #1] HIGHLY_RELEVANT ✓✓ ...
[Result #2] HIGHLY_RELEVANT ✓✓ ...
[Result #3] RELEVANT ✓ ...

================================================================================
QUESTION: Apollo 13 oxygen tank crisis
================================================================================
Results found: 5
Average distance: 0.18
[Result #1] HIGHLY_RELEVANT ✓✓ ...
[Result #2] HIGHLY_RELEVANT ✓✓ ...

================================================================================
QUESTION: Challenger space shuttle mission
================================================================================
Results found: 5
Average distance: 0.42
[Result #1] RELEVANT ✓ ...
[Result #2] RELEVANT ✓ ...

================================================================================
SUMMARY
================================================================================
Total Queries: 3
Highly Relevant: 4
Relevant: 2
Somewhat Relevant: 0
Not Relevant: 0
Success Rate: 100.0%
```

**Interpretation:**
- ✓ All 3 queries returned results
- ✓ 4 highly relevant, 2 relevant = 100% success
- ✓ Excellent batch validation score
- ✓ Ready for production use

---

## Success Indicators Checklist

✓ You're in good shape if you see:
- [ ] Most queries return results (< 5% empty)
- [ ] Average distances < 0.4 for most queries
- [ ] 70%+ of queries are Highly Relevant or Relevant
- [ ] Mission-specific queries return correct missions
- [ ] Technical queries return system documentation
- [ ] Incident queries return problem descriptions
- [ ] Crew queries return crew activities
- [ ] Success rate > 80%

---

## Performance Benchmarks

### Excellent Collection (Aim for This)
```
- Average distance: 0.15 - 0.30
- Highly Relevant: > 70%
- Relevant: > 20%
- Somewhat Relevant: < 8%
- Not Relevant: < 2%
- Success Rate: > 90%
- Empty Results: < 1%
```

### Good Collection
```
- Average distance: 0.30 - 0.45
- Highly Relevant: > 50%
- Relevant: > 30%
- Somewhat Relevant: < 15%
- Success Rate: 80-90%
```

### Needs Improvement
```
- Average distance: > 0.60
- Highly Relevant: < 40%
- Success Rate: < 70%
- Empty Results: > 10%
```

---

## Tips for Interpreting Results

1. **Compare across categories**: Some categories naturally have higher distances (technical terms)
2. **Look at distances, not just binary relevance**: A distance of 0.28 is better than 0.48
3. **Check metadata**: Verify mission and source are correct
4. **Preview text**: Read the first 300 characters to confirm relevance
5. **Test multiple queries per concept**: "Apollo 11" + "Apollo 11 moonwalk" + "Neil Armstrong"
6. **Iterate**: If scores are low, adjust chunk size and re-process data

---

## Next Steps After Validation

1. ✓ If success rate > 80%: Collection is ready for use
2. ✓ If success rate 60-80%: Minor adjustments may help (chunk size, overlap)
3. ✓ If success rate < 60%: Review data processing and chunk parameters
4. ✓ After deployment: Continue monitoring with periodic validation runs
