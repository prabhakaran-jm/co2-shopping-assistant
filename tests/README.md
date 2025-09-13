# CO2-Aware Shopping Assistant - Test Suite

## 🧪 **Comprehensive Testing Strategy**

This test suite provides comprehensive coverage for the CO2-Aware Shopping Assistant, ensuring reliability, performance, and correctness across all components.

## 📁 **Test Structure**

```
tests/
├── unit/                    # Unit tests for individual components
│   ├── test_agents.py      # AI agents testing
│   ├── test_mcp_servers.py # MCP servers testing
│   └── test_a2a_protocol.py # A2A protocol testing
├── integration/             # Integration tests
│   └── test_api_endpoints.py # API endpoint testing
├── e2e/                     # End-to-end tests
│   └── test_user_journey.py # Complete user workflows
├── fixtures/                # Test data and mocks
│   └── sample_data.json    # Sample test data
├── conftest.py             # Pytest configuration and fixtures
└── README.md               # This file
```

## 🎯 **Test Categories**

### **Unit Tests** (`tests/unit/`)
- **Purpose**: Test individual components in isolation
- **Coverage**: AI agents, MCP servers, A2A protocol
- **Mocking**: Heavy use of mocks for external dependencies
- **Speed**: Fast execution (< 1 second per test)

### **Integration Tests** (`tests/integration/`)
- **Purpose**: Test component interactions and API endpoints
- **Coverage**: API endpoints, service integrations
- **Mocking**: Limited mocking, real component interactions
- **Speed**: Medium execution (1-5 seconds per test)

### **End-to-End Tests** (`tests/e2e/`)
- **Purpose**: Test complete user workflows
- **Coverage**: Full user journeys, error scenarios
- **Mocking**: Minimal mocking, realistic scenarios
- **Speed**: Slower execution (5-30 seconds per test)

## 🚀 **Running Tests**

### **Prerequisites**
```bash
# Install test dependencies
pip install -r requirements-test.txt
```

### **Basic Test Execution**
```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests only
pytest tests/e2e/          # End-to-end tests only

# Run specific test file
pytest tests/unit/test_agents.py

# Run specific test function
pytest tests/unit/test_agents.py::TestHostAgent::test_host_agent_initialization
```

### **Using the Test Runner Script**
```bash
# Run all tests
./scripts/run-tests.sh

# Run with coverage
./scripts/run-tests.sh --coverage

# Run unit tests only
./scripts/run-tests.sh --unit

# Run with parallel execution
./scripts/run-tests.sh --all --parallel

# Generate HTML report
./scripts/run-tests.sh --all --html
```

### **Advanced Test Options**
```bash
# Run with coverage and HTML report
pytest --cov=src --cov-report=html --cov-report=term-missing

# Run tests in parallel
pytest -n auto

# Run with verbose output
pytest -v -s

# Run only fast tests (exclude slow ones)
pytest -m "not slow"

# Run specific markers
pytest -m "unit and not slow"
```

## 📊 **Test Coverage**

### **AI Agents Testing**
- **Host Agent**: Routing, orchestration, error handling
- **Product Discovery Agent**: Search, recommendations, inventory
- **CO2 Calculator Agent**: Emissions calculation, eco recommendations
- **Cart Management Agent**: Add/remove items, quantity updates
- **Checkout Agent**: Order processing, payment coordination

### **MCP Servers Testing**
- **Boutique MCP**: Product APIs, cart APIs, checkout APIs
- **CO2 MCP**: CO2 calculation APIs, environmental data APIs
- **Error Handling**: API failures, network issues, timeouts
- **Data Validation**: Input validation, response parsing

### **A2A Protocol Testing**
- **Message Creation**: Valid message construction
- **Serialization**: JSON serialization/deserialization
- **Validation**: Message validation and error handling
- **Communication Patterns**: Request-response, broadcast, chain

### **API Endpoints Testing**
- **Health Check**: System health monitoring
- **Chat Endpoint**: Main conversation interface
- **Product APIs**: Product listing and details
- **Cart APIs**: Cart operations
- **CO2 APIs**: CO2 calculations
- **Checkout APIs**: Order processing

### **User Journey Testing**
- **Eco-Friendly Shopping**: Complete sustainable purchase workflow
- **CO2 Education**: User learning about environmental impact
- **Error Recovery**: Handling failures and edge cases
- **Performance**: Concurrent users, load testing

## 🔧 **Test Configuration**

