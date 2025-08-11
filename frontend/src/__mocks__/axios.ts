const mockAxiosInstance = {
  get: jest.fn(),
  post: jest.fn(),
  put: jest.fn(),
  delete: jest.fn(),
  interceptors: {
    request: { use: jest.fn(), eject: jest.fn(), clear: jest.fn() },
    response: { use: jest.fn(), eject: jest.fn(), clear: jest.fn() },
  },
};

const axios = {
  create: jest.fn(() => mockAxiosInstance),
  isAxiosError: jest.fn(),
};

export default axios;
export { mockAxiosInstance };