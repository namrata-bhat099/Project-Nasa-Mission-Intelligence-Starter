# Debugging Poor Query Results (2/67 Relevant)

## Issue
You're getting only 2 out of 67 tests returning relevant results. This could be due to:
1. Chunks are too small/too large
2. Embeddings aren't capturing semantic meaning properly
3. Queries still don't match document content
4. Collection wasn't properly indexed

## Step 1: Run Diagnostics

```bash
# Run all diagnostics
python collection_diagnostic.py --test all

# Or run specific tests
python collection_diagnostic.py --test health      # Check if collection exists
python collection_diagnostic.py --test chunks      # Examine chunk quality
python collection_diagnostic.py --test phrases     # Test exact phrases from docs
python collection_diagnostic.py --test distance    # Show distance distribution
```

## What to Look For

### 1. Collection Health
```
Total documents: [should be > 100]
```
**If 0:** Data wasn't processed properly. Re-run:
```bash
python test_chunking.py --data-path ./data_text --chroma-dir ./chroma_db_openai
```

### 2. Chunk Quality
```
Chunk Length Statistics:
  Min: X chars
  Max: Y chars
  Avg: Z chars
```

**Analysis:**
- **Too small (< 200)**: Chunks lose context, hard to embed properly
  - Fix: Increase `--chunk-size` to 500-800
  
- **Too large (> 2000)**: Chunks are too broad, embeddings diluted
  - Fix: Decrease `--chunk-size` to 500-800

- **Good range**: 300-1000 chars per chunk

### 3. Exact Phrases Test
```
[Apollo/Saturn Launch Control] [RELEVANT] (Distance: 0.35)
[T minus] [NOT_RELEVANT] (Distance: 0.92)
```

**If most phrases NOT_RELEVANT:**
- Queries don't match document terminology
- OR embeddings model isn't suitable

### 4. Simple Queries Test
```
[Apollo 11] GOOD (Distance: 0.28)
[countdown] GOOD (Distance: 0.32)
[spacecraft] POOR (Distance: 0.75)
```

**If most POOR:**
- Collection indexing problem
- OR embedding model issue

### 5. Distance Distribution
Shows top 10 results and their distances. 
- **All high (> 0.8):** Major indexing problem
- **Mixed (0.2-0.8):** Some working, needs query adjustment
- **All low (< 0.3):** Collection working perfectly

## Step 2: If Collection Health is Good But Queries Fail

### Option A: Re-chunk with Different Size
```bash
# Try larger chunks (better context preservation)
python test_chunking.py --data-path ./data_text \
    --chunk-size 800 \
    --chunk-overlap 150 \
    --chroma-dir ./chroma_db_openai \
    --update-mode replace
```

### Option B: Re-chunk with Smaller Size
```bash
# Try smaller chunks (if too large)
python test_chunking.py --data-path ./data_text \
    --chunk-size 300 \
    --chunk-overlap 50 \
    --chroma-dir ./chroma_db_openai \
    --update-mode replace
```

## Step 3: Verify with Simple Validator
After diagnostics and potential re-chunking:

```bash
# Test with very simple, specific queries
python simple_validator.py --query "Apollo 11"
python simple_validator.py --query "countdown"
python simple_validator.py --query "Apollo 13"
python simple_validator.py --query "Challenger"
```

## Step 4: Run Full Validation Again
```bash
python validate_rag_collection.py --category missions
```

## Common Issues & Fixes

| Issue | Symptom | Fix |
|-------|---------|-----|
| Chunks too small | All distances > 0.7 | Increase chunk-size to 800 |
| Chunks too large | Mixed relevance | Decrease chunk-size to 400 |
| Query mismatch | HIGHLY_RELEVANT on exact phrases, NOT_RELEVANT on descriptive | Use exact phrase-based queries |
| No data | 0 documents | Re-process: `python test_chunking.py --data-path ./data_text` |
| Wrong embedding model | Consistent distance~0.5 | Check OpenAI connection/model |

## Quick Diagnosis Flow

```
1. python collection_diagnostic.py --test health
   ├─ If 0 documents → Re-process data
   └─ If >100 documents → Continue

2. python collection_diagnostic.py --test chunks
   ├─ Check chunk sizes
   ├─ If too small/large → Re-chunk
   └─ If reasonable → Continue

3. python collection_diagnostic.py --test phrases
   ├─ If most [RELEVANT] → Queries need work
   ├─ If mixed → Might be acceptable
   └─ If all NOT_RELEVANT → Major issue

4. python simple_validator.py --query "Apollo 11"
   ├─ If [RELEVANT] → Problem with complex queries
   └─ If NOT_RELEVANT → Collection problem

5. Fix based on findings → Re-validate
```

## What Results Should Look Like

### Healthy Collection:
```
Exact Phrases Test Summary:
  Highly Relevant: 10
  Relevant: 5
  Somewhat Relevant: 2
  Not Relevant: 0
```

### Current (Problem):
```
Only 2/67 [RELEVANT], 65/67 [NOT_RELEVANT]
→ All queries not matching documents
→ Likely chunk size or query mismatch issue
```

## Next Steps

**Run immediately:**
```bash
python collection_diagnostic.py --test all > diagnostic_report.txt
```

Then share what you see in the output, especially:
1. Total documents count
2. Chunk length statistics
3. Which exact phrases are [RELEVANT] vs [NOT_RELEVANT]
4. Distance distribution for "Apollo 11" query
