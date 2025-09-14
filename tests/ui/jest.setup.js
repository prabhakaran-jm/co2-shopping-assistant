/**
 * Jest setup file for UI tests
 * Configures the testing environment for CO2-Aware Shopping Assistant UI tests
 */

// Polyfills for Node.js environment
const { TextEncoder, TextDecoder } = require('util');
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;

// Mock fetch for API testing
global.fetch = jest.fn();

// Mock console methods to avoid noise in tests
global.console = {
    ...console,
    log: jest.fn(),
    debug: jest.fn(),
    info: jest.fn(),
    warn: jest.fn(),
    error: jest.fn(),
};

// Mock DOM methods that might not be available in jsdom
Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: jest.fn().mockImplementation(query => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: jest.fn(),
        removeListener: jest.fn(),
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
        dispatchEvent: jest.fn(),
    })),
});

// Mock scroll methods
Object.defineProperty(HTMLElement.prototype, 'scrollIntoView', {
    writable: true,
    value: jest.fn(),
});

Object.defineProperty(HTMLElement.prototype, 'scrollTop', {
    writable: true,
    value: 0,
});

// Mock animation methods
Object.defineProperty(HTMLElement.prototype, 'animate', {
    writable: true,
    value: jest.fn().mockImplementation(() => ({
        finished: Promise.resolve(),
        cancel: jest.fn(),
        pause: jest.fn(),
        play: jest.fn(),
    })),
});

// Setup test timeout
jest.setTimeout(10000);

// Global test utilities
global.testUtils = {
    createMockElement: (tagName = 'div', className = '') => {
        const element = document.createElement(tagName);
        if (className) element.className = className;
        return element;
    },
    
    createMockProduct: (overrides = {}) => ({
        name: 'Test Product',
        price: '$19.99',
        co2_emissions: '49.0kg (Medium)',
        eco_score: '9/10',
        description: 'Test product description',
        image_url: '/test-image.jpg',
        ...overrides
    }),
    
    simulateUserInput: (input) => ({
        target: { value: input },
        preventDefault: jest.fn(),
        key: 'Enter'
    }),
    
    mockAPIResponse: (data) => ({
        ok: true,
        json: () => Promise.resolve(data),
        status: 200
    }),
    
    mockAPIError: (status = 500) => ({
        ok: false,
        status,
        json: () => Promise.resolve({ error: 'API Error' })
    })
};

// Clean up after each test
afterEach(() => {
    jest.clearAllMocks();
    document.body.innerHTML = '';
});
