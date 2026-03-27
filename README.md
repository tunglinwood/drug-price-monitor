# Drug Price Monitor - Compound Tracking Dashboard

Automated tracking system for drug development compounds across multiple therapeutic areas.

## 🎯 Overview

This project maintains a comprehensive database of drug compounds with automated daily updates, validation, and a Streamlit dashboard for visualization.

**Live Dashboard:** https://tunglinwood-drug-price-monitor-g2n6ki5f2v8xczavexxlvd.streamlit.app

## 📊 Tracked Compounds

| Board | Compounds | Status |
|-------|-----------|--------|
| **GLP-1 Compounds** | 25 | Daily automated search |
| **THR-Beta Agonists** | 19 | Manual verification (9 verified, 2 partial, 8 not found) |
| **FGF21 Analogues** | 4 | Manual verification (3 active, 1 discontinued) |
| **Pan-PPAR Agonists** | 10 | Manual verification (1 marketed, 2 clinical, 1 discontinued, 6 preclinical) |

**Total:** 58 compounds tracked

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd drug-price-api
pip install -r requirements.txt
```

### 2. Run Dashboard Locally

```bash
streamlit run streamlit_app.py
```

Access at: http://localhost:8501

### 3. Login Credentials

Default admin credentials (change in production!):
- Username: `admin`
- Password: `admin123`

## 🏗️ Architecture

### Pipeline Components

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  1. SEARCH      │ →   │  2. EXTRACT     │ →   │  3. VALIDATE    │
│  (Raw Text)     │     │  (JSON)         │     │  (Merge/Flag)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

**Files:**
- `single_agent_search.py` - Web search agent (returns raw text)
- `extraction_agent.py` - Extracts structured JSON from raw search results
- `subagent_validator.py` - Validates new data against existing inventory
- `process_queue.py` - Daily batch processor (25 compounds, 5 concurrent)

### Data Files

- `compounds.json` - GLP-1 receptor agonists (25 compounds)
- `compounds_thrbeta.json` - THR-beta agonists (19 compounds)
- `compounds_fgf21.json` - FGF21 analogues (4 compounds)
- `compounds_ppar.json` - Pan-PPAR agonists (10 compounds)

### Authentication

- `simple_auth.py` - Simple bcrypt-based authentication
- `auth_config.yaml` - User credentials (bcrypt hashed passwords)

## 📅 Daily Execution

**Schedule:** 02:00 GMT+8 daily (via cron)

**Process:**
1. **02:00** - Launch 5 concurrent searches (Batch 1)
2. **02:05-05:00** - Continue batches (25 compounds total)
3. **05:00-05:10** - Extract JSON from raw results
4. **05:10-05:15** - Validate and merge data
5. **05:15** - Git commit & push
6. **05:17** - Streamlit Cloud auto-redeploys

## 🔧 Quality Checks

### Setup Pre-commit Hooks

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### Run Quality Checks Manually

```bash
# Lint with Ruff
ruff check .
ruff format .

# Type check with Mypy
mypy .

# Run all pre-commit hooks
pre-commit run --all-files
```

### Configuration Files

- `pyproject.toml` - Ruff linter configuration
- `mypy.ini` - Mypy type checker configuration
- `.pre-commit-config.yaml` - Pre-commit hooks configuration
- `.gitignore` - Git ignore patterns

## 📁 Project Structure

```
drug-price-api/
├── streamlit_app.py           # Main dashboard application
├── simple_auth.py             # Authentication module
├── auth_config.yaml           # User credentials
├── compounds*.json            # Compound data files
│
├── single_agent_search.py     # Search agent
├── extraction_agent.py        # Extraction agent
├── subagent_validator.py      # Validation agent
├── process_queue.py           # Queue processor
│
├── search_results/            # Raw search text files
├── validation_results/        # Validation outputs
│
├── requirements.txt           # Production dependencies
├── requirements-dev.txt       # Development dependencies
├── pyproject.toml            # Ruff configuration
├── mypy.ini                  # Mypy configuration
├── .pre-commit-config.yaml   # Pre-commit hooks
└── README.md                 # This file
```

## 🛠️ Development

### Adding New Compounds

1. Add compound to the appropriate `compounds_*.json` file
2. Update the summary statistics
3. Commit and push to trigger dashboard redeployment

### Adding New Therapeutic Boards

1. Create new `compounds_<name>.json` file
2. Update `streamlit_app.py` sidebar navigation
3. Add board selection logic
4. Commit and push

### Modifying Validation Rules

Edit `subagent_validator.py` to adjust:
- Merge decisions
- Quality regression flags
- Manual review triggers

## 📝 Validation Rules

| Field | Rule | Action |
|-------|------|--------|
| Clinical Trials | New has fewer trials | **MERGE** (keep all) |
| PubChem CID | Existing has CID, new is null | **KEEP EXISTING** |
| Key Findings | New is more specific | **ACCEPT NEW** |
| Clinical Stage | New is less advanced | **FLAG** (regression) |
| Data Quality | New is lower quality | **FLAG** (regression) |
| Contradictions | Conflicting data | **MANUAL REVIEW** |

## 🔐 Security

- **Never commit** `.env` files or API keys
- **Change default passwords** in production
- **Use bcrypt** for password hashing
- **Review manually** before auto-deploying sensitive data

## 📊 Data Quality Labels

- **verified** - Sufficient public data from authoritative sources
- **partial** - Some data available but incomplete
- **not_found** - No public data found across major databases
- **pending** - Awaiting verification

## 🌐 Deployment

### Streamlit Cloud

1. Connect GitHub repository
2. Set main file: `streamlit_app.py`
3. Auto-deploys on every push to `main` branch

### Local Development

```bash
streamlit run streamlit_app.py --server.port 8501
```

## 📈 Future Enhancements

- [ ] Email/Slack notifications for daily summaries
- [ ] Manual review queue UI
- [ ] Historical data tracking & trends
- [ ] Export to CSV/Excel
- [ ] API endpoints for programmatic access
- [ ] Supplier price tracking
- [ ] Combination therapy tracking

## 📄 License

MIT License

## 🔗 Resources

- [Streamlit Docs](https://docs.streamlit.io/)
- [Ruff Docs](https://docs.astral.sh/ruff/)
- [Pre-commit Docs](https://pre-commit.com/)
- [Mypy Docs](https://mypy.readthedocs.io/)