### **Pytest Configuration** (`pytest.ini`)
- **Test Discovery**: Automatic test discovery
- **Markers**: Custom markers for test categorization
- **Output**: Colored output, short tracebacks
- **Async Support**: Automatic async test handling
- **Logging**: Detailed logging configuration

### **Test Fixtures** (`conftest.py`)
- **Sample Data**: Realistic test data
- **Mock Objects**: Pre-configured mocks
- **Environment**: Test environment setup
- **Session Management**: Test session handling

### **Sample Data** (`fixtures/sample_data.json`)
- **Products**: Sample eco-friendly products
- **Cart Data**: Sample shopping cart contents
- **CO2 Data**: Sample emission calculations
- **User Queries**: Sample user interactions
- **API Responses**: Mock API responses

## 📈 **Test Metrics**

### **Coverage Targets**
- **Unit Tests**: > 90% code coverage
- **Integration Tests**: > 80% API coverage
- **E2E Tests**: > 70% user journey coverage

### **Performance Targets**
- **Unit Tests**: < 1 second per test
- **Integration Tests**: < 5 seconds per test
- **E2E Tests**: < 30 seconds per test
- **Total Suite**: < 5 minutes for full run

### **Quality Metrics**
- **Test Reliability**: > 99% pass rate
- **Test Maintainability**: Clear, readable test code
- **Test Documentation**: Comprehensive test documentation

## 🐛 **Debugging Tests**

### **Common Issues**
1. **Import Errors**: Ensure `src` is in Python path
2. **Mock Issues**: Check mock configurations
3. **Async Issues**: Use `pytest-asyncio` properly
4. **Environment Issues**: Check test environment setup

### **Debug Commands**
```bash
# Run with debug output
pytest -v -s --tb=long

# Run single test with debug
pytest -v -s tests/unit/test_agents.py::TestHostAgent::test_host_agent_initialization

# Run with logging
pytest --log-cli-level=DEBUG

# Run with pdb debugger
pytest --pdb
```

### **Test Data Issues**
- Check `fixtures/sample_data.json` for correct data
- Verify mock responses match expected format
- Ensure test data is realistic and comprehensive

## 🚀 **CI/CD Integration**

### **GitHub Actions Example**
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      - name: Run tests
        run: |
          pytest --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### **Test Reports**
- **Coverage Report**: `htmlcov/index.html`
- **HTML Report**: `test_report.html`
- **JSON Report**: `test_report.json`
- **JUnit Report**: `junit.xml`

## 🎯 **Best Practices**

### **Writing Tests**
1. **Arrange-Act-Assert**: Clear test structure
2. **Descriptive Names**: Clear test function names
3. **Single Responsibility**: One assertion per test
4. **Mock External Dependencies**: Isolate units under test
5. **Use Fixtures**: Reusable test data and setup

### **Test Data**
1. **Realistic Data**: Use realistic test data
2. **Edge Cases**: Test boundary conditions
3. **Error Scenarios**: Test error handling
4. **Performance**: Test with realistic data volumes

### **Maintenance**
1. **Regular Updates**: Keep tests up to date
2. **Refactoring**: Refactor tests with code changes
3. **Documentation**: Document complex test scenarios
4. **Review**: Regular test code reviews

## 🏆 **Hackathon Benefits**

### **Demonstrates Quality**
- **Professional Development**: Industry-standard testing practices
- **Code Reliability**: Comprehensive test coverage
- **Maintainability**: Well-structured, documented tests
- **CI/CD Ready**: Automated testing pipeline

### **Technical Excellence**
- **Unit Testing**: Individual component testing
- **Integration Testing**: Component interaction testing
- **E2E Testing**: Complete workflow testing
- **Performance Testing**: Load and stress testing

### **Production Readiness**
- **Error Handling**: Comprehensive error scenario testing
- **Edge Cases**: Boundary condition testing
- **User Scenarios**: Realistic user journey testing
- **Monitoring**: Test result reporting and metrics

## 📚 **Additional Resources**

- **Pytest Documentation**: https://docs.pytest.org/
- **FastAPI Testing**: https://fastapi.tiangolo.com/tutorial/testing/
- **Async Testing**: https://pytest-asyncio.readthedocs.io/
- **Coverage Testing**: https://coverage.readthedocs.io/

---

*This comprehensive test suite ensures the CO2-Aware Shopping Assistant is reliable, performant, and ready for production deployment! 🌱🤖*
