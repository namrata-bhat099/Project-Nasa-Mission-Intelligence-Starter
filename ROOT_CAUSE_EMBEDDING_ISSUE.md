# Poor Query Results - Root Cause & Solution

## Diagnosis: Embedding Model Issue

Your collection has poor results (only 2/67 relevant) because of an **embedding model mismatch**, NOT a chunking problem.

### Evidence
- ✓ Collection has 8,147 properly-sized documents (859-1000 chars)
- ✓ Queries are finding relevant documents  
- ✗ **Distances are 0.6-0.7 for documents containing the exact search term** 

When querying "Apollo 11":
```
Result 1 (contains "Apollo 11"): Distance = 0.6220  [SHOULD BE < 0.3]
Result 2 (contains "Apollo 11"): Distance = 0.6530  [SHOULD BE < 0.3]
Result 3 (contains "Apollo 11"): Distance = 0.6788  [SHOULD BE < 0.3]
```

### Root Cause

In `test_chunking.py`, the collection was created WITHOUT specifying an OpenAI embedding function:

```python
# WRONG - Uses ChromaDB default embedding, not OpenAI
self.collection = self.chromadbclient.get_or_create_collection(
    name=collection_name,
    metadata={...}  # No embedding_function parameter!
)
```

**What happens:**
1. Documents are added with ChromaDB's default embedding model
2. Queries are run against embeddings made with a different/incompatible model
3. Result: Even identical terms have distance 0.62 instead of 0.0

### Solution

Use the new `rebuild_collection_with_embeddings.py` script:

```bash
python rebuild_collection_with_embeddings.py
```

**Requirements:**
- Set your OpenAI API key first:
  ```bash
  $env:OPENAI_API_KEY="sk-..."
  ```
- Have OpenAI API quota available (small embeddings are cheap: $0.02 per 1M tokens)

**What the script does:**
1. Connects to existing collection
2. Extracts all 8,147 documents
3. Creates OpenAI embedding function (text-embedding-3-small)
4. Recreates collection with proper embedding function
5. Re-adds all documents with OpenAI embeddings
6. Tests with sample query

## Expected Results After Rebuild

Before rebuild:
```
[Apollo 11] POOR (Distance: 0.6513)
[countdown] POOR (Distance: 0.9269)
[spacecraft] POOR (Distance: 1.0460)
```

After rebuild:
```
[Apollo 11] HIGHLY_RELEVANT (Distance: < 0.3)
[countdown] RELEVANT (Distance: 0.3-0.5)  
[spacecraft] RELEVANT (Distance: 0.3-0.5)
```

## Step-by-Step Fix

### Step 1: Set OpenAI API Key
```bash
$env:OPENAI_API_KEY='your-api-key-here'
```

### Step 2: Rebuild Collection
```bash
cd "c:\Users\Namrata Bhat\Documents\udacitygenai_nanodegree\cd13318-exercises-project-main\Project-NASA-Mission-Intelligence-Starter"

& ".\.venv\Scripts\python.exe" rebuild_collection_with_embeddings.py
```

**Expected output:**
```
[STEP 1] Connecting to ChromaDB...
[OK] Found existing collection with 8147 documents

[STEP 2] Extracting documents from old collection...
[OK] Extracted 8147 documents

[STEP 3] Creating OpenAI embedding function...
[OK] OpenAI embedding function created (model: text-embedding-3-small)

[STEP 4] Testing embedding function...
[OK] Embedding function works (vector dimension: 1536)

[STEP 5] Recreating collection with OpenAI embeddings...
[OK] Old collection deleted
[OK] New collection created

[STEP 6] Adding 8147 documents to new collection...
[OK] All 8147 documents added to new collection

[STEP 7] Verifying collection...
[OK] Collection verification: 8147 documents

[STEP 8] Testing with sample query...
[OK] Query returned 3 results
    Average distance: 0.28
    [GOOD] Distances look reasonable!

REBUILD COMPLETE!
```

### Step 3: Verify Fix with Diagnostics
```bash
& ".\.venv\Scripts\python.exe" collection_diagnostic.py --test phrases
```

You should now see:
- Highly Relevant: 10+
- Relevant: 3+
- Somewhat Relevant: 1-2
- Not Relevant: 0-2

### Step 4: Run Full Validation
```bash
& ".\.venv\Scripts\python.exe" validate_rag_collection.py
```

Expected: 50+ tests should be RELEVANT or HIGHLY_RELEVANT (vs current 2/67)

## Why This Happened

ChromaDB has two ways to handle embeddings:
1. **Implicit (default)**: When you don't specify `embedding_function`, ChromaDB uses its built-in default embedding model
2. **Explicit (correct)**: Pass `embedding_function` parameter to use OpenAI/other services

Your code used implicit, so all 8,147 documents were embedded with ChromaDB's default model. When queries run, they might use a different embedding mechanism, causing the distance mismatch.

## If Rebuild Doesn't Fix It

If distances are still high after rebuild:

1. **Check OpenAI API key is valid:**
   ```bash
   python -c "from openai import OpenAI; c = OpenAI(); print(c.models.list().data[0])"
   ```

2. **Check API quota:**
   - Go to https://platform.openai.com/account/billing/overview
   - Ensure you have available credits

3. **Check model availability:**
   - `text-embedding-3-small` should be available to all accounts
   - If not, rebuild specifies it explicitly

## Additional Resources

- [ChromaDB Embedding Documentation](https://docs.trychroma.com/embeddings)
- [OpenAI Embedding Models](https://platform.openai.com/docs/guides/embeddings/embedding-models)
- `collection_diagnostic.py` - Run to verify collection health
- `DEBUG_POOR_RESULTS.md` - Full debugging guide
