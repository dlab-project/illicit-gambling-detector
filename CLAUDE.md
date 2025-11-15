# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **illegal gambling domain detection crawler MVP** that searches keywords, extracts URLs from search engine results, and stores them locally. The system is designed purely for URL collection without domain analysis, risk scoring, or UI components.

## Development Setup

### Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .
```

### Running the Crawler
```bash
# Basic execution
python main.py

# With virtual environment
source .venv/bin/activate && python main.py
```

## Architecture

The crawler follows a modular design with clear separation of concerns:

**Core Components:**
- `src/keyword_manager.py` - Loads keywords from JSON and generates 2-keyword combinations
- `src/search_engine.py` - Handles web searching with Selenium/requests fallback mechanism
- `src/url_extractor.py` - Extracts and cleans URLs from HTML using BeautifulSoup
- `src/json_storage.py` - Manages JSON file storage with deduplication
- `src/crawler.py` - Main orchestrator that coordinates all components

**Configuration Files:**
- `keywords.json` - Contains the list of gambling-related keywords to search
- `settings.json` - Controls search engine, headless mode, delays, and output settings
- `results.json` - Output file containing collected URLs with metadata

**Search Engine Strategy:**
The system implements a fallback mechanism: attempts Selenium with Chrome first, automatically falls back to requests-based HTTP calls if Chrome/ChromeDriver fails. This ensures functionality across different environments (including WSL/containers where GUI apps may not work).

**Data Flow:**
1. KeywordManager loads keywords and generates combinations
2. SearchEngine performs searches (Selenium → requests fallback)
3. URLExtractor parses HTML and cleans URLs (removes tracking parameters)
4. JSONStorage saves results with deduplication and timestamps
5. Crawler orchestrates the process with configurable delays between searches

**Important Implementation Notes:**
- The search engine includes bot detection avoidance (user-agent rotation, random delays, automation flags disabled)
- URL extraction filters out invalid URLs, removes tracking parameters, and deduplicates results
- All results are stored with timestamp and source keyword for traceability
- The system handles interruptions gracefully and provides progress feedback