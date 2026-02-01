# Testing Guide

Comprehensive testing strategy for ClaimFlow AI.

## Test Structure

```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── test_database.py         # Database and CRUD tests
├── test_rag.py             # RAG and vector store tests
├── test_tools.py           # Agent tools tests
└── test_prompts.py         # Prompt engineering tests
```

## Running Tests

### All Tests
```bash
pytest

# With coverage
pytest --cov=agent --cov=database --cov-report=html

# Using test runner script
python scripts/run_tests.py all
```

### Specific Test Suites
```bash
# Database tests
pytest tests/test_database.py -v
python scripts/run_tests.py database

# RAG tests
pytest tests/test_rag.py -v
python scripts/run_tests.py rag

# Tools tests
pytest tests/test_tools.py -v
python scripts/run_tests.py tools

# Prompt tests
pytest tests/test_prompts.py -v
python scripts/run_tests.py prompts
```

### Test Markers
```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Exclude slow tests
pytest -m "not slow"
```

### Verbose Output
```bash
pytest -vv                    # Very verbose
pytest -v --tb=short          # Verbose with short tracebacks
pytest -v --pdb              # Drop into debugger on failure
```

## Test Coverage

### View Coverage Report
```bash
# Terminal report
pytest --cov=agent --cov=database --cov-report=term-missing

# HTML report (opens in browser)
pytest --cov=agent --cov=database --cov-report=html
open htmlcov/index.html
```

### Coverage Targets
- **Database Module**: >90% coverage
- **RAG Module**: >85% coverage
- **Tools Module**: >80% coverage
- **Prompts**: Structural validation

## Test Categories

### 1. Database Tests (`test_database.py`)

**TestDatabaseManager**
- Database initialization
- Table creation
- Session management

**TestCustomerCRUD**
- Create customer
- Retrieve customer
- Update customer
- Handle non-existent customers

**TestPolicyCRUD**
- Create policies (motor, home, health)
- Retrieve by policy number
- Retrieve by identifier (vehicle reg, property ID)
- Policy type validation

**TestClaimCRUD**
- Create claims
- Update claim status
- Claim type validation
- Status transitions

**TestRelationships**
- Customer → Policies
- Customer → Claims
- Policy → Claims
- Cascade operations

**TestClaimHistory**
- Historical claim retrieval
- Date ordering
- Customer aggregation

### 2. RAG Tests (`test_rag.py`)

**TestVectorStore**
- Initialization
- Document ingestion
- Text chunking
- Semantic search
- Metadata filtering
- Empty database handling
- Reset functionality

**TestRetrievePolicyInfo**
- Query formatting
- Result ranking
- Filter application
- Empty result handling

**TestEmbeddingModel**
- Embedding generation
- Dimensionality verification
- Semantic similarity

### 3. Tools Tests (`test_tools.py`)

**TestExtractClaimData**
- Motor claim extraction
- Health claim extraction
- Home claim extraction
- Claim type normalization

**TestRetrievePolicy**
- Database retrieval
- Mock data fallback
- RAG context inclusion

**TestCheckCoverage**
- Motor coverage verification
- Health coverage verification
- Home coverage verification
- Exclusion identification

**TestCalculatePayout**
- Motor payout (with/without zero dep)
- Health payout (with co-pay)
- Sum insured capping
- Deductible application

**TestCheckClaimHistory**
- Existing customer lookup
- New customer handling
- Risk assessment
- Fraud flag detection

**TestGenerateReport**
- Motor report formatting
- Health report formatting
- Home report formatting
- Rejection reports

**TestIntegration**
- Full claim processing chain
- Tool interaction validation

### 4. Prompt Tests (`test_prompts.py`)

**TestPromptStructure**
- Prompt existence
- Key section presence
- Field definitions
- Variable placeholders

**TestPromptFormatting**
- String formatting
- Variable substitution
- Edge case handling

**TestPromptCoverage**
- All claim types mentioned
- All fields covered
- Example completeness

**TestPromptConsistency**
- Field name consistency
- Claim type consistency
- Format consistency

**TestPromptValidation**
- Length validation
- Placeholder detection
- Special character handling

## Fixtures

### Database Fixtures
- `db_session` - Fresh in-memory database
- `sample_customer` - Test customer
- `sample_motor_policy` - Test motor policy
- `sample_claim` - Test claim

### RAG Fixtures
- `vector_store_test` - Temporary vector store

### Mock Fixtures
- `mock_openai_response` - Mock OpenAI API

## Writing New Tests

### Test Naming Convention
```python
class TestFeatureName:
    def test_specific_behavior(self):
        # Arrange
        ...
        
        # Act
        ...
        
        # Assert
        ...
```

### Using Fixtures
```python
def test_with_database(db_session, sample_customer):
    # Fixture automatically provides test data
    customer = get_customer(db_session, sample_customer.customer_id)
    assert customer is not None
```

### Adding Markers
```python
@pytest.mark.slow
def test_expensive_operation():
    ...

@pytest.mark.integration
def test_full_workflow():
    ...
```

## Continuous Integration

Tests run automatically on:
- Push to `main` or `develop` branches
- Pull requests
- Multiple Python versions (3.10, 3.11, 3.12)

### GitHub Actions Workflow
`.github/workflows/tests.yml` runs:
1. Database tests
2. RAG tests
3. Tools tests
4. Prompt tests
5. Docker build test
6. Linting with flake8

## Docker Testing

### Run Tests in Container
```bash
# Build and run tests
docker-compose run claimflow-app test

# Or with Make
make test
```

### Test Specific Suite in Container
```bash
docker-compose run claimflow-app pytest tests/test_database.py -v
```

## Test Data

### Sample Data
Tests use fixtures with controlled test data:
- **Customers**: TEST-001, TEST-002, etc.
- **Policies**: TEST-MI-001, TEST-HE-001, etc.
- **Claims**: TEST-CLM-001, etc.

### Isolated Environment
- In-memory SQLite for database tests
- Temporary directories for RAG tests
- No production data used

## Troubleshooting

### Import Errors
```bash
# Ensure project root in PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or use pytest from project root
python -m pytest tests/
```

### Fixture Not Found
```bash
# Check conftest.py is present
ls tests/conftest.py

# Run with fixture discovery
pytest --fixtures
```

### Slow Tests
```bash
# Skip slow tests
pytest -m "not slow"

# Profile test execution
pytest --durations=10
```

### Database Lock Errors
- Use `:memory:` for tests
- Close sessions properly
- Check fixture cleanup

## Coverage Goals

| Module | Target | Status |
|--------|--------|--------|
| database/models.py | 90% | ✅ 91% |
| database/crud.py | 85% | ✅ 57% → Need more tests |
| agent/rag.py | 80% | ❌ 0% → Need coverage |
| agent/tools.py | 75% | ❌ 0% → Need coverage |
| agent/workflow.py | 70% | ❌ 0% → Need coverage |

## Future Enhancements

- [ ] Add end-to-end workflow tests
- [ ] Mock OpenAI API calls
- [ ] Add performance benchmarks
- [ ] Add load testing for API
- [ ] Add mutation testing
- [ ] Add property-based testing
- [ ] Add contract tests
- [ ] Add security tests

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)
