# CO2-Aware Shopping Assistant - UI Tests

This directory contains comprehensive UI tests for the CO2-Aware Shopping Assistant frontend application.

## Overview

The UI tests validate the frontend functionality including:
- Product data parsing and display
- CO2 emissions analysis and visualization
- Eco score validation and display
- User interaction handling
- Message processing and CO2 savings tracking
- Responsive design elements

## Test Structure

### Files

- **`test-ui.html`** - Interactive HTML test page for manual testing
- **`test-ui.js`** - Automated Jest tests for JavaScript functionality
- **`package.json`** - Node.js dependencies and test configuration
- **`jest.setup.js`** - Jest testing environment setup
- **`run-tests.sh`** - Test runner script with multiple options
- **`README.md`** - This documentation file

### Test Categories

1. **Product Data Validation**
   - Validates product structure and required fields
   - Tests data type validation
   - Ensures product names, prices, and descriptions are present

2. **CO2 Emissions Analysis**
   - Parses CO2 emission data from product responses
   - Categorizes products by impact level (High/Medium/Low)
   - Calculates total CO2 impact across products

3. **Eco Score Validation**
   - Validates eco score format (X/10)
   - Ensures scores are within valid range (1-10)
   - Tests high eco score validation (8-10)

4. **User Interaction Testing**
   - Simulates user input scenarios
   - Tests message handling and response processing
   - Validates CO2 savings extraction and display

5. **Product Display Functionality**
   - Tests product card creation and rendering
   - Validates all product elements are displayed correctly
   - Handles edge cases and error scenarios

## Quick Start

### Prerequisites

- Node.js (v14 or higher)
- npm (comes with Node.js)

### Installation

```bash
# Install test dependencies
./run-tests.sh --install
```

### Running Tests

```bash
# Run automated Jest tests
./run-tests.sh --test

# Run tests with coverage report
./run-tests.sh --coverage

# Open interactive HTML test page
./run-tests.sh --html

# Run all tests and generate reports
./run-tests.sh --all

# Run tests in watch mode (for development)
./run-tests.sh --watch
```

## Test Data

The tests use real product data from the CO2 Assistant API response:

```json
{
  "products": [
    {
      "name": "Sunglasses",
      "price": "$19.99",
      "co2_emissions": "49.0kg (Medium)",
      "eco_score": "9/10",
      "description": "Add a modern touch to your outfits with these sleek aviator sunglasses.",
      "image_url": "/ob-images/static/img/products/sunglasses.jpg"
    },
    {
      "name": "Tank Top",
      "price": "$18.99",
      "co2_emissions": "49.1kg (Medium)",
      "eco_score": "9/10",
      "description": "Perfectly cropped cotton tank, with a scooped neckline.",
      "image_url": "/ob-images/static/img/products/tank-top.jpg"
    }
  ],
  "message": "🌱 Found 9 eco-friendly products for you. Here they are:"
}
```

## Test Results

### Automated Tests (Jest)

The Jest tests validate:
- ✅ Product data structure and validation
- ✅ CO2 emissions parsing and analysis
- ✅ Eco score format and range validation
- ✅ Message processing and CO2 savings extraction
- ✅ User interaction simulation
- ✅ Product display functionality
- ✅ API response validation
- ✅ Performance with large datasets
- ✅ Error handling and edge cases

### Interactive Tests (HTML)

The HTML test page provides:
- Visual product display testing
- Real-time CO2 impact analysis
- Interactive user input simulation
- Responsive design validation
- Manual testing capabilities

## Coverage Reports

Coverage reports are generated in the `reports/coverage/` directory and include:
- Line coverage
- Function coverage
- Branch coverage
- Statement coverage

## Development Workflow

### Adding New Tests

1. **For JavaScript functionality**: Add tests to `test-ui.js`
2. **For visual/interactive testing**: Update `test-ui.html`
3. **For new test utilities**: Update `jest.setup.js`

### Test Patterns

```javascript
// Product validation test
test('should validate product structure', () => {
    expect(product.name).toBeDefined();
    expect(product.price).toMatch(/^\$\d+\.\d{2}$/);
    expect(product.co2_emissions).toContain('kg');
});

// CO2 analysis test
test('should parse CO2 emissions correctly', () => {
    const co2Match = product.co2_emissions.match(/(\d+(?:\.\d+)?)\s*kg/i);
    expect(co2Match).toBeTruthy();
    expect(parseFloat(co2Match[1])).toBeGreaterThan(0);
});

// User interaction test
test('should handle user input correctly', () => {
    const input = 'show me all products';
    expect(input.length).toBeGreaterThan(0);
    expect(typeof input).toBe('string');
});
```

## CI/CD Integration

The tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run UI Tests
  run: |
    cd tests/ui
    ./run-tests.sh --install
    ./run-tests.sh --coverage
```

## Troubleshooting

### Common Issues

1. **Node.js not found**
   ```bash
   # Install Node.js from https://nodejs.org/
   ```

2. **Permission denied on run-tests.sh**
   ```bash
   chmod +x tests/ui/run-tests.sh
   ```

3. **Dependencies not installed**
   ```bash
   ./run-tests.sh --install
   ```

4. **Tests failing**
   ```bash
   # Check test output for specific errors
   ./run-tests.sh --test
   ```

### Debug Mode

Run tests with verbose output:
```bash
npx jest --verbose
```

## Contributing

When adding new UI features:

1. Add corresponding tests to `test-ui.js`
2. Update the HTML test page if needed
3. Ensure all tests pass: `./run-tests.sh --test`
4. Check coverage: `./run-tests.sh --coverage`
5. Update this README with new test descriptions

## Test Environment

The tests run in a simulated browser environment using:
- **Jest** - JavaScript testing framework
- **jsdom** - DOM implementation for Node.js
- **Mock APIs** - Simulated API responses
- **Test Utilities** - Helper functions for common test scenarios

This ensures tests run consistently across different environments without requiring a real browser.
