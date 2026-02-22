const { expect } = require('@jest/globals');
const action = require('../index');

describe('RustChain Badge Action', () => {
  test('should generate correct badge URL', async () => {
    const wallet = 'frozen-factorio-ryan';
    const expectedUrl = `https://img.shields.io/endpoint?url=https://50.28.86.131/api/badge/${wallet}`;
    
    // Mock the core function
    const result = action.generateBadgeUrl(wallet);
    expect(result).toBe(expectedUrl);
  });

  test('should handle invalid wallet name', async () => {
    const wallet = '';
    expect(() => action.generateBadgeUrl(wallet)).toThrow('Wallet name is required');
  });
});