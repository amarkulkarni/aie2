# RAG Application with PDF Support - Testing Guide

## 🚀 Quick Start

### 1. Test PDF Functionality (No API Key Required)
```bash
# Test with default PDF
python quick_test.py

# Test with your own PDF
python quick_test.py data/your_document.pdf

# Test with API key
python quick_test.py data/your_document.pdf --api-key sk-your-key-here
```

### 2. Test Complete RAG Pipeline (API Key Required)
```bash
# With environment API key
export OPENAI_API_KEY="your-api-key-here"
python test_all.py

# With command line API key
python test_all.py data/your_document.pdf --api-key sk-your-key-here
```

### 3. Test End-to-End RAG Pipeline
```bash
# With environment API key
python test_rag_end_to_end.py

# With command line API key
python test_rag_end_to_end.py data/your_document.pdf --api-key sk-your-key-here
```

## 📋 Command Line Usage

All test scripts support the same command line interface:

```bash
python <script_name> [pdf_file] [--api-key KEY]
```

### Parameters:
- `pdf_file` (optional): Path to PDF file to test (default: `data/ai_research_paper.pdf`)
- `--api-key` (optional): OpenAI API key (can also use environment variable)

### Examples:

```bash
# Use default PDF, no API key
python quick_test.py

# Use custom PDF, no API key
python quick_test.py data/my_research.pdf

# Use custom PDF with API key
python quick_test.py data/my_research.pdf --api-key sk-abc123...

# Use default PDF with API key
python test_all.py --api-key sk-abc123...
```

## 📋 What Each Test Covers

### `quick_test.py`
- ✅ PDF loading with all methods (pdfplumber, pymupdf, pypdf2)
- ✅ Text splitting and chunking
- ✅ Mixed directory loading (TXT + PDF files)
- ✅ Content quality validation
- ⚡ Fast execution, no API calls

### `test_all.py`
- ✅ All quick test functionality
- ✅ Vector database creation and similarity search
- ✅ RAG pipeline with question answering
- 🔑 Requires OpenAI API key for full functionality

### `test_rag_end_to_end.py`
- ✅ Complete end-to-end RAG pipeline
- ✅ PDF loading → chunking → vectorization → retrieval → generation
- ✅ Multiple question answering examples
- 🔑 Requires OpenAI API key

## 🧪 Test Results

### Without API Key:
```
📄 PDF Loading: ✅ PASSED
✂️  Text Processing: ✅ PASSED
🔍 Vector Database: ⚠️  SKIPPED (needs API key)
🤖 RAG Pipeline: ⚠️  SKIPPED (needs API key)
```

### With API Key:
```
📄 PDF Loading: ✅ PASSED
✂️  Text Processing: ✅ PASSED
🔍 Vector Database: ✅ PASSED
🤖 RAG Pipeline: ✅ PASSED
```

## 🔧 Troubleshooting

### Common Issues:

1. **Import Errors**: Make sure you're in the correct directory and have installed dependencies:
   ```bash
   pip install PyPDF2 pdfplumber pymupdf reportlab
   ```

2. **PDF File Not Found**: Ensure the test PDF files exist:
   ```bash
   ls data/
   # Should show: ai_research_paper.pdf, sample_document.pdf, PMarcaBlogs.txt
   ```

3. **API Key Issues**: Set your OpenAI API key:
   ```bash
   export OPENAI_API_KEY="your-key-here"
   # Or create a .env file with: OPENAI_API_KEY=your-key-here
   ```

## 📁 Test Files

- `quick_test.py` - Fast PDF functionality test
- `test_all.py` - Comprehensive test suite
- `test_rag_end_to_end.py` - Complete RAG pipeline test
- `data/ai_research_paper.pdf` - Test PDF file
- `data/sample_document.pdf` - Simple test PDF

## 🎯 Expected Output

When everything is working correctly, you should see:
- ✅ All PDF loading methods working
- ✅ Text splitting creating proper chunks
- ✅ Vector database with similarity search
- ✅ RAG pipeline answering questions about PDF content
- 🎉 "All tests passed!" message

## 🚀 Next Steps

1. Run `python quick_test.py` to verify PDF support
2. Set your OpenAI API key
3. Run `python test_all.py` for complete testing
4. Use the enhanced RAG application with your own PDF files!

Your RAG application now supports both TXT and PDF files seamlessly! 🎉
